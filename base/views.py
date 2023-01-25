import discord
import os
import json
import re

from typing_extensions import Self
from typing import List, Union, Any, Callable, Coroutine, Optional

from discord import Embed, Interaction, TextStyle
from discord.ui import View, Modal, TextInput
from discord.utils import maybe_coroutine

from discord import ui, app_commands

from discord import File as dFile

from base.struct import Config

from base.functions import (getRelease, sendEmb)


class Paginacao(View):
    def __init__(self, pages: list, timeout: float, user: discord.Member | None = None) -> None:
        super().__init__(timeout=timeout)
        self.current_page = 0
        self.rmv_pages = pages

        self.pages = pages
        # print(self.pages)
        self.user = user
        self.lenght = len(self.pages)-1
        self.children[0].disabled, self.children[1].disabled = True, True
        self.response = None

    async def on_timeout(self):
        for i in self.rmv_pages:
            os.remove(i)
        await self.response(view=self)
        self.stop()

    async def update(self, page: int):
        self.current_page = page
        if page == 0:
            self.children[0].disabled = True
            self.children[1].disabled = True
            self.children[-1].disabled = False
            self.children[-2].disabled = False
        elif page == self.lenght:
            self.children[0].disabled = False
            self.children[1].disabled = False
            self.children[-1].disabled = True
            self.children[-2].disabled = True
        else:
            for i in self.children:
                i.disabled = False

    async def getPage(self, page):
        # tem tudo isso aqui pois ele pode ser usado como uma função de base para vários tipos de comando q precisam de paginação
        if isinstance(page, str):
            if page[-4:] == ".png" or ".jpg":
                with open(page, 'rb') as fp:
                    return None, [], dFile(fp, f'{page}')
            else:
                return page, [], []
        elif isinstance(page, discord.Embed):
            return None, [page], []
        elif isinstance(page, discord.File):
            return None, [], dFile(page)
        elif isinstance(page, List):
            if all(isinstance(x, discord.Embed) for x in page):
                return None, page, []
            if all(isinstance(x, discord.File) for x in page):
                return None, [], dFile(page)
            else:
                pass
        else:
            pass

    async def showPage(self, page: int, interaction: discord.Interaction):
        await self.update(page)
        content, embeds, files = await self.getPage(self.pages[page])
        await interaction.response.edit_message(
            content=content,
            embeds=embeds,
            attachments=[files] or [],
            view=self
        )

    @ui.button(emoji='⏪', style=discord.ButtonStyle.blurple)
    async def first_page(self, interaction, button):
        await self.showPage(0, interaction)

    @ui.button(emoji='◀️', style=discord.ButtonStyle.green)
    async def before_page(self, interaction, button):
        await self.showPage(self.current_page - 1, interaction)

    @ui.button(emoji='⏹️', style=discord.ButtonStyle.red)
    async def stop_page(self, interaction, button):
        for i in self.children:
            i.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()

        for i in self.pages:
            os.remove(i)

    @ui.button(emoji='▶️', style=discord.ButtonStyle.green)
    async def next_page(self, interaction, button):
        await self.showPage(self.current_page + 1, interaction)

    @ui.button(emoji='⏩', style=discord.ButtonStyle.blurple)
    async def last_page(self, interaction, button):
        await self.showPage(self.lenght, interaction)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.user:
            if interaction.user != self.user:
                await interaction.response.send_message(
                    "Esse comando é para outra pessoa",
                    ephemeral=True
                )
                return False
        return True
class reviewButton(View):
    def __init__(self, *, timeout=180) -> None:
        super().__init__(timeout=timeout)
        self.status = None

    async def on_timeout(self):
        for child in self.children:
            child.disable = True
        await self.response(view=self)
        self.stop()

    @ui.button(label='Sim', style=discord.ButtonStyle.green)
    async def accept_button(self, interaction, button):
        self.status = 'accept'

        self.stop()

    @ui.button(label='Não', style=discord.ButtonStyle.red)
    async def refuse_button(self, interaction, button):
        self.status = 'refuse'

        self.stop()

    @ui.button(label='Cancelar', style=discord.ButtonStyle.gray)
    async def cancel_button(self, interaction, button):
        for i in self.children:
            i.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()
