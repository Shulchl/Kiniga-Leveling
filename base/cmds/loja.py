import re
import os
import discord
import requests
import shutil
import ast
import json

from base.utilities import utilities
from base.views.views import Paginacao, SimpleModalWaitFor as cItemModal
from base.functions import (
    activity_cooldown,
    get_iventory,
    print_progress_bar as progress,
    error_delete_after,
    inventory_update_key,
    report_error,
    get_profile_info,
    send_error_response
)

from discord import File as dFile, Interaction, app_commands
from discord.ext import commands
from discord.app_commands.errors import AppCommandError

from base.Spinovelbot import SpinovelBot

# CLASS SHOP
botVar = SpinovelBot

botVar.shopItems = []
botVar.oldImgs = []


class Shop(commands.Cog):
    def __init__(self, bot: SpinovelBot) -> None:
        self.bot = bot

    def help_custom(self) -> tuple[str, str, str]:
        emoji = '🏪'
        label = "Loja"
        description = "Mostra a lista de comandos de loja."
        return emoji, label, description

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
            if error.command.name in ['usar', 'equipar', 'desequipar', 'canotbuy', 'canbuy']:
                res = "Não existe um item com esse número(ID) ou o item não está disponível para compra."

        elif isinstance(error, commands.MissingRequiredArgument):
            if error.command.name in ['comprar', 'usar', 'equipar', 'desequipar', 'canotbuy', 'canbuy']:
                res = "```Você não tem esse item.```"

        else:

            await report_error(self, interaction, error)
            res = "Ocorreu um erro inesperado. Favor, tente novamente.\nO errro já foi relatado à um administrador."

        await send_error_response(self, interaction, res)

    # @activity_cooldown
    @app_commands.command(name='comprar')
    async def comprar(self, interaction: Interaction, item_id: int) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        # await ctx.message.delete()
        result = await self.bot.database.query(
            f"""
                SELECT
                    i.id, i.value, i.type_, i.lvmin, i.name, i.group_, i.value_ori
                FROM itens i
                    JOIN shop l ON i.id = l.id
                WHERE l.id = {item_id}
            """)

        if not result:
            return await interaction.followup.send(
                f"{interaction.user.mention}, ou não existe um item com esse número(ID) "
                "ou o item não está disponível para compra.", ephemeral=True)

        item_real_id, item_value, item_type, item_lvmin, item_name, item_group, item_value_ori = result

        if item_lvmin == None:
            item_lvmin = 0
        if item_value == None:
            item_value = 0
        if item_value_ori == None:
            item_value_ori = 0

        user_ = await get_profile_info(self.bot, interaction.user.id, interaction.user.name)
        user_id, user_name, email, userInfo, rank, xp, xptotal, spark, ori, userBirth, created_at, updated_at = user_
        update_result = await inventory_update_key(
            self.bot, user_id, item_type,
            str(item_group + '.ids'),
            str(item_real_id), 'buy', 1
        )

        if update_result == "ITEM_ALREADY_EXISTS":
            return await interaction.followup.send(
                "Você não pode comprar mais de um item não consumível.", ephemeral=True)

        if update_result == "ITEM_ADDED_SUCCESSFULLY":
            if value_type := 'spark' if item_value != 0 else 'ori':
                if value_type == 'spark':
                    await self.bot.database.select(
                        '''
                            UPDATE users 
                            SET spark = (spark - $1)
                            WHERE id = ($2)
                            RETURNING spark
                        ''', item_value, str(interaction.user.id))
                    getCoin = spark - item_value
                else:
                    await self.bot.database.select(
                        '''
                            UPDATE users 
                            SET ori = (ori - $1)
                            WHERE id = ($2)
                            RETURNING ori
                        ''', item_value_ori, str(interaction.user.id))
                    getCoin = ori - item_value_ori

            await interaction.followup.send(
                "Você comprou %s! \n%s %s foram descontados de sua carteira e "
                "você agora tem %s." % (
                    item_name,
                    item_value if value_type == 'sparks' else item_value_ori,
                    value_type + 's', getCoin), ephemeral=True)

    @app_commands.command(name='usar')
    async def usar(self, interaction: Interaction, item_id: int) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        # await ctx.message.delete(
        result = await self.bot.database.select("""
            SELECT i.item_type_id, i.value, i.type_, i.lvmin, i.name, i.group_ 
            FROM itens i
                JOIN shop l ON i.item_type_id = l.item_type_id
            WHERE l.id=$1
            """, item_id, )

        if not result:
            raise commands.BadArgument

        item_real_id, item_value, item_type, item_lvmin, item_name, item_group = result

        # if item_type not in ['Utilizavel', 'Carro']:
        #     return await interaction.followup.send('Item não utilizável.', ephemeral=True)

        if item_lvmin == None:
            item_lvmin = 0
        if item_value == None:
            item_value = 0

        # GET ITENS FROM WITH SPECIFIC KEY
        # Check if the item_real_id already exists in the user_itens
        update_result = await inventory_update_key(
            self.bot, str(interaction.user.id), item_type,
            str(item_group + '.ids'),
            str(item_real_id), 'use', 0
        )

        if update_result == 'ITEM_DONT_EXISTS':
            return await interaction.followup.send(
                "Você não pode consumir um item que não tem.", ephemeral=True)

        if update_result == 'ITEM_ALREADY_EXISTS':
            return await interaction.followup.send(
                "Você não pode consumir um item que não é consumível.", ephemeral=True)

        if update_result == "ITEM_ADDED_SUCCESSFULLY":
            await interaction.followup.send(
                "Você usou %s!" % (item_name), ephemeral=True)

    @activity_cooldown
    @app_commands.command(name='equipar')
    async def equipar(self, interaction: Interaction, item_id: int):
        await interaction.response.defer(thinking=True)
        result = await self.bot.database.select(
            """
                SELECT 
                    item_type_id, type_, name, group_ 
                FROM itens 
                WHERE id=($1)
            """, int(item_id)
        )
        if not result:
            return await interaction.followup.send(
                "Esse item não existe.", ephemeral=True)

        id_, type_, name, group_ = result

        inv = await get_iventory(self, interaction.user.id)
        inv_ids = []
        for row in inv:
            if not row[1]: continue
            for items in row[1]:
                l = ast.literal_eval(str(items))
                for key, value in l.items():
                    inv_ids.append(key)

        if str(id_) not in inv_ids:
            raise commands.MissingRequiredArgument
        # É JSONB PORQUE É POSSÍVEL EQUIPAR MAIS DE 1 BADGE
        if type_.upper() == "BADGE":
            result = await self.bot.database.select(
                """
                     SELECT badge::json FROM iventory
                     WHERE iventory_id = (
                        SELECT iventory_id FROM users
                        WHERE id=($1)
                    )
                """, str(interaction.user.id))
            data = ast.literal_eval(result[0])

            if group_ not in data:
                data[group_] = []

            if str(id_) in data[group_]:
                return await interaction.followup.send(
                    "Item já equipado.", ephemeral=True
                )
            lengh_itens = data.get(group_)
            if len(lengh_itens) >= 5:
                return await interaction.followup.send(
                    "Não é possívle equipar mais de 5 badges.",
                    ephemeral=True
                )
            data[group_].append(str(id_))
            data = json.dumps(data)

            await self.bot.database.select(
                """
                    UPDATE iventory set badge = $1
                    WHERE iventory_id = (
                        SELECT iventory_id FROM users
                        WHERE id=($2)
                    )
                """, str(data), str(interaction.user.id)
            )
        else:
            print(type_, flush=True)
            await self.bot.database.select(
                """
                    UPDATE iventory SET %s=(\'%s\')
                    WHERE iventory_id=(
                        SELECT iventory_id FROM users 
                        WHERE id = (\'%s\')
                    )
                """ % (type_, id_, interaction.user.id)
            )
        await interaction.followup.send(
            "%s %s %s!" % (
                type_.title(),
                name,
                "equipada" if type_.endswith('a') else "equipado"
            ), ephemeral=True
        )

    #   Equipar
    @activity_cooldown
    @app_commands.command(name='desequipar')
    async def desequipar(self, interaction: Interaction, item_id: int):
        await interaction.response.defer(thinking=True)
        result = await self.bot.database.select(
            """
                SELECT 
                    item_type_id, type_, name, group_ 
                FROM itens 
                WHERE id=($1)
            """, str(item_id)
        )
        if result:
            item_id, type_, name, group_ = result

        inv = await get_iventory(self, interaction.user.id)

        inv_ids = []
        for row in inv:
            if not row[1]: continue
            for items in row[1]:
                l = ast.literal_eval(str(items))
                for key, value in l.items():
                    inv_ids.append(str(key))

        if str(item_id) not in inv_ids:
            return await interaction.followup.send(
                "Você não tem esse item.",
                ephemeral=True
            )
        result = await self.bot.database.select(
            """
                 SELECT badge::json FROM iventory
                 WHERE iventory_id = (
                    SELECT iventory_id FROM users
                    WHERE id=(\'%s\')
                )
            """ % (interaction.user.id))
        data = ast.literal_eval(result[0])

        if str(item_id) not in data[group_]:
            return await interaction.followup.send(
                "Esse item não está equipado.",
                ephemeral=True
            )
        data[group_].remove(str(item_id))
        data = json.dumps(data)

        try:
            if type_ == "badge":
                await self.bot.database.select(
                    """
                        UPDATE iventory SET badge = \'%s\'
                        WHERE iventory_id = (
                            SELECT iventory_id FROM users
                            WHERE id = ('%s')
                        )
                    """ % (data, interaction.user.id,)
                )
            else:
                await self.bot.database.select("""
                    UPDATE iventory SET %s = \'%s\'
                    WHERE iventory_id=(
                        SELECT iventory_id FROM users
                        WHERE id = (\'%s\')
                    );
                """ % (type_, data, interaction.user.id,)
                                               )

        except Exception as e:
            self.bot.log(message=e, name="cmds.loja")
        else:
            await interaction.followup.send(
                "%s %s %s!" %
                (type_.title(), name,
                 "desequipada" if type_.endswith('a') else "desequipado"),
                ephemeral=True
            )

    #   LOJAs
    @activity_cooldown
    @app_commands.command(name='loja')
    async def loja(self, interaction: Interaction, member: discord.Member = None) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            uMember = member
            if not uMember:
                uMember = interaction.user or interaction.guild.get_member(
                    interaction.user.id)

            total = await self.bot.database.select("shop", "COUNT(id)")
            total = int(re.sub(r"\D", "", str(total[0])))
            if total <= 0:
                return await interaction.followup.send(
                    "`No momento, não temos itens na loja.`",
                    ephemeral=True
                )

            result = await self.bot.database.select(
                "shop",
                "`id`, `name`, `type_`, `value`, `img`, `lvmin`, `category`",
                None, "value Desc"
            )

            try:
                items = []
                for i in range(total):
                    items.append({i: {
                        "id": str(result[i][0]),
                        "name": str(result[i][1]),
                        "type": str(result[i][2]),
                        "value": str(result[i][3]),
                        "img": str(result[i][4]),
                        "lvmin": str(result[i][5]),
                        "category": str(result[i][6])
                    }})
            except Exception as e:
                self.bot.log(message=e, name="cmd.loja")
            else:

                userResources = await self.bot.database.select(
                    "users",
                    "`spark`, `ori`", f"id='{uMember.id}'"
                )

                spark, ori = userResources

                if not spark:
                    spark = 0
                if not ori:
                    ori = 0

                banner_id = await self.bot.database.select(
                    "banners", "img_loja",
                    f"id=(SELECT banner FROM inventory WHERE id='{uMember.id}')"
                )
                banner = None

                if banner_id:
                    banner = banner_id[0]

            exist = os.path.exists(
                rf'./_temp/{botVar.oldImgs[0] if len(botVar.oldImgs) > 0 else False}')
            if botVar.shopItems == items and exist != False:
                items = botVar.shopItems
                pages = botVar.oldImgs
                # pageFile = botVar.oldImgs[0]

            else:
                botVar.oldImgs = []
                # pageFile = []
                try:
                    pages = await self.bot.loop.run_in_executor(
                        None,
                        utilities.shopnew.drawloja,
                        total, spark, ori, items, banner
                    )
                except Exception as a:
                    await interaction.followup.send(a)
                    self.bot.log(message=a, name="cmd.loja")
                else:
                    botVar.oldImgs = pages
                    botVar.shopItems = items

            pages = [os.path.join('./_temp/', i) for i in pages]
            view = Paginacao(pages, 60, interaction.user)
            await interaction.followup.send(
                file=dFile(rf'{pages[0]}'),
                view=view, ephemeral=True)
            out = interaction.edit_original_response
            view.response = out
        except Exception as i:
            await interaction.followup.send(f"`{i}`", ephemeral=True)
            self.bot.log(message=i, name="cmd.loja")

    #   SHOP OPTIONS
    @activity_cooldown
    @app_commands.checks.has_any_role(
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
    @app_commands.command(name='canotbuy')
    async def canotbuy(self, interaction: discord.Interaction, id: int):
        result = await self.bot.database.select(f'SELECT * FROM itens WHERE id = {id}')
        if result:
            await self.bot.database.select(f'UPDATE itens SET canbuy = False WHERE id = {id}')
            emb = discord.Embed(
                description=f'O item foi removido da loja.',
                color=discord.Color.green()).set_footer(
                text='Use [s.canbuy ID] para recolocar o item novamente.')
            await interaction.response.send_message(f'{interaction.user.mention}', embed=emb)
        else:
            await interaction.response.send_message("Não encontrei um item com esse ID", delete_after=5)

    @activity_cooldown
    @app_commands.command(name='canbuy')
    async def canbuy(self, interaction: discord.Interaction, id: int):
        result = await self.bot.database.select(f'SELECT * FROM itens WHERE id = {id}')
        if result:
            await self.bot.database.select(f'UPDATE itens SET canbuy = True WHERE id = {id}')
            emb = discord.Embed(
                description=f'O item foi adicionado à loja.',
                color=discord.Color.green()).set_footer(
                text='Use [s.canotbuy ID] para remover o item novamente.')
            await interaction.response.send_message(f'{interaction.user.mention}', embed=emb)
        else:
            await interaction.response.send_message("Não encontrei um item com esse ID", delete_after=5)

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
            await self.bot.database.select("""
                INSERT INTO banners 
                    (name, img_loja, img_perfil, canbuy, value) 
                VALUES 
                    ('%s',
                    'src/imgs/banners/%s',
                    'src/imgs/banners/%s',
                    true, 15500000) 
                ON CONFLICT (name) DO NOTHING 
            """ % (item_name, item, item))
            count = i + 1

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

        if value[4] != '':
            imgs = value[4].split(",")
            img_perfil = imgs[0]
            img_round_title = imgs[1]

        if value[2] == '':
            valor = 0
        else:
            valor = int(value[2])

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
                    try:
                        response = requests.get(paths[i], stream=True)
                        with open(img[i], 'wb') as out_file:
                            shutil.copyfileobj(response.raw, out_file)
                        del response
                    except Exception as b:
                        print(b, flush=True)
                        self.bot.log(message=b, name="cmds.loja")
                    count += 1

                print(f"{count} / {len(paths)} imagens salvas", flush=True)

            except Exception as i:
                print(i)
                return f"```{i}```"

            else:
                try:
                    await self.bot.database.select(
                        """
                            INSERT INTO itens (
                                name,
                                type_,
                                value,
                                img,
                                img_profile,
                                imgd,
                                lvmin,
                                canbuy
                            ) VALUES (%s, %s, %s, %s, %s, %s, 0, True)
                            ON CONFLICT (name) DO NOTHING
                        """ % (
                            str(name),
                            str(tipo),
                            int(valor),
                            str(img_loja),
                            str(img_perfil),
                            str(img_round_title),
                        )
                    )
                    print(f"Informações salvas na DB", flush=True)
                except Exception as e:
                    return e

                print("``` DADOS INSERIDOS ```", flush=True)

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


async def setup(bot: SpinovelBot) -> None:
    await bot.add_cog(Shop(bot), guilds=[discord.Object(id=943170102759686174)])
