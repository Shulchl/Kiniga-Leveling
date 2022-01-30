from __future__ import annotations

from asyncio import sleep as asyncsleep
from random import randint
from io import BytesIO

import discord, aiohttp, re
from discord import File as dFile
from discord import Member as dMember
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.errors import BadArgument, MissingPermissions, MissingRequiredArgument

from base.utilities import utilities
from base.functions import check_adm

# CLASS LEVELING
class Perfil(commands.Cog, name='Perfil', description='Comandos de Opções de perfil'):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = utilities.database(
            self.bot.loop, self.bot.cfg.postgresql_user, self.bot.cfg.postgresql_password)
        self.brake = []

    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        if message.author.id not in self.brake and message.author.id != self.bot.user.id:

            await check_adm(self, message.author, message.guild)

            if not await self.db.fetch(f'SELECT * FROM users WHERE id=\'{message.author.id}\''):
                await self.db.fetch(f'INSERT INTO users (id, rank, xp, xptotal) VALUES (\'{message.author.id}\', \'0\', \'0\', \'0\')')
                current_xp = 0
                #rankRole = discord.utils.find(lambda r: r.name == "Membro", message.guild.roles)
                #if rankRole:
                #    for rankRole in message.author.roles:
                #        pass
                #    else:
                #        await message.author.add_roles(rankRole)
                #else:
                #    nRole = await message.guild.create_role(name="Membro", reason="Novo rank", mentionable=True)
                #    await message.author.add_roles(nRole)
            else:
                result = await self.db.fetch(f'SELECT rank, xp, xptotal FROM users WHERE id=\'{message.author.id}\'')
                expectedXP = randint(
                    self.bot.cfg.min_message_xp, self.bot.cfg.max_message_xp)
                current_xp = result[0][1] + expectedXP
                if current_xp >= utilities.rankcard.neededxp(result[0][0]):
                    await self.db.fetch(f'UPDATE users SET rank=\'{result[0][0]+1}\', xptotal=\'{result[0][2]+expectedXP}\' WHERE id=\'{message.author.id}\'')
                    rank = await self.db.fetch(f'SELECT lv, name, r, g, b FROM ranks WHERE lv <={result[0][0]+1} ORDER BY lv DESC')
                    if rank:
                        rankRole = str(rank[0][1])

                        frankRole = discord.utils.find(lambda r: r.name == rankRole, message.guild.roles) or rankRole
                        if not frankRole in message.author.roles:
                            assert discord.utils.find(lambda r: r.name == rankRole, message.guild.roles)
                            try:
                                await message.author.add_roles(frankRole)
                                await message.channel.send("Você subiu de nível!", delete_after=5)
                            except MissingPermissions:
                                await message.channel.send("Eu não tenho permissão para adicionar/remover cargos, reporte isso à um ADM por favor.", delete_after=10)

                            if result[0][0]+1 > 10:
                                #rank2 = await self.db.fetch(f'SELECT lv, name, r, g, b FROM ranks WHERE lv <={result[0][0]} ORDER BY lv DESC')
                                removerole = discord.utils.find(lambda r: r.name == str(rank[1][1]), message.guild.roles)
                                await message.author.remove_roles(removerole)


                else:
                    await self.db.fetch(f'UPDATE users SET xp=\'{current_xp}\', xptotal=\'{result[0][2]+expectedXP}\' WHERE id=\'{message.author.id}\'')

                self.brake.append(message.author.id)
                await asyncsleep(2) #randint(15, 25)
                self.brake.remove(message.author.id)

        #await self.bot.process_commands(message)

    #   SQL inject
    @commands.is_owner()
    @commands.command(hidden=True)
    async def tsql(self, ctx, *, sql: str) -> None:
        output = await self.db.fetch(sql)
        await ctx.send(f'```{output}```')

    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.command(name='perfil', aliases=['p', 'profile'])
    async def perfil(self, ctx, member: dMember=None) -> None:
        if member:
            uMember = member
        else:
            uMember = ctx.author
        await self.db.fetch("CREATE TABLE IF NOT EXISTS users (id TEXT NOT NULL, rank INT NOT NULL, xp INT NOT NULL, xptotal INT NOT NULL, title TEXT UNIQUE, mold TEXT UNIQUE, info TEXT, coin INT DEFAULT 0, inv TEXT, birth TEXT DEFAULT '???', staff BOOLEAN DEFAULT FALSE, adm BOOLEAN DEFAULT FALSE, author BOOLEAN DEFAULT FALSE, lucky BOOLEAN DEFAULT FALSE)")
        result = await self.db.fetch(f"SELECT rank, xp, title, mold, info, coin, birth, staff, adm, author FROM users WHERE id='{uMember.id}'")
        if result:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{uMember.avatar_url_as(format="png", size=1024)}') as resp:
                    profile_bytes = await resp.read()
            total = await self.db.fetch('SELECT COUNT(lv) FROM ranks')
            d = re.sub('\\D', '', str(total))
            if int(d) > 0:
                rankss = await self.db.fetch(f"SELECT name, r, g, b FROM ranks WHERE lv <= {result[0][0]} ORDER BY lv DESC")
                if result[0][2] != None:
                    title = await self.db.fetch(f"SELECT img FROM itens WHERE name=(\'{result[0][2]}\')")
                    if title:
                        titleImg = title[0][0]
                else:
                    titleImg = None
                moldName, moldImg, moldImgR = None, None, None
                if result[0][3] != None:
                    mold = await self.db.fetch(f"SELECT name, img_profile, imgd FROM itens WHERE id=(\'{result[0][3]}\')")
                    if mold:
                        moldName, moldImg, moldImgR = mold[0][0], mold[0][1], mold[0][2]
                ranksUm, ranksDois, ranksTres, rankQuatro = 'Nenhuma', '0', '0', '0'
                if rankss:
                    ranksUm, ranksDois, ranksTres, rankQuatro = rankss[0][0], rankss[0][1], rankss[0][2], rankss[0][3]

                buffer = utilities.rankcard.draw(str(uMember), result[0][0], result[0][1], titleImg, moldName, moldImg, moldImgR, result[0][4], result[0][5], result[0][6], result[0][7], result[0][8], result[0][9], ranksUm, ranksDois, ranksTres, rankQuatro, BytesIO(profile_bytes))
            else:
                await ctx.send('É preciso adicionar alguma classe primeiro.')
            await ctx.send(file=dFile(fp=buffer, filename='rank_card.png'))
        else:
            await ctx.send(f"{uMember.mention}, você ainda não recebeu experiência.")

def setup(bot) -> None:
    bot.add_cog(Perfil(bot))

