import discord

from typing import Callable, Coroutine, Optional
from typing_extensions import Self

from discord import Interaction, TextStyle
from discord.ui import Modal, TextInput
from discord.utils import maybe_coroutine

from discord.ui import View
from discord import ui, app_commands

from discord import File as dFile
import os

class Paginacao(View):
    def __init__(self, pages:list, timeout:float, user:discord.Member | None = None) -> None:
        super().__init__(timeout=timeout)
        self.current_page = 0
        self.rmv_pages = pages
        
        self.pages = pages
        #print(self.pages)
        self.user = user
        self.lenght = len(self.pages)-1
        self.children[0].disabled,self.children[1].disabled = True, True
        self.response = None

    async def on_timeout(self):
        for i in self.rmv_pages:
            os.remove(i)
        await self.response(view=self)
        self.stop()
        

    async def update(self, page:int):
        self.current_page = page
        if page==0:
            self.children[0].disabled = True
            self.children[1].disabled = True
            self.children[-1].disabled = False
            self.children[-2].disabled = False
        elif page==self.lenght:
            self.children[0].disabled = False
            self.children[1].disabled = False
            self.children[-1].disabled = True
            self.children[-2].disabled = True
        else:
            for i in self.children: i.disabled=False
    
    async def getPage(self, page):
        ##tem tudo isso aqui pois ele pode ser usado como uma função de base para vários tipos de comando q precisam de paginação
        if isinstance(page, str):
            if page[-4:] == ".png":
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
    
    async def showPage(self, page:int, interaction: discord.Interaction):
        await self.update(page)
        content, embeds, files = await self.getPage(self.pages[page])
        await interaction.response.edit_message(
            content = content,
            embeds = embeds,
            attachments= [files] or [],
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
            i.disabled=True
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
            if interaction.user !=self.user:
                await interaction.response.send_message(
                    "Esse comando é para outra pessoa",
                    ephemeral=True
                )
                return False
        return True