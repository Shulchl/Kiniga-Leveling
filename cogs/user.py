from __future__ import annotations
from asyncio import sleep as asyncsleep

import discord, aiohttp, re, json, io, requests, random

from random import randint
from io import BytesIO

from discord import File as dFile
from discord import Member as dMember
from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.errors import BadArgument, MissingRequiredArgument

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

    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.command(name='rank', aliases=['nivel', 'lv', 'level', 'badge'])
    async def rank(self, ctx, member: dMember=None) -> None:
        if member:
            uMember = member
        else:
            uMember = ctx.author
        result = await self.db.fetch(f"SELECT rank, xp, xptotal FROM users WHERE id='{uMember.id}'")
        if result:
            #try:
            #    if uMember.is_avatar_animated:
            #        req = await self.bot.http.request(discord.http.Route("GET", "/users/{uid}", uid=uMember.id))
            #        banner_id = req["banner"]
            #        assert io.BytesIO(requests.get(f"https://cdn.discordapp.com/banners/{uMember.id}/{banner_id}?size=2048").content).getvalue()
            #        profile_bytes = io.BytesIO(requests.get(f"https://cdn.discordapp.com/banners/{uMember.id}/{banner_id}?size=2048").content).getvalue()
            #            #await ctx.send(f'https://cdn.discordapp.com/banners/{uMember.id}/{banner_id}?size=2048')

            #except:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{uMember.avatar_url}?size=512') as resp:
                    profile_bytes = await resp.read()
                    assert profile_bytes

            total = await self.db.fetch('SELECT COUNT(lv) FROM ranks')
            d = re.sub('\\D', '', str(total))
            if int(d) > 0:
                try:
                    rankss = await self.db.fetch(f"SELECT name, r, g, b FROM ranks WHERE lv <= {result[0][0]} ORDER BY lv DESC")
                    mold = await self.db.fetch(f"SELECT name, img_profile FROM itens WHERE name=(\'{rankss[0][0]}\')")
                    moldName = "Novato" #Muuita preguiça de fazer imagem pra novato, então só usei a mesma do Soldado Nadir
                    moldImg = "src\molduras\#1.png"
                    if mold:
                        moldName = mold[0][0]
                        moldImg = mold[0][1]
                except Exception as e:
                    raise e
                buffer = utilities.rankcard.rank(result[0][0], result[0][1], result[0][2], moldName, moldImg, BytesIO(profile_bytes))
            else:
                await ctx.send('É preciso adicionar alguma classe primeiro.')
            await ctx.send(file=dFile(fp=buffer, filename='profile_card.png'))
        else:
            await ctx.send(f"{uMember.mention}, você ainda não recebeu experiência.")

    @commands.command(name='pescar', help="Pesca ao digitar s.percar")
    async def pescar(self, ctx):
        await ctx.message.delete()
        if ctx.message.author.id not in self.brake:
            luck = random.choice([True, False])
            if luck:
                tcoin = await self.db.fetch(f'SELECT coin FROM users WHERE id=(\'{ctx.message.author.id}\')')
                try:
                    assert tcoin
                    if tcoin:
                        coins = tcoin[0][0]
                        luckycoin = randint(1, self.cfg.coin_max)
                        total_coins = int(coins + luckycoin)
                        await self.db.fetch(f'UPDATE users SET coin=(\'{total_coins}\')')
                        await ctx.send(f"Você minerou {luckycoin} Sparks e agora tem {total_coins} Sparks!",delete_after=5)
                        self.brake.append(ctx.message.author.id)
                        await asyncsleep(30) #randint(15, 25)
                        self.brake.remove(ctx.message.author.id)
                except:
                    await ctx.send("Algo deu errado. Contate um administrador.")
            else:
                await ctx.send(f"Você pescou {str(random.choice(self.bot.cfg.trash))}!",delete_after=10)
                self.brake.append(ctx.message.author.id)
                await asyncsleep(30) #randint(15, 25)
                self.brake.remove(ctx.message.author.id)

        else:
            await ctx.send(f"Você precisa esperar 5 minutos para poder minerar de novo.",delete_after=5)

    @commands.command(name='topspark',
                      help='Ao digitar s.topspark , mostra o TOP 5 mais ricos do servidor.',
                      aliases=["spark", "top", "ts"])
    #@commands.cooldown(1, 120, BucketType.user)
    async def topspark(self, ctx):
        member = ctx.author
        total = await self.db.fetch('SELECT COUNT(rank) FROM users')
        for t in total:
            d = re.sub(r"\D", "", str(t))
            d = int(d)
            result = await self.db.fetch(f'SELECT id, rank, coin FROM users ORDER BY coin DESC FETCH FIRST 10 ROWS ONLY')
            if result:
                emb = discord.Embed(title='TOP 10 MAIS RICOS DA KINIGA',
                                    description='Aqui estão listados as dez pessoas que mais tem sparks no servidor.',
                                    color= discord.Color.orange())
                if d+1 <= 10:
                    count_line = 0
                    while count_line <= d-1:
                        mid = result[count_line][0]
                        rank = result[count_line][1]
                        sparks = result[count_line][2]
                        user = [user.name for user in ctx.guild.members if user.id == int(mid)]
                        emb = emb.add_field(name=f"{count_line+1}º — {''.join(user)}, Nível {rank}", value=f"{sparks} Sparks", inline=False)
                        count_line +=1
                else:
                    count_line = 0
                    while count_line <= 10:
                        mid = result[count_line][0]
                        rank = result[count_line][1]
                        sparks = result[count_line][2]
                        user = [user.name for user in ctx.guild.members if user.id == int(mid)]
                        emb = emb.add_field(name=f"{count_line+1}º — {''.join(user)}', Nível {rank}", value=f"{sparks} Sparks", inline=False)
                        count_line +=1

                num = await self.db.fetch(f"WITH temp AS (SELECT id, row_number() OVER (ORDER BY coin DESC) AS rownum FROM users) SELECT rownum FROM temp WHERE id = '{member.id}'")
                member_row = re.sub(r"\D", "", str(num))
                member_details = await self.db.fetch(f"SELECT rank, coin FROM users WHERE id='{member.id}'")
                rank = member_details[0][0]
                sparks = member_details[0][1]
                emb = emb.add_field(name=f"Sua posição é {int(member_row)}º — {member.name}, Nível {rank}", value=f"{sparks} Sparks", inline=False)
                await ctx.send('',embed=emb)

    #   classe
    @commands.command(name='classes',
                      help='Ao digitar s.classes , mostra todas as classes disponíveis.',
                      aliases=["ranks", "niveis"])
    async def classes(self, ctx):
        await self.db.fetch('CREATE TABLE IF NOT EXISTS ranks (lv INT NOT NULL, name TEXT NOT NULL, localE TEXT NOT NULL, localRR TEXT NOT NULL, sigla TEXT, path TEXT)')
        total = await self.db.fetch(f'SELECT COUNT(lv) FROM ranks')
        for t in total:
            d = re.sub(r"\D", "", str(t))
            if int(d) > 0:
                emb = discord.Embed(title='Todos as classes',
                            description='Aqui estão listados todos as classes no servidor.',
                            color= discord.Color.orange()).set_footer(
                                text='Os números ao lado da classe representam seu nível limite, ou seja,\n'
                                    'passando do número limite da classes, sua classe subirá de nível.')
                count = 0
                #await ctx.send(int(d))
                while int(count) < int(d)-1:
                    try:
                        rows = await self.db.fetch('SELECT * FROM ranks ORDER BY lv ASC')
                        for row in rows:
                            #await ctx.send(row)
                            rank_lv = row[0]
                            rank_name = row[1]
                            emb = emb.add_field(name=f"{rank_lv}", value=f"{rank_name}", inline=False)
                            count += 1
                    except: break
                await ctx.send('',embed=emb)
            else: await ctx.send("```Parece que não temos nenhuma classe ainda...```", delete_after=5)


    #info
    @commands.command(name='info',
                      help='Ao digitar s.info "Texto-Para-Perfil-Aqui" (é preciso que o texto esteja entre aspas DUPLAS), define o texto de informação que aparecerá em seu s.perfil.',
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
    @commands.command(name='delinfo',
                      help='Ao digitar s.delinfo, remove o texto de informação atual do seu s.perfil e substitui por "Não há o que bisbilhotar aqui".')
    async def delinfo(self, ctx) -> None:
        await self.db.fetch(f'UPDATE users SET info = (\'\') WHERE id = (\'{ctx.author.id}\')')
        await ctx.send("```Campo de informações atualizado. Visualize utilizando d.perfil```", delete_after=5)

    #bday
    @commands.command(name='niver',
                      help= 'Ao digitar s.niver <dia/mês>, define a data de aniversário presente em seu s.perfil.'
                      '(NÃO COLOQUE ANO! É preciso que sejam números separados por uma barra. você pode fazer aniversário dia 99, por exemplo. Seja criativo!).',
                      aliases=["aniversario", "aniversário", "aniver"],)
    async def niver(self, ctx, niver) -> None:
        niver = niver.split("/")
        dia = niver[0]
        mes = niver[1]

        await ctx.message.delete()
        await self.db.fetch(f'UPDATE users SET birth = (\'{dia}/{mes}\') WHERE id = (\'{ctx.author.id}\')')

        await asyncsleep(2)
        await ctx.send("```Aniversário atualizado!```", delete_after=3)
    @commands.command(name='delniver', help='Ao digitar s.delniver, remove o a data de aniversário atual do seu s.perfil e substitui por "??/??".')
    async def delniver(self, ctx) -> None:
        await self.db.fetch(f'UPDATE users SET birth = (\'???\') WHERE id = (\'{ctx.author.id}\')')
        await ctx.send("```Aniversário atualizado!```", delete_after=5)

    @commands.command(name='inv',
                      help='Ao digitar s.inv, mostra todos os itens que você possui. Incluindo os que não podem mais ser obtidos na s.loja.',
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
                            emb = emb.add_field(name=f"{item[0][1].upper()}", value=f"{item[0][2]} | ID: {item[0][0]}", inline=True)
                        else:
                            emb = emb.add_field(name=f"-", value=f"-", inline=True)
            else:
                await ctx.send("Você ainda não comprou nada!", delete_after=5)

            await ctx.send(embed=emb, delete_after=30)




def setup(bot) -> None:
    bot.add_cog(User(bot))

