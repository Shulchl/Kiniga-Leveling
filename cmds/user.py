import discord
import logging
import re
import json
import random
import datetime
import os
import ast

from asyncio import sleep as asyncsleep
from random import randint
from io import BytesIO


from discord import File as dFile
from discord import app_commands
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.utils import format_dt

from base.functions import (
    get_roles, get_userBanner_func, get_userAvatar_func)
from base.utilities import utilities
from base.struct import Config
from base.views import Paginacao


longest_cooldown = app_commands.checks.cooldown(
    2, 300.0, key=lambda i: (i.guild_id, i.user.id))
activity_cooldown = app_commands.checks.cooldown(
    1, 30.0, key=lambda i: (i.guild_id, i.user.id))

varBot = commands.Bot

varBot.disUse = None
varBot.disBuy = None


# CLASS LEVELING
class User(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = utilities.database(self.bot.loop)
        self.brake = []

        with open('config.json', 'r') as f:
            self.cfg = Config(json.loads(f.read()))

    @app_commands.command(name='perfil', description='Monstrará informações sobre você xD')
    @app_commands.describe(member='Marque o usuário para mostrar seu nível. (opcional)')
    @activity_cooldown
    async def perfil(self, interaction: discord.Interaction, member: discord.Member = None) -> None:

        if member:
            uMember = member
        else:
            uMember = interaction.user

        staff = await get_roles(uMember, interaction.guild)

        result = await self.db.fetch("SELECT rank, info, spark, ori, birth, iventory_id FROM users WHERE id='%s'" % (uMember.id, ))

        if result:
            userRank = result[0][0]
            userInfo = result[0][1]
            userSpark = result[0][2]
            userOri = result[0][3]
            userBirth = result[0][4]
            userIventoryId = result[0][5]

            try:
                profile_bytes = await get_userBanner_func(uMember)
            except:
                profile_bytes = await get_userAvatar_func(uMember)

            if not await self.db.fetch('SELECT lv FROM ranks LIMIT 1'):
                return await interaction.response.send_message("`Não há nenhuma classe no momento.`")

            ranks = await self.db.fetch("SELECT name, r, g, b FROM ranks WHERE lv <= %s ORDER BY lv DESC" % (userRank + 1 if userRank == 0 else userRank, ))

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

            iventory = await self.db.fetch("SELECT mold, car, banner, badge::jsonb FROM iventory WHERE iventory_id = (\'%s\')" % (userIventoryId, ))

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
            await interaction.response.send_message("`%s, você ainda não tem nenhum ponto de experiência.`" % (uMember.mention, ), ephemeral=True)

    @perfil.error
    async def perfil_error(self, interaction, error):
        if isinstance(error, commands.CommandOnCooldown):
            await interaction.response.send_message(
                "%s você poderá usar este comando de novo."
                % (format_dt(datetime.datetime.now() + datetime.timedelta(seconds=error.retry_after), "R")))
        else:
            await interaction.response.send_message(error, delete_after=5)
    # @longest_cooldown

    @app_commands.command(name='nivel', description='Monstrará a barra de progresso, bem como a medalha de seu nível.')
    @app_commands.describe(member='Marque o usuário para mostrar seu nível. (opcional)')
    async def nivel(self, interaction: discord.Interaction, member: discord.Member = None) -> None:

        await interaction.response.defer(ephemeral=True, thinking=True)

        if member:
            uMember = member
        else:
            uMember = interaction.user

        result = await self.db.fetch("SELECT rank, xp, xptotal, iventory_id FROM users WHERE id = (\'%s\')" % (uMember.id, ))
        if not result:
            return await interaction.followup.send(f"{uMember.mention}, você ainda não recebeu experiência.")

        try:
            iventory = await self.db.fetch("SELECT banner FROM iventory WHERE iventory_id = (\'%s\')" % (result[0][3], ))
            banner_id = iventory[0][0]
            if banner_id is not None:
                banner = await self.db.fetch("SELECT img_perfil FROM banners WHERE id=(\'%s\')" % (banner_id, ))
                if banner:
                    background = banner[0][0]
            else:
                background = "src/imgs/extra/loja/banners/Fy-no-Planeta-Magnético.png"
        except Exception as e:
            return await interaction.followup.send("Não foi possível pegar o banner no usuário! %s" % (e, ))

        total = await self.db.fetch('SELECT COUNT(lv) FROM ranks')
        d = re.sub('\\D', '', str(total))
        if int(d) > 0:
            try:
                rankss = await self.db.fetch("SELECT name, badges, imgxp FROM ranks WHERE lv <= %s ORDER BY lv DESC" % (result[0][0], ))
                if rankss:
                    moldName, moldImg, xpimg = rankss[0][0], rankss[0][1], rankss[0][2]
                else:
                    moldName, moldImg, xpimg = None, None, None
            except Exception as e:
                raise e

            try:
                buffer = utilities.rankcard.rank(
                    result[0][0], result[0][1], result[0][2],
                    moldName, moldImg, xpimg, background)
            except Exception as e:
                print(e)
        else:
            await interaction.followup.send('É preciso adicionar alguma classe primeiro.')

        await interaction.followup.send(file=dFile(fp=buffer, filename='profile_card.png'), ephemeral=True)

    @nivel.error
    async def nivel_error(self, interaction: discord.Interaction, error):
        if isinstance(error, commands.CommandOnCooldown):
            await interaction.response.send_message(
                "%s você poderá usar este comando de novo."
                % (format_dt(datetime.datetime.now() + datetime.timedelta(seconds=error.retry_after), "R")))
        else:
            await interaction.response.send_message(error, delete_after=5)

    @app_commands.command()
    async def getavatar(self, interaction: discord.Interaction, member: discord.Member = None) -> None:
        if member:
            uMember = member
        else:
            uMember = interaction.user
        try:
            res = await get_userAvatar_func(uMember)
        except:
            res = "Não consegui pegar o avatar do usuário. Provavelmente é padrão do discord xD"

        return await interaction.response.send_message(res, ephemeral=True)

    @app_commands.command()
    async def getbanner(self, interaction: discord.Interaction, member: discord.Member = None) -> None:
        if member:
            uMember = member
        else:
            uMember = interaction.user
        try:
            res = await get_userAvatar_func(uMember)
        except:
            res = "Não consegui pegar o banner do usuário. Provavelmente é padrão do discord xD"

        return await interaction.response.send_message(res, ephemeral=True)

    @app_commands.command(name='pescar')
    @activity_cooldown
    async def pescar(self, interaction: discord.Interaction):
        luck = random.choice([True, False])
        if luck:
            try:
                luckycoin = randint(self.cfg.coinsmin, self.cfg.coinsmax)
                await self.db.fetch(
                    f"UPDATE users SET spark=(spark + {luckycoin}) WHERE id=('{interaction.user.id}')")
                await interaction.response.send_message(f"Você pescou {luckycoin} sparks!", ephemeral=True)
                self.brake.append(interaction.user.id)
                await asyncsleep(randint(15, 25))  # randint(15, 25)
                self.brake.remove(interaction.user.id)
            except Exception as e:
                await interaction.response.send_message(e)
        else:
            await interaction.response.send_message(
                f"Você pescou {random.choice([str(i) for i in self.cfg.trash])}!", ephemeral=True)

    @pescar.error
    async def pescar_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                "%s você poderá usar este comando de novo."
                % (format_dt(datetime.datetime.now() + datetime.timedelta(seconds=error.retry_after), "R")),
                ephemeral=True)            # [ :-7 ]

    @app_commands.command(name='topspark')
    @activity_cooldown
    async def topspark(self, interaction: discord.Interaction):
        member = interaction.user
        total = await self.db.fetch('SELECT COUNT(rank) FROM users')
        for t in total:
            d = re.sub(r"\D", "", str(t))
            d = int(d)
            result = await self.db.fetch(
                    """
					SELECT id, rank, spark, user_name FROM users ORDER BY spark DESC FETCH FIRST 10 ROWS ONLY
				""")
            if result:
                emb = discord.Embed(title='TOP 10 MAIS RICOS DA KINIGA',
                                    description='Aqui estão listados as dez pessoas que mais tem sparks no servidor.',
                                    color=discord.Color.blue())
                count_line = 0
                while count_line <= d - 1:
                    membId = result[count_line][0]
                    if membId is self.bot.user.id:
                        count_line += 1
                        membId = result[count_line][0]
                    rank = result[count_line][1]
                    sparks = result[count_line][2]
                    user = [
                        user.name for user in interaction.guild.members if user.id == int(membId)]
                    emb = emb.add_field(
                        name=f"{count_line + 1}º — {''.join(user) if user else result [ count_line ][ 3 ]}, Nível {rank}",
                        value=f"{sparks} sparks", inline=False)
                    count_line += 1

                num = await self.db.fetch(
                    """
					WITH temp AS (SELECT id, row_number() OVER (ORDER BY spark DESC) AS rownum FROM users) 
					SELECT rownum FROM temp WHERE id = '%s'

					""" % (member.id, )
                )
                member_row = re.sub(r"\D", "", str(num))
                member_details = await self.db.fetch(f"SELECT rank, spark FROM users WHERE id='{member.id}'")
                rank = member_details[0][0]
                sparks = member_details[0][1]
                emb = emb.add_field(name=f"Sua posição é {int(member_row)}º — {member.name}, Nível {rank}",
                                    value=f"{sparks} sparks", inline=False)
                await interaction.response.send_message('', embed=emb)

    #   classe
    @app_commands.command(name='classes')
    @activity_cooldown
    async def classes(self, interaction: discord.Interaction):
        await self.db.fetch(
            """
			CREATE TABLE IF NOT EXISTS ranks (
				lv INT NOT NULL, 
				name TEXT NOT NULL, 
				localE TEXT NOT NULL,
				localRR TEXT NOT NULL, 
				sigla TEXT, 
				path TEXT
			)
		""")
        total = await self.db.fetch("SELECT COUNT(lv) FROM ranks")
        for t in total:
            d = re.sub(r"\D", "", str(t))
            if int(d) > 0:
                emb = discord.Embed(title='Todos as classes',
                                    description='Aqui estão listados todos as classes no servidor.',
                                    color=discord.Color.blue()).set_footer(
                    text='Os números ao lado da classe representam seu nível mínimo, ou seja,\n'
                    'ao chegar ao nível, você terá atingido sua classe correspondente.')
                count = 0
                # await interaction.send(int(d))
                while int(count) < int(d) - 1:
                    try:
                        rows = await self.db.fetch('SELECT * FROM ranks ORDER BY lv ASC')
                        for row in rows:
                            # await interaction.send(row)
                            rank_lv = row[0]
                            rank_name = row[1]
                            emb = emb.add_field(
                                name=f"Nível {rank_lv}", value=f"{rank_name}", inline=False)
                            count += 1
                    except:
                        break
                await interaction.response.send_message('', embed=emb)
            else:
                await interaction.response.send_message("```Parece que não temos nenhuma classe ainda...```")

