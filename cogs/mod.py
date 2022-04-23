from __future__ import annotations

import asyncio
from datetime import datetime as dt
from datetime import timedelta
import datetime
import json
import random
import uuid
import requests
import urllib.request
import shutil
from asyncio import exceptions
from asyncio import sleep as asyncsleep
from asyncio.tasks import ensure_future
from shutil import ExecError
from typing import Text

import discord
import discord.utils
from base.functions import (convert, giveway_idFunction, starterRoles,
                            timeRemaning)
from base.image import ImageCaptcha
from base.struct import Config
from base.utilities import utilities
from discord import File as dFile
from discord.ext import commands, tasks
from discord.ext.commands.errors import ExtensionAlreadyLoaded
from discord_components import Button, ButtonStyle, Select, SelectOption
from discord_components.interaction import Interaction


class Mod(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = utilities.database(
            self.bot.loop, self.bot.cfg.postgresql_user, self.bot.cfg.postgresql_password)
        self.chosen = []

        if self.bot.cfg.bdayloop:
            self.bdayloop.start()

    def cog_unload(self):
        self.bdayloop.close()

    # UTILIDADES
    @commands.command(name="ori")
    @commands.cooldown(1, 50, commands.BucketType.member)
    @commands.has_permissions(administrator=True)
    async def ori(self, ctx, simbol: Text, amount: int, member: discord.Member = None):
        member = member or ctx.author
        if member:
            if simbol in ['-', '+']:
                if simbol == '+':
                    await self.db.fetch(f"UPDATE users SET coin = ( coin + {amount}) WHERE id= (\'{member.id}\')")
                    return await ctx.send(f"Foram adicionadas {amount} oris à {member.mention}!", delete_after=10)
                elif simbol == '-':
                    await self.db.fetch(f"UPDATE users SET coin = (coin - {amount}) WHERE id= (\'{member.id}\')")
                    return await ctx.send(f"Foram removidas {amount} oris de {member.mention}!", delete_after=10)
            else:
                return await ctx.reply("Você precisa usar + ou - para mexer nas oris dos usuários.")
        else:
            return await ctx.send("O usuário não está no servidor")

    async def createMold(self, ctx, type, name, valor, img_loja, img_perfil, img_round_title, nivel, canbuy):
        await asyncsleep(4)
        try:
            await self.db.fetch(
                f"INSERT INTO itens (name, type, value, img, img_profile, imgd, lvmin, canbuy) VALUES (\'{name}\', \'{type}\', {valor}, \'{img_loja}\', \'{img_perfil}\', \'{img_round_title}\', {nivel}, {canbuy}) ON CONFLICT (name) DO NOTHING")
        except Exception as i:
            await ctx.send(i)

    async def createItem(self, ctx, type, name, valor, img_loja, nivel, canbuy):
        await asyncsleep(4)
        try:
            await self.db.fetch(
                f"INSERT INTO itens (name, type, value, img, lvmin, canbuy) VALUES (\'{name}\', \'{type}\', {valor}, \'{img_loja}\', {nivel}, {canbuy}) ON CONFLICT (name) DO NOTHING")
        except Exception as i:
            await ctx.send(i)

    @commands.command(name='citem')
    @commands.has_permissions(administrator=True)
    async def citem(self, ctx, type, name, valor: int, nivel: int, img_loja, img_perfil=None, img_round_title=None,
                    canbuy: bool = True) -> None:
        msg = await ctx.reply(f"Deseja inserir {type} {name}, por {valor} oris, na loja?")
        verify = await self.bot.wait_for('message', timeout=10,
                                         check=lambda i: i.author == ctx.author and i.content in ['s', 'sim', 'Sim',
                                                                                                  'SIM', 'n', 'não',
                                                                                                  'Não'])
        try:
            if verify.content in ['s', 'S', 'sim', 'Sim', 'SIM']:
                if type.upper() == 'moldura'.upper():
                    molds = [f'src/imgs/molduras/molduras-loja/{type}-{name}.png',
                             f"src/imgs/molduras/molduras-perfil/bordas/{type}-{name}.png",
                             f"src/imgs/molduras/molduras-perfil/titulos/{type}-{name}.png"]
                    paths = [img_loja, img_perfil, img_round_title]
                    try:
                        await verify.reply('Criando a moldura...', delete_after=5)
                        for i in range(len(paths)):
                            response = requests.get(paths[i], stream=True)
                            with open(molds[i], 'wb') as out_file:
                                shutil.copyfileobj(response.raw, out_file)
                            del response
                        f = await self.createMold(self,
                                                  type.title(),
                                                  name,
                                                  valor,
                                                  molds[0],
                                                  molds[1],
                                                  molds[2],
                                                  nivel,
                                                  canbuy
                                                  )
                        await ctx.reply(f'{type}-{name} criada.', delete_after=5)
                    except Exception as j:
                        await ctx.send(j)
                        raise j
                elif type.upper() == 'titulo'.upper():
                    img = [f'src/imgs/titulos/{type}-{name}.png']
                    paths = [img_loja]
                    try:
                        await verify.reply('Criando o título...', delete_after=5)
                        for i in range(len(paths)):
                            response = requests.get(paths[i], stream=True)
                            with open(img[i], 'wb') as out_file:
                                shutil.copyfileobj(response.raw, out_file)
                            del response

                        f = await self.createItem(
                            ctx,
                            type.title(),
                            name,
                            valor,
                            img[0],
                            nivel,
                            canbuy
                        )
                        await ctx.reply(f'{name} criado/a.', delete_after=5)
                    except Exception as j:
                        await ctx.send(j)
                        raise j
                else:
                    img = [f'src/imgs/extra/{type}-{name}.png']
                    paths = [img_loja]
                    try:
                        await verify.reply('Criando o item...', delete_after=5)
                        for i in range(len(paths)):
                            response = requests.get(paths[i], stream=True)
                            with open(img[i], 'wb') as out_file:
                                shutil.copyfileobj(response.raw, out_file)
                            del response

                        f = await self.createItem(
                            ctx,
                            type.title(),
                            name,
                            valor,
                            img[0],
                            nivel,
                            canbuy
                        )
                        await ctx.reply(f'{type}-{name} criada/o.', delete_after=5)
                    except Exception as j:
                        await ctx.send(j)
                        raise j

            else:
                await ctx.message.delete()
                await verify.delete()
                return await msg.delete()
        except Exception as e:
            raise e

    # Pin/Unpin shop item

    @commands.has_any_role(
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
    @commands.cooldown(1, 300, commands.BucketType.member)
    @commands.command(aliases=["destaque"], name='dest',
                      help='SÓ PARA EQUIPE! \n Ao digitar s.det <ID-DO-ITEM>, destaca o item na loja.')
    async def dest(self, ctx, id):
        await ctx.message.delete()
        result = await self.db.fetch(f'SELECT * FROM itens WHERE id = {int(id)}')
        if result:
            await self.db.fetch(f'UPDATE itens SET dest = True WHERE id={int(id)}')
            emb = discord.Embed(
                description=f'O item foi adicionado aos destaques.',
                color=discord.Color.green()).set_footer(
                text='Use [s.tdestaque ID] para tirar o destaque do item.')
            await ctx.send(f'{ctx.author.mention}', embed=emb)
        else:
            await ctx.send("Não encontrei um item com esse ID", delete_after=5)

    #
    # Tira destaque do item // Unpin shop item

    @commands.has_any_role(
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
    @commands.command(aliases=["tirar", "td"], name='tdest',
                      help='SÓ PARA EQUIPE! \n Ao digitar s.tdet <ID-DO-ITEM>, remove o destaque do item na loja.')
    @commands.cooldown(1, 300, commands.BucketType.member)
    async def tdest(self, ctx, id):
        await ctx.message.delete()
        result = await self.db.fetch(f'SELECT * FROM itens WHERE id = {int(id)}')
        if result:
            await self.db.fetch(f'UPDATE itens SET dest = False WHERE id={int(id)}')
            emb = discord.Embed(
                description=f'O item foi removido dos destaques.',
                color=discord.Color.green()).set_footer(
                text='Use [s.destaque ID] para destacar o item novamente.')
            await ctx.send(f'{ctx.author.mention}', embed=emb)
        else:
            await ctx.send("Não encontrei um item com esse ID", delete_after=5)

    # CONFIG

    @commands.command(name='sorteio')
    @commands.has_any_role(
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
    async def sorteio(self, ctx):
        await ctx.send("Responda em 15 segundos.\n")
        q = ["Onde você quer que o sorteio aconteça? (marque o canal)",
             "Quanto tempo o sorteio vai durar?",
             "Qual é o prêmio?"]

        ans = []

        def validation(currentMessage):
            return currentMessage.author == ctx.author and currentMessage.channel == ctx.channel

        for i in q:
            await ctx.send(i)

            try:
                msg = await self.bot.wait_for('message', timeout=15.0, check=validation)
            except asyncio.TimeoutError:
                await ctx.send('Você não respondeu a tempo.', delete_after=5)
                return
            else:
                ans.append(msg.content)
        try:
            channel_id = int(ans[0][2:-1])
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
        global prize
        prize = ans[2]
        if prize.startswith("#"):
            pName = await self.db.fetch(f"SELECT name, id FROM itens WHERE id ='{int(prize.strip('#'))}'")
            if pName:
                prize = pName[0][0]
        await ctx.send(f"O sorteio ocorrerá em {channel.mention} e vai durar {ans[1]}!")

        # embed = discord.Embed(
        #     title="Giveaway!",
        #     description=f"{prize}",
        #     color= 0x006400
        # )
        # embed.add_field(
        #     name="Hosted by:",
        #     value=ctx.author.mention
        # )
        # embed.set_footer(
        #     text=f"Ends {ans[1]} from now!"
        # )
        end = datetime.timedelta(seconds=(3600 * 5)) + \
              datetime.timedelta(seconds=time)
        embed = discord.Embed(
            title=f"Reaja com 🎉 para ganhar **{prize}**!\nTempo até o vencedor ser decidido:  **{timeRemaning(time)}**",
            description="",
            color=0x006400
        )
        embed.set_author(name=f'{prize}', icon_url='')
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

        new_msg = await channel.fetch_message(my_msg.id)
        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(self.bot.user))

        winner = random.choice(users)

        # // {winner.mention} ganhou {prize}
        await channel.send(
            f"Parabéns, {winner.mention}!.\nVocê tem 1 minuto para falar no canal, do contrário o sorteio será refeito.")
        await channel.set_permissions(winner, send_messages=True)

        # await channel.send(winner.id)

        def winner_validation(currentMessage):
            return currentMessage.author == winner and currentMessage.channel == channel

        try:
            msg = await self.bot.wait_for('message', timeout=10.0, check=winner_validation)
            if prize.startswith("#"):
                invent = await self.db.fetch(f"SELECT inv FROM users WHERE id=(\'{winner.id}\')")
                if invent:
                    if str(pName[0][1]) in invent[0][0].split(","):
                        await ctx.send(
                            f'Que pena! {winner.mention} já tem esse item, então terei que refazer o sorteio...')
                        await channel.set_permissions(winner, send_messages=False)
                        await asyncsleep(5)
                        await self.bot.loop.create_task(self.reroll(ctx, channel, winner))
                    else:
                        await self.db.fetch(f"UPDATE users SET inv = (\'{str(invent[0][0]) +','+ str(pName[0][1])}\') WHERE id=(\'{winner.id}\') ")
                        await channel.send(f"Parabéns! {winner.mention} acaba de ganhar {prize}.")
                        await channel.set_permissions(winner, send_messages=False)
            else:
                await channel.send(f"Parabéns! {winner.mention} acaba de ganhar {prize}.")
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
                raise e

    @commands.has_any_role(
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
    @commands.command(aliases=["rr"], name='reroll',
                      help='SÓ PARA EQUIPE! \n Ao digitar s.reroll <#canal-do-sorteio> <@último-ganhador>, refaz o sorteio.')
    async def reroll(self, ctx, channel: discord.TextChannel, lastWinner: discord.Member):
        try:
            new_msg = await channel.fetch_message(giveway_idFunction.ids)
        except:
            return await ctx.send("O ID fornecido é incorreto")

        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(self.bot.user))
        nWinner = random.choice(users)
        while lastWinner == nWinner:
            nWinner = random.choice(users)
        await channel.send(f"Parabéns! {nWinner.mention} acaba de ganhar {prize}.")

    # LOOP DE ANIVERSÁRIO // BDAY LOOP
    @tasks.loop(seconds=10, count=1)
    async def bdayloop(self):
        channel = self.bot.get_channel(int(self.bot.cfg.chat_cmds))
        await channel.send("Verificando aniversariantes...", delete_after=5)
        await asyncsleep(5)
        birthday = await self.db.fetch("SELECT id FROM users WHERE birth=TO_CHAR(NOW() :: DATE, 'dd/mm')")

        for bday in birthday:
            await channel.send(f"Parabéns <@{bday[0]}>, hoje é seu aniversário! Todos dêem parabéns!")

    @bdayloop.before_loop  # wait for the bot before starting the task
    async def before_send(self):
        await self.bot.wait_until_ready()
        return

    # Controle de loop
    @commands.has_permissions(administrator=True)
    @commands.command(name='bdl')
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

    @commands.command(name="setroles")
    @commands.cooldown(1, 300, commands.BucketType.member)
    @commands.has_permissions(administrator=True)
    async def setroles(self, ctx):
        await starterRoles(self, ctx.message)
        return await ctx.reply("Done.")

    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 300, commands.BucketType.member)
    @commands.command(name='setup', aliases=['config'])
    async def setup(self, ctx, role: discord.Role = None) -> None:
        await ctx.message.delete()

        await starterRoles(self, ctx.message)

        def validation(currentMessage):
            return currentMessage.author == ctx.author and currentMessage.channel == ctx.channel

        emb = discord.Embed(title='Seja bem vindo(a) à KINIGA BRASIL!', color=0x2ecc71,
                            description=f'Aperte o botão para podermos verificar sua conta e te dar acesso ao servidor! '
                                        f':smiley:\n')
        emb.set_image(
            url="https://www.kiniga.com/wp-content/uploads/2017/10/New-Logo-Inv-150px.png")
        msg_id = await ctx.send(
            embed=emb,
            components=[
                Button(style=ButtonStyle.green,
                       label="VERIFICAR",
                       custom_id="VERIFY",
                       emoji="✅")])

        message_id = msg_id.id

        equal = await self.db.fetch(f"SELECT message_id, role_id FROM setup WHERE guild = '{ctx.guild.id}'")
        guildExist = False
        if equal:
            guildExist = True
        if not role:
            await ctx.send("Qual cargo servirá como verificado? (Apenas ID)", delete_after=10)
            msg = await self.bot.wait_for('message', timeout=15.0, check=validation)
            try:
                role = discord.utils.find(lambda r: r.id == int(msg.content), ctx.guild.roles) or discord.utils.find(
                    lambda r: r.id == int(equal[0][1]), ctx.guild.roles)
                if not role:
                    role = await ctx.guild.create_role(name="VERIFICADO")
                    await ctx.reply(f"Não foi possível encontrar um cargo o ID fornecido, portando criei um novo.",
                                    delete_after=5)
                await msg.delete()
            except Exception as i:
                raise i

        try:
            if guildExist:
                await self.db.fetch(f"UPDATE setup SET message_id={message_id}, role_id={role.id} WHERE guild = '{ctx.guild.id}'")
            else:
                await self.db.fetch(f"INSERT INTO setup VALUES ({ctx.guild.id}, {message_id}, {role.id})")
        except Exception as t:
            raise t

        return await ctx.send("Configurado!", delete_after=5)

    def randStr(self, string_length):
        """Returns a random string of length string_length."""
        random = str(uuid.uuid4())  # Convert UUID format to a Python string.
        random = random.upper()  # Make all characters uppercase.
        random = random.replace("-", "")  # Remove the UUID '-'.
        return random[0:string_length]  # Return the random string.

    def get_captcha(self, interaction):
        strings = [self.randStr(6),
                   self.randStr(6),
                   self.randStr(6),
                   self.randStr(6)]
        self.chosen = random.choice(strings)
        # await ctx.send(strings)
        # await ctx.send(chosen)
        self.images = ImageCaptcha(fonts=[
            'src/fonts/BarlowSemiCondensedBold.ttf',
            'src/fonts/MontserratBold.ttf',
            'src/fonts/MontserratExtraBold.ttf',
            'src/fonts/OpenSansBold.ttf',
            'src/fonts/MontserratRegular.ttf'])
        data = self.images.generate(str(self.chosen))
        embed = discord.Embed(
            title="Selecione a opção correspondente à imagem para continuar.", color=0x0f83ff)
        file = dFile(fp=data, filename='captcha.png')
        embed.set_image(url="attachment://captcha.png")
        return interaction.respond(
            file=file,
            embed=embed,
            components=[
                Select(
                    placeholder="CLIQUE PARA ESCOLHER!",
                    options=[
                        SelectOption(
                            label=str(strings[0]), value=str(strings[0])),
                        SelectOption(
                            label=str(strings[1]), value=str(strings[1])),
                        SelectOption(
                            label=str(strings[2]), value=str(strings[2])),
                        SelectOption(
                            label=str(strings[3]), value=str(strings[3])),

                    ], custom_id="verification"

                )
            ],
        )

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        result = await self.db.fetch(f"SELECT message_id, role_id FROM setup WHERE guild = (\'{interaction.guild.id}\')")
        if result:
            if interaction.message.id == int(result[0][0]):
                guild = self.bot.get_guild(interaction.guild.id)
                if guild is None:
                    return print("Servidor não encontrada\nFinalizando processo...")
                try:
                    discord.utils.get(interaction.guild.roles,
                                      id=int(result[0][1]))
                except Exception as e:
                    print("Cargo não encontrado\nFinalizando processo...")
                    raise e

                member = interaction.guild.get_member(interaction.user.id)

                if member is None:
                    return
                try:
                    await self.get_captcha(interaction)

                    # await message.respond(f"{strings}", file=dFile(fp=data, filename='captcha.png'))
                    # await member.add_roles(role)
                except Exception as e:
                    raise e

    @commands.Cog.listener()
    async def on_select_option(self, interaction):
        label = interaction.values
        for i in label:
            if interaction.custom_id == 'page_select':
                return
            try:
                if i in self.chosen:
                    try:
                        result = await self.db.fetch(
                            f"SELECT role_id FROM setup WHERE guild = '{interaction.guild.id}'")
                    except Exception as e:
                        raise e
                    assert result
                    if result:
                        try:
                            role = discord.utils.get(
                                interaction.guild.roles, id=int(result[0][0]))
                        except Exception as e:
                            raise e
                            # role = await interaction.guild.create_role(name="VERIFICADO")
                        member = interaction.guild.get_member(
                            interaction.user.id)
                        await member.add_roles(role)
                        await interaction.respond(
                            content=f"{interaction.user.mention}, você está verificado e já pode conversar no servidor!")
                else:
                    await self.get_captcha(interaction)
                    await interaction.respond(
                        content=f"{interaction.user.mention}, você está verificado e já pode conversar no servidor!")
            except Exception as e:
                await interaction.respond(content=f"Captcha inválido. Tente novamente. {e}")
                if interaction.custom_id == "verification":
                    return await self.get_captcha(interaction)

    @commands.command(name='clear', help='Limpa um determinado número de mensagens ao digitar `.clear <número>`')
    @commands.has_any_role(
        943171518895095869,
        943174476839936010,
        943192163947274341,
        943172687642132591,
        943171893752659979,
        943172687642132591,
        943193084584402975,
        943251043838468127,

        855117820814688307
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def clear(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount + 1)
        await asyncio.sleep(2)
        emb = discord.Embed(title='Limpei!', description='{} mensagens foram apagadas!'.format(amount),
                            color=discord.Color.red())
        await ctx.send('', embed=emb, delete_after=3)

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

    @commands.is_owner()
    @commands.command()
    @commands.cooldown(1, 300, commands.BucketType.member)
    async def shutdown(self, ctx):
        if ctx.message.author.id == 179440483796385792:
            await ctx.message.delete()
            print((("-" * 20) + "shutdown" + ("-" * 20)))
            try:
                await self.bot.close()
            except Exception as e:
                raise await self.bot.clear(e)

        else:
            await ctx.send("You do not own this bot!")

def setup(bot) -> None:
    bot.add_cog(Mod(bot))
