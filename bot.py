from __future__ import annotations

import json
import logging
import os

import aiohttp
import discord
import asyncio
from bs4 import BeautifulSoup
from discord.ext import commands, tasks
from discord import app_commands

from base.struct import Config

logging.basicConfig(filename='log.log', encoding='utf-8', level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

intents = discord.Intents.all()


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            intents=intents,
            command_prefix=commands.when_mentioned_or('s.'),
            description='Kiniga Brasil',
            activity=discord.Activity(type=discord.ActivityType.watching,
                                      name="Kiniga")
        )

        with open('config.json', 'r', encoding='utf-8') as f:
            self.cfg = Config(json.loads(f.read()))


bot = Bot()

tree = bot.tree
TEST_GUILD = discord.Object(id=943170102759686174)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

    #tree.copy_global_to(guild=TEST_GUILD)
    #await tree.sync(guild=TEST_GUILD)

    for filename in os.listdir('./cmds'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cmds.{filename[ :-3 ]}')
            except Exception as e:
                print(f'Error occured while cog "{filename}" was loaded.\n{e}')
                logging.error(e)


async def main():
    async with aiohttp.ClientSession() as session, bot:
        bot.session = session
        await bot.start(bot.cfg.bot_token)
asyncio.run(main())

# bot.start(bot.cfg.bot_token)