#    @activity_cooldown
    @app_commands.command(name='info')
    async def info(self, interaction: discord.Interaction, *, content: str) -> None:
        info = "".join(content)
        size = len(info)
        if int(size) > 80:
            logging.error(size)
            return await interaction.response.send_message(
                "O texto deve conter 80 caracteres ou menos, contando espaços.", ephemeral=True)

        await self.db.fetch(
            f"UPDATE users SET info = '{content}' WHERE id = '{interaction.user.id}'"
        )
        await interaction.response.send_message(
            f"```Campo de informações atualizado. Visualize utilizando /perfil```", ephemeral=True)

    @info.error
    async def info_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.TransformerError):
            return await interaction.response.send_message(
                "O texto deve conter 80 caracteres ou menos, contando espaços.", ephemeral=True)
        else:
            return await interaction.response.send_message(
                error, ephemeral=True)

    @app_commands.command(name='delinfo')
    @activity_cooldown
    async def delinfo(self, interaction: discord.Interaction) -> None:
        await self.db.fetch(f"UPDATE users SET info = (\'\') WHERE id = ('{interaction.user.id}')")
        await interaction.response.send_message("```Campo de informações atualizado. "
                                                "Visualize utilizando d.perfil```", ephemeral=True)

    @app_commands.command(name='niver')
    @app_commands.checks.cooldown(1, 86400, key=lambda i: (i.guild_id, i.user.id))
    async def niver(self, interaction: discord.Interaction, niver: str) -> None:

        niver = niver.split("/")
        dia = niver[0]
        mes = niver[1]

        await self.db.fetch(f"UPDATE users SET birth = '{dia}/{mes}' WHERE id = ('{interaction.user.id}')")

        await interaction.response.send_message("```Aniversário atualizado!```", ephemeral=True)

    @niver.error
    async def niver_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"Você precisa esperar {str(datetime.timedelta(seconds=error.retry_after))[ :-7 ]} horas para poder "
                f"usar este comando de novo.",
                ephemeral=True)

    @app_commands.command(name='delniver')
    @longest_cooldown
    async def delniver(self, interaction: discord.Interaction) -> None:
        await self.db.fetch(f"UPDATE users SET birth = ('???') WHERE id = ('{interaction.user.id}')")
        await interaction.response.send_message("```Aniversário atualizado!```", ephemeral=True)

    # @activity_cooldown
    @app_commands.command(name='inv')
    async def inv(self, interaction: discord.Interaction) -> None:
        rows = await self.db.fetch("""
			SELECT * FROM jsonb_each_text(
				(
					SELECT itens::jsonb FROM iventory 
					WHERE iventory_id=(
						SELECT iventory_id FROM users WHERE id = ('%s')
					)
				)
			);
		""" % (interaction.user.id,)
        )

        item_ids = []
        for row in rows:
            items_key = row[0]
            items_value = ast.literal_eval(row[1])
            for key, value in items_value.items():
                if value != {}:
                    if items_key == "Badge" or "Moldura":
                        for key, value in value.items():
                            item_ids.append([str(key), int(value)])
                    else:
                        item_ids.append([str(key), int(value)])
                else:
                    pass
                    #print("Grupo %s de %ss não tem nada" % (key, items_key, ))
        if len(item_ids) < 1:
            return await interaction.response.send_message(
                "`Você não tem nenhum item. Compre utilizando sparks ou oris na loja! [/loja]`")
        rows = await self.db.fetch("""
			SELECT id, name, img, img_profile, category, type_ FROM itens WHERE item_type_id IN %s
		""" % (tuple(str(i[0]) for i in item_ids),)
        )
        items = []
        c = 0
        for row in rows:
            items.append({c: {
                "id": str(row[0]),
                "name": str(row[1]),
                "img": str(row[2] if str(row[5]) == "Badge" else row[3]),
                "category": str(row[4]).replace(" ", ""),
                "type": str(row[5])
            }})
            c += 1
            # items.append(row[0])
        user_info = await self.db.fetch("""
			SELECT banner as eqp_banner, spark as Spark, ori as Ori
				FROM iventory, users
			WHERE iventory.iventory_id=(
				SELECT iventory_id FROM users WHERE id = ('%s')
			) and users.iventory_id=(
				SELECT iventory_id FROM users WHERE id = ('%s')
			);
		""" % (interaction.user.id, interaction.user.id,)
        )
        if user_info:
            if user_info[0][0] == None:
                banner_img = 'src/imgs/extra/loja/banners/Fy-no-Planeta-Magnético.png'
            else:
                banner_img = await self.db.fetch("""
					SELECT img_loja FROM banners WHERE id=(\'%s\')
				""" % (user_info[0][0], )
                )
                banner_img = banner_img[0][0]

            banner, spark, ori = banner_img, user_info[0][1], user_info[0][2]

        async with interaction.channel.typing():
            pages = utilities.rankcard.drawiventory(
                banner, spark, ori, items, c)
            pages = [os.path.join('./_temp/', i) for i in pages]
            #view = None
            # if len(pages) > 1:
            view = Paginacao(pages, 60, interaction.user)
        await interaction.response.send_message(file=dFile(rf'{pages[0]}'),
                                                view=view, ephemeral=True)
        out = interaction.edit_original_response
        view.response = out

    @inv.error
    async def inv_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                'Você precisa esperar {:.2f} segundos para poder usar este comando de novo.'.format(
                    error.retry_after),
                ephemeral=True)

    # description='Use diariamente para receber recompensas incríveis'
    @app_commands.command(name='daily')
    # @app_commands.checks.cooldown(1, 86400)
    async def daily(self, interaction: discord.Interaction):
        chest_itens = {'chest': 80, 'ori': 10, 'xp': 10}
        choosed = random.choices(*zip(*chest_itens.items()), k=1)
        oris = randint(self.cfg.coinsmin, self.cfg.coinsmax)
        xp = randint(self.bot.cfg.min_message_xp, self.bot.cfg.max_message_xp)
        print(choosed)
        if choosed[0] == 'ori':
            oris = randint(self.cfg.coinsmin, self.cfg.coinsmax)
            return await interaction.response.send_message(f"Você ganhou {oris} oris!", ephemeral=True)
        elif choosed[0] == 'xp':
            xp = randint(self.bot.cfg.min_message_xp,
                         self.bot.cfg.max_message_xp)
            return await interaction.response.send_message(f"Você ganhou {xp} de experiência!", ephemeral=True)
        elif choosed[0] == 'chest':
            chest_prize = [' oris', ' de experiência', ' uma chave']
            emb = discord.Embed(
                title='BAÚ DE RECOMPENSA!',
                description='Você acaba de ganhar um baú, use uma chave para abrí-lo e saber o que tem dentro!',
                color=discord.Color.from_rgb(255, 231, 51)
            )

            emb.set_image(url="https://i.imgur.com/8qp96eb.png")
            emb.timestamp = datetime.datetime.now()

            invent = await self.db.fetch(f"SELECT inv FROM users WHERE id=('{interaction.user.id}')")
            print(invent[0][0])
            iventory = invent[0][0]
            itens = [iventory.split(",") if iventory != None else None]
            # Terminar essa porra amanhã
            key_id = None
            varBot.disUse, varBot.disBuy = False, True
            if itens[0] != None:
                for i, value in enumerate(itens):
                    item = await self.db.fetch(f"SELECT id, name, type_ FROM itens WHERE id={int(itens[ i ])}")
                    if item:
                        if item[0][1] == 'Chave' and item[0][2] == 'Utilizavel':
                            key_id = item[0][0]
                            varBot.disUse, varBot.disBuy = False, True
                            print("Def buttons")
                        else:
                            print("Not def buttons")
                            pass

            print("Before view")
            view = DailyConfirm(itens, emb, key_id, oris,
                                chest_prize, xp, self.db)

            channel = interaction.guild.get_channel(0)
            await interaction.response.send_message(embed=emb,
                                                    view=view
                                                    )
            await view.wait()
            print("After view")
            # Aguardar botão

            if view.value is None:
                await interaction.response.send_message('Não consegui identificar o item', ephemeral=True)

            else:
                await channel.send_message('Sua presença diária foi confirmada, confirme novamente em 24 horas '
                                           'para receber recompensas incríveis!', ephemeral=True)

    @daily.error
    async def daily_error(self, interaction, error):
        if isinstance(error, commands.CommandOnCooldown):
            await interaction.send(
                f'Você precisa esperar {str(datetime.timedelta(seconds=error.retry_after))[ :-7 ]} horas para poder '
                f'usar este comando de novo.')

    @app_commands.command(name='oris')
    async def oris(self, interaction: discord.Interaction):
        key_value = await self.db.fetch(f"SELECT coin FROM users WHERE id='{interaction.user.id}'")
        await interaction.response.send_message(f'Você tem {key_value[ 0 ][ 0 ]} dinheiros.', ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(User(bot))
