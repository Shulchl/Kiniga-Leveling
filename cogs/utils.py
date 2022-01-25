from __future__ import annotations
from asyncio import events, sleep as asyncsleep
import datetime, discord.utils, re, json
from discord.ext.commands.errors import BadArgument
from base.utilities import utilities
from discord.ext import commands, tasks
from discord import Member as dMember
from random import randint
from discord.ext.commands.cooldowns import BucketType
from base.struct import Config


        
class Utils(commands.Cog, name='Utils', description='Comandos de Utilidade Pública'):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = utilities.database(
            self.bot.loop, self.bot.cfg.postgresql_user, self.bot.cfg.postgresql_password)
        self.brake = []

    
def setup(bot) -> None:
    bot.add_cog(Utils(bot))
    

