import discord

from base.utilities import utilities
from base.struct import Config


def __init__(self, bot) -> None:
        self.bot = bot
        self.db = utilities.database(
            self.bot.loop, self.bot.cfg.postgresql_user, self.bot.cfg.postgresql_password)

def convert(time):
    pos = ["s", "m", "h", "d"]

    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24}

    unit = time[-1]

    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2

    return val * time_dict[unit]

    # SAVING MESSAGE ID FROM GIVEAWAY


def giveway_idFunction(msg_id):
    giveway_idFunction.ids = msg_id

    #  NOT WORKING YET
def timeRemaning(seconds):
    #print(f"{seconds} this seconds")
    a = str(seconds // 3600)
    #print(a + 'this a')
    # print('more than 48h but works')
    b = str((seconds % 3600) // 60)
    #print(b + 'this b')
    if int(a) > 48:
        c = str((seconds // 3600) // 24)
        d = "{} dias {} horas".format(c, b)
        return d
    else:
        d = "{} horas {} minutos".format(a, b)
        return d
    
async def starterRoles(self, msg):
        try:
            await self.db.fetch("CREATE TABLE IF NOT EXISTS setup (guild TEXT NOT NULL, message_id TEXT NOT NULL, role_id TEXT NOT NULL)")
        except:
            pass
        ranks = self.bot.cfg.ranks
        #x = []
        colors = self.bot.cfg.colors
        count= 0
        for i, value in enumerate(ranks):
            
            if i >= len(ranks):
                break
            
            z = colors[i]
            #x = tuple((z[0], z[1], z[2]))
            #''.join((f"{z[0]}, {z[1]}, {z[2]}"))
            rankRole = discord.utils.find(lambda r: r.name == value, msg.guild.roles) or await msg.guild.create_role(name=str(value), color=discord.Colour.from_rgb(z[0], z[1], z[2]))
            try:
                await self.db.fetch(f"INSERT INTO ranks (lv, name, r, g, b, roleid) VALUES ({count}, \'{value}\', {z[0]}, {z[1]}, {z[2]}, {rankRole.id})")
            except:
                pass
            count += 10

#That's disgusting, but fuck it
   
async def check_adm(self, member, guild):
        adm = discord.utils.find(lambda r: r.name == "Administrador", guild.roles)
        staff = discord.utils.find(lambda r: r.name == "Equipe", guild.roles)
        author = discord.utils.find(lambda r: r.name == "Autor(a)", guild.roles)
        if adm in member.roles:
            await self.db.fetch(f'UPDATE users SET adm=True WHERE id=\'{member.id}\'')
        else:
            await self.db.fetch(f'UPDATE users SET adm=False WHERE id=\'{member.id}\'')

        if staff in member.roles:
            await self.db.fetch(f'UPDATE users SET staff=True WHERE id=\'{member.id}\'')
        else:
            await self.db.fetch(f'UPDATE users SET staff=False WHERE id=\'{member.id}\'')

        if author in member.roles:
            await self.db.fetch(f'UPDATE users SET author=True WHERE id=\'{member.id}\'')
        else:
            await self.db.fetch(f'UPDATE users SET author=False WHERE id=\'{member.id}\'')