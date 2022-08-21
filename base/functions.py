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

__all__ = [ 'Functions' ]


def __init__(self, bot) -> None:
    self.bot = bot
    self.db = utilities.database(
        self.bot.loop, self.bot.cfg.postgresql_user, self.bot.cfg.postgresql_password)


def convert(time):
    """
    Divide os formatos de tempo em tempo, dã
    """
    pos = [ "s", "m", "h", "d" ]

    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24}

    unit = time[ -1 ]

    if unit not in pos:
        return -1
    try:
        val = int(time[ :-1 ])
    except Exception as e:
        return -2

    return val * time_dict[ unit ]

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

        z = colors[ i ]
        # x = tuple((z[0], z[1], z[2]))
        # ''.join((f"{z[0]}, {z[1]}, {z[2]}"))
        rankRole = discord.utils.find(lambda r: r.name == value, msg.guild.roles) or await msg.guild.create_role(
            name=str(value), color=discord.Colour.from_rgb(z[ 0 ], z[ 1 ], z[ 2 ]))
        try:
            await self.db.fetch(
                f"INSERT INTO ranks (lv, name, r, g, b, badges, roleid, imgxp) VALUES ({count}, \'{value}\', {z[ 0 ]},"
                f" {z[ 1 ]}, {z[ 2 ]}, \'src/imgs/badges/#{i}.png\', {rankRole.id}, \'src/imgs/molduras/molduras"
                f"-perfil/xp-bar/#{i}xp.png\')")
        except:
            pass
        count += 10
        
async def starterItens(self):
    """
    Adiciona os itens criados à loja
    """
    
    try:
        await self.db.fetch(
            "INSERT INTO itens (name, type, value, img, imgd, img_profile, lvmin) "
            "VALUES ('Novato','Moldura',1000,'src/imgs/molduras/molduras-loja/#1.png',"
            "'src/imgs/molduras/molduras-perfil/titulos/#1E.png','src/imgs/molduras/molduras-perfil/bordas/#1.png', 0 ) "
            "ON CONFLICT (name) DO NOTHING")

        await self.db.fetch(
            "INSERT INTO itens (name, type, value, img, imgd, img_profile, lvmin) "
            "VALUES ('Soldado Nadir','Moldura', 500000,'src/imgs/molduras/molduras-loja/#1.png',"
            " 'src/imgs/molduras/molduras-perfil/titulos/#1E.png', 'src/imgs/molduras/molduras-perfil/bordas/#1.png', 10) "
            "ON CONFLICT (name) DO NOTHING")

        await self.db.fetch(
            "INSERT INTO itens (name, type, value, img, imgd, img_profile, lvmin) "
            "VALUES ('Sargento Aurora','Moldura', 1000000,'src/imgs/molduras/molduras-loja/#2.png',"
            " 'src/imgs/molduras/molduras-perfil/titulos/#2E.png', 'src/imgs/molduras/molduras-perfil/bordas/#2.png', 20) "
            "ON CONFLICT (name) DO NOTHING")

        await self.db.fetch(
            "INSERT INTO itens (name, type, value, img, imgd, img_profile, lvmin) "
            "VALUES ('Tenente Zênite','Moldura', 2500,'src/imgs/molduras/molduras-loja/#3.png',"
            "'src/imgs/molduras/molduras-perfil/titulos/#3E.png','src/imgs/molduras/molduras-perfil/bordas/#3.png', 30) "
            "ON CONFLICT (name) DO NOTHING")

        await self.db.fetch(
            "INSERT INTO itens (name, type, value, img, imgd, img_profile, lvmin) "
            "VALUES ('Capitão Solar','Moldura', 4000000,'src/imgs/molduras/molduras-loja/#4.png', "
            "'src/imgs/molduras/molduras-perfil/titulos/#4E.png', 'src/imgs/molduras/molduras-perfil/bordas/#4.png', 40) "
            "ON CONFLICT (name) DO NOTHING")

        await self.db.fetch(
            "INSERT INTO itens (name, type, value, img, imgd, img_profile, lvmin) "
            "VALUES ('Major Solar','Moldura', 6500000,'src/imgs/molduras/molduras-loja/#5.png', "
            "'src/imgs/molduras/molduras-perfil/titulos/#5E.png', 'src/imgs/molduras/molduras-perfil/bordas/#5.png', 50) "
            "ON CONFLICT (name) DO NOTHING")

        await self.db.fetch(
            "INSERT INTO itens (name, type, value, img, imgd, img_profile, lvmin) "
            "VALUES ('Coronel Umbra','Moldura', 8000000,'src/imgs/molduras/molduras-loja/#6.png',"
            "'src/imgs/molduras/molduras-perfil/titulos/#6E.png', 'src/imgs/molduras/molduras-perfil/bordas/#6.png', 60) "
            "ON CONFLICT (name) DO NOTHING")

        await self.db.fetch(
            "INSERT INTO itens (name, type, value, img, imgd, img_profile, lvmin) "
            "VALUES ('General Blazar',   'Moldura', 100000000,   'src/imgs/molduras/molduras-loja/#7.png', "
            "'src/imgs/molduras/molduras-perfil/titulos/#7E.png', 'src/imgs/molduras/molduras-perfil/bordas/#7.png', 70) "
            "ON CONFLICT (name) DO NOTHING")

        await self.db.fetch(
            "INSERT INTO itens (name, type, value, img, imgd, img_profile, lvmin) "
            "VALUES ('Marechal Quasar','Moldura', 100000000,'src/imgs/molduras/molduras-loja/#8.png', "
            "'src/imgs/molduras/molduras-perfil/titulos/#8E.png', 'src/imgs/molduras/molduras-perfil/bordas/#8.png', 80) "
            "ON CONFLICT (name) DO NOTHING")

        await self.db.fetch(
            "INSERT INTO itens (name, type, value, img, imgd, img_profile, lvmin) "
            "VALUES ('COMRADE','Titulo', 2500,'src/imgs/titulos/#1.png', "
            "'','',0) ON CONFLICT (name) DO NOTHING")
    except:
        pass
    


async def get_roles(member: discord.Member, guild, roles=[
                                                            943171518895095869,
                                                            943174476839936010,
                                                            943192163947274341,
                                                            943172687642132591,
                                                            943171893752659979,
                                                            943172687642132591,
                                                            943193084584402975,
                                                            943251043838468127,
                                                            949805774484426783,
                                                            1010184007394283630
                                                        ]):
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

        #print(staff)
        return staff


def saveImage(url, fpath):
    contents = urlopen(url)
    try:
        f = open(fpath, 'w')
        os.path.splitext(f.write(contents.read()))
        f.close()
    except Exception:
        raise
