import asyncio
import json
import random
import discord

from datetime import datetime
from asyncio import sleep as asyncsleep

from discord.ext import commands, tasks
from discord.utils import format_dt

from base.functions import (
    convert,
    giveway_idFunction,
    timeRemaning,
    get_iventory
)

from base.webhooks import TrelloFunctions

from base.Spinovelbot import SpinovelBot


class Mod(commands.Cog, name='Moderação'):
    def __init__(self, bot: SpinovelBot) -> None:
        self.bot = bot
        self.chosen = []

        self.cfg = self.bot.config

        if self.cfg['other']['bdayloop']:
            self.bdayloop.start()

    def help_custom(self) -> tuple[str, str, str]:
        emoji = '🏪'
        label = "Moderação"
        description = "Mostra a lista de comandos de moderação."
        return emoji, label, description

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
        pName = None
        if prize_.startswith("#"):
            pName = await self.bot.database.select(
                "itens",
                "`name`, `id`,  `type_`, `group_`",
                f"id={int(prize_.strip('#'))}"
            )
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
            f"Parabéns, {winner.mention}!.\n`"
            f"Você tem {format_dt(datetime.now() + datetime.timedelta(seconds=60), 'R')} "
            f"minutos para falar no canal, do contrário o sorteio será refeito.`",
            delete_after=59
        )

        await channel.set_permissions(winner, send_messages=True)
        def winner_validation(currentMessage):
            return currentMessage.author == winner and currentMessage.channel == channel

        try:
            msg = await self.bot.wait_for('message', timeout=10.0, check=winner_validation)
            if prize_.startswith("#"):
                invent = await self.bot.database.select(
                    "inventory",
                    "itens",
                    f"id={winner.id}"
                )
                if invent:
                    itens_json = json.loads(invent[0])
                    for key, value in itens_json.items():
                        if pName[0][2].title() in ["Moldura", "Badge"]:
                            itens_list = itens_json[f"{pName[0][2]}"][f"{pName[0][3]}"]["ids"]
                            if str(pName[0][1]) in itens_list:
                                return await self.pitty_reroll(ctx, winner, channel)
                            itens_json[f"{pName[0][2]}"][f"{pName[0][3]}"]["ids"].append(pName[0][1])
                            break
                        elif pName[0][2].title() == 'Utilizavel':
                            new_value = 1
                            if str(pName[0][1]) in itens_json[f"{pName[0][2]}"]["ids"]:
                                new_value = itens_json[f"{pName[0][2]}"]["ids"].get(f"{pName[0][1]}") + 1
                            print(new_value)
                            itens_json[f"{pName[0][2]}"]["ids"][f"{pName[0][1]}"] = new_value
                        elif pName[0][1].title() in itens_json[f"{pName[0][2]}"]["ids"]:
                            return await self.pitty_reroll(ctx, winner, channel)
                        else:
                            itens_json[f"{pName[0][2]}"]["ids"].append(pName[0][1])
                        break
                    json.dumps(itens_json)
                    await self.bot.database.update(
                        "inventory",
                        {"itens": f"{itens_json}"},
                        f"id={winner.id}"
                    )
                    await channel.set_permissions(winner, send_messages=True)
                    await channel.send(f"Parabéns! {winner.mention} acaba de ganhar {prize_}.")
            else:
                await channel.set_permissions(winner, send_messages=True)
                await channel.send(f"Parabéns! {winner.mention} acaba de ganhar {prize_}.")
        except asyncio.TimeoutError:
            await channel.set_permissions(winner, send_messages=False)
            await ctx.send(f'{winner} não respondeu, então terei que refazer o sorteio...')
            await asyncsleep(5)
            await self.bot.loop.create_task(self.reroll(ctx, channel, winner))

        return giveaway_messageId

    async def pitty_reroll(self, ctx, winner, channel):
        await channel.set_permissions(winner, send_messages=False)
        await ctx.send(f'Que pena! {winner.mention} já tem esse item, então terei que refazer o sorteio...')
        await asyncsleep(5)
        await self.bot.loop.create_task(self.reroll(ctx, channel, winner))

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
                    all_itens = await self.bot.database.select("inventory", "itens", f"={user.id}")
                    itens_json = json.loads(all_itens)
                    itens_ids = await get_iventory(self.bot, user.id)
                    new_itens = []
                    j = [[t[0][0], t[0][1]] for t in
                         [await self.bot.database.select("items", "id, name", f"id={i}")[0] for i in
                          itens_ids] if
                         str(t[0][1]) == 'Ticket']
                    # await channel.send(str(j[0][0]) if j else "Nada")
                    if not j:
                        await message.remove_reaction(payload.emoji, user)
                        await channel.send(f"{user.mention}, você precisa comprar um ticket primeiro.")
                        return
                    for l in j:
                        await channel.send(
                            "Descontarei um ticket de seu inventário. Você poderá comprar outro na loja a qualquer "
                            "momento.")
                        if str(l[1]).title() == "Ticket".title():
                            itens_json["Utilizavel"]["ids"].remove(j[0])
                        json.dumps(itens_json)
                        await self.bot.database.update(
                            "inventory",
                            {"itens":f"{json.dumps(itens_ids)}"}
                        )
                except Exception as e:
                    raise e

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
        birthday = await self.bot.database.select(
            "users",
            "id",
            "birth=TO_CHAR(NOW(), 'dd/mm')"
        )
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
        trello = TrelloFunctions(self.bot)
        trello_items = await trello.get_last_card()

        emb = []
        for item in trello_items:
            item = json.loads(item)
            print(item, flush=True)
            emb.append(discord.Embed.from_dict(item))

        await ctx.send(embeds=emb)


async def setup(bot: SpinovelBot) -> None:
    await bot.add_cog(Mod(bot))
