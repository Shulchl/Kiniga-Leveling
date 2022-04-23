from __future__ import annotations
from asyncio import sleep as asyncsleep

import discord, aiohttp, re, json, io, requests, random, datetime

from random import randint
from io import BytesIO

from discord import File as dFile
from discord import Member as dMember
from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.errors import BadArgument, MissingRequiredArgument

from discord_components import Button, ButtonStyle, Select, SelectOption

from base.utilities import utilities
from base.struct import Config


# CLASS LEVELING
class User(commands.Cog, name='Usuario', description='Comandos de Opções dos Usuários'):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = utilities.database(self.bot.loop, self.bot.cfg.postgresql_user, self.bot.cfg.postgresql_password)
        self.brake = []

        with open('config.json', 'r') as f:
            self.cfg = Config(json.loads(f.read()))

    @commands.cooldown(1, 300, commands.BucketType.member)
    @commands.command(name='nivel', aliases=['rank', 'lv', 'level', 'badge'],
                      help="Monstrará a barra de progressp, bem como a medalha de seu nível.")
    async def nivel(self, ctx, member: dMember = None) -> None:
        if member:
            uMember = member
        else:
            uMember = ctx.author
        result = await self.db.fetch(f"SELECT rank, xp, xptotal FROM users WHERE id='{uMember.id}'")
        if result:
            try:
                if uMember.is_avatar_animated:
                    req = await self.bot.http.request(discord.http.Route("GET", "/users/{uid}", uid=uMember.id))
                    banner_id = req["banner"]
                    assert io.BytesIO(requests.get(
                        f"https://cdn.discordapp.com/banners/{uMember.id}/{banner_id}?size=2048").content).getvalue()
                    profile_bytes = io.BytesIO(requests.get(
                        f"https://cdn.discordapp.com/banners/{uMember.id}/{banner_id}?size=2048").content).getvalue()
                    # await ctx.send(f'https://cdn.discordapp.com/banners/{uMember.id}/{banner_id}?size=2048')

            except:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f'{uMember.avatar_url}?size=512') as resp:
                        profile_bytes = await resp.read()

            total = await self.db.fetch('SELECT COUNT(lv) FROM ranks')
            d = re.sub('\\D', '', str(total))
            if int(d) > 0:
                try:
                    rankss = await self.db.fetch(
                        f"SELECT name, badge, imgxp FROM ranks WHERE lv <= {result[0][0]} ORDER BY lv DESC")
                    if rankss:
                        moldName, moldImg, xpimg = rankss[0][0], rankss[0][1], rankss[0][2]
                    else:
                        moldName, moldImg, xpimg = None, None, None
                except Exception as e:
                    raise e
                buffer = utilities.rankcard.rank(result[0][0], result[0][1], result[0][2], moldName, moldImg, xpimg,
                                                 BytesIO(profile_bytes))
            else:
                await ctx.send('É preciso adicionar alguma classe primeiro.')
            await ctx.send(file=dFile(fp=buffer, filename='profile_card.png'))
        else:
            await ctx.send(f"{uMember.mention}, você ainda não recebeu experiência.")

    @nivel.error
    async def nivel_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                'Você precisa esperar {:.2f} segundos para poder usar este comando de novo.'.format(error.retry_after),
                delete_after=5)

    @commands.cooldown(5, 300, commands.BucketType.member)
    @commands.command(name='pescar', help="Pesca ao digitar s.percar")
    async def pescar(self, ctx):
        await ctx.message.delete()
        if ctx.message.author.id not in self.brake:
            luck = random.choice([True, False])
            if luck:
                try:
                    luckycoin = randint(self.cfg.coinsmin, self.cfg.coinsmax)
                    await self.db.fetch(
                        f"UPDATE users SET coin=(coin + {luckycoin}) WHERE id=(\'{ctx.message.author.id}\')")
                    await ctx.send(f"Você pescou {luckycoin} oris!", delete_after=5)
                    self.brake.append(ctx.message.author.id)
                    await asyncsleep(randint(15, 25))  # randint(15, 25)
                    self.brake.remove(ctx.message.author.id)
                except Exception as e:
                    await ctx.send(e)
            else:
                await ctx.send(f"Você pescou {random.choice(self.bot.cfg.trash)}!", delete_after=10)
                self.brake.append(ctx.message.author.id)
                await asyncsleep(randint(15, 25))  # randint(15, 25)
                self.brake.remove(ctx.message.author.id)

        else:
            raise BucketType.CommandOnCooldown

    @commands.cooldown(1, 86400, commands.BucketType.member)
    @commands.command(
        name='daily',
        aliases=['dl', 'd', 'dia', 'diario', 'checkin', 'presente', 'presença'],
        help="Assina a presença do dia, podendo ganhar oris, xp ou um baú que poderá conter itens diversos.")
    async def daily(self, ctx):
        await ctx.message.delete()
        chest_itens = {'chest': 80, 'ori': 10, 'xp': 10}
        choosed = random.choices(*zip(*chest_itens.items()), k=1)
        oris = randint(self.cfg.coinsmin, self.cfg.coinsmax)
        xp = randint(self.bot.cfg.min_message_xp, self.bot.cfg.max_message_xp)
        if choosed[0] == 'ori':
            oris = randint(self.cfg.coinsmin, self.cfg.coinsmax)
            await ctx.send(f"Você ganhou {oris} oris!")
        elif choosed[0] == 'xp':
            xp = randint(self.bot.cfg.min_message_xp, self.bot.cfg.max_message_xp)
            await ctx.send(f"Você ganhou {xp} de experiência!")
        elif choosed[0] == 'chest':
            chest_prize = [' oris', ' de experiência', ' uma chave']
            emb = discord.Embed(
                title='BAÚ DE RECOMPENSA!',
                description='Você acaba de ganhar um baú, use uma chave para abrí-lo e saber o que tem dentro!',
                color=discord.Color.from_rgb(255, 231, 51)
            )

            emb.set_image(url="https://i.imgur.com/8qp96eb.png")
            emb.timestamp = datetime.datetime.now()

            invent = await self.db.fetch(f"SELECT inv FROM users WHERE id=(\'{ctx.author.id}\')")
            itens = invent[0][0].split(",")
            global key_id
            for i in range(len(itens)):
                item = await self.db.fetch(f"SELECT id, name, type FROM itens WHERE id={int(itens[i])}")
                if item:
                    if item[0][1] == 'Chave' and item[0][2] == 'Utilizavel':
                        key_id = item[0][0]
                        disUse = False
                        disBuy = True
                    else:
                        disUse = True
                        disBuy = False

            msg = await ctx.send(embed=emb,
                                 components=[
                                     [
                                         Button(
                                             label='Usar Chave',
                                             custom_id='use_key',
                                             disabled=disUse,
                                             emoji='🗝'
                                         ),
                                         Button(
                                             label='Comprar Chave',
                                             custom_id='buy_key',
                                             disabled=disBuy,
                                             emoji='💰'
                                         )
                                     ]
                                 ]
                                 )

            # check if user has key

            # Aguardar botão

            interaction = await self.bot.wait_for("button_click",
                                                  check=lambda i: i.message.id == msg.id and i.user.id == ctx.author.id)
            # await ctx.message.delete()
            try:

                # Se uso chave
                if interaction.custom_id == 'use_key':
                    # print(key_id, int(itens.index(key_id)), itens)
                    # print(key_id, itens, int(itens.index(str(key_id))))
                    # itens.remove(key_id)
                    [itens.remove(i) for i in itens if i == str(key_id)]
                    itens = ', '.join(itens)
                    await self.db.fetch(f"UPDATE users SET inv=(\'{itens}\') WHERE id=(\'{ctx.author.id}\')")

                    emb = discord.Embed(
                        title='BAÚ DE RECOMPENSA!',
                        description='Você utilizou uma chave para abrir o baú. Veja abaixo o que recebeu!',
                        color=discord.Color.from_rgb(255, 231, 51)
                    )

                    emb.set_image(url='https://i.imgur.com/DXSJmJ6.png')
                    emb.timestamp = datetime.datetime.now()

                    emb.add_field(name=f"Você ganhou...", value=f"{oris} {chest_prize[0]} e {xp} {chest_prize[1]}!",
                                  inline=True)

                    await interaction.respond(embed=emb)
                    await msg.delete()

                # Se quer comprar chave
                elif interaction.custom_id == 'buy_key':
                    key_value = await self.db.fetch(f"SELECT id, value FROM itens WHERE name='Chave'")
                    if key_value:
                        await self.db.fetch(
                            f"UPDATE users SET coin=(coin - {key_value[0][1]}) WHERE id=(\'{ctx.author.id}\')")
                    else:
                        return interaction.respond(
                            "Não foi possível comprar uma chave, pois aparentemente não há nenhuma na loja. \nContate "
                            "algum administrador.")

                    emb = discord.Embed(
                        title='BAÚ DE RECOMPENSA!',
                        description='Você comprou e utilizou uma chave para abrir o baú. Veja abaixo o que recebeu!',
                        color=discord.Color.from_rgb(255, 231, 51)
                    )

                    emb.set_image(url='https://i.imgur.com/DXSJmJ6.png')
                    emb.timestamp = datetime.datetime.now()

                    emb.add_field(name=f"Você ganhou...", value=f"{oris} {chest_prize[0]} e {xp} {chest_prize[1]}!",
                                  inline=True)

                    await interaction.respond(embed=emb)
                    await msg.delete()
                else:
                    raise


            except Exception as e:
                raise e

    @daily.error
    async def daily_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f'Você precisa esperar {str(datetime.timedelta(seconds=error.retry_after))[:-7]} horas para poder '
                f'usar este comando de novo.',
                delete_after=5)

    @commands.cooldown(1, 300, commands.BucketType.member)
    @commands.command(name='topori',
                      help='Ao digitar s.topori , mostra o TOP 5 mais ricos do servidor.',
                      aliases=["top", "ts"])
    # @commands.cooldown(1, 120, BucketType.user)
    async def topori(self, ctx):
        member = ctx.message.author
        total = await self.db.fetch('SELECT COUNT(rank) FROM users')
        for t in total:
            d = re.sub(r"\D", "", str(t))
            d = int(d)
            result = await self.db.fetch(
                f'SELECT id, rank, coin FROM users ORDER BY coin DESC FETCH FIRST 10 ROWS ONLY')
            if result:
                emb = discord.Embed(title='TOP 10 MAIS RICOS DA KINIGA',
                                    description='Aqui estão listados as dez pessoas que mais tem oris no servidor.',
                                    color=discord.Color.blue())
                count_line = 0
                while count_line <= d - 1:
                    membId = result[count_line][0]
                    if membId is self.bot.user.id:
                        count_line += 1
                        membId = result[count_line][0]
                    rank = result[count_line][1]
                    oris = result[count_line][2]
                    user = [user.name for user in ctx.guild.members if user.id == int(membId)]
                    emb = emb.add_field(
                        name=f"{count_line + 1}º — {''.join(user) if user else 'Anônimo'}, Nível {rank}",
                        value=f"{oris} oris", inline=False)
                    count_line += 1

                num = await self.db.fetch(
                    f"WITH temp AS (SELECT id, row_number() OVER (ORDER BY coin DESC) AS rownum FROM users) SELECT "
                    f"rownum FROM temp WHERE id = '{member.id}'")
                member_row = re.sub(r"\D", "", str(num))
                member_details = await self.db.fetch(f"SELECT rank, coin FROM users WHERE id='{member.id}'")
                rank = member_details[0][0]
                oris = member_details[0][1]
                emb = emb.add_field(name=f"Sua posição é {int(member_row)}º — {member.name}, Nível {rank}",
                                    value=f"{oris} oris", inline=False)
                await ctx.send('', embed=emb)

    #   classe
    @commands.cooldown(1, 300, commands.BucketType.member)
    @commands.command(name='classes',
                      help='Ao digitar s.classes , mostra todas as classes disponíveis.',
                      aliases=["ranks", "niveis"])
    async def classes(self, ctx):
        await self.db.fetch(
            'CREATE TABLE IF NOT EXISTS ranks (lv INT NOT NULL, name TEXT NOT NULL, localE TEXT NOT NULL, '
            'localRR TEXT NOT NULL, sigla TEXT, path TEXT)')
        total = await self.db.fetch(f'SELECT COUNT(lv) FROM ranks')
        for t in total:
            d = re.sub(r"\D", "", str(t))
            if int(d) > 0:
                emb = discord.Embed(title='Todos as classes',
                                    description='Aqui estão listados todos as classes no servidor.',
                                    color=discord.Color.blue()).set_footer(
                    text='Os números ao lado da classe representam seu nível mínimo, ou seja,\n'
                         'ao chegar ao nível, você terá atingido sua classe correspondente.')
                count = 0
                # await ctx.send(int(d))
                while int(count) < int(d) - 1:
                    try:
                        rows = await self.db.fetch('SELECT * FROM ranks ORDER BY lv ASC')
                        for row in rows:
                            # await ctx.send(row)
                            rank_lv = row[0]
                            rank_name = row[1]
                            emb = emb.add_field(name=f"Nível {rank_lv}", value=f"{rank_name}", inline=False)
                            count += 1
                    except:
                        break
                await ctx.send('', embed=emb)
            else:
                await ctx.send("```Parece que não temos nenhuma classe ainda...```", delete_after=5)

    # info
    @commands.cooldown(2, 300, commands.BucketType.member)
    @commands.command(name='info',
                      help='Ao digitar s.info "Texto-Para-Perfil-Aqui" (é preciso que o texto esteja entre aspas '
                           'DUPLAS), define o texto de informação que aparecerá em seu s.perfil.',
                      aliases=["status", "bio"])
    async def info(self, ctx, *, content) -> None:
        info = ("").join(content)
        size = len(info)
        if size > 55:
            raise BadArgument

        await self.db.fetch(f'UPDATE users SET info = (\'{info}\') WHERE id = (\'{ctx.author.id}\')')
        await ctx.send("```Campo de informações atualizado. Visualize utilizando d.perfil```", delete_after=5)

    @info.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send("O texto deve conter 55 palavras ou menos, contando espaços.", delete_after=5)

    @commands.cooldown(1, 300, commands.BucketType.member)
    @commands.command(name='delinfo',
                      help='Ao digitar s.delinfo, remove o texto de informação atual do seu s.perfil e substitui por '
                           '"Não há o que bisbilhotar aqui".')
    async def delinfo(self, ctx) -> None:
        await self.db.fetch(f'UPDATE users SET info = (\'\') WHERE id = (\'{ctx.author.id}\')')
        await ctx.send("```Campo de informações atualizado. Visualize utilizando d.perfil```", delete_after=5)

    # bday
    @commands.cooldown(1, 86400, commands.BucketType.member)
    @commands.command(name='niver',
                      help='Ao digitar s.niver <dia/mês>, define a data de aniversário presente em seu s.perfil.'
                           '(NÃO COLOQUE ANO! É preciso que sejam números separados por uma barra. você pode fazer '
                           'aniversário dia 99, por exemplo. Seja criativo!).',
                      aliases=["aniversario", "aniversário", "aniver"], )
    async def niver(self, ctx, niver) -> None:
        niver = niver.split("/")
        dia = niver[0]
        mes = niver[1]

        await ctx.message.delete()
        await self.db.fetch(f'UPDATE users SET birth = (\'{dia}/{mes}\') WHERE id = (\'{ctx.author.id}\')')

        await asyncsleep(2)
        await ctx.send("```Aniversário atualizado!```", delete_after=3)

    @niver.error
    async def niver_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f'Você precisa esperar {str(datetime.timedelta(seconds=error.retry_after))[:-7]} horas para poder '
                f'usar este comando de novo.',
                delete_after=5)

    @commands.cooldown(2, 300, commands.BucketType.member)
    @commands.command(name='delniver',
                      help='Ao digitar s.delniver, remove o a data de aniversário atual do seu s.perfil e substitui '
                           'por "??/??".')
    async def delniver(self, ctx) -> None:
        await self.db.fetch(f'UPDATE users SET birth = (\'???\') WHERE id = (\'{ctx.author.id}\')')
        await ctx.send("```Aniversário atualizado!```", delete_after=5)

    @commands.cooldown(1, 300, commands.BucketType.member)
    @commands.command(name='inv',
                      help='Ao digitar s.inv, mostra todos os itens que você possui. Incluindo os que não podem mais '
                           'ser obtidos na s.loja.',
                      aliases=["inventário", "inventario", "bag", "bolsa", "mochila"])
    async def inv(self, ctx):
        invent = await self.db.fetch(f"SELECT inv FROM users WHERE id=(\'{ctx.author.id}\')")
        if invent:
            inv = invent[0][0]
            if inv != None:
                inv = inv.split(",")
                total = len(inv)
                if total > 0:
                    emb = discord.Embed(title='INVENTÁRIO',
                                        description=f'Aqui estão todos os seus itens.',
                                        color=discord.Color.green())
                    await ctx.message.delete()
                    itens = str(invent[0][0]).split(",")
                    for i in range(len(itens)):
                        item = await self.db.fetch(f"SELECT id, name, type FROM itens WHERE id={int(itens[i])}")
                        if item:
                            emb = emb.add_field(name=f"{item[0][1].upper()}", value=f"{item[0][2]} | ID: {item[0][0]}",
                                                inline=True)
                        else:
                            emb = emb.add_field(name=f"-", value=f"-", inline=True)
                await ctx.send(embed=emb, delete_after=30)
            else:
                return await ctx.send("Você ainda não comprou nada!", delete_after=5)


def setup(bot) -> None:
    bot.add_cog(User(bot))
