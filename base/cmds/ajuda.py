import discord, json, os
from discord.ext import commands
from discord.errors import Forbidden
from base.struct import Config
from discord import app_commands


async def send_embed(interaction: discord.Interaction, embed: discord.Embed):
    try:
        await interaction.response.send_message(embed=embed)
    except Forbidden:
        try:
            await interaction.response.send_message(
                "Parece que eu não consigo enviar embeds, por favor, verifique minhas permissões! :)")
        except Forbidden:
            await interaction.user.send(
                f"Parece que eu não consigo enviar mensagens em {interaction.guild.name}\n"
                f"Teria como avisar o exelentíssimo Shuichi, sobre isso? :slight_smile: ", embed=embed)


class Ajuda(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        with open('config.json', 'r') as f:
            self.cfg = Config(json.loads(f.read()))

    @app_commands.command(name='ajuda', description='Mostra esta mensagem.')
    @app_commands.guilds(discord.Object(id=943170102759686174))
    # @commands.bot_has_permissions(add_reactions=True,embed_links=True)
    async def ajuda(self, interaction: discord.Interaction, modulo: str = None):
        module = " ".join(modulo)
        """Shows all modules of that bot"""

        # !SET THOSE VARIABLES TO MAKE THE COG FUNCTIONAL!
        prefix = self.cfg.prefix  # ENTER YOUR PREFIX - loaded from config, as string or how ever you want!
        version = 1.0  # enter version of your code

        # setting owner name - if you don't wanna be mentioned remove line 49-60 and adjust help text (line 88) 
        owner = 179440483796385792  # ENTER YOUR DISCORD-ID
        owner_name = "Shuichi#6996"  # ENTER YOUR USERNAME#1234
        bot_name = "Docinho Bot"  # ENTER YOUR BOT'S NAME HERE
        general_color = 0x2ecc71  # THE HELP COMMAND'S COLOR WHEN SHOWING MAIN MENU
        specific_color = 0x206694  # THE HELP COMMAND'S COLOR WHEN SHOWING MODULES
        error_color = 0x992d22  # THE HELP COMMAND'S COLOR FOR ERRORS
        issues_site = "marque <@!179440483796385792>"  # WHERE SHOULD USERS SEND ISSUES?

        # checks if cog parameter was given
        # if not: sending all modules and commands not associated with a cog
        if len(module) == 0:
            # checks if owner is on this server - used to 'tag' owner
            try:
                owner = interaction.guild.get_member(owner).mention

            except AttributeError as e:
                owner = owner

            # starting to build embed
            emb = discord.Embed(title='Comandos e módulos', color=general_color,
                                description=f'Use `{prefix}ajuda <módulo>` para receber informações sobre o comando. '
                                            f':smiley:\n')

            # iterating trough cogs, gathering descriptions
            cogs_desc = ''
            for cog in self.bot.cogs:
                cogs_desc += f'`{cog}` {self.bot.cogs[ cog ].description}\n'

            # adding 'list' of cogs to embed
            emb.add_field(name='Módulos de Comandos', value=cogs_desc, inline=False)

            # integrating trough uncategorized commands
            commands_desc = ''
            for command in self.bot.walk_commands():
                # if cog not in a cog
                # listing command if cog name is None and command isn't hidden
                if not command.cog_name and not command.hidden:
                    commands_desc += f'{command.name} - {command.help}\n'

            # adding those commands to embed
            if commands_desc:
                emb.add_field(name='Não pertencem à um módulo', value=commands_desc, inline=False)
            # setting information about author
            emb.add_field(name="Sobre", value=f"\n\
                                    {bot_name} foi criado especialmente para a Kiniga Brasil <:Kiniga:859801384429158420> \n\
                                    Favor, {issues_site} para dar idéias e reportar bugs.")
            # emb.add_field(name="Compartilhe o servidor!", value="https://discord.gg/FhsAgEGZdf")
            # emb.set_image(url="https://i.imgur.com/rDzfiZq.gif")
            emb.set_footer(text=f"{bot_name} — versão: {version}")
        else:
            # block called when one cog-name is given
            # trying to find matching cog and it's commands
            # iterating trough cogs
            for cog in self.bot.cogs:
                # check if cog is the matching one
                if cog.lower() == module.lower():

                    # making title - getting description from doc-string below class
                    emb = discord.Embed(title=f'{cog} - Comandos', description=self.bot.cogs[ cog ].description,
                                        color=specific_color)

                    # getting commands from cog
                    for command in self.bot.get_cog(cog).get_commands():
                        # if cog is not hidden
                        if not command.hidden:
                            emb.add_field(name=f"`{prefix}{command.name}`", value=command.help, inline=False)
                    # found cog - breaking loop
                    break

            # if input not found
            # yes, for-loops have an else statement, it's called when no 'break' was issued
            else:
                emb = discord.Embed(title="O que é isso?!",
                                    description=f"Eu nunca ouvi falar de um módulo chamado `{module}` antes :scream:",
                                    color=error_color)

        # sending reply embed using our own function defined above
        await interaction.response.send_message(embed=emb)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Ajuda(bot))
