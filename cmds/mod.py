from __future__ import annotations

import asyncio
import datetime
import json
import random
import uuid
from asyncio import sleep as asyncsleep

import discord
import discord.utils
from base.functions import (convert, giveway_idFunction, starterRoles, starterItens, timeRemaning)
from base.image import ImageCaptcha
from base.struct import Config
from base.utilities import utilities
from discord import File as dFile
from discord.ext import commands, tasks
from typing import Literal
from typing import Optional

import aiohttp
from io import BytesIO
import requests


class Mod(commands.Cog, name='Moderação'):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = utilities.database(
            self.bot.loop, self.bot.cfg.postgresql_user, self.bot.cfg.postgresql_password)
        self.chosen = [ ]

        if self.bot.cfg.bdayloop:
            self.bdayloop.start()

    def cog_unload(self):
        self.bdayloop.close()

    # CONFIG

    @commands.command(name='sorteio')
    @commands.has_any_role(
        667839130570588190,
        815704339221970985,
        677283492824088576,
        'Administrador',
        'Admin',
        943171518895095869,
        943174476839936010,
        943192163947274341,
        943172687642132591,
        943171893752659979,
        943172687642132591,
        943193084584402975,
        943251043838468127)
    async def sorteio(self, ctx):
        await ctx.send("Responda em 15 segundos.\n")
        q = [ "Onde você quer que o sorteio aconteça? (marque o canal)",
              "Quanto tempo o sorteio vai durar?",
              "Qual é o prêmio?" ]

        ans = [ ]

        def validation(currentMessage):
            return currentMessage.author == ctx.author and currentMessage.channel == ctx.channel

        for i in q:
            await ctx.send(i)

            try:
                msg = await self.bot.wait_for('message', timeout=15.0, check=validation)
            except asyncio.TimeoutError:
                await ctx.send('Você não respondeu a tempo.', delete_after=5)
                return
            else:
                ans.append(msg.content)
        try:
            channel_id = int(ans[ 0 ][ 2:-1 ])
        except Exception as e:
            return await ctx.send(f"Não consegui encontrar esse canal. {e}", delete_after=5)

        channel = self.bot.get_channel(channel_id)

        time = convert(ans[ 1 ])
        if time == -1:
            await ctx.send("Não consegui entender o tempo, por favor, use s|m|h|d", delete_after=10)
            return
        elif time == -2:
            await ctx.send("O tempo tem que ser em números inteiros.", delete_after=5)
            return
        global prize
        prize = ans[ 2 ]
        if prize.startswith("#"):
            pName = await self.db.fetch(f"SELECT name, id FROM itens WHERE id ='{int(prize.strip('#'))}'")
            if pName:
                prize = pName[ 0 ][ 0 ]
        await ctx.send(f"O sorteio ocorrerá em {channel.mention} e vai durar {ans[ 1 ]}!")

        # embed = discord.Embed(
        #     title="Giveaway!",
        #     description=f"{prize}",
        #     color= 0x006400
        # )
        # embed.add_field(
        #     name="Hosted by:",
        #     value=ctx.author.mention
        # )
        # embed.set_footer(
        #     text=f"Ends {ans[1]} from now!"
        # )
        end = datetime.timedelta(seconds=(3600 * 5)) + \
              datetime.timedelta(seconds=time)
        embed = discord.Embed(
            title=f"Reaja com 🎉 para ganhar **{prize}**!\nTempo até o vencedor ser decidido:  **{timeRemaning(time)}**",
            description="",
            color=0x006400
        )
        embed.set_author(name=f'{prize}', icon_url='')
        embed.add_field(
            name=f"Criado por:",
            value=ctx.author.mention
        )
        embed.set_footer(
            text=f"Sorteio irá durar por {ans[ 1 ]}\n. {end} por enquanto!")
        # await ctx.send(file=discord.File('./src/extra/ori.png'))

        my_msg = await channel.send(embed=embed)
        giveaway_messageId = await giveway_idFunction(my_msg.id)

        await my_msg.add_reaction("🎉")
        await asyncio.sleep(time)

        new_msg = await channel.fetch_message(my_msg.id)
        users = await new_msg.reactions[ 0 ].users().flatten()
        users.pop(users.index(self.bot.user))

        winner = random.choice(users)

        # // {winner.mention} ganhou {prize}
        await channel.send(
            f"Parabéns, {winner.mention}!.\nVocê tem 1 minuto para falar no canal, do contrário o sorteio será refeito.")
        await channel.set_permissions(winner, send_messages=True)

        # await channel.send(winner.id)

        def winner_validation(currentMessage):
            return currentMessage.author == winner and currentMessage.channel == channel

        try:
            msg = await self.bot.wait_for('message', timeout=10.0, check=winner_validation)
            if prize.startswith("#"):
                invent = await self.db.fetch(f"SELECT inv FROM users WHERE id=(\'{winner.id}\')")
                if invent:
                    if str(pName[ 0 ][ 1 ]) in invent[ 0 ][ 0 ].split(","):
                        await ctx.send(
                            f'Que pena! {winner.mention} já tem esse item, então terei que refazer o sorteio...')
                        await channel.set_permissions(winner, send_messages=False)
                        await asyncsleep(5)
                        await self.bot.loop.create_task(self.reroll(ctx, channel, winner))
                    else:
                        await self.db.fetch(
                            f"UPDATE users SET inv = (\'{str(invent[ 0 ][ 0 ]) + ',' + str(pName[ 0 ][ 1 ])}\') WHERE id=(\'{winner.id}\') ")
                        await channel.send(f"Parabéns! {winner.mention} acaba de ganhar {prize}.")
                        await channel.set_permissions(winner, send_messages=False)
            else:
                await channel.send(f"Parabéns! {winner.mention} acaba de ganhar {prize}.")
                await channel.set_permissions(winner, send_messages=False)
        except asyncio.TimeoutError:
            await ctx.send(f'Que pena, {winner}, mas terei que refazer o sorteio...')
            await channel.set_permissions(winner, send_messages=False)
            await asyncsleep(5)
            await self.bot.loop.create_task(self.reroll(ctx, channel, winner))

        return giveaway_messageId

        # REROLL

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        channel = self.bot.get_channel(payload.channel_id)
        if payload.message_id == giveway_idFunction.ids and payload.user_id != self.bot.user.id:
            message = await channel.fetch_message(payload.message_id)
            user = (self.bot.get_user(payload.user_id))
            if not user:
                user = await self.bot.fetch_user(payload.user_id)

            # if payload.emoji != '🎉':
            #    await message.remove_reaction(payload.emoji, user)

            try:
                inv = await self.db.fetch(f"SELECT inv FROM users WHERE id=('{user.id}')")
                itens = inv[ 0 ][ 0 ].split(',')
                j = [ [ t[ 0 ][ 0 ], t[ 0 ][ 1 ] ] for t in
                      [ (await self.db.fetch(f"SELECT id, name FROM itens WHERE id=('{i}')")) for i in itens ] if
                      str(t[ 0 ][ 1 ]) == 'Ticket' ]
                # await channel.send(str(j[0][0]) if j else "Nada")
                for l in j:
                    await channel.send(
                        "Descontarei um ticket de seu inventário. Você poderá comprar outro na loja a qualquer momento.")
                    if str(j[ 0 ][ 1 ]).title() == "Ticket".title():
                        itens.remove(str(j[ 0 ][ 0 ]))
                        await self.db.fetch(f"UPDATE users SET inv = ('{','.join(itens)}')")
                else:
                    await message.remove_reaction(payload.emoji, user)
                    await channel.send(f"{user.mention}, você precisa comprar um ticket primeiro.")

            except Exception as e:
                raise e

    @commands.has_any_role(
        667839130570588190,
        815704339221970985,
        677283492824088576,
        'Administrador',
        'Admin',
        943171518895095869,
        943174476839936010,
        943192163947274341,
        943172687642132591,
        943171893752659979,
        943172687642132591,
        943193084584402975,
        943251043838468127
    )
    @commands.command(aliases=[ "rr" ], name='reroll',
                      help='SÓ PARA EQUIPE! \n Ao digitar s.reroll <#canal-do-sorteio> <@último-ganhador>, refaz o sorteio.')
    async def reroll(self, ctx, channel: discord.TextChannel, lastWinner: discord.Member):
        try:
            new_msg = await channel.fetch_message(giveway_idFunction.ids)
        except:
            return await ctx.send("O ID fornecido é incorreto")

        users = await new_msg.reactions[ 0 ].users().flatten()
        users.pop(users.index(self.bot.user))
        nWinner = random.choice(users)
        while lastWinner == nWinner:
            nWinner = random.choice(users)
        await channel.send(f"Parabéns! {nWinner.mention} acaba de ganhar {prize}.")

    # LOOP DE ANIVERSÁRIO // BDAY LOOP
    @tasks.loop(seconds=10, count=1)
    async def bdayloop(self):
        channel = self.bot.get_channel(int(self.bot.cfg.chat_cmds))
        await channel.send("Verificando aniversariantes...", delete_after=5)
        await asyncsleep(5)
        birthday = await self.db.fetch("SELECT id FROM users WHERE birth=TO_CHAR(NOW() :: DATE, 'dd/mm')")

        for bday in birthday:
            await channel.send(f"Parabéns <@{bday[ 0 ]}>, hoje é seu aniversário! Todos dêem parabéns!")

    @bdayloop.before_loop  # wait for the bot before starting the task
    async def before_send(self):
        await self.bot.wait_until_ready()
        return

    # Controle de loop
    @commands.has_permissions(administrator=True)
    @commands.command(name='bdl')
    async def bdl(self, ctx, opt):
        if opt == "on":
            await ctx.send("Iniciando...", delete_after=2)
            await asyncsleep(2)
            with open('config.json', 'r+') as g:
                data = json.load(g)
                data[ 'bdayloop' ] = True
                g.seek(0)
                await asyncsleep(1)
                json.dump(data, g, indent=4)
                g.truncate()
                await self.bdayloop.start()
        if opt == "off":
            await ctx.send("Desligando...", delete_after=2)
            await asyncsleep(2)
            with open('config.json', 'r+') as g:
                data = json.load(g)
                data[ 'bdayloop' ] = False
                g.seek(0)
                await asyncsleep(1)
                json.dump(data, g, indent=4)
                g.truncate()
                await self.bdayloop.close()

    @commands.command(name='clear', help='Limpa um determinado número de mensagens ao digitar `.clear <número>`')
    @commands.has_any_role(
        943171518895095869,
        943174476839936010,
        943192163947274341,
        943172687642132591,
        943171893752659979,
        943172687642132591,
        943193084584402975,
        943251043838468127,

        855117820814688307
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def clear(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount + 1)
        emb = discord.Embed(title='Limpei!', description='{} mensagens foram apagadas!'.format(amount),
                            color=discord.Color.red())
        await ctx.send('', embed=emb, delete_after=3)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.UserInputError):
            await ctx.send('Você precisa colocar o número de mensagem que deseja apagar.')
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                'Você precisa esperar {:.2f}s, para poder usar esse comando de novo.'.format(
                    error.retry_after),
                delete_after=5)
        else:
            await ctx.send(error)

    @commands.is_owner()
    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.member)
    async def load(self, ctx, extension):
        await self.bot.load_extension(f'cmds.{extension}')
        await ctx.reply("Carreguei os comandos")

    @load.error
    async def load_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                'Você precisa esperar {:.2f}s, para poder usar esse comando de novo.'.format(
                    error.retry_after),
                delete_after=5)

    @commands.is_owner()
    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.member)
    async def reload(self, ctx, extension):
        await self.bot.unload_extension(f'cmds.{extension}')
        await self.bot.load_extension(f'cmds.{extension}')
        await ctx.reply("Recarreguei os comandos")

    @reload.error
    async def reload_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                'Você precisa esperar {:.2f}s, para poder usar esse comando de novo.'.format(
                    error.retry_after),
                delete_after=5)

    @commands.is_owner()
    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.member)
    async def unload(self, ctx, extension):
        await self.bot.unload_extension(f'cmds.{extension}')
        await ctx.reply("Descarreguei os comandos")

    @unload.error
    async def unload_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                'Você precisa esperar {:.2f}s, para poder usar esse comando de novo.'.format(
                    error.retry_after),
                delete_after=5)

    @commands.is_owner()
    @commands.command()
    @commands.cooldown(1, 300, commands.BucketType.member)
    async def shutdown(self, ctx):
        if ctx.message.author.id == 179440483796385792:
            await ctx.message.delete()
            print((("-" * 20) + "shutdown" + ("-" * 20)))
            try:
                await self.bot.close()
            except Exception as e:
                raise await self.bot.clear(e)
            else:
                await ctx.reply("Deu merda aqui em. Melhor ver isso logo...")

        else:
            await ctx.send("You do not own this bot!")

    @commands.has_permissions(administrator=True)
    @commands.command(name="tsql")
    async def tsql(self, ctx, *, sql: str) -> None:
        output = await self.db.fetch(sql)
        await ctx.send(f'```{output}```')

    @commands.has_permissions(administrator=True)
    @commands.command(name="tsqlist")
    async def tsqlist(self, ctx, *, sql: str) -> None:
        output = await self.db.fetchList(sql)
        await ctx.send(f'```{output}```')

    @commands.is_owner()
    @commands.command(name="sync")
    @commands.guild_only()
    async def sync(self, ctx, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        if not guilds:
            if spec == "~":
                synced = await self.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                self.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await self.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                self.bot.tree.clear_commands(guild=ctx.guild)
                await self.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await self.bot.tree.sync()

            await ctx.send(
                f"Sincronizei {len(synced)} comandos {'globalmente' if spec is None else 'ao servidor atual.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Trees sincronizadas em {ret}/{len(guilds)} servidores.")

    @commands.command(name='ranking')
    async def ranking(self, ctx, opt: Optional[Literal["Ori", "Nivel"]]):
        await ctx.message.delete()
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{ctx.author.display_avatar.url}?size=1024?format=png") as resp:
                profile_bytes = await resp.read()

        

        if opt == "Ori":
            rows = await self.db.fetch(
                        "SELECT id, coin FROM users ORDER BY coin Desc")
        elif opt == "Nivel":
            rows = await self.db.fetch(
                        "SELECT id, rank, xptotal FROM users ORDER BY xptotal Desc")
        if rows:
            user_position = 0
            count = 0
            # if (total/3) > int(total/3):
            #    return await ctx.send(f"O limite de páginas é {int(total/3)}", delete_after=5)
            # elif (total/3) < int(total/3):
            #    return await ctx.send(f"O limite de páginas é {int(total/3)+1}", delete_after=5)
            try:
                users = []
                while count < len(rows):
                    user = ctx.guild.get_member(int(rows[count][0]))
                    if user.name == ctx.author.name:
                        user_position = count
                    avatar = user.display_avatar.url
                    rank_image = await self.db.fetch(f"SELECT badges FROM ranks WHERE lv <= {rows[count][1]} ORDER BY lv Desc LIMIT 1")
                    if rank_image:
                        users.append({count: {
                            "avatar_url": str(avatar),
                            "name": str(user),
                            "value": str(rows[count][2]) if opt == "Nivel" else str(rows[count][1]),
                            "type": str(opt),
                            "rank_image": str(rank_image[0][0]) if opt == "Nivel" else "",
                        }})

                    count += 1
            except Exception:
                raise
        async with ctx.channel.typing():
            buffer = await utilities.topcard.topdraw(ctx.author.id, users, user_position, BytesIO(profile_bytes))
        await ctx.send(file=dFile(fp=buffer, filename='ranking.png'))

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Mod(bot))
