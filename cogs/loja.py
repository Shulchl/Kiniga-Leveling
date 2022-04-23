from __future__ import annotations

import re
from asyncio import sleep as asyncsleep
from io import BytesIO
from random import randint

import aiohttp
import discord
from base.utilities import utilities
from discord import File as dFile
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.errors import BadArgument, MissingRequiredArgument

from discord_components import Button, ButtonStyle, Select, SelectOption


# CLASS SHOP


class Shop(commands.Cog, name='Loja', description='Comandos de Opções Loja'):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = utilities.database(
            self.bot.loop, self.bot.cfg.postgresql_user, self.bot.cfg.postgresql_password)

    async def nextPage(self, ctx, page, member: discord.Member):
        return await self.loja(ctx, page, member)

    #   LOJA
    @commands.cooldown(1, 500, commands.BucketType.member)
    @commands.max_concurrency(100, per=commands.BucketType.guild, wait=500)
    @commands.command(name='loja',
                      help='Ao digitar s.loja, mostra a loja, com diversas molduras e títulos para comprar!',
                      aliases=["shop", "lojinha"])
    async def loja(self, ctx, page: int = None, member: discord.Member = None) -> None:
        if member:
            uMember = member
        else:
            uMember = ctx.author or ctx.guild.get_member(member)

        total = await self.db.fetch('SELECT COUNT(id) FROM itens WHERE canbuy = True')
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{uMember.avatar_url_as(format="png", size=1024)}') as resp:
                userImg = await resp.read()
        for t in total:
            d = re.sub(r"\D", "", str(t))
            total = int(d)
            if total > 0:
                if not page:
                    page = 1
                rows = await self.db.fetch(
                    "SELECT id, name, type, value, img, imgd, lvmin, dest FROM itens WHERE canbuy = True ORDER BY id "
                    "Desc")
                if rows:
                    count = 0
                    # if (total/3) > int(total/3):
                    #    return await ctx.send(f"O limite de páginas é {int(total/3)}", delete_after=5)
                    # elif (total/3) < int(total/3):
                    #    return await ctx.send(f"O limite de páginas é {int(total/3)+1}", delete_after=5)
                    try:
                        itens = []
                        while count < total:
                            itens.append({count: {
                                "id": str(rows[count][0]),
                                "name": str(rows[count][1]),
                                "type": str(rows[count][2]),
                                "value": str(rows[count][3]),
                                "img": str(rows[count][4]),
                                "imgs": str(rows[count][5]),
                                "lvmin": str(rows[count][6]),
                                "dest": str(rows[count][7])
                            }})

                            count += 1
                    except Exception:
                        raise
                    for coin in await self.db.fetch(f'SELECT coin FROM users WHERE id = (\'{uMember.id}\')'):
                        if coin[0] == None:
                            coin[0] = 0
                        coin = coin[0]
                    buffer = utilities.shop.drawloja(
                        total, itens, page, coin, BytesIO(userImg))  # byteImg

                    page = int(page)
                    # count = 1
                    # opt = dict()

                    # while ((((page+count)*6)-5) ** 0.5 <= total ** 0.5):
                    #    opt = (
                    #            SelectOption(
                    #                label=str(count), value=str(count)
                    #            )
                    #        )
                    #    count +=1

                    components = [
                        Button(style=ButtonStyle.blue,
                               label="Página Anterior",
                               custom_id=str(page - 1),
                               emoji="⏪",
                               disabled=True if (page - 1 <= 0) else False),
                        Button(style=ButtonStyle.blue,
                               label="Próxima Página",
                               custom_id=str(page + 1),
                               emoji="⏩",
                               disabled=False if ((((page + 1) * 6) - 5) ** 0.5 <= total ** 0.5) else True),
                    ]

                    msg = await ctx.reply(file=dFile(fp=buffer, filename='lojinha.png'),
                                          components=[components],
                                          )
                    interaction = await self.bot.wait_for("button_click", check=lambda
                        i: i.message.id == msg.id and i.user.id == uMember.id)
                    try:
                        await interaction.message.delete()
                        await self.nextPage(ctx, int(interaction.custom_id), interaction.user)
                    except Exception as e:
                        await ctx.send(e)
                else:
                    await ctx.reply(f'{uMember.mention}, parece que ainda não temos nenhum item comprável.')

    @loja.error
    async def loja_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.message.delete()
            return await ctx.send(
                "```Só um usuário pode usar esse comando por vez, por favor aguarde {:.2f} segundos.```".format(
                    error.retry_after), delete_after=5)
        elif isinstance(error, commands.MaxConcurrencyReached):
            await ctx.message.delete()
            return await ctx.send('Estou muito ocupada, tenve novamente em {:.2f}'.format(error.retry_after),
                                  delete_after=5)
        else:
            await ctx.message.delete()
            return print('{}'.format(error))

    #   Comprar
    @commands.cooldown(1, 30, commands.BucketType.member)
    @commands.command(name='comprar',
                      help='Ao digitar s.comprar <ID-DO-ITEM>, efetua a compra de um item utilizando o ID deste na '
                           'loja.',
                      aliases=["buy", "compra"])
    async def comprar(self, ctx, id: int) -> None:
        # await ctx.message.delete()
        item = await self.db.fetch(
            f'SELECT id, name, value, type, lvmin FROM itens WHERE id=\'{id}\' and canbuy = True')
        if item:
            item_id, item_name, item_value, item_type, lvmin = item[
                                                                   0][0], item[0][1], item[0][2], item[0][3], item[0][4]
            try:
                inv = await self.db.fetch(f'SELECT coin, inv, rank FROM users WHERE id = (\'{ctx.author.id}\')')
                if inv:
                    if int(lvmin - 9) <= int(inv[0][2]):
                        if int(inv[0][0]) >= int(item_value):
                            if item_type == 'Moldura':
                                tipo, esstipo = "a moldura", "essa moldura"
                            elif item_type == 'Titulo':
                                tipo, esstipo = "o título", "esse título"
                            else:
                                tipo, esstipo = "o/a " + str(item_type), "esse item"
                            emb = discord.Embed(
                                title='Bela compra!',
                                description=f'Você acaba de comprar {tipo} {item_name}!',
                                color=discord.Color.green()
                            ).set_footer(
                                text='Para equipar em seu perfil, basta digitar:\n'
                                     's.equipar'
                            )

                            if inv[0][1] is not None:
                                invent = str(inv[0][1])
                                if str(id) in invent.split(","):
                                    return await ctx.send(f"Você já tem {esstipo}.", delete_after=5)
                                else:
                                    return await self.db.fetch(
                                        f'UPDATE users SET inv = (\'{str(invent) + "," + str(item_id)}\'), coin = ({int(inv[0][0]) - int(item_value)})  WHERE id=\'{ctx.author.id}\'')
                            else:
                                await self.db.fetch(
                                    f'UPDATE users SET inv = (\'{item_id}\'), coin = ({int(inv[0][0]) - int(item_value)}) WHERE id=\'{ctx.author.id}\'')
                            return await ctx.send(embed=emb, delete_after=10)
                        else:
                            return await ctx.send("Você é pobre, vá trabalhar.", delete_after=5)
                    else:
                        return await ctx.send("Você não tem nível para comprar isso.", delete_after=5)
                else:
                    return await ctx.send(
                        "Aconteceu algo enquanto eu tentava buscar as informações do usuário. Tente novamente mais "
                        "tarde.",
                        delete_after=5)
            except:
                raise
        else:
            return await ctx.send(
                f'{ctx.author.mention}, ou não existe um item com esse número(ID) ou o item não está disponível para '
                f'compra.',
                delete_after=5)

    #

    #   Equipar
    @commands.cooldown(1, 300, commands.BucketType.member)
    @commands.command(name='equipar',
                      help='Ao digitar s.equipar <ID-DO-ITEM>, equipa em seu s.perfil, um item do seu inventário, '
                           'utilizando o ID deste.')
    async def equipar(self, ctx, id: int):
        await ctx.message.delete()
        item = await self.db.fetch(f"SELECT name, type FROM itens WHERE id='{id}'")
        if item:
            name = item[0][0]
            type = item[0][1]

            inv = await self.db.fetch(f"SELECT inv FROM users WHERE id='{ctx.author.id}'")
            if inv:
                inv = str(inv[0][0]).split(",")
                if str(id) in inv:
                    if str(type).upper() == "MOLDURA":
                        await self.db.fetch(f"UPDATE users SET mold=(\'{id}\') WHERE id='{ctx.author.id}'")
                        await ctx.send("{} {} equipada!".format(type.capitalize(), name.title()), delete_after=5)
                    if str(type).upper() == "TITULO":
                        await self.db.fetch(f"UPDATE users SET title=(\'{id}\') WHERE id='{ctx.author.id}'")
                        await ctx.send("{} {} equipada!".format(type.capitalize(), name.title()), delete_after=5)
            else:
                raise MissingRequiredArgument
        else:
            raise BadArgument

    #   Equipar
    @commands.cooldown(1, 300, commands.BucketType.member)
    @commands.command(name='desequipar',
                      help='Ao digitar s.equipar <ID-DO-ITEM>, equipa em seu s.perfil, um item do seu inventário, '
                           'utilizando o ID deste.')
    async def desequipar(self, ctx, id: int):
        await ctx.message.delete()
        item = await self.db.fetch(f"SELECT name, type FROM itens WHERE id='{id}'")
        if item:
            name = item[0][0]
            type = item[0][1]

            inv = await self.db.fetch(f"SELECT inv FROM users WHERE id='{ctx.author.id}'")
            if inv:
                inv = str(inv[0][0]).split(",")
                if str(id) in inv:
                    if str(type).upper() == "MOLDURA":
                        await self.db.fetch(f"UPDATE users SET mold=Null WHERE id='{ctx.author.id}'")
                        await ctx.send("{} {} desequipada!".format(type.capitalize(), name.title()), delete_after=5)
                    if str(type).upper() == "TITULO":
                        await self.db.fetch(f"UPDATE users SET title=Null WHERE id='{ctx.author.id}'")
                        await ctx.send("{} {} desequipada!".format(type.capitalize(), name.title()), delete_after=5)
            else:
                raise MissingRequiredArgument
        else:
            raise BadArgument

    @equipar.error
    async def equipar_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("```Esse item não existe.```", delete_after=5)
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("```Você não tem esse item.```", delete_after=5)


def setup(bot) -> None:
    bot.add_cog(Shop(bot))