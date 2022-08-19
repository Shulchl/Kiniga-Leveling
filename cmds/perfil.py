from __future__ import annotations

import logging
import re
from asyncio import sleep as asyncsleep
from io import BytesIO
from random import randint

import sys
import aiohttp
import json
import io
import requests
import discord
from discord import app_commands
from discord.ext import commands

from base.functions import get_roles
from base.utilities import utilities
from discord import File as dFile
from discord import Member as dMember
from discord.ext.commands.errors import MissingPermissions

from base.struct import Config


# CLASS LEVELING


class Perfil(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = utilities.database(self.bot.loop, self.bot.cfg.postgresql_user, self.bot.cfg.postgresql_password)
        self.brake = [ ]
        self.cd_mapping = commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.member)
        
        
        self.lvUpChannel = self.bot.get_channel(943945066836283392)

        with open('config.json', 'r') as f:
            self.cfg = Config(json.loads(f.read()))

    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        bucket = self.cd_mapping.get_bucket(message)
        if not bucket.update_rate_limit():
            if message.author.id is not self.bot.user.id:
                aId = message.author.id
                if await self.db.fetch(f"SELECT id FROM users WHERE id=('{aId}')"):
                    oris = randint(self.cfg.coinsmin, self.cfg.coinsmax)
                    result = await self.db.fetch(f"SELECT rank, xp, xptotal FROM users WHERE id=('{aId}')")
                    expectedXP = randint(
                        self.bot.cfg.min_message_xp, self.bot.cfg.max_message_xp)
                    current_xp = result[ 0 ][ 1 ] + expectedXP
                    if current_xp >= utilities.rankcard.neededxp(result[ 0 ][ 0 ]):
                        try:
                            await self.db.fetch(
                                f"UPDATE users SET rank={result[ 0 ][ 0 ] + 1}, xptotal= xptotal + "
                                f"{expectedXP if result[ 0 ][ 0 ] <= 80 else 0}, coin=(coin + {oris}) WHERE id=\'{aId}\'")
                            await self.lvUpChannel.send("{}, você subiu de nível!".format(message.author.mention))
                            rank = await self.db.fetch(
                                f"SELECT name FROM ranks WHERE lv <={result[ 0 ][ 0 ] + 1} ORDER BY lv DESC")
                            prole = await self.db.fetch(
                                f"SELECT name FROM ranks WHERE lv <{result[ 0 ][ 0 ] - 1} ORDER BY lv DESC")
                            if rank:
                                rankRole = str(rank[ 0 ][ 0 ])
                                frankRole = discord.utils.find(
                                    lambda r: r.name == rankRole, message.guild.roles) or rankRole
                                if not frankRole in message.author.roles:
                                    try:
                                        await message.author.add_roles(frankRole)
                                        prevRole = str(prole[ 0 ][ 0 ])
                                        # await self.lvUpChannel.send("+"*10+prevRole +"+"*10)
                                        prevRole = discord.utils.find(
                                            lambda r: r.name == prevRole, message.guild.roles) or prevRole
                                        if prevRole in message.author.roles:
                                            try:
                                                await message.author.remove_roles(prevRole)
                                            except Exception as e:
                                                await self.lvUpChannel.send("Não consigo remover cargos! \n\n{}".format(e))
                                    except MissingPermissions:
                                        return await self.lvUpChannel.send(
                                            "Eu não tenho permissão para adicionar/remover cargos, "
                                            "reporte isso à um ADM por favor.")

                                        # rank2 = await self.db.fetch(f'SELECT lv, name, r, g, b FROM ranks WHERE lv <={
                                        # result[0][0]} ORDER BY lv DESC')
                        except Exception as e:
                            print(e)
                    else:
                        await self.db.fetch(
                            f"UPDATE users SET xp=({current_xp}), xptotal=(xptotal + "
                            f"{expectedXP if result[ 0 ][ 0 ] <= 80 else 0}), coin=(coin + {oris}) WHERE id=\'{aId}\'")

                    #self.brake.append(message.author.id)
                    #await asyncsleep(randint(0, 5))  #
                    #self.brake.remove(message.author.id)
                else:
                    await self.db.fetch(
                        f'INSERT INTO users (id, rank, xp, xptotal) VALUES (\'{aId}\', \'0\', \'0\', \'0\')')
                    current_xp = 0

    @app_commands.command(name='perfil')
    @app_commands.guilds(discord.Object(id=943170102759686174))
    async def perfil(self, interaction: discord.Interaction, member: discord.Member = None) -> None:

        if member:
            uMember = member
        else:
            uMember = interaction.user

        staff = await get_roles(uMember, interaction.guild)
        result = await self.db.fetch(
            f"SELECT rank, xp, title, mold, info, coin, birth FROM users WHERE id='{uMember.id}'")
        if result:
            try:
                if uMember.is_avatar_animated:
                    req = await self.bot.http.request(discord.http.Route("GET", "/users/{uid}", uid=uMember.id))
                    banner_id = req[ "banner" ]
                    profile_bytes = io.BytesIO(requests.get(
                        f"https://cdn.discordapp.com/banners/{uMember.id}/{banner_id}?size=2048").content).getvalue()
                    # await ctx.send(f'https://cdn.discordapp.com/banners/{uMember.id}/{banner_id}?size=2048')

            except:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{uMember.display_avatar.url}?size=1024?format=png") as resp:
                        profile_bytes = await resp.read()

            total = await self.db.fetch('SELECT COUNT(lv) FROM ranks')
            d = re.sub('\\D', '', str(total))
            if int(d) > 0:
                rankss = await self.db.fetch(
                    f"SELECT name, r, g, b, imgxp FROM ranks WHERE lv <= "
                    f"{result[ 0 ][ 0 ] + 1 if result[ 0 ][ 0 ] == 0 else result[ 0 ][ 0 ]} ORDER BY lv DESC")
                titleImg = None
                if result[ 0 ][ 2 ] is not None:
                    title = await self.db.fetch(f"SELECT img FROM itens WHERE id=(\'{result[ 0 ][ 2 ]}\')")
                    if title:
                        titleImg = title[ 0 ][ 0 ]
                moldName, moldImg, moldImgR = None, None, None
                if result[ 0 ][ 3 ] is not None:
                    mold = await self.db.fetch(
                        f"SELECT name, img_profile, imgd FROM itens WHERE id=(\'{result[ 0 ][ 3 ]}\')")
                    if mold:
                        moldName, moldImg, moldImgR = mold[ 0 ][ 0 ], mold[ 0 ][ 1 ], mold[ 0 ][ 2 ]
                    else:
                        moldName, moldImg, moldImgR = None, None, None
                if rankss:
                    ranksUm, ranksDois, ranksTres, rankQuatro, ranksCinco = rankss[ 0 ][ 0 ], rankss[ 0 ][ 1 ], \
                                                                            rankss[ 0 ][ 2 ], \
                                                                            rankss[ 0 ][ 3 ], rankss[ 0 ][ 4 ]
                else:
                    ranksUm, ranksDois, ranksTres, rankQuatro, ranksCinco = None, None, None, None, None

                buffer = utilities.rankcard.draw(str(uMember), result[ 0 ][ 0 ], result[ 0 ][ 1 ], titleImg, moldName,
                                                 moldImg,
                                                 moldImgR, result[ 0 ][ 4 ], result[ 0 ]
                                                 [ 5 ], result[ 0 ][ 6 ], staff, ranksUm, ranksDois, ranksTres,
                                                 rankQuatro,
                                                 ranksCinco, BytesIO(profile_bytes))
            else:
                await interaction.response.send_message('É preciso adicionar alguma classe primeiro.')

            await interaction.response.send_message(file=dFile(fp=buffer, filename='rank_card.png'))
        else:
            await interaction.response.send_message(f"{uMember.mention}, você não tem experiência.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Perfil(bot), guilds=[ discord.Object(id=943170102759686174) ])
