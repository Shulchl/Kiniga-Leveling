import os
import discord
from typing import Literal
from io import BytesIO

from discord import File as dFile

from base.functions import (
    starterRoles,
    starterItens,
    get_userAvatar_func
)
from base.utilities import utilities

from base.Spinovelbot import SpinovelBot
from base.classes.utilities import GuildContext, bot_has_permissions, load_config, cogs_manager, reload_views, \
    cogs_directory, root_directory

from typing import Optional
from datetime import datetime
from discord.ext import commands
from discord.utils import format_dt


class Admin(commands.Cog, name='Administração'):
    '''
        Comandos de administração, incluso:

        load;
        unload;
        reload;
        shutdown;
        tsql;
        sync
        setroles;
        setitens;
        updateitens.

        Require intents: 
            - message_content
        
        Require bot permission:
            - read_messages
            - send_messages
            - attach_files

    '''

    def __init__(self, bot: SpinovelBot) -> None:
        self.bot = bot
        self.chosen = []

        self.cfg = self.bot.config
        self.database = self.bot.database

    def help_custom(self) -> tuple[str, str, str]:
        emoji = '⚙️'
        label = "Admin"
        description = "Mostra a lista de comandos de administração."
        return emoji, label, description

    @commands.group()
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def config(self, ctx):
        pass

    @bot_has_permissions(send_messages=True)
    @commands.is_owner()
    @config.command(name="loadcog")
    async def load_cog(self, ctx: commands.Context, cog: str) -> None:
        """Load a cog."""
        await cogs_manager(self.bot, "load", [f"base.cmds.{cog}"])
        await ctx.send(f":point_right: Cog {cog} loaded!")

    @bot_has_permissions(send_messages=True)
    @config.command(name="unloadcog")
    @commands.is_owner()
    async def unload_cog(self, ctx: commands.Context, cog: str) -> None:
        """Unload a cog."""
        await cogs_manager(self.bot, "unload", [f"base.cmds.{cog}"])
        await ctx.send(f":point_left: Cog {cog} unloaded!")

    @bot_has_permissions(send_messages=True)
    @config.command(name="reloadallcogs", aliases=["rell"])
    @commands.is_owner()
    async def reload_all_cogs(self, ctx: commands.Context) -> None:
        """Reload all cogs."""
        cogs = [cog for cog in self.bot.extensions]
        await cogs_manager(self.bot, "reload", cogs)

        await ctx.send(f":muscle: All cogs reloaded: `{len(cogs)}`!")

    @bot_has_permissions(send_messages=True)
    @config.command(name="reload", aliases=["rel"], require_var_positional=True)
    @commands.is_owner()
    async def reload_specified_cogs(self, ctx: commands.Context, *cogs: str) -> None:
        """Reload specific cogs."""
        reload_cogs = [f"base.cmds.{cog}" for cog in cogs]
        await cogs_manager(self.bot, "reload", reload_cogs)

        await ctx.send(f":thumbsup: `{'` `'.join(cogs)}` reloaded!")

    @bot_has_permissions(send_messages=True)
    @config.command(name="reloadlatest", aliases=["rl"])
    @commands.is_owner()
    async def reload_latest_cogs(self, ctx: commands.Context, n_cogs: int = 1) -> None:
        """Reload the latest edited n cogs."""

        def sort_cogs(cogs_last_edit: list[list]) -> list[list]:
            return sorted(cogs_last_edit, reverse=True, key=lambda x: x[1])

        cogs = []
        for file in os.listdir(cogs_directory):
            actual = os.path.splitext(file)
            if actual[1] == ".py":
                file_path = os.path.join(cogs_directory, file)
                latest_edit = os.path.getmtime(file_path)
                cogs.append([actual[0], latest_edit])

        sorted_cogs = sort_cogs(cogs)
        reload_cogs = [f"base.cmds.{cog[0]}" for cog in sorted_cogs[:n_cogs]]
        await cogs_manager(self.bot, "reload", reload_cogs)

        await ctx.send(f":point_down: `{'` `'.join(reload_cogs)}` reloaded!")

    @bot_has_permissions(send_messages=True)
    @config.command(name="reloadviews", aliases=["rv"])
    @commands.is_owner()
    async def reload_view(self, ctx: commands.Context) -> None:
        """Reload each registered views."""
        infants = reload_views()
        succes_text = f"👌 All views reloaded ! | 🔄 __`{sum(1 for _ in infants)} view(s) reloaded`__ : "
        for infant in infants:
            succes_text += f"`{infant.replace('base.views.', '')}` "
        await ctx.send(succes_text)

    @bot_has_permissions(send_messages=True)
    @config.command(name="reloadconfig", aliases=["rc"])
    @commands.is_owner()
    async def reload_config(self, ctx: commands.Context) -> None:
        """Reload each json config file."""
        self.bot.config = load_config()
        await ctx.send(f":handshake: `{len(self.bot.config)}` config file(s) reloaded!")

    @bot_has_permissions(send_messages=True)
    @config.command(name="synctree", aliases=["st"])
    @commands.is_owner()
    async def sync_tree(self, ctx: commands.Context, guild_id: Optional[str] = None) -> None:
        """Sync application commands."""
        if guild_id:
            if ctx.guild and (guild_id == "guild" or guild_id == "~"):
                guild_id = str(ctx.guild.id)
            tree = await self.bot.tree.sync(guild=discord.Object(id=guild_id))
        else:
            tree = await self.bot.tree.sync()

        self.bot.log(
            message=f"{ctx.author} synced the tree({len(tree)}): {tree}",
            name="discord.cogs.admin.sync_tree",
        )

        await ctx.send(f":pinched_fingers: `{len(tree)}` synced!")

    @bot_has_permissions(send_messages=True, attach_files=True)
    @config.command(name="botlogs", aliases=["bl"])
    @commands.is_owner()
    async def show_bot_logs(self, ctx: commands.Context) -> None:
        """Upload the bot logs"""
        logs_file = os.path.join(root_directory, "discord.log")

        await ctx.send(file=discord.File(fp=logs_file, filename="bot.log"))

    @bot_has_permissions(send_messages=True)
    @config.command(name="changeprefix", aliases=["cp", "prefix"], require_var_positional=True)
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def change_guild_prefix(self, ctx: GuildContext, new_prefix: str) -> None:
        """Change the guild prefix."""
        if not self.bot.usedatabase or not ctx.guild:
            await ctx.send(":warning: Database not used, prefix not changed.")
            return
        try:
            table = self.bot.config["bot"]["prefix_table"]["table"]
            await self.database.insert_onduplicate(table, {"guild_id": ctx.guild.id, "guild_prefix": new_prefix})

            self.bot.prefixes[ctx.guild.id] = new_prefix
            await ctx.send(f":warning: Prefix changed to `{new_prefix}`")
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @bot_has_permissions(send_messages=True)
    @config.command(name="uptime")
    @commands.is_owner()
    async def show_uptime(self, ctx: commands.Context) -> None:
        """Show the bot uptime."""
        uptime = datetime.now() - self.bot.uptime
        await ctx.send(f":clock1: {format_dt(self.bot.uptime, 'R')} ||`{uptime}`||")

    @bot_has_permissions(send_messages=True)
    @config.command(name="shutdown")
    @commands.is_owner()
    async def shutdown_structure(self, ctx: commands.Context) -> None:
        """Shutdown the bot."""
        await ctx.send(f":wave: `{self.bot.user}` is shutting down...")

        await self.bot.close()

    @config.command(name="tsql")
    async def tsql(self, ctx, *, sql: str) -> None:
        await ctx.message.delete()
        output = await self.database.query(sql)
        await ctx.send(f'```{output[0]}```', delete_after=20)

    @tsql.error
    async def tsql_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                "%s você poderá usar este comando de novo."
                % (format_dt(datetime.now() + datetime.timedelta(seconds=error.retry_after), "R")),
                delete_after=int(error.retry_after - 1)
            )
        else:
            await ctx.send(error, delete_after=5)

    '''
        s.config sync -> global sync
        s.config sync ~ -> sync current guild
        s.config sync * -> copies all global app commands to current guild and syncs
        s.config sync ^ -> clears all commands from the current guild target and syncs (removes guild commands)
        s.config sync id_1 id_2 -> syncs guilds with id 1 and 2
    '''

    @config.command(name="sync")
    async def sync(self, ctx, guilds: commands.Greedy[discord.Object],
                   spec: Optional[Literal["~", "*", "^"]] = None
                   ) -> None:
        if not guilds:
            if spec == "~":
                synced = await self.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                self.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await self.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                self.bot.tree.clear_commands(guild=ctx.guild)
                await self.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await self.bot.tree.sync()

            await ctx.send(
                f"Sincronizei {len(synced)} comandos {'globalmente' if spec is None else 'ao servidor atual.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Trees sincronizadas em {ret}/{len(guilds)} servidores.")

    @config.command(name='setroles')
    async def setroles(self, ctx):
        await ctx.message.delete()

        e = await starterRoles(self.bot, ctx.message)

        await ctx.send(e, delete_after=15)

    @config.command(name='setitens')
    async def setitens(self, ctx):
        await ctx.message.delete()

        has_ranks = await self.database.select("ranks", "name", None, "1")

        if not has_ranks:
            return await ctx.reply(
                "Você precisa usar o comando `s.setroles` primeiro.",
                delete_after=10
            )

        try:
            await starterItens(self.bot)
        except Exception as e:
            raise e
        finally:
            await ctx.send("Itens criados.", delete_after=10)

    @config.command(name='updateitens')
    async def updateitens(self, ctx, opt: Optional[
        Literal[
            "loja", "*", "molds", "banners", "badges", "others"
        ]
    ] = None):
        res = []
        if not opt:
            return await ctx.send(
                "Você precisa adicionar uma opção. \n(loja, *, molds, titulos, util, banners, badges)")

        if opt == "loja":
            res = await self.shopupdate()
        elif opt == "banners":
            res = await self.updatebanners()
        elif opt == "molds":
            res = await self.updatemolds()
        elif opt == "badges":
            res = await self.updatebadges()
        elif opt == "others":
            res = await self.updateothers()
        elif opt == "*":
            res.append([
                await self.updatemolds(),
                await self.updatebanners(),
                await self.updatebadges(),
                await self.updateothers(),
                await self.shopupdate()
            ])
        if isinstance(res, list):
            for i in res:
                await ctx.send(i)
        else:
            await ctx.send(res)

    async def shopupdate(self):
        try:

            await self.database.query("DELETE FROM shop WHERE value >= 0;")
            await self.database.query(
                """
                    INSERT IGNORE INTO shop(
                        id, name, value, type_, dest, img, lvmin
                    )
                    SELECT id, name, value, type_, dest, img, lvmin
                    FROM items WHERE canbuy=true ;
                """
            )
        except Exception as i:
            return f"Não foi possível atualizar a loja: \n`{i}`"
        else:
            return "`A loja foi atualizada com sucesso.`"

    # BANNERS
    async def updatebanners(self):
        try:
            await self.database.query("DELETE FROM items WHERE type_=('Banner')")
            await self.database.query(
                """
                    INSERT IGNORE INTO items(
                        ID_ITEM, name, img,
                        img_profile, canbuy, value, type_
                    )
                    SELECT id, name, img_loja,
                        img_profile, canbuy, value, type_
                    FROM banners WHERE canbuy=true ;
                """
            )
        except Exception as i:
            return f"Não foi possível atualizar os banners: \n`{i}`"
        else:
            return "`Os banners foram atualizados com sucesso.`"

    # MOLDURAS
    async def updatemolds(self):
        try:
            await self.database.query("DELETE FROM items WHERE type_=('Moldura')")
            await self.database.query(
                """
                    INSERT IGNORE INTO items(
                        ID_ITEM, name, type_, value, lvmin,
                        img, imgd, img_profile, canbuy, group_, category
                    )
                    SELECT id, name, type_, value, lvmin,
                        img, imgxp, img_profile, canbuy, group_, category
                    FROM molds;
                """
            )
        except Exception as i:
            return f"Não foi possível atualizar as molduras: \n`{i}`"
        else:
            return "`As molduras foram atualizadas com sucesso.`"

    '''
    async def updatetitles(self):
        try:
            await self.database.query("DELETE FROM items WHERE type_=('Titulo')")
            await self.database.query(
                """
                    INSERT IGNORE INTO items(
                        ID_ITEM, name, type_,
                        img, value, canbuy
                    )
                    SELECT id, name, type_,
                        localimg, value, canbuy
                    FROM titles WHERE canbuy=True ;
                """
            )
        except Exception as i:
            return f"Não foi possível atualizar os titulos: \n`{i}`"
        else:
            return "`Os títulos foram atualizados com sucesso.`"
    '''
    '''
    async def updateutil(self):
        try:
            await self.database.query("DELETE FROM items WHERE type_=('Utilizavel')")
            await self.database.query(
                """
                    INSERT IGNORE INTO items(
                        ID_ITEM, name, type_,
                        img, value, canbuy
                    )
                    SELECT id, name, type_,
                        img, value, canbuy
                    FROM consumables WHERE canbuy=True ;
                """
            )
        except Exception as i:
            return f"Não foi possível atualizar os utilizáveis: \n`{i}`"
        else:
            return "`Os utilizáveis foram atualizados com sucesso.`"
    '''
    # BADGES
    async def updatebadges(self):
        try:
            await self.database.query("DELETE FROM items WHERE type_=('Badge')")
            await self.database.query(
                """
                    INSERT IGNORE INTO items(
                        ID_ITEM, name, 
                        type_, img, value, lvmin, 
                        canbuy, group_, category
                    )
                    SELECT id, name, type_,
                        img, value, lvmin, 
                        canbuy, group_, category
                    FROM badges ;
                """
            )
        except Exception as i:
            return f"Não foi possível atualizar as badges: \n`{i}`"
        else:
            return "`As badges foram atualizadas com sucesso.`"

    async def updateothers(self):
        try:

            badges_staff = 'src/imgs/badges/equipe/'
            for e in os.listdir(badges_staff):
                if e.endswith('.png'):
                    print(str(e[:-4].title()))
                    print(badges_staff + e)
                    await self.database.query(
                        f"""
                            INSERT IGNORE INTO badges (
                                name, img, canbuy, 
                                value, type_, 
                                group_, category
                            )
                            VALUES (
                                "{str(e[:-4]).title()}","{str(badges_staff + e)}",
                                {False},99999999,"Badge","equipe","Lendário"
                            ) 
                        """
                    )

            badges_supporter = 'src/imgs/badges/supporter/'
            for e in os.listdir(badges_supporter):
                if e.endswith('.png'):
                    print(str(e[:-4].title()))
                    print(badges_supporter + e)
                    await self.database.query(
                        f"""
                            INSERT IGNORE INTO badges (
                                name, img, canbuy, 
                                value, type_, 
                                group_, category

                            )
                            VALUES (
                                "{str(e[:-4].title())}","{str(badges_supporter + e)}",
                                {False},99999999,"Badge","apoiador","Lendário"
                            ) 
                        """
                    )

        except Exception as e:
            return f"Não foi possível atualizar outros itens: \n`{e}`"
        else:
            return "`Outros itens também foram atualizado.`"

    @commands.command(name='ranking')
    async def ranking(self, ctx, opt: Optional[Literal["Ori", "Nivel"]] = "Nivel"):
        await ctx.message.delete()

        profile_bytes = await get_userAvatar_func(ctx.author)
        rows, users, user_position = None, None, None
        if opt == "Ori":
            rows = await self.database.query(
                "SELECT id, spark FROM users ORDER BY spark Desc LIMIT 10")
        elif opt == "Nivel":
            rows = await self.database.query(
                "SELECT id, rank, xptotal FROM users ORDER BY xptotal Desc LIMIT 10")

        if rows:
            # if (total/3) > int(total/3):
            #    return await ctx.send(f"O limite de páginas é {int(total/3)}", delete_after=5)
            # elif (total/3) < int(total/3):
            #    return await ctx.send(f"O limite de páginas é {int(total/3)+1}", delete_after=5)
            try:
                users = []
                user_position = 0
                count = 0
                for i, value in enumerate(rows):
                    user = ctx.guild.get_member(int(rows[count][0]))
                    if user:
                        avatar = user.display_avatar.url
                        user = user
                        if user == ctx.author.name:
                            user_position = i

                    else:
                        user = "Desconhecido#0000"
                        avatar = "src/imgs/extra/spark.png"

                    rank_image = await self.database.query(
                        f"SELECT badges FROM ranks WHERE lv <= {rows[count][1]} ORDER BY lv Desc LIMIT 1")
                    if rank_image:
                        users.append({count: {
                            "avatar_url": str(avatar),
                            "name": str(user),
                            "value": str(rows[count][2]) if opt == "Nivel" else str(rows[count][1]),
                            "type": str(opt),
                            "rank_image": str(rank_image[0][0]) if opt == "Nivel" else "",
                        }})

                    count += 1
            except Exception as e:
                raise e

        async with ctx.channel.typing():
            buffer = await self.bot.loop.run_in_executor(
                None,
                utilities.topcard.topdraw,
                ctx.author.id, users, user_position, BytesIO(profile_bytes)
            )
        await ctx.send(file=dFile(fp=buffer, filename='ranking.png'))


async def setup(bot: SpinovelBot) -> None:
    await bot.add_cog(Admin(bot))
