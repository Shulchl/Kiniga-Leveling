from __future__ import annotations

import re
from asyncio import sleep as asyncsleep
from io import BytesIO
from random import randint

import aiohttp
import discord
import json
from base.functions import get_roles
from base.utilities import utilities
from discord import File as dFile
from discord import Member as dMember
from discord.ext import commands
from discord.ext.commands.errors import MissingPermissions

from base.struct import Config


# CLASS LEVELING


class Perfil(commands.Cog, name='Perfil', description='Comandos de Opções de perfil'):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = utilities.database(
            self.bot.loop, self.bot.cfg.postgresql_user, self.bot.cfg.postgresql_password)
        self.brake = []

        with open('config.json', 'r') as f:
            self.cfg = Config(json.loads(f.read()))

    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        aId = message.author.id
        if aId not in self.brake and message.author.id is not self.bot.user.id:

            if not await self.db.fetch(f'SELECT id FROM users WHERE id=\'{aId}\''):
                await self.db.fetch(
                    f'INSERT INTO users (id, rank, xp, xptotal) VALUES (\'{aId}\', \'0\', \'0\', \'0\')')
                current_xp = 0
            else:
                oris = randint(self.cfg.coinsmin, self.cfg.coinsmax)
                result = await self.db.fetch(f'SELECT rank, xp, xptotal FROM users WHERE id=\'{aId}\'')
                expectedXP = randint(
                    self.bot.cfg.min_message_xp, self.bot.cfg.max_message_xp)
                current_xp = result[0][1] + expectedXP
                if current_xp >= utilities.rankcard.neededxp(result[0][0]):
                    await self.db.fetch(
                        f'UPDATE users SET rank=\'{result[0][0] + 1}\', xptotal= xptotal + {expectedXP if result[0][0] <= 80 else 0}, coin=(coin + {oris}) WHERE id=\'{aId}\'')
                    await message.channel.send("{}, você subiu de nível!".format(message.author.mention),
                                               delete_after=3)
                    rank = await self.db.fetch(f'SELECT name FROM ranks WHERE lv <={result[0][0] + 1} ORDER BY lv DESC')
                    prole = await self.db.fetch(f'SELECT name FROM ranks WHERE lv <{result[0][0] - 1} ORDER BY lv DESC')
                    if rank:
                        rankRole = str(rank[0][0])
                        frankRole = discord.utils.find(
                            lambda r: r.name == rankRole, message.guild.roles) or rankRole
                        if not frankRole in message.author.roles:
                            try:
                                assert frankRole
                                await message.author.add_roles(frankRole)
                                prevRole = str(prole[0][0])
                                # await message.channel.send("+"*10+prevRole +"+"*10)
                                prevRole = discord.utils.find(
                                    lambda r: r.name == prevRole, message.guild.roles) or prevRole
                                if prevRole in message.author.roles:
                                    try:
                                        await message.author.remove_roles(prevRole)
                                    except Exception as e:
                                        await message.channel.send("Não consigo remover cargos! \n\n{}".format(e))
                            except AssertionError as i:
                                return await ctx.send(i)
                            except MissingPermissions:
                                return await message.channel.send(
                                    "Eu não tenho permissão para adicionar/remover cargos, "
                                    "reporte isso à um ADM por favor.", delete_after=10)

                                # rank2 = await self.db.fetch(f'SELECT lv, name, r, g, b FROM ranks WHERE lv <={
                                # result[0][0]} ORDER BY lv DESC')
                else:

                    await self.db.fetch(
                        f"UPDATE users SET xp=({current_xp}), xptotal=(xptotal + {expectedXP if result[0][0] <= 80 else 0}), coin=(coin + {oris}) WHERE id=\'{aId}\'")

                self.brake.append(message.author.id)
                await asyncsleep(randint(0, 5))  #
                self.brake.remove(message.author.id)

    #   SQL inject

    @commands.is_owner()
    @commands.command(hidden=True)
    async def tsql(self, ctx, *, sql: str) -> None:
        output = await self.db.fetch(sql)
        await ctx.send(f'```{output}```')

    #   SQL inject
    @commands.is_owner()
    @commands.command(hidden=True)
    async def tsqlist(self, ctx, *, sql: str) -> None:
        output = await self.db.fetchList(sql)
        await ctx.send(f'```{output}```')

    @commands.cooldown(1, 5, commands.BucketType.member)
    @commands.command(name='perfil', aliases=['p', 'profile'])
    async def perfil(self, ctx, member: discord.Member = None) -> None:
        if member:
            uMember = member
        else:
            uMember = ctx.author

        staff = await get_roles(uMember, ctx.guild)
        await self.db.fetch("CREATE TABLE IF NOT EXISTS users (id TEXT NOT NULL, rank INT NOT NULL, xp INT NOT NULL, "
                            "xptotal INT NOT NULL, title TEXT UNIQUE, mold TEXT UNIQUE, info TEXT, coin INT DEFAULT "
                            "0, inv TEXT, birth TEXT DEFAULT '???', staff BOOLEAN DEFAULT FALSE, adm BOOLEAN DEFAULT "
                            "FALSE, author BOOLEAN DEFAULT FALSE, lucky BOOLEAN DEFAULT FALSE)")
        result = await self.db.fetch(
            f"SELECT rank, xp, title, mold, info, coin, birth FROM users WHERE id='{uMember.id}'")
        if result:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{uMember.avatar_url_as(format="png", size=1024)}') as resp:
                    profile_bytes = await resp.read()
            total = await self.db.fetch('SELECT COUNT(lv) FROM ranks')
            d = re.sub('\\D', '', str(total))
            if int(d) > 0:
                rankss = await self.db.fetch(
                    f"SELECT name, r, g, b, imgxp FROM ranks WHERE lv <= {result[0][0] + 1 if result[0][0] == 0 else result[0][0]} ORDER BY lv DESC")
                titleImg = None
                if result[0][2] is not None:
                    title = await self.db.fetch(f"SELECT img FROM itens WHERE id=(\'{result[0][2]}\')")
                    if title:
                        titleImg = title[0][0]
                moldName, moldImg, moldImgR = None, None, None
                if result[0][3] is not None:
                    mold = await self.db.fetch(
                        f"SELECT name, img_profile, imgd FROM itens WHERE id=(\'{result[0][3]}\')")
                    if mold:
                        moldName, moldImg, moldImgR = mold[0][0], mold[0][1], mold[0][2]
                    else:
                        moldName, moldImg, moldImgR = None, None, None
                if rankss:
                    ranksUm, ranksDois, ranksTres, rankQuatro, ranksCinco = rankss[0][0], rankss[0][1], rankss[0][2], \
                                                                            rankss[0][3], rankss[0][4]
                else:
                    ranksUm, ranksDois, ranksTres, rankQuatro, ranksCinco = None, None, None, None, None

                buffer = utilities.rankcard.draw(str(uMember), result[0][0], result[0][1], titleImg, moldName, moldImg,
                                                 moldImgR, result[0][4], result[0]
                                                 [5], result[0][6], staff, ranksUm, ranksDois, ranksTres, rankQuatro,
                                                 ranksCinco, BytesIO(profile_bytes))
            else:
                await ctx.send('É preciso adicionar alguma classe primeiro.')

            await ctx.reply(file=dFile(fp=buffer, filename='rank_card.png'))
            await ctx.message.delete()
        else:
            await ctx.send(f"{uMember.mention}, você não tem experiência.")

    @perfil.error
    async def perfil_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                'Você precisa esperar {:.2f} segundos para poder usar este comando de novo.'.format(error.retry_after),
                delete_after=5)


def setup(bot) -> None:
    bot.add_cog(Perfil(bot))
