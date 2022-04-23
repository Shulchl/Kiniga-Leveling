# coding: utf-8
"""
    base.functions
    ~~~~~~~~~~~~~

    Funções para facilitar meu trabalho.
"""

import discord, os
from pkg_resources import EmptyProvider

from base.struct import Config
from base.utilities import utilities

from urllib.request import urlopen

__all__ = ['Functions']


def __init__(self, bot) -> None:
    self.bot = bot
    self.db = utilities.database(
        self.bot.loop, self.bot.cfg.postgresql_user, self.bot.cfg.postgresql_password)


def convert(time):
    """
    Divide os formatos de tempo em tempo, dã
    """
    pos = ["s", "m", "h", "d"]

    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24}

    unit = time[-1]

    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except Exception as e:
        return -2

    return val * time_dict[unit]

    # SAVING MESSAGE ID FROM GIVEAWAY


async def giveway_idFunction(msg_id):
    """
    Salva os ids
    """
    giveway_idFunction.ids = msg_id

    #  NOT WORKING YET


def timeRemaning(seconds):
    """
    Calcula o tempo restante para o término do sorteio
    """
    # print(f"{seconds} this seconds")
    a = str(seconds // 3600)
    # print(a + 'this a')
    # print('more than 48h but works')
    b = str((seconds % 3600) // 60)
    # print(b + 'this b')
    if int(a) > 48:
        c = str((seconds // 3600) // 24)
        d = f"{c} dias {b} horas"
        return d
    else:
        d = f"{a} horas {b} minutos"
        return d


async def starterRoles(self, msg):
    """
    Adiciona os cargos criados à DB
    """
    try:
        await self.db.fetch(
            "CREATE TABLE IF NOT EXISTS setup (guild TEXT NOT NULL, message_id TEXT NOT NULL, role_id TEXT NOT NULL)")
    except:
        pass

    ranks = self.bot.cfg.ranks
    # x = []
    colors = self.bot.cfg.colors
    count = 0
    for i, value in enumerate(ranks):

        if i >= len(ranks):
            break

        z = colors[i]
        # x = tuple((z[0], z[1], z[2]))
        # ''.join((f"{z[0]}, {z[1]}, {z[2]}"))
        rankRole = discord.utils.find(lambda r: r.name == value, msg.guild.roles) or await msg.guild.create_role(
            name=str(value), color=discord.Colour.from_rgb(z[0], z[1], z[2]))
        try:
            await self.db.fetch(
                f"INSERT INTO ranks (lv, name, r, g, b, roleid, imgxp) VALUES ({count}, \'{value}\', {z[0]}, {z[1]}, {z[2]}, {rankRole.id}, \'src/molduras/#{i}xp.png\')")
        except:
            pass
        count += 10


async def get_roles(member: discord.Member, guild, roles=[943171518895095869,
                                                          943174476839936010,
                                                          943192163947274341,
                                                          943172687642132591,
                                                          943171893752659979,
                                                          943172687642132591,
                                                          943193084584402975,
                                                          943251043838468127,
                                                          949805774484426783]):
    rr = []
    for role in member.roles:
        if role.id in roles:
            rr.append(role.id)
    if len(rr) > 0:
        staff = []
        for r in rr:
            role = discord.utils.find(lambda j: j.id == r, guild.roles)
            staff.append(
                {rr.index(r): {'name': role.name, 'color': role.color.to_rgb()}})

        return staff


def saveImage(url, fpath):
    contents = urlopen(url)
    try:
        f = open(fpath, 'w')
        os.path.splitext(f.write(contents.read()))
        f.close()
    except Exception:
        raise
