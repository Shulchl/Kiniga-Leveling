from __future__ import annotations

import json
import logging

import aiohttp
import discord
from bs4 import BeautifulSoup
from discord.ext import commands, tasks
from discord_components import DiscordComponents

from base.struct import Config

logging.basicConfig(level=logging.INFO)

intents = discord.Intents().all()

class Bot(commands.Bot):
    def __init__(self):

        super().__init__(
            intents=intents,
            command_prefix=commands.when_mentioned_or('s.'),
            description='Bot de nível da Kiniga Brasil.',
            activity=discord.Activity(type=discord.ActivityType.watching,
                                      name="Kiniga")
        ),
        DiscordComponents(self)

        with open('config.json', 'r', encoding='utf-8') as f:
            self.cfg = Config(json.loads(f.read()))

        self.cog_list = ['cogs.ajuda', 'cogs.loja',
                         'cogs.mod', 'cogs.perfil', 'cogs.user']
        for cog in self.cog_list:
            try:
                self.load_extension(cog)
            except Exception as e:
                print(f'Error occured while cog "{cog}" was loaded.\n{e}')

    # def cog_unload(self):
    # return self.feed.close()
    # def cog_load(self):
    #    return self.feed.start()

    def startup(self):
        self.run(self.cfg.bot_token)

    # @tasks.loop(seconds=5)
    async def feed(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("http://kiniga.com/") as resp:
                soup = BeautifulSoup(await resp.text(), 'lxml')
                table = soup.find(
                    'table', attrs={'class': 'manga-chapters-listing'})
                links, titles = soup.find('td', attrs={'class': 'title'}), table.find_all(
                    'td', attrs={'class': 'release'})[0].find_all('a', href=True)
                for t in titles:
                    try:
                        for l in links:
                            try:
                                emoji = self.get_emoji(id=769235205407637505)
                                channel = discord.utils.get(self.get_all_channels(),
                                                            guild__name=self.cfg.guild,
                                                            id=self.cfg.chat_cmds)
                                messages = await channel.history(limit=1).flatten()
                                messages.reverse()
                                cont = '{} | **{}** — **{}**! {}'.format(emoji, l.get_text(),
                                                                         t.get_text(),
                                                                         l['href'])
                                member = channel.guild.get_member(
                                    737086135037329540)
                                webhooks = await channel.webhooks()
                                webhook = discord.utils.get(
                                    webhooks, name="Capitulos Recentes")

                                if webhook is None:
                                    webhook = await channel.create_webhook(name="Capitulos Recentes")

                                for i, message in enumerate(messages):
                                    if i >= 1:
                                        return
                                    message = message.content
                                    if message == cont:
                                        pass
                                    else:
                                        await webhook.send(cont, username=member.name, avatar_url=member.avatar_url)
                            except Exception as e:
                                raise e
                        else:
                            break
                    except Exception as e:
                        raise e
                else:
                    pass

    #@feed.before_loop  # wait for the bot before starting the task
    async def before_send(self):
        await self.wait_until_ready()
        return


if __name__ == '__main__':
    Bot().startup()
