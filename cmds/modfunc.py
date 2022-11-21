from __future__ import annotations

from datetime import datetime as dt
from datetime import timedelta
from pydoc import describe
from types import NoneType
from arcade import View
from numpy import str0
import requests
import shutil
from asyncio import sleep as asyncsleep
import re
import os
import json

import discord
import discord.utils
from discord.ext import commands
from discord import app_commands
from typing import Literal
from typing import Optional

from base.utilities import utilities
from base.views import Paginacao, reviewButton, publishButton
from base.struct import Config
from base.mail import sendMail, getEmailMessage

from discord import File as dFile

# Mod Functions Commands Class


class ModFunc(commands.Cog, name='Editoria'):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()

        self.bot = bot

        self.db = utilities.database(
            self.bot.loop, self.bot.cfg.postgresql_user, self.bot.cfg.postgresql_password)

        self.ctx_menu = app_commands.ContextMenu(
            name='Avaliar história!',
            callback=self.analise,
        )
        self.bot.tree.add_command(self.ctx_menu)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(
            self.ctx_menu.name, type=self.ctx_menu.type)

    # UTILIDADES
    @app_commands.command(name="ori")
    @app_commands.checks.has_permissions(administrator=True)
    async def ori(self, interaction: discord.Interaction, simbol: Optional[Literal['-', '+']], amount: int, member: discord.Member = None):
        member = member or interaction.user
        if member:
            if simbol == '+':
                await self.db.fetch(f"UPDATE users SET spark = ( spark + {amount}) WHERE id= (\'{member.id}\')")
                return await interaction.response.send_message(f"Foram adicionadas {amount} oris à {member.mention}!", delete_after=10)
            elif simbol == '-':
                await self.db.fetch(f"UPDATE users SET spark = (spark - {amount}) WHERE id= (\'{member.id}\')")
                return await interaction.response.send_message(f"Foram removidas {amount} oris de {member.mention}!", delete_after=10)
        else:
            return await interaction.response.send_message("O usuário não está no servidor")

    # Pin/Unpin shop item

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
    @app_commands.command(name='dest')
    async def dest(self, interaction: discord.Interaction, id: int):
        result = await self.db.fetch(f'SELECT * FROM itens WHERE id = {int(id)}')
        if result:
            await self.db.fetch(f'UPDATE itens SET dest = True WHERE id={int(id)}')
            emb = discord.Embed(
                description=f'O item foi adicionado aos destaques.',
                color=discord.Color.green()).set_footer(
                text='Use [s.tdestaque ID] para tirar o destaque do item.')
            await interaction.response.send_message(f'{interaction.user.mention}', embed=emb)
        else:
            await interaction.response.send_message("Não encontrei um item com esse ID", delete_after=5)

    #
    # Tira destaque do item // Unpin shop item

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
    @app_commands.command(name='tdest')
    async def tdest(self, interaction: discord.Interaction, id: int):
        result = await self.db.fetch(f"SELECT * FROM itens WHERE id = {int(id)}")
        if result:
            await self.db.fetch(f"UPDATE itens SET dest = False WHERE id={int(id)}")
            emb = discord.Embed(
                description=f'O item foi removido dos destaques.',
                color=discord.Color.green()).set_footer(
                text='Use [s.destaque ID] para destacar o item novamente.')
            await interaction.response.send_message(f'{interaction.user.mention}', embed=emb)
        else:
            await interaction.response.send_message("Não encontrei um item com esse ID", delete_after=5)

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
        result = await self.db.fetch(f'SELECT * FROM itens WHERE id = {id}')
        if result:
            await self.db.fetch(f'UPDATE itens SET canbuy = False WHERE id = {id}')
            emb = discord.Embed(
                description=f'O item foi removido da loja.',
                color=discord.Color.green()).set_footer(
                text='Use [s.canbuy ID] para recolocar o item novamente.')
            await interaction.response.send_message(f'{interaction.user.mention}', embed=emb)
        else:
            await interaction.response.send_message("Não encontrei um item com esse ID", delete_after=5)

    @app_commands.command(name='canbuy')
    async def canbuy(self, interaction: discord.Interaction, id: int):
        result = await self.db.fetch(f'SELECT * FROM itens WHERE id = {id}')
        if result:
            await self.db.fetch(f'UPDATE itens SET canbuy = True WHERE id = {id}')
            emb = discord.Embed(
                description=f'O item foi adicionado à loja.',
                color=discord.Color.green()).set_footer(
                text='Use [s.canotbuy ID] para remover o item novamente.')
            await interaction.response.send_message(f'{interaction.user.mention}', embed=emb)
        else:
            await interaction.response.send_message("Não encontrei um item com esse ID", delete_after=5)

    # AVALIAÇÃO DE HISTÓRIAS

    async def getfile(self, message):
        fileInfo = []
        attach = message.attachments
        for i in range(len(attach)):
            # print(attach)
            if i >= 1:
                break

            fileInfo.append([attach[1].url,
                            attach[1].filename])

        res = None
        try:
            url = fileInfo[0][0]
            filename = fileInfo[0][1]
            r = requests.get(url, stream=True)
            r.raise_for_status()
            with open('./_temp/%s' % (filename), 'w') as f:
                f.write(r.text)
            f.close()
            res = r.text

        except Exception as e:
            raise e
        return filename, res

    async def getinfo(self, message):
        try:
            filename, content = await self.getfile(message)
        except Exception as e:
            return await message.channel.send(
                content="`%s`" % (e, ))

        authoremail = re.findall("([\w\.-]+@[\w\.-]+)", content)
        authordiscord = re.findall("([\w\.-]+#[\w\.-]+)", content)
        historyID = re.findall("( #[\w\.-]+)", content)

        return authordiscord, authoremail, str(historyID), filename

    async def checkuseringuild(self, user: str, guild):
        if isinstance(user, str):
            user = user.replace('"', '')
            user = user.replace("'", '')
            user = user.replace("[", '')
            user = user.replace("]", '')
        try:
            if isinstance(user, discord.Member):
                user = guild.get_member_named(user)
            elif isinstance(user, int):
                user = guild.get_member(user)
                user = guild.get_member_named(str(user))
            elif isinstance(user, str):
                raise
        except:
            user = guild.get_member_named(user)
        if user != None:
            return user
        else:
            return "Usuário não encontrado."

    async def senduseringuild(self, author):
        err = None
        errBool = None
        try:
            # to author
            message = discord.Embed(
                title=f"{author.name}, meus parabéns por se tornar um autor da Kiniga!",
                description="\n Fique ligado no canal <#678060799213830201> para saber quando sua história será publicada! ",
                color=0x00ff33).set_author(
                    name="Kiniga Brasil",
                    url='https://kiniga.com/',
                    icon_url='https://kiniga.com/wp-content/uploads/fbrfg/favicon-32x32.png').set_footer(
                        text='Espero que seja muito produtivo escrevendo!')
            await author.send(embed=message)

            errBool = False

        except Exception as e:
            # to staff
            err = e
            errBool = True
            raise e

        return errBool, err

    def channel_check(interaction: discord.Interaction) -> bool:
        with open('config.json', 'r') as f:
            cfg = Config(json.loads(f.read()))
        f.close()
        return interaction.channel.id == cfg.acept_channel or cfg.refuse_channel

    @app_commands.check(channel_check)
    @app_commands.checks.has_any_role(943171518895095869, 943174476839936010, 982960318890254358, 943192163947274341)
    async def analise(self, interaction: discord.Interaction, message: discord.Message):
        accept_channel = self.bot.get_channel(1035252705406500935)  # mudar
        refused_channel = self.bot.get_channel(1035252941927489586)  # mudar

        await interaction.response.defer(ephemeral=False, thinking=True)

        view = reviewButton()
        msgId = await interaction.followup.send(
            "Deseja aceitar ou recusar a história? \n`Use o botão \"Sim\" para aceitar e \"Não\" para recusar.`",
            view=view)

        await view.wait()  # Espera resposta
        # PEGA INFO DA FILE
        authorDiscord, authorEmail, historyID, filename = await self.getinfo(message)

        if view.status == 'accept':

            # checkguild = await self.checkguild()

            useringuild = await self.checkuseringuild(str(authorDiscord), interaction.guild)

            emailhtml, emailtxt = getEmailMessage(status='accept')

            if (isinstance(useringuild, str)):
                return await interaction.response.edit_message(
                    content="`Não foi possível encontrar o/a autor/a no servidor. Favor, entre em contato pessoalmente.`", view=None
                )
            else:
                errBool, err = await self.senduseringuild(useringuild)
                if errBool == True:
                    return await interaction.response.edit_message(
                        content="Não foi possível enviar a mensagem para o/a autor/a. Tente novamente mais tarde.\n\n`%s`" % (err), view=None
                    )
                else:
                    pass
            await accept_channel.send("História %s pronta para ser publicada. \n`"
                                      "Use o botão \"Sim\" para finalizar o processo de publicação, \"Não\" para excluir a história da fila.`" % (
                                          str(historyID), ),
                                      file=dFile(rf'./_temp/{filename}'), view=publishButton(user_discord=authorDiscord, hid=str(historyID), message=message)
                                      )
            # (await self.getinfo(message))[0])
        elif view.status == 'refuse':
            emailhtml, emailtxt = getEmailMessage(status='refuse')
            try:
                for name in os.listdir('./_temp'):
                    if name == filename:
                        os.remove('./_temp/%s' % (name, ))
                else:

                    await interaction.channel.send("`( 〃．．)` Não foi possível remover %s. Marca o Jonathan aí." % (str(historyID)), delete_after=10)
            except Exception as e:
                await interaction.channel.send("`( 〃．．)` Deu um erro aqui... \n`%s` " % (e), delete_after=10)

            await refused_channel.send("`ID %s recusada.`" % (str(historyID)))

            await message.edit(content="**Recusada** (#%s)" % (str(historyID)), attachments=[])
        await msgId.delete()
        await sendMail(email=authorEmail, mailhtml=emailhtml, mailtxt=emailtxt)


async def setup(bot: commands.Bot) -> None:
    # guilds=[discord.Object(id=943170102759686174)]
    await bot.add_cog(ModFunc(bot))
