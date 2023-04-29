import discord
import re
import json
import random
import datetime
import os
import ast
import sys

from asyncio import sleep as asyncsleep
from random import randint
from io import BytesIO


from discord import File as dFile
from discord import app_commands
from discord.app_commands import AppCommandError

from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.utils import format_dt

from base.functions import (
    longest_cooldown,
    activity_cooldown,
    get_roles, 
    get_userBanner_func, 
    get_userAvatar_func, 
    error_delete_after,
    get_iventory,
    report_error,
    get_profile_info
    )
from base.utilities import utilities
from base.struct import Config
from base.views import Paginacao

from base import log, cfg

varBot = commands.Bot

varBot.disUse = None
varBot.disBuy = None


# CLASS LEVELING
class User(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = utilities.database(self.bot.loop)
        self.brake = []

        self.cfg = cfg

    def cog_load(self):
        sys.stdout.write(f'Cog carregada: {self.__class__.__name__}\n')
        sys.stdout.flush()

    def cog_unload(self):
        sys.stdout.write(f'Cog descarregada: {self.__class__.__name__}\n')
        sys.stdout.flush()

    async def cog_app_command_error(
        self, 
        interaction: discord.Interaction, 
        error: AppCommandError
    ):
        if isinstance(error, app_commands.CommandOnCooldown):
            return await error_delete_after(interaction, error)

        elif isinstance(error, app_commands.TransformerError):
            res = "O texto deve conter 80 caracteres ou menos, contando espaços."

        elif isinstance(error, commands.BadArgument):
            if error.command.name in ['usar', 'equipar', 'desequipar', 'canotbuy', 'canbuy' ]:
                res = "Não existe um item com esse número(ID) ou o item não está disponível para compra."

        elif isinstance(error, commands.MissingRequiredArgument):
            if error.command.name in ['comprar', 'usar', 'equipar', 'desequipar', 'canotbuy', 'canbuy' ]:
                res = "```Você não tem esse item.```"

        else:
            
            await report_error(self, interaction, error)
            res = "Ocorreu um erro inesperado. Favor, tente novamente.\nO errro já foi relatado à um administrador."
        
        await send_error_response(self, interaction, res)

    @activity_cooldown
    @app_commands.command(name='perfil', description='Monstrará informações sobre você xD')
    @app_commands.describe(member='Marque o usuário para mostrar seu nível. (opcional)')
    async def perfil(self, interaction: discord.Interaction, member: discord.Member = None) -> None:
        
        await interaction.response.defer(ephemeral=True, thinking=True)

        if member:
            uMember = member
        else:
            uMember = interaction.user


        # Get user roles and return staff roles
        staff = await get_roles(uMember, interaction.guild)

        # Insert the user into db if it's not already and return it, or only return de user
        user_ = await get_profile_info(self, uMember.id, uMember.name)
        user_id, userRank, xp, xptotal, userInfo, userSpark, userOri, userIventoryId, userBirth, rank_id, user_name, email = user_

        # Check if theres any rank on db
        if (all_ranks := await self.db.fetchrow(
            """
                SELECT name, r, g, b FROM ranks
                WHERE lvmin <= %s ORDER BY lvmin DESC
            """ % (userRank + 1 if userRank == 0 else userRank, )
        )) is None:
            return await interaction.followup.send(
                "`Não há nenhuma classe no momento.`")

        rankName, rankR, rankG, rankB = all_ranks
        
        try:
            profile_bytes = await get_userAvatar_func(uMember)
        except:
            with open("../src/imgs/extra/Icon-Kiniga.png", "rb") as image:
                profile_bytes = image.read()
                image.close()


        user_iventory = await self.db.fetchrow(
            """
                SELECT moldura, car, banner, badge::jsonb
                FROM iventory 
                WHERE iventory_id = ($1)
            """, userIventoryId )

        user_moldura, user_car, user_banner, user_badge = user_iventory

        mold_id = user_moldura

        # Pega moldura equipada
        moldImage = None
        if mold_id is not None:
            mold = await self.db.fetch("SELECT img_profile FROM molds WHERE id=(\'%s\')" % (mold_id, ))
            if mold:
                moldImage = mold[0][0]

        banner_id = user_banner

        # Pega banner equipado
        bannerImg = None
        if banner_id is not None:
            banner = await self.db.fetch("SELECT img_perfil FROM banners WHERE id=(\'%s\')" % (banner_id, ))
            if banner:
                bannerImg = banner[0][0]
        else:
            bannerImg = "src/imgs/extra/loja/banners/Fy-no-Planeta-Magnético.png"

        # Pega badges equipadas
        badge_ids = user_badge
        badge_images = []

        if badge_ids != '{}':
            badges_values = []
            l = ast.literal_eval(badge_ids)
            for key, value in l.items():
                badges_values.append(value)
            if badge_rows := [j for i in badges_values for j in i] if len(badges_values) > 1 else badges_values:
                if len(badge_rows) > 1:
                    rows = await self.db.fetch(
                        """
                            SELECT img FROM itens 
                            WHERE item_type_id IN %s 
                            ORDER BY lvmin ASC
                        """ % (tuple(str(i) for i in badge_rows),)
                    )
                else:
                    rows = await self.db.fetch(
                        """
                            SELECT img FROM itens
                            WHERE item_type_id = \'%s\'
                            ORDER BY lvmin ASC
                        """ % ( badge_rows[0] )
                    )
                for row in rows:
                    badge_images.append(row[0])

        buffer = await self.bot.loop.run_in_executor(
            None,
            utilities.rankcard.draw_new,
            str(uMember), badge_images, bannerImg,
            moldImage, userInfo, userSpark, userOri,
            userBirth, staff, rankName, rankR, rankG,
            rankB, BytesIO(profile_bytes)
        )

        await interaction.followup.send(
            file=dFile(
                fp=buffer,
                filename='profile_card.png'
            )
        )

    # @longest_cooldown

    @activity_cooldown
    @app_commands.command(name='nivel', description='Monstrará a barra de progresso, bem como a medalha de seu nível.')
    @app_commands.describe(member='Marque o usuário para mostrar seu nível. (opcional)')
    async def nivel(self, interaction: discord.Interaction, member: discord.Member = None) -> None:

        await interaction.response.defer(ephemeral=True, thinking=True)

        if member:
            uMember = member
        else:
            uMember = interaction.user

        user_ = await self.db.fetchrow(
            """
                SELECT rank, xp, xptotal, iventory_id 
                FROM users 
                WHERE id = (\'%s\')
            """ % (uMember.id, )
        )

        if not user_:
            return await interaction.followup.send(
                "%s, você ainda não recebeu experiência." % (uMember.mention)
            )

        user_rank, user_xp, user_xptotal, user_iventory_id  = user_
        

        try:
            background = await self.db.fetchval(
                """
                    SELECT img_perfil 
                    FROM banners 
                    WHERE id=(
                        SELECT banner 
                        FROM iventory 
                        WHERE iventory_id = (\'%s\')
                    )
                """ % (user_iventory_id, )
            )

            if not background:
                background = "src/imgs/extra/loja/banners/Fy-no-Planeta-Magnético.png"
                
        except Exception as e:
            return await interaction.followup.send(
                "Não foi possível pegar o banner no usuário! %s" % (e, )
            )

        total = await self.db.fetch('SELECT COUNT(lvmin) FROM ranks')
        d = re.sub('\\D', '', str(total))
        if int(d) > 0:
            rankss = await self.db.fetchrow(
                """
                    SELECT name, badges, imgxp 
                    FROM ranks 
                    WHERE lvmin <= %s 
                    ORDER BY lvmin DESC
                """ % (user_rank, )
            )
            if rankss:
                moldName, moldImg, xpimg = rankss
            else:
                moldName, moldImg, xpimg = None, None, None


            buffer = await self.bot.loop.run_in_executor(
                None,
                utilities.rankcard.rank,
                user_rank, user_xp, user_xptotal,
                moldName, moldImg, xpimg, background
            )
        else:
            await interaction.followup.send('É preciso adicionar alguma classe primeiro.')

        await interaction.followup.send(file=dFile(fp=buffer, filename='rank_card.png'), ephemeral=True)

    @activity_cooldown
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
    @activity_cooldown
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

    @activity_cooldown
    @app_commands.command(name='pescar')
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

    @activity_cooldown
    @app_commands.command(name='topspark')
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
    @activity_cooldown
    @app_commands.command(name='classes')
    async def classes(self, interaction: discord.Interaction):
        total = await self.db.fetch("SELECT COUNT(lvmin) FROM ranks")
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
                        rows = await self.db.fetch('SELECT * FROM ranks ORDER BY lvmin ASC')
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

    @activity_cooldown
    @app_commands.command(name='info')
    async def info(self, interaction: discord.Interaction, *, content: str) -> None:
        info = "".join(content)
        size = len(info)
        if int(size) > 80:
            return await interaction.response.send_message(
                "O texto deve conter 80 caracteres ou menos, contando espaços.", ephemeral=True)

        await self.db.fetch(
            f"UPDATE users SET info = '{content}' WHERE id = '{interaction.user.id}'"
        )
        await interaction.response.send_message(
            f"```Campo de informações atualizado. Visualize utilizando /perfil```", ephemeral=True)

    @activity_cooldown
    @app_commands.command(name='delinfo')
    async def delinfo(self, interaction: discord.Interaction) -> None:
        await self.db.fetch(f"UPDATE users SET info = (\'\') WHERE id = ('{interaction.user.id}')")
        await interaction.response.send_message("```Campo de informações atualizado. "
                                                "Visualize utilizando d.perfil```", ephemeral=True)

    @activity_cooldown
    @app_commands.command(name='niver')
    @app_commands.checks.cooldown(1, 86400, key=lambda i: (i.guild_id, i.user.id))
    async def niver(self, interaction: discord.Interaction, niver: str) -> None:

        niver = niver.split("/")
        dia = niver[0]
        mes = niver[1]

        await self.db.fetch(f"UPDATE users SET birth = '{dia}/{mes}' WHERE id = ('{interaction.user.id}')")

        await interaction.response.send_message("```Aniversário atualizado!```", ephemeral=True)

    @activity_cooldown
    @app_commands.command(name='delniver')
    async def delniver(self, interaction: discord.Interaction) -> None:
        await self.db.fetch(f"UPDATE users SET birth = ('???') WHERE id = ('{interaction.user.id}')")
        await interaction.response.send_message("```Aniversário atualizado!```", ephemeral=True)

    @activity_cooldown
    @app_commands.command(name='inv')
    async def inv(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        # GET ITENS FROM WITH SPECIFIC KEY
        user_itens = await get_iventory(self, interaction.user.id)
        print(user_itens, flush=True)
        # APPEND ONLY ITEMS KEY
        item_ids = []
        for items in user_itens:
            itemsType = items[0]
            itemsIds = items[1]
            if not itemsIds: continue
            for dicts in itemsIds:
                itemsDict = ast.literal_eval(str(dicts)) if type(dicts) is not dict else dicts
                for k, v in itemsDict.items():
                    item_ids.append(k)

        if not item_ids:
            return await interaction.followup.send(
                "`Você não tem nenhum item. Compre utilizando sparks ou oris na loja! [/loja]`")

        rows = []
        for i in item_ids:
            rows_ = await self.db.fetch("""
                SELECT id, name, img, img_profile, category, type_ FROM itens WHERE item_type_id = \'%s\'
            """ % (i)
            )

            rows.append(rows_)
        items = []
        c = 0
        print(rows, flush=True)
        for rows_ in rows:
            for row in rows_:
                items.append({c: {
                    "id": str(row[0]),
                    "name": str(row[1]),
                    "img": str(row[2]) if str(row[5]) == "Badge" or "Utilizavel" else str(row[3]),
                    "category": str(row[4]).replace(" ", ""),
                    "type": str(row[5])
                }})
                c += 1
                # items.append(row[0])

        print("-*-"*20, flush=True)
        print(items, flush=True)
        print("-*-"*20, flush=True)

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

        print("Tentando gerar páginas...", flush=True)

        pages = await self.bot.loop.run_in_executor(
            None,
            utilities.rankcard.drawiventory,
            banner, spark, ori, items, c
        )

        if pages:
            print(pages, flush=True)

        pages = [os.path.join('./_temp/', i) for i in pages]
        #view = None
        # if len(pages) > 1:
        view = Paginacao(pages, 60, interaction.user)
        await interaction.followup.send(
            file=dFile(rf'{pages[0]}'),
            view=view, ephemeral=True)
        out = interaction.edit_original_response
        view.response = out

    # description='Use diariamente para receber recompensas incríveis'
    @longest_cooldown
    @app_commands.command(name='daily')
    # @app_commands.checks.cooldown(1, 86400)
    async def daily(self, interaction: discord.Interaction):
        chest_itens = {'chest': 80, 'ori': 10, 'xp': 10}
        choosed = random.choices(*zip(*chest_itens.items()), k=1)
        oris = randint(self.cfg.coinsmin, self.cfg.coinsmax)
        xp = randint(self.cfg.min_message_xp, self.cfg.max_message_xp)
        print(choosed)
        if choosed[0] == 'ori':
            oris = randint(self.cfg.coinsmin, self.cfg.coinsmax)
            return await interaction.response.send_message(f"Você ganhou {oris} oris!", ephemeral=True)
        elif choosed[0] == 'xp':
            xp = randint(self.cfg.min_message_xp,
                         self.cfg.max_message_xp)
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

    @activity_cooldown
    @app_commands.command(name='sparks')
    async def sparks(self, interaction: discord.Interaction):
        key_value = await self.db.fetch(f"SELECT spark FROM users WHERE id='{interaction.user.id}'")
        await interaction.response.send_message(f'Você tem {key_value[ 0 ][ 0 ]} dinheiros.', ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(User(bot), guilds=[discord.Object(id=943170102759686174)])
