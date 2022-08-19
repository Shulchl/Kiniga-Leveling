from __future__ import annotations

import logging
import re
from asyncio import sleep as asyncsleep
from io import BytesIO
from random import randint

import aiohttp
import discord
import requests
import shutil

from shutil import ExecError

from base.utilities import utilities
from discord import File as dFile
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.errors import BadArgument, MissingRequiredArgument
from discord import app_commands

from discord import Intents

from typing import Callable, Coroutine, Optional
from typing_extensions import Self

from discord import Interaction, TextStyle
from discord.ui import Modal, TextInput
from discord.utils import maybe_coroutine

# CLASS SHOP


class Shop(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = utilities.database(
            self.bot.loop, self.bot.cfg.postgresql_user, self.bot.cfg.postgresql_password)
        

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
                img = [ f'src/imgs/molduras/molduras-loja/{tipo}-{name}.png',
                        f"src/imgs/molduras/molduras-perfil/bordas/{tipo}-{name}.png",
                        f"src/imgs/molduras/molduras-perfil/titulos/{tipo}-{name}.png"]
                paths = [ img_loja, img_perfil ]
                img_loja = img[ 0 ],
                img_perfil = img[ 1 ],
                img_round_title = img[ 2 ],
         
            elif tipo == "Titulo":
                img = [ f'src/imgs/titulos/{tipo}-{name}.png' ]
                paths = [ img_loja ]
                img_loja = img[ 0 ]
            else:
                img = [ f'src/imgs/extra/{tipo}-{name}.png' ]
                paths = [ img_loja ]
                img_loja = img[ 0 ]

            try:
                count = 0
                for i in range(len(paths)):
                    response = requests.get(paths[ i ], stream=True)
                    with open(img[ i ], 'wb') as out_file:
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
                        "INSERT INTO itens (name, type, value, img, img_profile, imgd, lvmin, canbuy) "
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
    @app_commands.guilds(discord.Object(id=943170102759686174))
    async def comprar(self, interaction: discord.Interaction, id: int) -> None:
        # await ctx.message.delete()
        item = await self.db.fetch(
            f'SELECT id, name, value, type, lvmin FROM itens WHERE id=\'{id}\' and canbuy = True')
        if item:
            item_id, item_name, item_value, item_type, lvmin = item[
                0][0], item[0][1], item[0][2], item[0][
                3], item[0][4]
            try:
                inv = await self.db.fetch(f'SELECT coin, inv, rank FROM users WHERE id = (\'{interaction.user.id}\')')
                if inv:
                    if int(lvmin - 9) <= int(inv[0][2]):
                        if int(inv[0][0]) >= int(item_value):
                            if item_type == 'Moldura':
                                tipo, esstipo = "a moldura", "essa moldura"
                            elif item_type == 'Titulo':
                                tipo, esstipo = "o título", "esse título"
                            else:
                                tipo, esstipo = "o/a " + \
                                    str(item_type), "esse item"
                            emb = discord.Embed(
                                title='Bela compra!',
                                description=f'Você acaba de comprar {tipo} {item_name}!',
                                color=discord.Color.green()
                            ).set_footer(
                                text='Para equipar em seu perfil, basta digitar:\n'
                                     's.equipar'
                            )

                            if inv[0][1] is not None:
                                invent = str(inv[0][1])
                                if str(id) in invent.split(","):
                                    return await interaction.response.send_message(f"Você já tem {esstipo}.")
                                else:
                                    return await self.db.fetch(
                                        f'UPDATE users SET inv = (\'{str(invent) + "," + str(item_id)}\'), coin = ({int(inv[ 0 ][ 0 ]) - int(item_value)})  WHERE id=\'{interaction.user.id}\'')
                            else:
                                await self.db.fetch(
                                    f'UPDATE users SET inv = (\'{item_id}\'), coin = ({int(inv[ 0 ][ 0 ]) - int(item_value)}) WHERE id=\'{interaction.user.id}\'')
                            return await interaction.response.send_message(embed=emb)
                        else:
                            return await interaction.response.send_message("Você é pobre, vá trabalhar.")
                    else:
                        return await interaction.response.send_message("Você não tem nível para comprar isso.")
                else:
                    return await interaction.response.send_message(
                        "Aconteceu algo enquanto eu tentava buscar as informações do usuário. Tente novamente mais "
                        "tarde.",
                        delete_after=5)
            except:
                raise
        else:
            return await interaction.response.send_message(
                f'{interaction.user.mention}, ou não existe um item com esse número(ID) ou o item não está disponível para compra.')

    #

    #   Equipar
    @app_commands.command(name='equipar')
    @app_commands.guilds(discord.Object(id=943170102759686174))
    async def equipar(self, interaction: discord.Interaction, id: int):
        item = await self.db.fetch(f"SELECT name, type FROM itens WHERE id=('{id}')")
        if item:
            name = item[0][0]
            type = item[0][1]

            inv = await self.db.fetch(f"SELECT inv FROM users WHERE id=('{interaction.user.id}')")
            if inv:
                inv = str(inv[0][0]).split(",")
                if str(id) in inv:
                    if str(type).upper() == "MOLDURA":
                        await self.db.fetch(f"UPDATE users SET mold=(\'{id}\') WHERE id=('{interaction.user.id}')")
                        await interaction.response.send_message("{} {} equipada!"
                                                                .format(type.capitalize(), name.title()))
                    if str(type).upper() == "TITULO":
                        await self.db.fetch(f"UPDATE users SET title=(\'{id}\') WHERE id=('{interaction.user.id}')")
                        await interaction.response.send_message("{} {} equipada!"
                                                                .format(type.capitalize(), name.title()))
            else:
                raise MissingRequiredArgument
        else:
            raise BadArgument

    #   Equipar
    @app_commands.command(name='desequipar')
    @app_commands.guilds(discord.Object(id=943170102759686174))
    async def desequipar(self, interaction: discord.Interaction, id: int):
        item = await self.db.fetch(f"SELECT name, type FROM itens WHERE id='{id}'")
        if item:
            name = item[0][0]
            type = item[0][1]

            inv = await self.db.fetch(f"SELECT inv FROM users WHERE id='{interaction.user.id}'")
            if inv:
                inv = str(inv[0][0]).split(",")
                if str(id) in inv:
                    if str(type).upper() == "MOLDURA":
                        await self.db.fetch(f"UPDATE users SET mold=Null WHERE id='{interaction.user.id}'")
                        await interaction.response.send_message("{} {} desequipada!".format(type.capitalize(), name.title()))
                    if str(type).upper() == "TITULO":
                        await self.db.fetch(f"UPDATE users SET title=Null WHERE id='{interaction.user.id}'")
                        await interaction.response.send_message("{} {} desequipada!".format(type.capitalize(), name.title()))
            else:
                raise MissingRequiredArgument
        else:
            raise BadArgument

    @equipar.error
    async def equipar_error(self, interaction: discord.Interaction, error):
        if isinstance(error, commands.BadArgument):
            await interaction.response.send_message("```Esse item não existe.```", ephemeral=True)
        if isinstance(error, commands.MissingRequiredArgument):
            await interaction.response.send_message("```Você não tem esse item.```", ephemeral=True)

    async def nextpage(self, interaction, page, member: discord.Member):
        # await app_commands.CommandTree.get_command(app_commands.tree, 'loja', interaction.guild)

        # return await self.command(interaction, page, member)
        cmd = self.bot.tree.get_command('loja', guild=interaction.guild)
        # ctxo = await self.bot.tree.call(cmd)
        return await cmd(interaction, page, member)

    #   LOJA
    @app_commands.command(name='loja')
    @app_commands.guilds(discord.Object(id=943170102759686174))
    async def loja(self, interaction: discord.Interaction, page: int = None, member: discord.Member = None) -> None:
        uMember = member
        if not uMember:
            uMember = interaction.user or interaction.guild.get_member(
                interaction.user.id)

        total = await self.db.fetch("SELECT COUNT(id) FROM itens WHERE canbuy = True")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{uMember.avatar.replace(size=1024, format='png')}") as resp:
                userImg = await resp.read()

        for t in total:
            d = re.sub(r"\D", "", str(t))
            total = int(d)
            if total > 0:
                if not page:
                    page = 1

                rows = await self.db.fetch(
                    "SELECT id, name, type, value, img, imgd, lvmin, dest FROM itens WHERE canbuy = True ORDER BY id "
                    "Desc")
                if rows:
                    count = 0
                    # if (total/3) > int(total/3):
                    #    return await ctx.send(f"O limite de páginas é {int(total/3)}", delete_after=5)
                    # elif (total/3) < int(total/3):
                    #    return await ctx.send(f"O limite de páginas é {int(total/3)+1}", delete_after=5)
                    try:
                        items = []
                        while count < total:
                            items.append({count: {
                                "id": str(rows[count][0]),
                                "name": str(rows[count][1]),
                                "type": str(rows[count][2]),
                                "value": str(rows[count][3]),
                                "img": str(rows[count][4]),
                                "imgs": str(rows[count][5]),
                                "lvmin": str(rows[count][6]),
                                "dest": str(rows[count][7])
                            }})

                            count += 1
                    except Exception:
                        raise
                    for coin in await self.db.fetch(f"SELECT coin FROM users WHERE id = (\'{uMember.id}\')"):
                        if coin[0] is None:
                            coin[0] = 0
                        coin = coin[0]
                    buffer = utilities.shop.drawloja(
                        total, items, page, coin, BytesIO(userImg))  # byteImg

                    page = int(page)
                    # count = 1
                    # opt = dict()

                    # while ((((page+count)*6)-5) ** 0.5 <= total ** 0.5):
                    #    opt = (
                    #            SelectOption(
                    #                label=str(count), value=str(count)
                    #            )
                    #        )
                    #    count +=1

                    # components = [
                    #    Button(style=ButtonStyle.blue,
                    #           label="Anterior",
                    #           custom_id=str(page - 1),
                    #           emoji=":rewind:",
                    #           disabled=True if (page - 1 <= 0) else False
                    #           ),
                    #        Button(style=ButtonStyle.green,
                    #           label="Atualizar",
                    #           custom_id=str(page),
                    #           emoji=":repeat:"
                    #           ),
                    #    Button(style=ButtonStyle.blue,
                    #           label="Próxima",
                    #            custom_id=str(page + 1),
                    #           emoji=":fast_forward:",
                    #           disabled=False if ((((page + 1) * 6) - 5) ** 0.5 <= total ** 0.5) else True
                    #            ),
                    # ]
                    async with interaction.channel.typing():
                        try:
                            buffer = utilities.shop.drawloja(total, items, page, coin,
                                                                BytesIO(userImg)
                                                            )
                        except Exception as e:
                            return interaction.response.send_message(f"```{e}```") 
                        
                        view = shopPageConfirm(total, page, coin, items)
                        await interaction.response.send_message(file=dFile(
                                                                        fp=buffer, 
                                                                        filename='lojinha.png'
                                                                    ), 
                                                                    view=view,
                                                                    ephemeral=True
                                                                )   
                    print("got view value")

class shopPageConfirm(discord.ui.View):

    def __init__(self, total, page, coin, items):
        super().__init__(timeout=100.0)
        self.items = items
        self.total = total
        self.pageNumb = int(page)
        self.coin = coin
        self.value = None
        self.buffer = None
        print("starting")
        print(self.pageNumb)

    @discord.ui.button(label='Anterior', style=discord.ButtonStyle.green, emoji='⏪', custom_id='anterior:green',
                       disabled=True) 
    async def previousbutton(self, interaction: discord.Interaction, button: discord.ui.Button):
        print("prev")

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{interaction.user.avatar.replace(size=1024, format='png')}") as resp:
                self.userImg = await resp.read()

        if int(self.pageNumb ) == 0:
            print("<<< Acabaram as páginas ")
            self.stop()

        if int(self.pageNumb -1 ) == 0:
            button.disabled = True
        else:
            button.disabled = False

        self.pageNumb -= 1
        async with interaction.channel.typing():
            self.buffer = utilities.shop.drawloja(self.total, self.items, self.pageNumb, self.coin, BytesIO(self.userImg))
        await interaction.response.edit_message(attachments=[dFile(fp=self.buffer, filename='lojinha.png')], view=self)

    @discord.ui.button(label='Atualizar', style=discord.ButtonStyle.primary, emoji='🔁', custom_id='atualizar:green',
                       disabled=False)
    async def actualizebutton(self, interaction: discord.Interaction, button: discord.ui.Button):
        print("att")

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{interaction.user.avatar.replace(size=1024, format='png')}") as resp:
                self.userImg = await resp.read()

        async with interaction.channel.typing():
            self.buffer = utilities.shop.drawloja(self.total, self.items, self.pageNumb, self.coin, BytesIO(self.userImg))
        await interaction.response.edit_message(attachments=[dFile(fp=self.buffer, filename='lojinha.png')], view=self)

        self.stop()

    @discord.ui.button(label='Próximo', style=discord.ButtonStyle.green, emoji='⏩', custom_id='proxima:green',
                       disabled= False)
    async def nextbutton(self, interaction: discord.Interaction, button: discord.ui.Button):        
        print("next")

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{interaction.user.avatar.replace(size=1024, format='png')}") as resp:
                self.userImg = await resp.read()

        self.value = False

        if int(((self.pageNumb + 1) * 6) ** 0.8) <= self.total:
            button.disabled = True
        else:
            button.disabled = False

        self.pageNumb += 1

        async with interaction.channel.typing():
            self.buffer = utilities.shop.drawloja(self.total, self.items, self.pageNumb, self.coin, BytesIO(self.userImg))
        await interaction.response.edit_message(attachments=[dFile(fp=self.buffer, filename='lojinha.png')], view=self)


class SimpleModalWaitFor(Modal):
    def __init__(
        self,
        title: str = "Waiting For Input",
        *,
        check: Optional[Callable[[Self, Interaction], Union[Coroutine[Any, Any, bool], bool]]] = None,
        timeout: int = 300,
        input_label: str = "Input text",
        input_max_length: int = 100,
        input_min_length: int = 5,
        input_style: TextStyle = TextStyle.short,
        input_placeholder: Optional[str] = None,
        input_default: Optional[str] = None,
    ):
        super().__init__(title=title, timeout=timeout, custom_id="wait_for_modal")
        self._check: Optional[Callable[[Self, Interaction], Union[Coroutine[Any, Any, bool], bool]]] = check
        self.value: Optional[str] = None
        self.interaction: Optional[Interaction] = None

        #type, name, valor: int, nivel: int, img_loja, img_perfil=None, img_round_title=None,canbuy: bool = True


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
            required = False,
            style=input_style,
            default=input_default,
            custom_id=self.custom_id + "4" + "_input_field",
        )
        #self.img_round_title = TextInput(
        #    label="Link da imagem arredondada do nome do rank?",
        #    placeholder="(Se o Tipo for Titulo, não insira nada aqui)",
        #    required = False,
        #    style=input_style,
        #    default=input_default,
        #    custom_id=self.custom_id + "5" + "_input_field",
        #)


        self.add_item(self.name)
        self.add_item(self.type)
        self.add_item(self.value)
        self.add_item(self.img_loja)
        self.add_item(self.img_perfil)
        #self.add_item(self.img_round_title)

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
    await bot.add_cog(Shop(bot), guilds=[ discord.Object(id=943170102759686174) ])
