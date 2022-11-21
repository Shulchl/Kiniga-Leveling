from __future__ import annotations

import re
import os
import discord
import requests
import shutil
import ast

from base.utilities import utilities
from base.functions import (
    get_userAvatar_func as getUserAvatar, user_inventory)

from discord import File as dFile
from discord.ext import commands

from typing import Callable, Coroutine, Optional
from typing_extensions import Self

from discord import Interaction, TextStyle
from discord.utils import maybe_coroutine

from discord.ui import View, Modal, TextInput
from discord import app_commands

from base.views import Paginacao

from typing import Union, Any
# CLASS SHOP

botVar = commands.Bot

botVar.shopItems = []
botVar.oldImgs = []


class Shop(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = utilities.database(
            self.bot.loop, self.bot.cfg.postgresql_user, self.bot.cfg.postgresql_password)
    
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
            else:
                img = [f'src/imgs/extra/{tipo}-{name}.png']
                paths = [img_loja]
                img_loja = img[0]

            try:
                count = 0
                for i in range(len(paths)):
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

                return f"``` DADOS INSERIDOS ```"

        except Exception as i:
            return i

    @app_commands.command(name='citem')
    async def citem(self, interaction) -> None:
        """Test command to wait for input. This will trigger a modal."""
        def check(modal: SimpleModalWaitFor, modal_interaction: Interaction) -> bool:
            return modal_interaction.user.id == interaction.user.id
        wait_modal = SimpleModalWaitFor(
            title=f"{interaction.user.name}, insira as informações solicitadas.",
            input_label="What is your name?",
            input_max_length=20,
            check=check,
        )
        await interaction.response.send_modal(wait_modal)

        wait_value = await wait_modal.wait()
        if wait_modal.value is None:
            # Send a followup message to the channel.
            await interaction.followup.send(f"{interaction.user} did not enter a value in time.")
            return
        res = await self.createitem(interaction, wait_modal.value)

        await wait_modal.interaction.response.send_message(res)

    @app_commands.command(name='comprar')
    async def comprar(self, interaction: discord.Interaction, item_id: int) -> None:
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
        user_itens = await user_inventory(self, interaction.user.id, 'get', [str(ivent_key_name)])
        #user_itens = await user_inventory(self, interaction.user.id, 'add', [str(ivent_key_name)], [int(item_id)])
        
        # RETURN IF HAS IT ALREADY
        if ivent_key_name == "Badge":
            for i in user_itens:
                print(i[1])
                if str(item_id) in i[1]:
                    return await interaction.response.send_message("Você já tem esse item.", ephemeral=True)
                else: pass
                
        else:
            if str(item_id) in user_itens[0][1]:
                return await interaction.response.send_message("Você já tem esse item.", ephemeral=True)

        user_info = await self.db.fetch(f"""
            SELECT spark, rank, inventory_id FROM users WHERE id=('{interaction.user.id}')
        """)
        if not user_info:
            return await interaction.response.send_message(
                "Usuário não encontrado na database", ephemeral=True
            )
        spark, rank, iventory_id = user_info[0][0], user_info[0][1], user_info[0][2]
        
        if item_lvmin == None:
            item_lvmin = 0
        if item_value == None:
            item_value = 0
        
        if spark < item_value:
            return await interaction.response.send_message(
                "Você não tem sparks o suficiênte para comprar este item. D:", ephemeral=True
            )
        if int(rank) < int(item_lvmin):
            return await interaction.response.send_message(
                "Você não tem nível o bastante para comprar este item. D:", ephemeral=True
            )
        l = await user_inventory(self, interaction.user.id, 'add', [str(ivent_key_name)], [item_id_uui])
        
        getSpark = await self.db.fetch("""
            UPDATE users SET spark = (spark - %s) WHERE id = ('%s') RETURNING spark
        """ % (item_value, interaction.user.id, )
        )

        await interaction.response.send_message(
            "Você comprou %s! \n%s sparks foram descontados de sua carteira e você agora tem %s. " % (
                item_name if item_type != "Badge" else f"Badge {item_name}", item_value, getSpark[0][0]), ephemeral=True)

    #   Equipar
    @app_commands.command(name='equipar')
    async def equipar(self, interaction: discord.Interaction, item_id: int):
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
                    ) WHERE ivent_id=(
                        SELECT inventory_id FROM users WHERE id=(\'%s\')
                    )

                    RETURNING badge::jsonb;
                """ % (itype, group_, id_, interaction.user.id))
            else:
                await self.db.fetch("""
                    UPDATE iventory SET %s=(\'%s\') 
                    WHERE ivent_id=(
                        SELECT inventory_id FROM users WHERE id = (\'%s\')
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
    async def equipar_error(self, interaction: discord.Interaction, error):
        if isinstance(error, commands.BadArgument):
            await interaction.response.send_message("```Esse item não existe.```", ephemeral=True)
        if isinstance(error, commands.MissingRequiredArgument):
            await interaction.response.send_message("```Você não tem esse item.```", ephemeral=True)

    #   Equipar
    @app_commands.command(name='desequipar')
    async def desequipar(self, interaction: discord.Interaction, item_id: int):
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
                    ) WHERE ivent_id=(
                        SELECT inventory_id FROM users WHERE id=(\'%s\')
                    )

                    RETURNING badge::jsonb;
                """ % (itype, group_, item_id, interaction.user.id))
            else:
                await self.db.fetch("""
                    UPDATE iventory SET %s= Null
                    WHERE ivent_id=(
                        SELECT inventory_id FROM users WHERE id = (\'%s\')
                    );
                """ % (itype, interaction.user.id, ))
        except Exception as e:
            raise e
        else:
            await interaction.response.send_message("%s %s %s!" %
                (type_.title(), name,"deequipada" if type_.endswith('a') else "equipado"), ephemeral=True)            

    #   LOJAs
    @app_commands.command(name='loja')
    async def loja(self, interaction: discord.Interaction, member: discord.Member = None) -> None:
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
        
            userResources = await self.db.fetch("SELECT spark, ori, inventory_id FROM users WHERE id = ('%s')" % (uMember.id, ))
                
            spark = userResources[0][0]
            if userResources[0][0] is None:
                spark = 0
            
            ori = userResources[0][1]
            if userResources[0][1] is None:
                ori = 0
            
            banner_id = await self.db.fetch("""
                SELECT img_loja FROM banners WHERE id =
                    (
                        SELECT banner FROM iventory WHERE ivent_id=('%s')
                    )
                    """ % (userResources[0][2], ))
            banner = None
            
            if banner_id:
                banner = banner_id[0][0]
        await interaction.response.defer(ephemeral = True, thinking = True)
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

class SimpleModalWaitFor(Modal):
    def __init__(
        self,
        title: str = "Waiting For Input",
        *,
        check: Optional[Callable[[Self, Interaction],
                                 Union[Coroutine[Any, Any, bool], bool]]] = None,
        timeout: int = 300,
        input_label: str = "Input text",
        input_max_length: int = 100,
        input_min_length: int = 5,
        input_style: TextStyle = TextStyle.short,
        input_placeholder: Optional[str] = None,
        input_default: Optional[str] = None,
    ):
        super().__init__(title=title, timeout=timeout, custom_id="wait_for_modal")
        self._check: Optional[Callable[[Self, Interaction],
                                       Union[Coroutine[Any, Any, bool], bool]]] = check
        self.value: Optional[str] = None
        self.interaction: Optional[Interaction] = None

        # type, name, valor: int, nivel: int, img_loja, img_perfil=None, img_round_title=None,canbuy: bool = True

        self.name = TextInput(
            label="Qual o nome do item?",
            placeholder="",
            max_length=30,
            min_length=3,
            style=input_style,
            default=input_default,
            custom_id=self.custom_id + "_input_field",
        )
        self.type = TextInput(
            label="Qual o tipo do item?",
            placeholder="(Moldura/Titulo/Consumivel)",
            max_length=input_max_length,
            min_length=input_min_length,
            style=input_style,
            default=input_default,
            custom_id=self.custom_id + "0" + "_input_field",
        )
        self.value = TextInput(
            label="Qual o valor do item?",
            placeholder="Números inteiros apenas.",
            max_length=45,
            min_length=3,
            style=input_style,
            default=input_default,
            custom_id=self.custom_id + "1" + "_input_field",
        )
        self.img_loja = TextInput(
            label="Link da imagem que aparecerá na loja?",
            placeholder="(Dimensão máxima: 170x140)",
            min_length=1,
            style=input_style,
            default=input_default,
            custom_id=self.custom_id + "3" + "_input_field",
        )
        self.img_perfil = TextInput(
            label="Link da imagem que aparecerá no perfil?",
            placeholder="Exemplo: [url perfil, url arredondado] (Se não for Moldura, não insira nada aqui)",
            required=False,
            style=input_style,
            default=input_default,
            custom_id=self.custom_id + "4" + "_input_field",
        )
        # self.img_round_title = TextInput(
        #    label="Link da imagem arredondada do nome do rank?",
        #    placeholder="(Se o Tipo for Titulo, não insira nada aqui)",
        #    required = False,
        #    style=input_style,
        #    default=input_default,
        #    custom_id=self.custom_id + "5" + "_input_field",
        # )

        self.add_item(self.name)
        self.add_item(self.type)
        self.add_item(self.value)
        self.add_item(self.img_loja)
        self.add_item(self.img_perfil)
        # self.add_item(self.img_round_title)

    async def interaction_check(self, interaction: Interaction) -> bool:
        if self._check:
            allow = await maybe_coroutine(self._check, self, interaction)
            return allow

        return True

    async def on_submit(self, interaction: Interaction) -> None:
        itens = interaction.data
        values = []

        for key, value in itens.items():
            if key == 'components':
                for i in value:
                    for value in i['components']:
                        values.append(value['value'])

        self.value = values
        self.interaction = interaction
        self.stop()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Shop(bot))
