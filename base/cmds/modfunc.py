import requests
import re
import os
import json
import discord
import sys

from discord.ext import commands
from discord import app_commands
from typing import Literal
from typing import Optional

from discord.app_commands.errors import AppCommandError

from base.utilities import utilities
from base.views import reviewButton, publishButton, editItemModal
from base.struct import Config
from base.mail import Mail
from base.webhooks import *
from base.functions import (
    error_delete_after,
    getfile,
    inventory_update_key
)

from discord import File as dFile

# Mod Functions Commands Class

longest_cooldown = app_commands.checks.cooldown(
    2, 300.0, key=lambda i: (i.guild_id, i.user.id))
activity_cooldown = app_commands.checks.cooldown(
    1, 5.0, key=lambda i: (i.guild_id, i.user.id))


class ModFunc(commands.Cog, name='Editoria', command_attrs=dict(hidden=True)):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        self.db = utilities.database(self.bot.loop)

        with open('config.json', 'r') as f:
            self.cfg = Config(json.loads(f.read()))

        # TRELLO THINGS
        self.trelloList = str(self.cfg.trelloList)
        self.trelloKey = str(self.cfg.trelloKey)
        self.trelloToken = str(self.cfg.trelloToken)

        self.ctx_menu = [
            app_commands.ContextMenu(
                name='Avaliar história!',
                callback=self.analise,
            ),
            app_commands.ContextMenu(
                name='Publicar história!',
                callback=self.publish,
            ),
            app_commands.ContextMenu(
                name='Remover cartão!',
                callback=self.trello_cart_remove,
            ),
            app_commands.ContextMenu(
                name='Alterar cartão!',
                callback=self.trello_cart_alter,
            )
        ]
        for a in self.ctx_menu:
            self.bot.tree.add_command(a)

    async def cog_app_command_error(
            self,
            interaction: discord.Interaction,
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

    async def cog_unload(self) -> None:
        for a in self.ctx_menu:
            self.bot.tree.remove_command(
                a.name, type=a.type)

    def cog_load(self):
        sys.stdout.write(f'Cog carregada: {self.__class__.__name__}\n')
        sys.stdout.flush()

    @commands.hybrid_group(name='opt')
    @commands.is_owner()
    @commands.guild_only()
    async def opt(self, ctx):
        pass

    @activity_cooldown
    @opt.command(name="spark")
    @app_commands.checks.has_permissions(administrator=True)
    async def spark(self, ctx, simbolo: Optional[Literal['-', '+']], quantia: int,
                    member: discord.Member = None):
        member = member or ctx.author
        if not simbolo:
            simbolo = '+'
        if member:
            if simbolo == '+':
                await self.db.execute("UPDATE users SET spark = ( spark + $1) WHERE id= ($2)", quantia, str(member.id))
                return await ctx.send(
                    f"Foram adicionadas {quantia} sparks à {member.mention}!"
                )
            elif simbolo == '-':
                await self.db.execute("UPDATE users SET spark = ( spark - $1) WHERE id= ($2)", quantia, str(member.id))
                return await ctx.send(
                    f"Foram removidas {quantia} sparks de {member.mention}!"
                )
        else:
            return await ctx.send(
                "O usuário não está no servidor"
            )

    @activity_cooldown
    @opt.command(name="ori")
    @app_commands.checks.has_permissions(administrator=True)
    async def ori(self, ctx, simbolo: Optional[Literal['-', '+']], quantia: int,
                    member: discord.Member = None):
        member = member or ctx.author
        if not simbolo:
            simbolo = '+'
        if member:
            if simbolo == '+':
                await self.db.execute("UPDATE users SET ori = ( ori + $1) WHERE id= ($2)", quantia, str(member.id))
                return await ctx.send(
                    f"Foram adicionadas {quantia} oris à {member.mention}!"
                )
            elif simbolo == '-':
                await self.db.execute("UPDATE users SET ori = ( ori - $1) WHERE id= ($2)", quantia, str(member.id))
                return await ctx.send(
                    f"Foram removidas {quantia} oris de {member.mention}!"
                )
        else:
            return await ctx.send(
                "O usuário não está no servidor"
            )

    @activity_cooldown
    @opt.command(name="item")
    @app_commands.checks.has_permissions(administrator=True)
    async def item(self, ctx, item_id, member: discord.Member = None):
        if not member:
            member = ctx.author

        item = await self.db.fetch("""
            SELECT item_type_id, type_, group_, name FROM itens 
                WHERE id=( '%s' )
            """ % (item_id,))
        if not item:
            return await ctx.send("Não encontrei um item com esse id.")

        user_iventory_id = await self.db.fetchval(
            "SELECT iventory_id FROM users WHERE id = ( '%s' ) " % (member.id,)
        )
        print(type(str(user_iventory_id.hex)), flush=True)

        item_id_uui, item_group, item_subgroup, ivent_name, ivent_id = item[0][0], item[0][1], item[0][2], item[0][
            3], str(user_iventory_id.hex)

        print([i for i in [str(user_iventory_id.hex), item_group, item_subgroup, ivent_name, ivent_id]])

        update_result = await inventory_update_key(
            self, ivent_id, item_group, str(item_subgroup + '.ids'), item_id_uui, 'buy', 1
        )

        if update_result == "ITEM_ALREADY_EXISTS":
            return await ctx.send(
                "O usuário já tem esse item.", delete_after=10)

        if update_result == "ITEM_ADDED_SUCCESSFULLY":
            await ctx.send(update_result)

    # AVALIAÇÃO DE HISTÓRIAS
    async def getinfo(self, message):
        try:
            filename, content = await getfile(message)
        except Exception as e:
            return await message.channel.send(
                content="`%s`" % (e,))

        authoremail = re.findall("([\w\.-]+@[\w\.-]+)", content)
        authordiscord = re.findall("([\w\.-]+#[\w\.-]+)", content)
        historyID = re.findall("( #[\w\.-]+)", content)

        return authordiscord[0], authoremail[0], historyID[0], filename, content

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
        errBool = False
        try:
            # to author
            message = discord.Embed(
                title=f"{author.name}, meus parabéns por se tornar um autor da Kiniga!",
                description="Sua história acaba de ser aceita.\n"
                            "Fique ligado(a) no canal <#678060799213830201> para saber quando sua história será publicada! ",
                color=0x00ff33).set_author(
                name="Kiniga Brasil",
                url='https://kiniga.com/',
                icon_url='https://kiniga.com/wp-content/uploads/fbrfg/favicon-32x32.png').set_footer(
                text='Espero que seja muito produtivo escrevendo!')
            await author.send(embed=message)

        except Exception as e:
            # to staff
            err = e
            errBool = True
            raise (err)

        return errBool, err

    @activity_cooldown
    @app_commands.checks.has_any_role(943171518895095869, 943174476839936010, 982960318890254358, 943192163947274341)
    async def analise(self, interaction: discord.Interaction, message: discord.Message):
        await interaction.response.defer(ephemeral=True, thinking=True)

        ## CANAIS ÚTEIS
        self.publish_channel = self.bot.get_channel(int(self.cfg.publish_c))
        self.refused_channel = self.bot.get_channel(int(self.cfg.refuse_c))  # mudar
        self.trello_log_channel = self.bot.get_channel(int(self.cfg.trello_l_c))

        view = reviewButton()
        await interaction.followup.send(
            "Deseja aceitar ou recusar a história? \n`Use o botão \"Sim\" para aceitar e \"Não\" para recusar.`",
            view=view, ephemeral=True)

        await view.wait()  # Espera resposta
        # PEGA INFO DA FILE
        authorDiscord, authorEmail, historyID, filename, content = await self.getinfo(message)
        if view.status == 'cancel':
            return

        elif view.status == 'accept':

            # checkguild = await self.checkguild()

            useringuild = await self.checkuseringuild(str(authorDiscord), interaction.guild)

            emailhtml, emailtxt = Mail.getEmailMessage(status='accept')

            if (isinstance(useringuild, str)):
                return await interaction.response.edit_message(
                    content="`Não foi possível encontrar o/a autor/a no servidor. Favor, entre em contato pessoalmente.`",
                    view=None
                )
            else:
                errBool, err = await self.senduseringuild(useringuild)
                if errBool == True:
                    return await interaction.response.edit_message(
                        content="Não foi possível enviar a mensagem para o/a autor/a. Tente novamente mais tarde.\n\n`%s`" % (
                            err), view=None
                    )
                else:
                    await interaction.edit_original_response(
                        content="A mensagem foi enviada ao(à) autor(a) com sucesso. (ID %s)" % (str(historyID)),
                        view=None)

            await self.publish_channel.send(
                "História %s pronta para ser publicada. \n"
                "`Clique na mensagem ou pressione para publicar.`" % (
                    str(historyID),),
                file=dFile(rf'./_temp/h/{filename}')
            )  # , view=publishButton(user_discord=authorDiscord, hid=str(historyID), message=message)

            tResponse = addCard.get_response(
                novelId=str(historyID),
                desc=str(content),
                trelloList=self.trelloList,
                trelloKey=self.trelloKey,
                trelloToken=self.trelloToken
            )

            await self.trello_log_channel.send(f'`{tResponse}`')

            # (await self.getinfo(message))[0])
        elif view.status == 'refuse':
            emailhtml, emailtxt = Mail.getEmailMessage('refuse')
            try:
                for name in os.listdir('./_temp/h/'):
                    if name == filename:
                        os.remove('./_temp/h/%s' % (name,))
                else:
                    await interaction.message.delete()
                    await interaction.channel.send(
                        "`( 〃．．)` Não foi possível remover %s. Marca o Jonathan aí." %
                        (str(historyID)), delete_after=10)
            except Exception as e:
                await interaction.channel.send(
                    "`( 〃．．)` Deu um erro aqui... \n`%s` " %
                    (e), delete_after=10)

            await self.refused_channel.send(
                "ID: %s (%s) **Recusado por %s**" %
                (str(historyID), authorEmail, interaction.user))
        await Mail(authorEmail, emailhtml, emailtxt).sendMail()

    @activity_cooldown
    @app_commands.checks.has_any_role(943171518895095869, 943174476839936010, 982960318890254358, 943192163947274341)
    async def publish(self, interaction: discord.Interaction, message: discord.Message):

        await interaction.response.defer(ephemeral=True, thinking=True)

        authorDiscord, authorEmail, historyID, filename, content = await self.getinfo(message)

        view = publishButton(user_discord=authorDiscord, hid=str(historyID), message=message)
        await interaction.followup.send(
            "Deseja publicar a história? \n`Use o botão \"Sim\" para prosseguir.`",
            view=view, ephemeral=True)

        out = interaction.edit_original_response
        view.response = out

    @activity_cooldown
    @app_commands.checks.has_any_role(943171518895095869, 943174476839936010, 982960318890254358, 943192163947274341)
    async def trello_cart_remove(self, interaction: discord.Interaction, message: discord.Message):

        await interaction.response.defer(ephemeral=True, thinking=True)

        authorDiscord, authorEmail, historyID, filename, content = await self.getinfo(message)

        view = publishButton(user_discord=authorDiscord, hid=str(historyID), message=message)
        await interaction.followup.send(
            "Deseja publicar a história? \n`Use o botão \"Sim\" para prosseguir.`",
            view=view, ephemeral=True)

        out = interaction.edit_original_response
        view.response = out

    @activity_cooldown
    @app_commands.checks.has_any_role(943171518895095869, 943174476839936010, 982960318890254358, 943192163947274341)
    async def trello_cart_alter(self, interaction: discord.Interaction, message: discord.Message):

        await interaction.response.defer(ephemeral=True, thinking=True)

        authorDiscord, authorEmail, historyID, filename, content = await self.getinfo(message)

        view = publishButton(user_discord=authorDiscord, hid=str(historyID), message=message)
        await interaction.followup.send(
            "Deseja publicar a história? \n`Use o botão \"Sim\" para prosseguir.`",
            view=view, ephemeral=True)

        out = interaction.edit_original_response
        view.response = out


async def setup(bot: commands.Bot) -> None:
    # guilds=[discord.Object(id=943170102759686174)]
    await bot.add_cog(ModFunc(bot))
