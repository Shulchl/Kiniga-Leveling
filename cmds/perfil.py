import json
import discord
import ast

from asyncio import sleep as asyncsleep
from io import BytesIO
from random import randint
from discord import app_commands
from discord.ext import commands


from base.functions import (
    get_roles, get_userBanner_func, get_userAvatar_func)
from base.utilities import utilities

from discord import File as dFile
from discord import Member as dMember
from discord.ext.commands.errors import MissingPermissions, RoleNotFound

from base.struct import Config

# CLASS LEVELING


class Perfil(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = utilities.database(
            self.bot.loop, self.bot.cfg.postgresql_user, self.bot.cfg.postgresql_password)
        self.brake = []
        self.cd_mapping = commands.CooldownMapping.from_cooldown(
            1, 1, commands.BucketType.member)

        self.lvUpChannel = self.bot.get_channel(943945066836283392)

        with open('config.json', 'r') as f:
            self.cfg = Config(json.loads(f.read()))

    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        bucket = self.cd_mapping.get_bucket(message)
        if not bucket.update_rate_limit():
            if message.author.id is not self.bot.user.id:
                print("on_message")
                aId = message.author.id
                try:
                    user_infos = await self.db.fetch(f"SELECT rank, xp, xptotal, id, inventory_id FROM users WHERE id=('{aId}')")
                except:
                    raise e

                if not user_infos:
                    await self.db.fetch(f"""
                        INSERT INTO users (id, rank, xp, xptotal, user_name) 
                        VALUES (\'{aId}\', \'0\', \'0\', \'0\', \'{message.author.name}\')
                    """)
                    await self.db.fetch("""
                        INSERT INTO iventory (ivent_id, itens) 
                        VALUES (\'%s\', \'%s\')
                        """ % (user_infos[0][4],
                               '{"Carro": {"ids": []}, "Badge": {"rank": [], "equipe": [], "moldura": [], "apoiador": []}, "Banner": {"ids": []}, "Titulo": {"ids": []}, "Moldura": {"ids": []}, "Utilizavel": {"ids": []}}'
                               )
                    )
                    current_xp = 0
                    return

                spark = randint(self.cfg.coinsmin, self.cfg.coinsmax)
                # result = await self.db.fetch(f"SELECT rank, xp, xptotal FROM users WHERE id=('{aId}')")
                expectedXP = randint(
                    self.bot.cfg.min_message_xp, self.bot.cfg.max_message_xp)
                current_xp = user_infos[0][1] + expectedXP
                if current_xp >= utilities.rankcard.neededxp(user_infos[0][0]):
                    try:
                        up = await self.db.fetch(
                            f"UPDATE users SET rank={user_infos[ 0 ][ 0 ] + 1}, xptotal= xptotal + "
                            f"{expectedXP if user_infos[ 0 ][ 0 ] <= 80 else 0}, spark=(spark + {spark}) WHERE id=\'{aId}\' RETURNING rank")

                        rank = up[0][0]
                        print(rank)

                        names = await self.db.fetch(
                            f"SELECT name FROM ranks WHERE lv <= {rank+1} and lv < {rank-1} ORDER BY lv DESC")

                        ranks, prole = names[0][0], None if len(
                            names) < 2 else names[1][0]
                        print(ranks, prole)

                        ranks = discord.utils.find(
                            lambda r: r.name == ranks, message.guild.roles) or ranks
                        print(ranks)
                        try:
                            if ranks in message.author.roles:
                                return
                            await message.author.add_roles(ranks)
                            if prole != None:
                                prevRole = str(prole)
                                # await self.lvUpChannel.send("+"*10+prevRole +"+"*10)
                                prevRole = discord.utils.find(
                                    lambda r: r.name == prevRole, message.guild.roles) or prevRole
                                if prevRole in message.author.roles:
                                    try:
                                        await message.author.remove_roles(prevRole)
                                    except Exception as e:
                                        await self.lvUpChannel.send("Não consigo remover cargos! \n\n`{}`".format(e))
                        except Exception as i:
                            if isinstance(Exception, MissingPermissions):
                                return await self.lvUpChannel.send(
                                    "`Eu não tenho permissão para adicionar/remover cargos, "
                                    "reporte à um ADM.`")
                            elif isinstance(Exception, RoleNotFound):
                                return
                            else:
                                raise i
                        else:
                            print("Cargos adicionados/removidos com sucesso.")
                            # rank2 = await self.db.fetch(f'SELECT lv, name, r, g, b FROM ranks WHERE lv <={
                            # user_infos[0][0]} ORDER BY lv DESC')
                    except Exception as e:
                        raise e
                    else:
                        await self.lvUpChannel.send("{}__, você subiu de nível!__ \n`+{} sparks +{} pontos de experiência.`".format(message.author.mention, spark, expectedXP))
                else:
                    await self.db.fetch(
                        f"UPDATE users SET xp=({current_xp}), xptotal=(xptotal + "
                        f"{expectedXP if user_infos[ 0 ][ 0 ] <= 80 else 0}), spark=(spark + {spark}) WHERE id=\'{aId}\'")

                # self.brake.append(message.author.id)
                #await asyncsleep(randint(0, 5))  #
                # self.brake.remove(message.author.id)

    @app_commands.command(name='perfil')
    async def perfil(self, interaction: discord.Interaction, member: discord.Member = None) -> None:

        if member:
            uMember = member
        else:
            uMember = interaction.user

        staff = await get_roles(uMember, interaction.guild)

        result = await self.db.fetch(
            f"SELECT rank, info, spark, ori, birth, inventory_id FROM users WHERE id='{uMember.id}'")
        if result:
            userRank = result[0][0]
            userInfo = result[0][1]
            userSpark = result[0][2]
            userOri = result[0][3]
            userBirth = result[0][4]
            userIventoryId = result[0][5]

            try:
                profile_bytes = await get_userBanner_func(uMember)
                # await ctx.send(f'https://cdn.discordapp.com/banners/{uMember.id}/{banner_id}?size=2048')
            except:
                profile_bytes = await get_userAvatar_func(uMember)

            if not await self.db.fetch('SELECT lv FROM ranks LIMIT 1'):
                return await interaction.response.send_message("`Não há nenhuma classe no momento.`")

            ranks = await self.db.fetch(
                f"SELECT name, r, g, b FROM ranks WHERE lv <= "
                f"{userRank + 1 if userRank == 0 else userRank} ORDER BY lv DESC")
            if ranks:
                rankName = ranks[0][0]
                rankR = ranks[0][1]
                rankG = ranks[0][2]
                rankB = ranks[0][3]
            else:
                rankName = None
                rankR = None
                rankG = None
                rankB = None

            iventory = await self.db.fetch("SELECT mold, car, banner, badge::jsonb FROM iventory WHERE ivent_id = (\'%s\')" % (userIventoryId, ))

            mold_id = iventory[0][0]

            # Pega moldura equipada
            moldImage = None
            if mold_id is not None:
                mold = await self.db.fetch("SELECT img_profile FROM molds WHERE id=(\'%s\')" % (mold_id, ))
                if mold:
                    moldImage = mold[0][0]

            banner_id = iventory[0][2]
            # Pega titulo equipado
            bannerImg = None
            if banner_id is not None:
                banner = await self.db.fetch("SELECT img_perfil FROM banners WHERE id=(\'%s\')" % (banner_id, ))
                if banner:
                    bannerImg = banner[0][0]
            else:
                bannerImg = "src/imgs/extra/loja/banners/Fy-no-Planeta-Magnético.png"

            badge_ids = iventory[0][3]
            badge_rows = []
            badge_images = []
            l = ast.literal_eval(badge_ids)
            for key, value in l.items():
                badge_rows.append(value)
            if len(badge_rows) > 0:
                rows = await self.db.fetch("""
                    SELECT img FROM itens WHERE item_type_id IN %s
                """ % (tuple(str(i) for i in badge_rows),)
                )
                for row in rows:
                    badge_images.append(row[0])
            # return print(badge_rows[0][0])
                print(badge_rows)

            buffer = utilities.rankcard.draw_new(
                str(uMember), badge_images, bannerImg,
                moldImage, userInfo, userSpark, userOri,
                userBirth, staff, rankName, rankR, rankG,
                rankB, BytesIO(profile_bytes))

            await interaction.response.send_message(file=dFile(fp=buffer, filename='rank_card.png'))
        else:
            await interaction.response.send_message(f"`{uMember.mention}, você ainda não tem nenhum ponto de experiência.`", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    # , guilds=[ discord.Object(id=943170102759686174), discord.Object(id=1010183521907789977)]
    await bot.add_cog(Perfil(bot))
