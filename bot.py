#!/usr/bin/env python

from __future__ import annotations

from base.struct import Config

from bs4 import BeautifulSoup
from discord_components import DiscordComponents

from discord.ext import commands, tasks
import discord, json, logging, aiohttp

logging.basicConfig(level=logging.INFO)

intents = discord.Intents().all()

class Bot(commands.Bot):
    def __init__(self):

        super().__init__(
            intents=intents,
            command_prefix=commands.when_mentioned_or('s.'),
            description='Bot de nível da Kiniga Brasil.',
            activity=discord.Streaming(name="https://kiniga.com/", url='https://kiniga.com/')
            ),
        DiscordComponents(self),
        self.remove_command('help')


        with open('config.json', 'r', encoding='utf-8') as f:
            self.cfg = Config(json.loads(f.read()))

        self.cog_list = ['cogs.ajuda', 'cogs.loja', 'cogs.mod', 'cogs.perfil', 'cogs.user']
        for cog in self.cog_list:
            try:
                self.load_extension(cog)
            except Exception as e:
                print(f'Error occured while cog "{cog}" was loaded.\n{e}')


    def cog_unload(self):
      self.feed.close()
      return

    def startup(self):
        self.run(self.cfg.bot_token)
        self.feed.start()

    @tasks.loop(minutes = 5)
    async def feed(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("http://kiniga.com/") as resp:
                soup = BeautifulSoup(await resp.text(), 'lxml')
                table = soup.find('table', attrs={'class':'manga-chapters-listing'})
                titles = table.find('td', attrs={'class':'title'})
                for t in titles:
                    try:
                        links = table.find_all('td', attrs={'class':'release'})[0]
                        for l in links.find_all('a', href=True):
                            try:
                                emoji = self.get_emoji(id=785300070857572372)
                                channel = discord.utils.get(self.get_all_channels(),
                                                            guild__name=self.cfg.guild,
                                                            id=self.cfg.chat_cmds)
                                messages = await channel.history(limit=1).flatten()
                                messages.reverse()
                                cont = '{} | Saiu o **{}** de **{}**!\n{}'.format(emoji, l.get_text(),
                                                                            t.get_text(),
                                                                            l['href'])
                                member = channel.guild.get_member(741770490598653993)
                                webhooks = await channel.webhooks()
                                webhook = discord.utils.get(webhooks, name = "Capitulos Recentes")

                                if webhook is None:
                                    webhook = await channel.create_webhook(name = "Capitulos Recentes")

                                for i, message in enumerate(messages):
                                    message = message.content
                                    if message == cont:
                                        pass
                                    else:
                                        await webhook.send(cont, username = member.name, avatar_url = member.avatar_url)
                            except Exception as e: raise e
                        else: pass
                    except Exception as e: raise e
                else: pass

    @feed.before_loop  # wait for the bot before starting the task
    async def before_send(self):
        await self.wait_until_ready()
        return


if __name__ == '__main__':
    Bot().startup()
