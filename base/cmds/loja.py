import re
import os
import discord
import requests
import shutil
import ast

from base.utilities import utilities
from base.views import Paginacao, SimpleModalWaitFor as cItemModal
from base.functions import (
    get_userAvatar_func as getUserAvatar, 
    user_inventory, 
    print_progress_bar as progress, 
    error_delete_after)

from discord import File as dFile, Interaction, app_commands
from discord.ext import commands
from discord.utils import format_dt
from discord.app_commands.errors import AppCommandError

# CLASS SHOP

botVar = commands.Bot

botVar.shopItems = []
botVar.oldImgs = []

longest_cooldown = app_commands.checks.cooldown(
    2, 300.0, key=lambda i: (i.guild_id, i.user.id))
activity_cooldown = app_commands.checks.cooldown(
    1, 5.0, key=lambda i: (i.guild_id, i.user.id))


class Shop(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = utilities.database(self.bot.loop)

    async def cog_app_command_error(
        self, 
        interaction: Interaction, 
        error: AppCommandError
    ):
        if isinstance(
            error, 
            app_commands.CommandOnCooldown
        ):
            return await error_delete_after(interaction, error)
        if isinstance(
            error, 
            app_commands.TransformerError
        ):
            return await interaction.response.send_message(
                "O texto deve conter 80 caracteres ou menos, contando espaços.", ephemeral=True)

    def checktype_(self, type):
        match str(type).upper():
            case "MOLDURA":
                itype = 'mold'
            case "TITULO":
                itype = 'title'
            case "BANNER":
                itype = 'banner'
            case "CARRO":
                itype = 'car'
            case "BADGE":
                itype = 'badge'
        return itype

    @activity_cooldown
    @app_commands.command(name='cbanners')
    async def createBanners(self, interaction) -> None:

        await interaction.response.defer(ephemeral=True, thinking=True)
        banners = [filename for filename in os.listdir(
            'src/imgs/banners') if filename.endswith('.png')]
        count = 0
        for i, item in enumerate(banners):
            progress(i, len(banners), " progresso de banners criadas")
            item_name = ' '.join(item.split('-'))[0:-4]
            await self.db.fetch("""
                INSERT INTO banners 
                    (name, img_loja, img_perfil, canbuy, value) 
                VALUES 
                    ('%s',
                    'src/imgs/banners/%s',
                    'src/imgs/banners/%s',
                    true, 15500000) 
                ON CONFLICT (name) DO NOTHING 
            """ % (item_name, item, item))
            count = i+1

        print(f"{count} Banners criadas")
        await interaction.followup.send(f"{count} Banners criadas", ephemeral=True)

    async def createitem(self, interaction, value):
        name = value[0].title()
        tipo = value[1].title()
        img_loja = value[3]
        img_perfil = ''
        img_round_title = ''
        img = []
        paths = []

        print(value)

        if value[4] != '':
            imgs = value[4].split(",")
            img_perfil = imgs[0]
            img_round_title = imgs[1]

        if value[2] == '':
            valor = 0
        else:
            valor = int(value[2])

        print(value)
        try:
            if tipo == "Moldura":
                img = [f'src/imgs/molduras/molduras-loja/{tipo}-{name}.png',
                       f"src/imgs/molduras/molduras-perfil/bordas/{tipo}-{name}.png",
                       f"src/imgs/molduras/molduras-perfil/titulos/{tipo}-{name}.png"]
                paths = [img_loja, img_perfil]
                img_loja = img[0],
                img_perfil = img[1],
                img_round_title = img[2],

            elif tipo == "Titulo":
                img = [f'src/imgs/titulos/{tipo}-{name}.png']
                paths = [img_loja]
                img_loja = img[0]
            elif tipo == "Banner":
                img = [f'src/imgs/banners/{tipo}-{name}.png']
            else:
                img = [f'src/imgs/extra/{tipo}-{name}.png']
                paths = [img_loja]
                img_loja = img[0]

            try:
                count = 0
                for i, value in enumerate(paths):
                    response = requests.get(paths[i], stream=True)
                    with open(img[i], 'wb') as out_file:
                        shutil.copyfileobj(response.raw, out_file)
                    del response
                    count += 1

                print(f"{count} / {len(paths)} imagens salvas")

            except Exception as i:
                print(i)
                return "```{i}```"

            else:
                try:
                    await self.db.fetch(
                        "INSERT INTO itens (name, type_, value, img, img_profile, imgd, lvmin, canbuy) "
                        "VALUES (\'{}\', \'{}\', {}, \'{}\', \'{}\', \'{}\', 0, True) ON CONFLICT (name)"
                        " DO NOTHING".format(name, tipo, valor, img_loja, img_perfil, img_round_title))
                    print(f"Informações salvas na DB")
                except Exception as e:
                    return e

                print("``` DADOS INSERIDOS ```")

        except Exception as i:
            return i

    @activity_cooldown
    @app_commands.command(name='citem')
    async def citem(self, interaction) -> None:
        """Test command to wait for input. This will trigger a modal."""
        def check(modal: cItemModal, modal_interaction: Interaction) -> bool:
            return modal_interaction.user.id == interaction.user.id

        wait_modal = cItemModal(
            title=f"{interaction.user.name}, insira as informações solicitadas.",
            check=check,
        )
        await interaction.response.send_modal(wait_modal)

        await wait_modal.wait()

        if wait_modal.value is None:
            # Send a followup message to the channel.
            await interaction.followup.send(f"{interaction.user} did not enter a value in time.")
            return

        res = await self.createitem(interaction, wait_modal.value)

        await wait_modal.interaction.response.send_message(res)

    #@activity_cooldown
    @app_commands.command(name='comprar')
    async def comprar(self, interaction: Interaction, item_id: int) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        # await ctx.message.delete()
        item = await self.db.fetch("""
            SELECT item_type_id, value, type_, lvmin, name FROM itens 
                WHERE id=(
                    SELECT id FROM shop WHERE id=(%s)
                )
            """ % (item_id, ))

        if not item:
            return await interaction.response.send_message(
                f"{interaction.user.mention}, ou não existe um item com esse número(ID) "
                "ou o item não está disponível para compra.", ephemeral=True)

        item_id_uui,  item_value, item_type, item_lvmin, item_name = item[
            0][0], item[0][1], item[0][2], item[0][3], item[0][4]

        ivent_key_name = item_type
        # print (ivent_key_name)

        # GET ITENS FROM WITH SPECIFIC KEY
        user_itens = await user_inventory(self, interaction.user.id, 'get', str(ivent_key_name), item_id_uui)
        # user_itens = await user_inventory(self, interaction.user.id, 'add', [str(ivent_key_name)], [int(item_id)])
        # RETURN IF HAS IT ALREADY
        if ivent_key_name == "Badge":
            for i in user_itens:
                if str(item_id) in i[1]:
                    return await interaction.followup.send("Você já tem esse item.", ephemeral=True)
                else:
                    pass
        elif ivent_key_name == "Banner":
            for i in user_itens:
                if i[0] and str(i[0]) == str(item_id_uui):
                    return await interaction.followup.send("Você já tem esse item.", ephemeral=True)
        else:
            if str(item_id) in user_itens[0][1]:
                return await interaction.followup.send("Você já tem esse item.", ephemeral=True)

        user_info = await self.db.fetch(f"""
            SELECT spark, rank, iventory_id FROM users WHERE id=('{interaction.user.id}')
        """)
        if not user_info:
            return await interaction.followup.send(
                "Usuário não encontrado na database", ephemeral=True
            )
        spark, rank, iventory_id = user_info[0][0], user_info[0][1], user_info[0][2]

        if item_lvmin == None:
            item_lvmin = 0
        if item_value == None:
            item_value = 0

        if spark < item_value:
            return await interaction.followup.send(
                "Você não tem sparks o suficiênte para comprar este item. D:", ephemeral=True
            )
        if int(rank) < int(item_lvmin):
            return await interaction.followup.send(
                "Você não tem nível o bastante para comprar este item. D:", ephemeral=True
            )
        l = await user_inventory(self, interaction.user.id, 'add', str(ivent_key_name), item_id_uui)

        getSpark = await self.db.fetch(
            """
                UPDATE users SET spark = (spark - %s) WHERE id = (\'%s\') RETURNING spark
            """ % (int(item_value), interaction.user.id, )
        )

        await interaction.followup.send(
            "Você comprou %s! \n%s sparks foram descontados de sua carteira e você agora tem %s. " % (
                item_name if item_type != "Badge" else f"Badge {item_name}", item_value, getSpark[0][0]), ephemeral=True)

    @activity_cooldown
    @app_commands.command(name='equipar')
    async def equipar(self, interaction: Interaction, item_id: int):
        item = await self.db.fetch("""
            SELECT item_type_id, type_, name, group_ FROM itens WHERE id=(%s)
            
        """ % (item_id, )
        )
        if item:
            id_ = item[0][0]
            type_ = item[0][1]
            name = item[0][2]
            group_ = item[0][3]

        inv = await user_inventory(self, interaction.user.id, 'get', [type_])

        inv_ids = []
        for row in inv:
            l = ast.literal_eval(row[1])
            for key, value in l.items():
                inv_ids.append(key)

        itype = self.checktype_(type_)

        if str(id_) not in inv_ids:
            return await interaction.response.send_message("Você não tem esse item.", ephemeral=True)

        try:
            if itype == "badge":
                await self.db.fetch("""
                    UPDATE iventory SET badge = (
                        SELECT jsonb_set(
                            %s::jsonb,
                            '{%s}'::text[],
                            '\"%s\"'::jsonb
                        )
                    ) WHERE iventory_id=(
                        SELECT iventory_id FROM users WHERE id=(\'%s\')
                    )

                    RETURNING badge::jsonb;
                """ % (itype, group_, id_, interaction.user.id))
            else:
                await self.db.fetch("""
                    UPDATE iventory SET %s=(\'%s\') 
                    WHERE iventory_id=(
                        SELECT iventory_id FROM users WHERE id = (\'%s\')
                    )
                    RETURNING mold;
                """ % (itype, id_, interaction.user.id, ))
        except Exception as e:
            raise e
        else:
            await interaction.response.send_message("%s %s %s!" %
                                                    (type_.title(), name,
                                                     "equipada" if type_.endswith('a') else "equipado"), ephemeral=True)

    @equipar.error
    async def equipar_error(self, interaction: Interaction, error):
        if isinstance(error, commands.BadArgument):
            await interaction.response.send_message("```Esse item não existe.```", ephemeral=True)
        elif isinstance(error, commands.MissingRequiredArgument):
            await interaction.response.send_message("```Você não tem esse item.```", ephemeral=True)
        else:
            pass

    #   Equipar
    @activity_cooldown
    @app_commands.command(name='desequipar')
    async def desequipar(self, interaction: Interaction, item_id: int):
        item = await self.db.fetch("""
            SELECT item_type_id, type_, name, group_ FROM itens WHERE id=(%s)
            
        """ % (item_id, )
        )
        if item:
            item_id = item[0][0]
            type_ = item[0][1]
            name = item[0][2]
            group_ = item[0][3]

        inv = await user_inventory(self, interaction.user.id, 'get', [type_])

        inv_ids = []
        for row in inv:
            l = ast.literal_eval(row[1])
            for key, value in l.items():
                inv_ids.append(key)

        itype = self.checktype_(type_)

        if str(item_id) not in inv_ids:
            return await interaction.response.send_message("Você não tem esse item.", ephemeral=True)

        try:
            if itype == "badge":
                await self.db.fetch("""
                    UPDATE iventory SET badge = (
                        SELECT jsonb_set(
                            %s::jsonb,
                            '{%s}'::text[],
                            '\"%s\"'::jsonb
                        )
                    ) WHERE iventory_id=(
                        SELECT iventory_id FROM users WHERE id=(\'%s\')
                    )

                    RETURNING badge::jsonb;
                """ % (itype, group_, item_id, interaction.user.id))
            else:
                await self.db.fetch("""
                    UPDATE iventory SET %s= Null
                    WHERE iventory_id=(
                        SELECT iventory_id FROM users WHERE id = (\'%s\')
                    );
                """ % (itype, interaction.user.id, ))
        except Exception as e:
            raise e
        else:
            await interaction.response.send_message("%s %s %s!" %
                                                    (type_.title(), name, "deequipada" if type_.endswith('a') else "equipado"), ephemeral=True)
    @desequipar.error
    async def desequipar_error(self, interaction: Interaction, error):
        if isinstance(error, commands.BadArgument):
            await interaction.response.send_message("```Esse item não existe.```", ephemeral=True)
        elif isinstance(error, commands.MissingRequiredArgument):
            await interaction.response.send_message("```Você não tem esse item.```", ephemeral=True)
        else:
            pass

    #   LOJAs
    @activity_cooldown
    @app_commands.command(name='loja')
    async def loja(self, interaction: Interaction, member: discord.Member = None) -> None:
        uMember = member
        if not uMember:
            uMember = interaction.user or interaction.guild.get_member(
                interaction.user.id)

        total = await self.db.fetch("SELECT COUNT(id) FROM shop")
        total = int(re.sub(r"\D", "", str(total[0][0])))
        if total <= 0:
            return await interaction.response.send_message("`No momento, não temos itens na loja.`", ephemeral=True)

        rows = await self.db.fetch("""
            SELECT id, name, type_, value, img, lvmin 
            FROM shop ORDER BY value Desc
        """)

        try:
            items = []
            for i in range(total):
                items.append({i: {
                    "id": str(rows[i][0]),
                    "name": str(rows[i][1]),
                    "type": str(rows[i][2]),
                    "value": str(rows[i][3]),
                    "img": str(rows[i][4]),
                    "lvmin": str(rows[i][5])
                }})
        except Exception as e:
            raise e
        else:

            userResources = await self.db.fetch("SELECT spark, ori, iventory_id FROM users WHERE id = ('%s')" % (uMember.id, ))

            spark = userResources[0][0]
            if userResources[0][0] is None:
                spark = 0

            ori = userResources[0][1]
            if userResources[0][1] is None:
                ori = 0

            banner_id = await self.db.fetch("""
                SELECT img_loja FROM banners WHERE id =
                    (
                        SELECT banner FROM iventory WHERE iventory_id=('%s')
                    )
                    """ % (userResources[0][2], ))
            banner = None

            if banner_id:
                banner = banner_id[0][0]

        await interaction.response.defer(ephemeral=True, thinking=True)
        exist = os.path.exists(
            rf'./_temp/{botVar.oldImgs[0] if len(botVar.oldImgs) > 0 else False}')
        if botVar.shopItems == items and exist != False:
            items = botVar.shopItems
            pages = botVar.oldImgs
            #pageFile = botVar.oldImgs[0]

        else:
            botVar.oldImgs = []
            #pageFile = []

            pages = utilities.shopnew.drawloja(
                total, spark, ori, items, banner
            )
            botVar.oldImgs = pages
            botVar.shopItems = items

        pages = [os.path.join('./_temp/', i) for i in pages]
        view = Paginacao(pages, 60, interaction.user)
        await interaction.followup.send(file=dFile(rf'{pages[0]}'), view=view, ephemeral=True)
        out = interaction.edit_original_response
        view.response = out

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Shop(bot))
