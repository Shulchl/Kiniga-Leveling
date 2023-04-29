import asyncio
import datetime
import json
import random
import os
import discord
import sys
import ast

from asyncio import sleep as asyncsleep
from typing import Literal, Optional
from io import BytesIO

from discord import File as dFile
from discord.ext import commands, tasks
from discord.utils import format_dt

from base.functions import (
    convert,
    giveway_idFunction,
    starterRoles,
    starterItens,
    timeRemaning,
    user_inventory,
    get_userAvatar_func
)
from base.image import ImageCaptcha
from base.struct import Config
from base.utilities import utilities

from base.webhooks import trello


class Mod(commands.Cog, name='Moderação', command_attrs=dict(hidden=True)):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = utilities.database(self.bot.loop)
        self.chosen = []

        with open('config.json', 'r', encoding='utf-8') as f:
            self.cfg = Config(json.loads(f.read()))

        if self.cfg.bdayloop:
            self.bdayloop.start()
            
    def cog_load(self):
        sys.stdout.write(f'Cog carregada: {self.__class__.__name__}\n')
        sys.stdout.flush()
    
    def cog_unload(self):
        self.bdayloop.close()
        sys.stdout.write(f'Cog descarregada: {self.__class__.__name__}\n')
        sys.stdout.flush()

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

    '''

    @commands.group()
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def config(self, ctx):
        pass

    @config.command()
    @commands.cooldown(1, 30, commands.BucketType.member)
    async def load(self, ctx, extension):
        await self.bot.load_extension(f'base.cmds.{extension}')
        await ctx.message.delete()
        await ctx.send("Carreguei os comandos", delete_after=5)

    @load.error
    async def load_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                "%s você poderá usar este comando de novo."
                % (format_dt(datetime.datetime.now() + datetime.timedelta(seconds=int(error.retry_after)), "R")),
                delete_after=error.retry_after
            )
        else:
            await ctx.send(error, delete_after=5)

    @config.command()
    @commands.cooldown(1, 30, commands.BucketType.member)
    async def reload(self, ctx, extension):
        await self.bot.unload_extension(f'base.cmds.{extension}')
        await self.bot.load_extension(f'base.cmds.{extension}')
        await ctx.message.delete()
        await ctx.send("Recarreguei os comandos", delete_after=5)

    @reload.error
    async def reload_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                "%s você poderá usar este comando de novo."
                % (format_dt(datetime.datetime.now() + datetime.timedelta(seconds=error.retry_after), "R")),
                delete_after=int(error.retry_after-1)
            )
        else:
            await ctx.send(error, delete_after=5)

    @config.command()
    @commands.cooldown(1, 30, commands.BucketType.member)
    async def unload(self, ctx, extension):
        await self.bot.unload_extension(f'base.cmds.{extension}')
        await ctx.message.delete()
        await ctx.send("Descarreguei os comandos", delete_after=5)

    @unload.error
    async def unload_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                "%s você poderá usar este comando de novo."
                % (format_dt(datetime.datetime.now() + datetime.timedelta(seconds=error.retry_after), "R")),
                delete_after=int(error.retry_after-1)
            )
        else:
            await ctx.send(error, delete_after=5)

    @config.command()
    @commands.cooldown(1, 300, commands.BucketType.member)
    async def shutdown(self, ctx):
        await ctx.message.delete()
        print((("-" * 20) + "shutdown" + ("-" * 20)))
        try:
            await self.bot.close()
        except Exception as e:
            await ctx.send("Deu merda aqui em. Melhor ver isso logo...", delete_after=5)
            raise (e)


    @config.command(name="tsql")
    async def tsql(self, ctx, *, sql: str) -> None:
        await ctx.message.delete()
        output = await self.db.fetch(sql)
        await ctx.send(f'```{output}```', delete_after=20)

    @tsql.error
    async def tsql_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                "%s você poderá usar este comando de novo."
                % (format_dt(datetime.datetime.now() + datetime.timedelta(seconds=error.retry_after), "R")),
                delete_after=int(error.retry_after-1)
            )
        else:
            await ctx.send(error, delete_after=5)

    @config.command(name="tsqlist")
    async def tsqlist(self, ctx, *, sql: str) -> None:
        await ctx.message.delete()
        output = await self.db.fetchList(sql)
        await ctx.send(f'```{output}```', delete_after=20)

    @tsqlist.error
    async def tsqlist_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                "%s você poderá usar este comando de novo."
                % (format_dt(datetime.datetime.now() + datetime.timedelta(seconds=error.retry_after), "R")),
                delete_after=int(error.retry_after-1)
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
                   spec: Optional[Literal["~", "*", "^"]] = None) -> None:
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

        e = await starterRoles(self, ctx.message)

        await ctx.send(e, delete_after=10)

    
    @config.command(name='setitens')
    async def setitens(self, ctx):
        await ctx.message.delete()

        has_ranks = await self.db.fetch(
            """
                SELECT name FROM ranks LIMIT 1
            """
        )

        if not has_ranks:
            return await ctx.reply(
                "Você precisa usar o comando `s.setroles` primeiro.", 
                delete_after=10
            )

        try:
            await starterItens(self)
        except Exception as e:
            raise (e)
        finally:
            await ctx.send("Itens criados.", delete_after=10)

    @config.command(name='updateitens')
    async def updateitens(self, ctx, opt: Optional[
        Literal[
            "loja", "*", "molds", "titulos", "util", "banners", "badges", "others"
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
        elif opt == "titulos":
            res = await self.updatetitles()
        elif opt == "util":
            res = await self.updateutil()
        elif opt == "badges":
            res = await self.updatebadges()
        elif opt == "others":
            res = await self.updateothers()
        elif opt == "*":
            res.append([
                await self.updatemolds(),
                await self.updatebanners(),
                await self.updatebadges(),
                await self.updateutil(),
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

            await self.db.execute("DELETE FROM shop WHERE lvmin >= 0")
            await self.db.execute(
                """
                    INSERT INTO shop(
                        id, name, value, type_, dest, img, lvmin, item_type_id
                    )
                    SELECT id, name, value, type_, dest, img, lvmin, item_type_id
                    FROM itens WHERE canbuy=true ON CONFLICT (item_type_id) DO NOTHING;
                """
            )
        except Exception as i:
            return f"Não foi possível atualizar a loja: \n`{i}`"
        else:
            return "`A loja foi atualizada com sucesso.`"

    # BANNERS
    async def updatebanners(self):
        try:
            await self.db.execute("DELETE FROM itens WHERE type_=('Banner')")
            await self.db.execute(
                """
                    INSERT INTO itens(
                        item_type_id, name, img,
                        img_profile, canbuy, value, type_
                    )
                    SELECT id, name, img_loja,
                        img_perfil, canbuy, value, type_
                    FROM banners WHERE canbuy=true ON CONFLICT (id) DO NOTHING;
                """
            )
        except Exception as i:
            return f"Não foi possível atualizar os banners: \n`{i}`"
        else:
            return "`Os banners foram atualizados com sucesso.`"

    # MOLDURAS
    async def updatemolds(self):
        try:
            await self.db.execute("DELETE FROM itens WHERE type_=('Moldura')")
            await self.db.execute(
                """
                    INSERT INTO itens(
                        item_type_id, name, type_, value, lvmin,
                        img, imgd, img_profile, canbuy, group_, category
                    )
                    SELECT id, name, type_, value, lvmin,
                        img, imgxp, img_profile, canbuy, group_, category
                    FROM molds ON CONFLICT (id) DO NOTHING;
                """
            )
        except Exception as i:
            return f"Não foi possível atualizar as molduras: \n`{i}`"
        else:
            return "`As molduras foram atualizadas com sucesso.`"

    # TITULOS
    async def updatetitles(self):
        try:
            await self.db.execute("DELETE FROM itens WHERE type_=('Titulo')")
            await self.db.execute(
                """
                    INSERT INTO itens(
                        item_type_id, name, type_,
                        img, value, canbuy
                    )
                    SELECT id, name, type_,
                        localimg, value, canbuy
                    FROM titles WHERE canbuy=True ON CONFLICT (id) DO NOTHING;
                """
            )
        except Exception as i:
            return f"Não foi possível atualizar os titulos: \n`{i}`"
        else:
            return "`Os títulos foram atualizados com sucesso.`"

    # UTILIZÁVEIS
    async def updateutil(self):
        try:
            await self.db.execute("DELETE FROM itens WHERE type_=('Utilizavel')")
            await self.db.execute(
                """
                    INSERT INTO itens(
                        item_type_id, name, type_,
                        img, value, canbuy
                    )
                    SELECT id, name, type_,
                        img, value, canbuy
                    FROM utilizaveis WHERE canbuy=True ON CONFLICT (id) DO NOTHING;
                """
            )
        except Exception as i:
            return f"Não foi possível atualizar os utilizáveis: \n`{i}`"
        else:
            return "`Os utilizáveis foram atualizados com sucesso.`"

    # BADGES
    async def updatebadges(self):
        try:
            await self.db.execute("DELETE FROM itens WHERE type_=('Badge')")
            await self.db.execute(
                """
                    INSERT INTO itens(
                        item_type_id, name, 
                        type_, img, value, lvmin, 
                        canbuy, group_, category
                    )
                    SELECT id, name, type_,
                        img, value, lvmin, 
                        canbuy, group_, category
                    FROM badges ON CONFLICT (id) DO NOTHING;
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
                    await self.db.execute(
                        """
                            INSERT INTO badges (
                                name, 
                                img, 
                                canbuy, 
                                value, 
                                type_, 
                                group_, 
                                category
                            )
                            VALUES (\'%s\', \'%s\', %s, %s, \'%s\', \'%s\', \'%s\') ON CONFLICT (name) DO NOTHING
                        """ % (
                            str(e[:-4]).title(),
                            str(badges_staff + e),
                            False,
                            99999999,
                            "Badge",
                            "equipe",
                            "Lendário"
                        )
                    )

            badges_supporter = 'src/imgs/badges/supporter/'
            for e in os.listdir(badges_supporter):
                if e.endswith('.png'):
                    print(str(e[:-4].title()))
                    print(badges_supporter + e)
                    await self.db.execute(
                        """
                            INSERT INTO badges (
                                name, 
                                img, 
                                canbuy, 
                                value, 
                                type_, 
                                group_, 
                                category
                            )
                            VALUES (\'%s\', \'%s\', %s, %s, \'%s\', \'%s\', \'%s\') ON CONFLICT (name) DO NOTHING 
                        """ % (
                            str(e[:-4].title()),
                            str(badges_supporter + e),
                            False,
                            99999999,
                            "Badge",
                            "apoiador",
                            "Lendário"
                        )
                    )

        except Exception as e:
            return (f"Não foi possível atualizar outros itens: \n`{e}`")
        else:
            return ("`Outros itens também foram atualizado.`")

    '''
        async def FindItemTypes(self):
            x = await self.db.fetch("""
                SELECT type_, string_agg('[' || item_type_id || ', ' || type_ || ', ' || name || ', ' || value || ']', ', ')
                    FROM itens
                    GROUP BY type_;
            """)
            if not x:
                return False

            z = [list(map(str.strip, u'{v[1]}'.strip('][').strip('][').replace("'", "").split(','))) for v in x]
            # z = [list(map(str.strip, json.loads(u'%s' % v[1]))) for v in x]
            types_ = [k[0] for k in x]

            print(types_, z[0])
            return types_, z[0]
    '''
    @commands.command(name='showitens')
    async def showitens(self, ctx):
        items = await self.FindItemTypes()

        if not items:
            return await ctx.send("Não encontrei um item com esse id.")

        emb = discord.Embed(
            title="Itens",
            description="Aqui estão listados todos os itens cadastrados."
        ).color = 0x006400

        items_ = []
        for i, value in enumerate(items):
            items_.append(items[1])

        await ctx.send(items_)


    @commands.command(name='ranking')
    async def ranking(self, ctx, opt: Optional[Literal["Ori", "Nivel"]]):
        await ctx.message.delete()

        profile_bytes = await get_userAvatar_func(ctx.author)

        if not opt:
            opt = "Nivel"

        if opt == "Ori":
            rows = await self.db.fetch(
                "SELECT id, spark FROM users ORDER BY spark Desc LIMIT 10")
        elif opt == "Nivel":
            rows = await self.db.fetch(
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

                    rank_image = await self.db.fetch(
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
                raise (e)

        async with ctx.channel.typing():
            buffer = await self.bot.loop.run_in_executor(
                None,
                utilities.topcard.topdraw,
                ctx.author.id, users, user_position, BytesIO(profile_bytes)
            )
        await ctx.send(file=dFile(fp=buffer, filename='ranking.png'))

    '''

        Comandos de moderação, incluso:

        sorteio;
        reroll;
        bdl;
        clear;

    '''

    @commands.group()
    @commands.has_any_role(
        'Equipe', 
        'Moderação', 
        'Rings', 
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
        943251043838468127)
    @commands.guild_only()
    async def mod(self, ctx):
        pass



    @mod.command(name='sorteio')
    async def sorteio(self, ctx, channel: discord.Object, time: str, prize: str):
        if channel and time and prize:
            ans = [channel.id, time, str(prize.replace('"', ''))]
        else:
            ans = []

            await ctx.send("Responda em 15 segundos.\n")
            q = ["Onde você quer que o sorteio aconteça? (marque o canal)",
                 "Quanto tempo o sorteio vai durar?",
                 "Qual é o prêmio?"]

            def validation(currentMessage):
                return currentMessage.author == ctx.author and currentMessage.channel == ctx.channel

            for i in q:
                await ctx.send(i)

                try:
                    msg = await self.bot.wait_for('message', timeout=15.0, check=validation)
                except asyncio.TimeoutError:
                    return await ctx.send('Você não respondeu a tempo.', delete_after=5)

                else:
                    ans.append(msg.content)
        try:
            channel_id = int(ans[0])  # [2:-1]
        except Exception as e:
            return await ctx.send(f"Não consegui encontrar esse canal. {e}", delete_after=5)

        channel = self.bot.get_channel(channel_id)

        time = convert(ans[1])
        if time == -1:
            await ctx.send("Não consegui entender o tempo, por favor, use s|m|h|d", delete_after=10)
            return
        elif time == -2:
            await ctx.send("O tempo tem que ser em números inteiros.", delete_after=5)
            return
        global prize_
        prize_ = ans[2]
        if prize_.startswith("#"):
            pName = await self.db.fetch(f"SELECT name, id FROM itens WHERE id ='{int(prize_.strip('#'))}'")
            if pName:
                prize_ = pName[0][0]
        await ctx.send(f"O sorteio ocorrerá em {channel.mention} e vai durar {ans[1]}!")
        '''
        embed = discord.Embed(
            title="Giveaway!",
            description=f"{prize_}",
            color= 0x006400
        )
        embed.add_field(
            name="Hosted by:",
            value=ctx.author.mention
        )
        embed.set_footer(
            text=f"Ends {ans[1]} from now!"
        )
        '''
        end = datetime.timedelta(seconds=(3600 * 5)) + \
              datetime.timedelta(seconds=time)
        embed = discord.Embed(
            title=f"Reaja com 🎉 para ganhar **{prize_}**!\nTempo até o vencedor ser decidido:  **{timeRemaning(time)}**",
            description="",
            color=0x006400
        )
        embed.set_author(name=f'{prize_}', icon_url='')
        embed.add_field(
            name=f"Criado por:",
            value=ctx.author.mention
        )
        embed.set_footer(
            text=f"Sorteio irá durar por {ans[1]}\n. {end} por enquanto!")
        # await ctx.send(file=discord.File('./src/extra/ori.png'))

        my_msg = await channel.send(embed=embed)
        giveaway_messageId = await giveway_idFunction(my_msg.id)

        await my_msg.add_reaction("🎉")
        await asyncio.sleep(time)

        try:
            new_msg = await channel.fetch_message(my_msg.id)
        except:
            return await ctx.send("O ID fornecido é incorreto")

        reaction = new_msg.reactions[0]
        users = set()
        async for user in reaction.users():
            users.add(user)

        users.remove(self.bot.user)

        await ctx.send(f"users: {', '.join(user.name for user in users)}")

        if len(users) > 1:
            winner = random.choice(users)
        else:

            winner = next(iter(users or []), None)
        # // {winner.mention} ganhou {prize_}
        await channel.send(
            "Parabéns, %s!.\n`Você tem %s minutos para falar no canal, do contrário o sorteio será refeito.`" %
            (winner.mention, format_dt(datetime.datetime.now() +
                                       datetime.timedelta(seconds=60), 'R')),
            delete_after=59)

        await channel.set_permissions(winner, send_messages=True)

        # await channel.send(winner.id)

        def winner_validation(currentMessage):
            return currentMessage.author == winner and currentMessage.channel == channel

        try:
            msg = await self.bot.wait_for('message', timeout=10.0, check=winner_validation)
            if prize_.startswith("#"):
                invent = await self.db.fetch(f"SELECT inv FROM users WHERE id=(\'{winner.id}\')")
                if invent:
                    if str(pName[0][1]) in invent[0][0].split(","):
                        await ctx.send(
                            f'Que pena! {winner.mention} já tem esse item, então terei que refazer o sorteio...')
                        await channel.set_permissions(winner, send_messages=False)
                        await asyncsleep(5)
                        await self.bot.loop.create_task(self.reroll(ctx, channel, winner))
                    else:
                        await self.db.fetch(
                            f"UPDATE users SET inv = (\'{str(invent[0][0]) + ',' + str(pName[0][1])}\') WHERE id=(\'{winner.id}\') ")
                        await channel.send(f"Parabéns! {winner.mention} acaba de ganhar {prize_}.")
                        await channel.set_permissions(winner, send_messages=False)
            else:
                await channel.send(f"Parabéns! {winner.mention} acaba de ganhar {prize_}.")
                await channel.set_permissions(winner, send_messages=False)
        except asyncio.TimeoutError:
            await ctx.send(f'Que pena, {winner}, mas terei que refazer o sorteio...')
            await channel.set_permissions(winner, send_messages=False)
            await asyncsleep(5)
            await self.bot.loop.create_task(self.reroll(ctx, channel, winner))

        return giveaway_messageId

        # REROLL

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if giveway_idFunction.ids:
            channel = self.bot.get_channel(payload.channel_id)
            if payload.message_id == giveway_idFunction.ids and payload.user_id != self.bot.user.id:
                message = await channel.fetch_message(payload.message_id)
                user = (self.bot.get_user(payload.user_id))
                if not user:
                    user = await self.bot.fetch_user(payload.user_id)

                # if payload.emoji != '🎉':
                #    await message.remove_reaction(payload.emoji, user)

                try:
                    inv = await self.db.fetch(f"SELECT inv FROM users WHERE id=('{user.id}')")
                    itens = inv[0][0].split(',')
                    j = [[t[0][0], t[0][1]] for t in
                         [(await self.db.fetch(f"SELECT id, name FROM itens WHERE id=('{i}')")) for i in itens] if
                         str(t[0][1]) == 'Ticket']
                    # await channel.send(str(j[0][0]) if j else "Nada")
                    for l in j:
                        await channel.send(
                            "Descontarei um ticket de seu inventário. Você poderá comprar outro na loja a qualquer momento.")
                        if str(j[0][1]).title() == "Ticket".title():
                            itens.remove(str(j[0][0]))
                            await self.db.fetch(f"UPDATE users SET inv = ('{','.join(itens)}')")
                    else:
                        await message.remove_reaction(payload.emoji, user)
                        await channel.send(f"{user.mention}, você precisa comprar um ticket primeiro.")

                except Exception as e:
                    raise (e)

    @mod.command(
        name='reroll',
        help='SÓ PARA EQUIPE! \nRefaz o sorteio ao digitar s.config reroll <#canal-do-sorteio> <@último-ganhador>.')
    async def reroll(self, ctx, channel: discord.TextChannel, lastWinner: discord.Member):
        try:
            new_msg = await channel.fetch_message(giveway_idFunction.ids)
        except:
            return await ctx.send("O ID fornecido é incorreto")

        reaction = new_msg.reactions[0]

        users = set()
        async for user in reaction.users():
            users.add(user)

        users.remove(self.bot.user)

        await ctx.send(f"users: {', '.join(user.name for user in users)}")

        if len(users) > 0:
            nWinner = random.choice(users)
        else:
            nWinner = next(iter(users or []), None)

        print(nWinner)

        if lastWinner == nWinner and len(users) > 1:
            nWinner = random.choice(users)
        else:
            return await channel.send("`Número insuficiênte de articipantes.`")

        await channel.send(f"Parabéns, {nWinner.mention}! Você ganhou.")

    # LOOP DE ANIVERSÁRIO // BDAY LOOP
    @tasks.loop(seconds=10, count=1)
    async def bdayloop(self):
        channel = self.bot.get_channel(int(self.cfg.chat_cmds))
        await channel.send("Verificando aniversariantes...", delete_after=5)
        await asyncsleep(5)
        birthday = await self.db.fetch("SELECT id FROM users WHERE birth=TO_CHAR(NOW() :: DATE, 'dd/mm')")

        for bday in birthday:
            await channel.send(f"Parabéns <@{bday[0]}>, hoje é seu aniversário! Todos dêem parabéns!")

    @bdayloop.before_loop  # wait for the bot before starting the task
    async def before_send(self):
        await self.bot.wait_until_ready()
        return

    @mod.command(name='bdl')
    async def bdl(self, ctx, opt):
        if opt == "on":
            await ctx.send("Iniciando...", delete_after=2)
            await asyncsleep(2)
            with open('config.json', 'r+') as g:
                data = json.load(g)
                data['bdayloop'] = True
                g.seek(0)
                await asyncsleep(1)
                json.dump(data, g, indent=4)
                g.truncate()
                await self.bdayloop.start()
        if opt == "off":
            await ctx.send("Desligando...", delete_after=2)
            await asyncsleep(2)
            with open('config.json', 'r+') as g:
                data = json.load(g)
                data['bdayloop'] = False
                g.seek(0)
                await asyncsleep(1)
                json.dump(data, g, indent=4)
                g.truncate()
                await self.bdayloop.close()

    @mod.command(name='clear', help='Limpa um determinado número de mensagens ao digitar `.clear <número>`')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def clear(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f'`{amount} mensagens foram apagadas.`', delete_after=3)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.UserInputError):
            await ctx.send('Você precisa colocar o número de mensagem que deseja apagar.')
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                'Você precisa esperar {:.2f}s, para poder usar esse comando de novo.'.format(
                    error.retry_after),
                delete_after=5)
        else:
            await ctx.send(error)

    @mod.command(mod='proxnovel')
    async def proxnovel(self, ctx):
        await ctx.message.delete()

        trello_items = await trello.get_last_card()

        emb = []
        for item in trello_items:
            item = json.loads(item)
            print(item, flush=True)
            emb.append(discord.Embed.from_dict(item))

        await ctx.send(embeds=emb)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Mod(bot))