class publishButton(View):
    def __init__(self, user_discord, hid, message) -> None:
        super().__init__()
        self.status = None
        self.user_discord = user_discord
        self.hid = hid
        self.message = message

        with open('config.json', 'r') as f:
            self.cfg = Config(json.loads(f.read()))

    async def release(self, interaction):
        # author = await self.fetch_user(interation.user.id)
        if not self.user_discord:
            return await interaction.response.send_message(
                'Você não adicionou um autor.', delete_after=15, ephemeral=True)

        if isinstance(self.user_discord, discord.Member):
            user = interaction.guild.get_member(self.user_discord.id)
            user = interaction.guild.get_member_named(user)
        elif isinstance(self.user_discord, list):
            member = [m.replace('"', '') for m in self.user_discord]
            member = ''.join(member)
            user = interaction.guild.get_member_named(member)
        elif isinstance(self.user_discord, str):
            member = self.user_discord.replace('"', '')
            member = ''.join(member)
            user = interaction.guild.get_member_named(member)

        if not user:
            return await interaction.response.send_message(
                "Não encontrei ninguém com o nome \"%s\"." % (user if user != None else self.user_discord, ), ephemeral=True)

        try:
            autorRole = discord.utils.get(interaction.guild.roles,
                                          id=self.cfg.aut_role)
            creatorRole = discord.utils.get(interaction.guild.roles,
                                            id=self.cfg.creat_role)
            markAuthorRole = discord.utils.get(interaction.guild.roles,
                                               id=self.cfg.mark_role)
            eqpRole = discord.utils.get(interaction.guild.roles,
                                        id=self.cfg.eqp_role)
            channel = interaction.guild.get_channel(self.cfg.chat_release)

            embb = discord.Embed(title='Deseja lançar uma nova história?',
                                 description='O ideal seria aguardar alguns segundos após publicar, para que o bot possa identificar a nova história',
                                 color=discord.Color.green()).set_footer(text='Use a reação para confirmar.')

            view = reviewButton()
            view.remove_item(view.cancel_button)

            await interaction.response.edit_message(embed=embb, view=view)

            await view.wait()
            # eqpRole in i.user.roles and

            if view.status == 'accept':
                try:
                    # await interaction.response.defer(ephemeral=False, thinking=True)
                    releaseMessage = await getRelease(self, interaction)
                    userMessages = await sendEmb(user=user, author=interaction.user)

                    ## Fazer um doc de errors para embeds ##
                except Exception as u:
                    return await interaction.user.send(content=u)

                else:
                    if releaseMessage.title == "Ops":
                        return await interaction.channel.send(embed=releaseMessage)
                    else:
                        # '\@everyone',

                        await channel.send(embed=releaseMessage)

                        await user.add_roles(markAuthorRole, autorRole, creatorRole if not markAuthorRole in user.roles else autorRole, creatorRole)

                        await user.send(embeds=userMessages)

                        releaseMessage = discord.Embed(
                            title=f"História Publicada!",
                            color=0x00ff33).set_author(
                            name="Kiniga Brasil",
                            url='https://kiniga.com/',
                            icon_url='https://kiniga.com/wp-content/uploads/fbrfg/favicon-32x32.png'
                        ).set_footer(text='Qualquer coisa, marque o Shuichi! :D')

                return releaseMessage

            elif view.status == 'refuse':
                try:
                    emb = discord.Embed(
                        description='Certo!',
                        color=discord.Color.blue())
                    await user.remove_roles(markAuthorRole, autorRole, creatorRole
                                            if not markAuthorRole in user.roles
                                            else autorRole, creatorRole)

                    return emb
                except Exception as a:
                    return "%s Não consegui finalizar por conta do seguinte erro: \n%s \n\n Marca o Jonathan aí." % (interaction.user.mention, a, )
        # Fim
        except Exception as e:
            return "Ocorreu um erro \n `%s` \n Tente novamente em alguns segundos." % (e, )

    @ui.button(label='Publicar', style=discord.ButtonStyle.green)
    async def publish_button(self, interaction, button):
        self.status = 'publish'
        res = await self.release(interaction)
        try:
            if (isinstance(res, str)):
                await interaction.response.edit_message(content=res)
            elif (isinstance(res, discord.Embed)):
                newres = res.to_dict()
                newres["title"] = "História %s Publicada" % (self.hid,)
                res = Embed.from_dict(newres)
                await interaction.response.edit_message(embed=res)
        except: 
            await interaction.message.delete()
            if (isinstance(res, str)):
                await interaction.channel.send(content=res)
            elif (isinstance(res, discord.Embed)):
                newres = res.to_dict()
                newres["title"] = "História %s Publicada" % (self.hid,)
                res = Embed.from_dict(newres)
                await interaction.channel.send(embed=res)
        #await self.message.edit(content="**Aceita** (#%s)" % (self.hid))
        await self.message.add_reaction('✔')
        self.stop()

    @ui.button(label='Remover', style=discord.ButtonStyle.red)
    async def remove_button(self, interaction, button):
        self.status = 'remove'
        for i in self.children:
            self.remove_item(i)
        hid = re.search(r"#\d+", str(interaction.message.content))
        await interaction.response.edit_message(content='`História %s retirada da fila por %s.`' % (hid.group(), interaction.user), view=self)
        await self.message.add_reaction('❌')
        self.stop()
class SimpleModalWaitFor(Modal):
    def __init__(
        self,
        title: Optional[str] = None,
        *,
        check: Optional[Callable[[Self, Interaction],
                                 Union[Coroutine[Any, Any, bool], bool]]] = None,
        timeout: int = 300,
        input_label: Optional[str] = None,
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
        print(values)

        self.value = values
        self.interaction = interaction
        self.stop()

class editItemModal(Modal):
    def __init__(
        self,
        title: Optional[str] = None,
        *,
        check: Optional[Callable[[Self, Interaction],
                                 Union[Coroutine[Any, Any, bool], bool]]] = None,
        timeout: int = 300,
        input_label: Optional[str] = None,
        input_max_length: int = 100,
        input_min_length: int = 5,
        input_style: TextStyle = TextStyle.short,
        input_placeholder: Optional[str] = None,
        input_default: Optional[str] = None,
    ):
        super().__init__(title=title, timeout=timeout, custom_id="edit_item_modal")
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
        print(values)

        self.value = values
        self.interaction = interaction
        self.stop()
