# coding: utf-8
"""
    base.functions
    ~~~~~~~~~~~~~

    Funções para facilitar meu trabalho.
"""

import ast
import asyncio
import datetime
import json
import random
import sys
import time
from io import BytesIO
from os import listdir
from os.path import join, splitext
from typing import Literal
from typing import Optional
from urllib.request import urlopen

import aiohttp
import discord
import requests
from bs4 import BeautifulSoup
from discord import app_commands
from discord.utils import format_dt

from base.classes.utilities import root_directory
from platform import python_version

__all__ = []

longest_cooldown = app_commands.checks.cooldown(
    2, 300.0, key=lambda i: (i.guild_id, i.user.id))
activity_cooldown = app_commands.checks.cooldown(
    1, 5.0, key=lambda i: (i.guild_id, i.user.id))


def print_progress_bar(index, total, label):
    n_bar = 20  # Progress bar width
    progress = index / total
    sys.stdout.write('\r')
    sys.stdout.write(
        f"[{'=' * int(n_bar * progress):{n_bar}s}] {int(100 * progress)}%  {label}\n")
    sys.stdout.flush()


async def error_delete_after(interaction, error):
    if interaction.response.type == discord.InteractionResponseType.channel_message:
        return await interaction.response.send_message(
            content="%s você poderá usar este comando de novo." % format_dt(
                datetime.datetime.now() +
                datetime.timedelta(seconds=error.retry_after),
                'R'),
            delete_after=int(error.retry_after) - 1)

    elif interaction.response.type == discord.InteractionResponseType.deferred_message_update:
        return await interaction.followup.send(
            content="%s você poderá usar este comando de novo." % format_dt(
                datetime.datetime.now() +
                datetime.timedelta(seconds=error.retry_after),
                'R'),
            delete_after=int(error.retry_after) - 1)


async def report_error(self, interaction, error):
    self.bot.log(message=error, name="functions.report_error")
    admin = self.bot.get_user(int(self.bot.config["bot"]["report_to"]))

    embed = discord.Embed(title="Relatório de erros", color=0xe01b24)
    embed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
    embed.add_field(name=error.command.name, value=error.__cause__, inline=False)
    embed.set_footer(text=datetime.datetime.now())

    await admin.send(embed=embed)


async def initiate_user(self, member_id, member_name, info=None):
    user_ = await self.database.insert(
        "users",
        {
            "id": member_id,
            "rank": 0,
            "xp": 5,
            "xptotal": 5,
            "user_name": str(member_name),
        }
    )

    self.log(message=f"{user_}", name="TESTE-functions.initiate_user")

    await self.database.insert(
        "inventory",
        {
            "id": member_id
        }
    )
    user_ = await self.database.select("users", info, f"id={member_id}")
    return user_


async def get_profile_info(self, member_id, member_name, info: str = None):
    if not info:
        info = "*"
    user_ = await self.database.select("users", info, f"id={member_id}")
    if not user_:
        user_ = await initiate_user(self, member_id, member_name, info)

    return user_[0]


async def send_error_response(self, interaction, msg):
    if interaction.response.type == discord.InteractionResponseType.channel_message:
        return await interaction.response.send_message(msg, ephemeral=True)
    elif interaction.response.type == discord.InteractionResponseType.deferred_message_update:
        return await interaction.followup.send(msg, ephemeral=True)


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


async def createTables(self):
    # CRIA TABLES
    with open(join('./base/classes', 'SCHEMA.sql'), 'r') as e:
        try:
            await self.database.query(e.read())

        except Exception as f:
            self.log(message=f, name="functions.createTables")
            return f

        return True


async def starterRoles(self, msg):
    """
    Adiciona os cargos criados à DB
    """

    # CRIAR TABELAS
    _tables = await createTables(self)
    if not _tables:
        return f"Os cargos não puderam ser criados. {_tables}"

    config = self.config["other"]
    classes = config["ranks"]
    # x = []
    colors = config["colors"]
    count = 0

    if not classes:
        return f"Parece que você não inseriu nenhuma classe nas configurações."

    if not colors:
        return f"Parece que você não inseriu nenhuma cor nas configurações."

    if len(classes) != len(colors):
        return f"Toda classe precisa ter uma cor e toda cor precisa ter uma classe. " \
               " Verifique se o número de cor é o mesmo que o de classes." \
               f"\n\nNúmero de classes/cor: {len(classes)}/{len(colors)}"

    for i, value in enumerate(classes):
        if i > len(classes):
            break

        z = colors[i]
        # x = tuple((z[0], z[1], z[2]))
        # ''.join((f"{z[0]}, {z[1]}, {z[2]}"))
        rankRole = discord.utils.find(lambda r: r.name == value, msg.guild.roles) or await msg.guild.create_role(
            name=str(value), color=discord.Colour.from_rgb(z[0], z[1], z[2]))
        imgPathName = '-'.join(value.split())
        try:

            await self.database.insert(
                "ranks",
                {
                    "name": str(value),
                    "lvmin": int(count),
                    "r": int(z[0]),
                    "g": int(z[1]),
                    "b": int(z[2]),
                    "roleid": str(rankRole.id),
                    "badges": f"src/imgs/badges/rank/{imgPathName}.png",
                    "imgxp": f"src/imgs/molduras/molduras-perfil/xp-bar/{imgPathName}.png",
                }
            )

        except Exception as o:
            await msg.channel.send(f"`{o}`")
            self.log(message=str(o), name="functions.starterRoles")
        else:
            print_progress_bar(
                i, len(classes), " progresso de badges criadas")
        finally:
            count += 10
    return "Todas as classes foram criadas"


def uuid_formulate(target, uuid) -> str:
    """

    Parameters
    ----------
    uuid

    Returns bin(hex('uuid'))
    -------

    """
    return f"UNHEX(REPLACE({target},'-',''))=(UNHEX(REPLACE({uuid},'-','')))"
    # return f"bin(hex('{uuid}'))"


def check_case(type_) -> str:
    """

    Parameters
    ----------
    type_ of the item

    Returns str(type_)
    -------

    """
    type_ = type_.title()
    if python_version() >= "3.9":
        match type_:
            case "Banner":
                return "banners"
            case "Badge":
                return "badges"
            case "Moldura":
                return "molds"
            case "Consumable":
                return "consumables"
    else:
        if type_ == "Banner":
            return "banners"
        elif type_ == "Badge":
            return "badges"
        elif type_ == "Moldura":
            return "molds"
        elif type_ == "Consumable":
            return "consumables"


def check_case_reverse(type_) -> str:
    """

    Parameters
    ----------
    type_ of the item

    Returns str(type_)
    -------

    """
    type_ = type_.title()
    if python_version() >= "3.9":
        match type_:
            case "banners":
                return "type_='Banner'"
            case "badges":
                return "type_='Badge'"
            case "molds":
                return "type_='Moldura'"
            case "consumables":
                return "type_='Consumable'"
            case "consumables":
                return "ID is not Null"
            case "shop":
                return "ID is not Null"
    else:
        if type_ == "banners":
            return "type_='Banner'"
        elif type_ == "badges":
            return "type_='Badge'"
        elif type_ == "molds":
            return "type_='Moldura'"
        elif type_ == "consumables":
            return "type_='Consumable'"
        elif type_ == "items" or "shop":
            return "ID is not Null"
    if type_ not in ['molds', 'banners', 'badges', 'consumables', 'shop', 'items']:
        return f"type_='{type_.title()}'"


async def get_item(
        self, target, isinnerjoin: bool = False, innerjoinfrom=None,
        item_id=None, type_=None, condition=None, order=None
):
    """

    Parameters
    ----------
    self
    target
    isinnerjoin
    innerjoinfrom
    item_id
    type_
    condition
    order

    Returns sql dict
    -------

    """
    if not type_:
        type_ = await self.database.select("items", "`type_`", f"id={item_id}", None, "1")
        type_ = type_[0][0]
        self.log(message=f"{type_}", name="type_.test")
    type_case = check_case(type_)
    # self.log(message=type_case, name="functions.get_item")
    # self.log(message=f'"{type_case}", "{target}", {condition}, {order}', name="SDFASA")
    if not condition:
        condition = f"id={item_id}"
    item = await self.database.select(
        f"{type_case if not isinnerjoin else type_case + ' i ' + innerjoinfrom}",
        f"{target}",
        condition,
        order
    )
    return item


async def drop_itens(self, type):
    """

    Parameters
    ----------
    self
    """
    if type in ['molds', 'banners', 'badges', 'consumables', 'shop', 'items']:
        try:
            await self.database.query(f"DELETE FROM {type} WHERE {check_case_reverse(type)})")
        except Exception as e:
            raise e
        finally:
            self.log(message=f"\n{type.upper()} FORAM REMOVIDAS...", name="functions.drop_itens")

    """
    if type == 'molds':
        try:
            await self.database.query("DELETE FROM molds WHERE type_=('Moldura')")
        except Exception as e:
            raise e
        finally:
            self.log(message="\nTODAS AS MOLDURAS FORAM REMOVIDAS...", name="functions.drop_itens")
    elif type == 'banners':
        try:
            await self.database.query("DELETE FROM banners WHERE type_=('Banner')")
        except Exception as e:
            raise e
        finally:
            self.log(message="\nTODAS AS BANNERS FORAM REMOVIDAS...", name="functions.drop_itens")
    elif type == 'badges':
        try:
            await self.database.query("DELETE FROM badges WHERE type_=('Badge')")
        except Exception as e:
            raise e
        finally:
            self.log(message="\nTODAS AS BADGES FORAM REMOVIDAS...", name="functions.drop_itens")
    elif type == 'consumables':
        try:
            await self.database.query("DELETE FROM consumables WHERE ID is not Null")
        except Exception as e:
            raise e
        finally:
            self.log(message="\nTODOS OS ITENS CONSUMÍVEIIS FORAM REMOVIDOS...", name="functions.drop_itens")
    elif type == 'shop':
        try:
            await self.database.query("DELETE FROM shop WHERE ID is not Null")
        except Exception as e:
            raise e
        finally:
            self.log(message="\nTODAS LOJA FOI REMOVIDA...", name="functions.drop_itens")
    elif type == 'items':
        try:
            await self.database.query("DELETE FROM items WHERE ID is not Null")
        except Exception as e:
            raise e
        finally:
            self.log(message="\nTODAS OS ITENS DE BACKUP FORAM REMOVIDOS...", name="functions.drop_itens")
    else:
        try:
            await self.database.query(f"DELETE FROM {type} WHERE ID is not Null")
        except Exception as e:
            raise e
        finally:
            self.log(message=f"\nTODAS OS ITENS em {type} FORAM REMOVIDOS...", name="functions.drop_itens")
    """


async def setMolds(self, molduras_rank, molduras_extra):
    """

    Parameters
    ----------
    self
    molduras_rank
        List of molds images directory
    molduras_extra
        List of molds images directory
    """

    await drop_itens(self, 'molds')

    for i, item in enumerate(molduras_rank):
        item_name = ' '.join(item.split('-'))[0:-4]
        self.log(message=f"{item_name}", name="mold rank name")
        try:
            '''
                * Imagens:
                - moldura loja
                - barra de xp
                - badge
                - moldura perfil
                - barra em que fica o nome do rank
            '''

            await self.database.insert(
                "molds",
                {
                    "name": str(item_name),
                    "lvmin": 0,
                    "canbuy": True,
                    "img": f"src/imgs/molduras/molduras-loja/{item}",
                    "imgxp": f"src/imgs/molduras/molduras-perfil/xp-bar/{item}",
                    "img_bdg": f"src/imgs/badges/rank/{item}",
                    "img_profile": f"src/imgs/molduras/molduras-perfil/bordas/rank/{item}",
                    "img_mold_title": f"src/imgs/molduras/molduras-perfil/titulos/{item}"
                }
            )

        except Exception as o:
            self.log(message=str(o), name="starterRoles.molduras_rank")
        else:
            print_progress_bar(
                i, len(molduras_rank), " progresso de molduras de rank criadas")

    sys.stdout.write("\nMolduras de rank inseridas...\n")
    sys.stdout.flush()
    # Molduras "extra""
    for i, item in enumerate(molduras_extra):
        item_name = ' '.join(item.split('-'))[0:-4]
        try:
            self.log(message=f"{item}", name="mold extra name")
            await self.database.insert(
                "molds",
                {
                    "name": str(item_name),
                    "lvmin": 0,
                    "canbuy": True,
                    "group_": "moldura",
                    "category": "Lendário",
                    "img": f"src/imgs/molduras/molduras-perfil/bordas/extra/{item}",
                    "img_profile": f"src/imgs/molduras/molduras-perfil/bordas/extra/{item}"
                }
            )

        except Exception as f:
            self.log(message=str(f), name="starterRoles.molduras_extra")
            raise f
        finally:
            print_progress_bar(i, len(molduras_extra), " progresso de molduras 'extras' criadas")
    sys.stdout.write("\nMolduras extras inseridas...\n")
    sys.stdout.flush()

    sys.stdout.write("\nAtualizando lvmin das molduras...\n")
    sys.stdout.flush()
    await self.database.query(
        """
            UPDATE molds SET lvmin = (
                SELECT lvmin FROM ranks WHERE ranks.name = molds.name
            )
        """
    )
    sys.stdout.write("\nTodas as molduras foram criadas e atualizadas\n")
    sys.stdout.flush()


async def setBadges(self, badges_staff, badges_supporter):
    """

    Parameters
    ----------
    self
    badges_supporter
        List of badges images directory
    badges_staff
        List of badges images directory
    """
    await drop_itens(self, 'badges')
    await self.database.query("""
        INSERT IGNORE INTO badges(name, img, lvmin) 
        SELECT molds.name, molds.img_bdg, molds.lvmin 
        FROM molds WHERE molds.img_bdg is not Null;
    """)

    for e in listdir(badges_staff):
        if e.endswith('.png'):
            print(str(e[:-4].title()))
            print(badges_staff + e)

            await self.database.query(
                f"""
                    INSERT IGNORE INTO badges (
                        name, img, canbuy, 
                        value, type_, 
                        group_, category
                    )
                    VALUES (
                        "{str(e[:-4]).title()}","{str(badges_staff + e)}",
                        false,99999999,"Badge","equipe","Lendário"
                    ) 
                """
            )
    for e in listdir(badges_supporter):
        if e.endswith('.png'):
            print(str(e[:-4].title()))
            print(badges_supporter + e)

            await self.database.query(
                f"""
                    INSERT IGNORE INTO badges (
                        name, img, canbuy, 
                        value, type_, 
                        group_, category
                    )
                    VALUES (
                        "{str(e[:-4].title())}","{str(badges_supporter + e)}",
                        false,99999999,"Badge","apoiador","Lendário"
                    ) 
                """
            )
    sys.stdout.write("\nTodas as badges foram criadas\n")
    sys.stdout.flush()

    sys.stdout.write("\nAtualizando lvmin das badges...\n")
    sys.stdout.flush()
    await self.database.query(
        """
            UPDATE badges SET lvmin = (
                SELECT lvmin FROM ranks WHERE ranks.name = badges.name
            )
        """
    )
    sys.stdout.write("\nTodas as badges foram criadas e atualizadas...\n")
    sys.stdout.flush()


async def setBanners(self, banners):
    """

    Parameters
    ----------
    self
    banners
        List of banners images directory
    """
    await drop_itens(self, 'banners')
    for i, item in enumerate(banners):
        item_name = ' '.join(item.split('-'))[0:-4]

        await self.database.insert(
            "banners",
            {
                "name": str(item_name),
                "canbuy": True,
                "img_loja": f"src/imgs/banners/{item}",
                "img_profile": f"src/imgs/banners/{item}"
            }
        )

        print_progress_bar(i, len(banners), " progresso de banners criadas")
    sys.stdout.write("\nTodas os banners foram criadas\n")
    sys.stdout.flush()


async def setConsumables(self, consumables: list):
    """

    Parameters
    ----------
    self
    consumables
        List of banners images directory
    """
    await drop_itens(self, 'consumables')
    for i, item in enumerate(consumables):
        item_name = ' '.join(item.split('-'))[0:-4]
        self.log(f"{item, consumables}", "test.consumables")
        await self.database.insert(
            "consumables",
            {
                "name": str(item_name),
                "canbuy": True,
                "category": "Raro",
                "img_loja": f"src/imgs/consumables/{item}"
            }
        )

        print_progress_bar(i, len(consumables), " progresso de consumables criadas")
    sys.stdout.write("\nTodos os consumables foram criadas\n")
    sys.stdout.flush()


async def starterItens(self, opt:str):
    """
    Adiciona os itens criados à loja
    {Muuita preguiça de fazer loop pra tudo, só usei os que eu já tinha }

    """

    # titles = [filename for filename in listdir(
    #     'src/imgs/titulos') if filename.endswith('.png')]
    # title_value = [12000, 25000, 69000, 70000, 125000, 178000, 200000]

    imgs_dir = join(root_directory, 'src', 'imgs')

    banners = [filename for filename in listdir(
        join(imgs_dir, 'banners')) if filename.endswith('.png')]
    molduras_rank = [filename for filename in listdir(
        join(imgs_dir, 'molduras', 'molduras-loja')) if filename.endswith('.png')]
    molduras_extra = [filename for filename in listdir(
        join(imgs_dir, 'molduras', 'molduras-perfil', 'bordas', 'extra')) if filename.endswith('.png')]
    badges_staff = 'src/imgs/badges/equipe/'
    badges_supporter = 'src/imgs/badges/supporter/'
    consumables = ['src/imgs/consumables/']
    # START MOLDS INSERT
    if opt == 'molds': await setMolds(self, molduras_rank, molduras_extra)
    elif opt == 'banners': await setBanners(self, banners)
    elif opt == 'badges': await setBadges(self, badges_staff, badges_supporter)
    elif opt == 'consumables': await setConsumables(self, consumables)
    elif opt == 'shop': await drop_itens(self, "shop")
    elif opt == 'items': await drop_itens(self, "items")
    elif opt == '*':
        await setMolds(self, molduras_rank, molduras_extra)
        await setBanners(self, banners)
        await setBadges(self, badges_staff, badges_supporter)
        await setConsumables(self, consumables)
        await drop_itens(self, "shop")
        await drop_itens(self, "items")
    else: await drop_itens(self, str(opt))


async def get_roles(
        member: discord.Member,
        guild,
        roles=[
            855117820814688307
        ]
):
    """

    Parameters
    ----------
    member
    guild
    roles

    Returns
    -------

    """
    # roles = [943171518895095869,
    #    943174476839936010,
    #    943192163947274341,
    #    943172687642132591,
    #    943171893752659979,
    #    943172687642132591,
    #    943193084584402975,
    #    943251043838468127,
    #    949805774484426783,
    #    1010184007394283630]
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

        # print(staff)
        return staff


def saveImage(url, fpath):
    """

    Parameters
    ----------
    url
    fpath
    """
    contents = urlopen(url)
    try:
        f = open(fpath, 'w')
        splitext(f.write(contents.read()))
        f.close()
    except Exception as o:
        raise (o)


async def get_userBanner_func(self, member: discord.Member):
    """

    Parameters
    ----------
    self
    member

    Returns
    -------

    """
    uMember = member
    uMember_id = member.id
    if uMember.avatar.is_animated:
        req = await self.http.request(discord.http.Route("GET", "/users/{uid}", uid=uMember_id))
        banner_id = req["banner"]
        return BytesIO(requests.get(
            f"https://cdn.discordapp.com/banners/{uMember.id}/{banner_id}?size=2048")
                       .content).getvalue()


async def get_userAvatar_func(member: discord.Member):
    """

    Parameters
    ----------
    member

    Returns
    -------

    """
    uMember = member
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{uMember.display_avatar.url}?size=1024?format=png") as resp:
            return await resp.read()


def banner_image_choose():
    imgs = ['src/imgs/extra/bg/banner_perfil_1.jpg',
            'src/imgs/extra/bg/banner_perfil_2.jpg', 'src/imgs/extra/bg/banner_perfil_3.jpg']
    return random.choice(imgs)


async def get_iventory(self, memberId):
    start_time = time.time()

    items_ids_ = []

    try:
        rows = await self.database.select(
            "inventory",
            "itens",
            f"id={memberId}"
        )
        item_ids = []
        if rows:
            # transform item_type | item_groups_and_ids in list 
            rows = ast.literal_eval(rows)
            for row_key, row_value in rows.items():
                items_key = row_key
                items_value_ids = row_value

                list_value = []

                # separate groups ans keys
                for key, value in items_value_ids.items():
                    if key == 'ids':
                        if not value:
                            continue
                        list_value.append(value)
                        continue

                    for k, v in value.items():

                        new_value = v

                        if not new_value:
                            continue

                    list_value.append(new_value)

                item_ids.append([items_key, list_value])

        print(time.time() - start_time, flush=True)
        print("Itens >>>>>")
        print(item_ids)
        print("<<<<< Itens")
        return item_ids

    except Exception as e:
        self.log(message=str(e), name="functions.get_iventory")


def checktype_(type):
    a = str(type).upper()
    itype = None

    if a == "MOLDURA":
        itype = 'molds'
    elif a == "BANNER":
        itype = 'banners'
    elif a == "CARRO":
        itype = 'cars'
    elif a == "BADGE":
        itype = 'badges'
    elif a == "Consumable":
        itype = 'utilizaveis'

    return itype


## USE THIS ONE INSTEAD
async def inventory_update_key(
        self,
        user_inventory_id: int, group: str, sub_group: Optional[Literal[str]], item_id: str,
        purpose: Optional[Literal['buy', 'use', 'show']],
        increment: Optional[Literal[0, 1]]
) -> str:
    """
    user_inventory_id:
        the id (int) of the user's inventory
    group:
        the first key in the JSON structure where the new key should be added
    sub_group:
        the sub-key inside the first key where the new key should be added, or 'ids' if the new key should be added directly to the ids sub-key
    item_id:
        the UUID of the new key
    purpose:
        optional / choose if the action to buy the item or to use it, 
        so it doesn't mix and add an item when the user is triyng to use
        smt he doesn't have
    increment:
        1 if the item should be incremented, else 0 if it must be removed


    """
    if not sub_group:
        sub_group = 'ids'

    try:
        # Define the query to fetch the current data for the group
        result = await self.database.select("inventory", "itens", f"id = {user_inventory_id}")

        self.log(message=group, name="functions.inventory_update_key")
        data = ast.literal_eval(result[0][0])
        self.log(message=data, name="functions.inventory_update_key")
        if purpose == 'show':
            return data
        if group not in data:
            self.log(message="inside if", name="functions.inventory_update_key")
            data[group] = {}

        subkeys = sub_group.split('.')

        self.log(message=subkeys, name="functions.inventory_update_key")
        current_subkey = data[group]

        if group != "Consumable":
            for subkey in subkeys:
                self.log(message=subkey, name="functions.inventory_update_key after append")
                if subkey not in current_subkey and not current_subkey.get("ids"):
                    current_subkey[subkey] = {"ids": {}}
                current_subkey = current_subkey[subkey]
                if subkey != "ids":
                    current_subkey = current_subkey["ids"]

                if increment == 0 and item_id in current_subkey:
                    return "ITEM_ALREADY_EXISTS"
                elif increment == 0 and item_id not in current_subkey:
                    current_subkey.remove(item_id)
                elif increment == 1 and item_id in current_subkey:
                    return "ITEM_ALREADY_EXISTS"
                elif increment == 1 and item_id not in current_subkey:
                    current_subkey.append(item_id)

                self.log(message=current_subkey, name="functions.inventory_update_key after append")
        elif not group:
            current_subkey = current_subkey[subkeys]

            self.log(message=current_subkey, name="functions.inventory_update_key Consumable ")
            # if subkeys in ['Badge', 'Moldura']:
            #    current_subkey[]
            if increment == 0 and item_id in current_subkey:
                return "ITEM_ALREADY_EXISTS"
            elif increment == 0 and item_id not in current_subkey:
                current_subkey.remove(item_id)
            elif increment == 1 and item_id in current_subkey:
                return "ITEM_ALREADY_EXISTS"
            elif increment == 1 and item_id not in current_subkey:
                current_subkey.append(item_id)
            current_subkey[str(item_id)] = current_subkey.get(
                str(item_id)) + increment if increment == 1 else current_subkey.get(str(item_id)) - 1
            if current_subkey[str(item_id)] == 0:
                del current_subkey[str(item_id)]

        self.log(message=data, name="functions.inventory_update_key after insert")

        data = json.dumps(data)
        self.log(message=data, name="functions.inventory_update_key after data")
        await self.database.update(
            "inventory",
            {"itens": f"{data}"},
            f"id={user_inventory_id}"
        )

        return "ITEM_ADDED_SUCCESSFULLY"

    except Exception as f:
        self.log(message=f, name="functions.inventory_update_key")
        self.log(message=repr(f), name="functions.inventory_update_key")


## -------

# FUNÇÕES DE NOVO AUTOR
async def sendEmb(user, author):
    try:
        # to author
        welcome = discord.Embed(title=f"{user.name}, meus parabéns por se tornar um autor da Kiniga!",
                                description="\n Leia as informações abaixo sobre como publicar capítulos "
                                            "no site e à quem recorrer para você não ficar perdido caso precise de ajuda.",
                                color=0x00ff33).set_author(name="Kiniga Brasil",
                                                           url='https://kiniga.com/',
                                                           icon_url='https://kiniga.com/wp-content/uploads/fbrfg/favicon-32x32.png').set_footer(
            text='Espero que seja muito produtivo escrevendo!')
        # creators
        creators = discord.Embed(title='Clique aqui para ir ao canal dos criadores.',
                                 description='Lá, você poderá encontrar, nas mensagens fixadas, todas as informações necessárias'
                                             ' para a publicação de novos capítulos.',
                                 url='https://discord.com/channels/667838471301365801/694308861699686420',
                                 color=0x00ff33)
        # tags
        tags = discord.Embed(title='Clique aqui para ir ao canal das tags.',
                             description='Lá, você poderá criar uma tag com o nome da sua história. O passo a passo também '
                                         'está nas mensagens fixadas.',
                             url='https://discord.com/channels/667838471301365801/831561655329751062',
                             color=0x00ff33)
        #  dúvidas
        dúvidas = discord.Embed(title='Clique aqui para ir ao canal das Perguntas Frequentes.',
                                description='Lá, você encontrará um link para o documento que lista e explica qualquer '
                                            'dúvida que você possa ter sobre a comunidade.',
                                url='https://discord.com/channels/667838471301365801/855526372403445830',
                                color=0x00ff33)
        #  passos para fixados
        fixados = discord.Embed(title='Não sabe como acessar as mensagens fixadas?',
                                description='Siga os passos da imagem abaixo.',
                                color=0x00ff33
                                ).set_image(
            url='https://media4.giphy.com/media/pURSYHBjYBEUhr04XQ/giphy.gif?cid=790b7611ecb81458c0064e87d5413028a19bfe17a95ed280&rid=giphy.gif&ct=g')
        #  novo projeto
        newProject = discord.Embed(title='Não entendeu como criar uma tag?',
                                   description='Siga o passo a passo abaixo para entender como solicitar a criação de uma tag '
                                               'para a sua história.',
                                   color=0x00ff33).set_image(
            url='https://media0.giphy.com/media/1IY0E9XoHQ2iJeLNwx/giphy.gif?cid=790b7611ed4435131498a759f83547158e2d9029c5e9b083&rid=giphy.gif&ct=g')

        return [welcome, creators, tags, dúvidas, fixados, newProject]

    except Exception as e:
        await author.send("Não foi possível prosseguir por conta do seguinte erro: \n\n"
                          "```{}``` \n\nPor favor, fale com o Shuichi".format(e))


async def checkRelease(self, interaction):
    try:
        channel = interaction.guild.get_channel(self.config["chat_release"])
        messages = [message async for message in channel.history(limit=1)]
        # messages = await channel.history(limit=1).flatten()
        messages.reverse()
        c = discord.Embed(title="Ocorreu um erro")
        for i, message in enumerate(messages):
            # print(message.embeds[0].to_dict())
            c = message.embeds[0] if len(
                message.embeds) >= 1 else message.content

        return c
    except Exception as i:
        raise i


async def getRelease(self, interaction):
    soup = BeautifulSoup(requests.get("http://kiniga.com/").text, 'lxml')
    table = soup.find_all('div', attrs={'class': 'tab-content-wrap'})[3]
    novel_recente = table.find_all(
        'div', attrs={'class': 'page-item-detail'})[0]
    t = novel_recente.find_all('div', attrs={'class': 'item-summary'})[0]
    title = t.find('div', attrs={'class': 'post-title'})
    if title:
        try:
            for l in title.find_all('a', href=True):
                try:
                    novel = BeautifulSoup(
                        requests.get(l['href']).text, 'lxml')
                    link = l['href']  # link
                    titulo = title.get_text()  # titulo da história
                    author = novel.find('div', attrs={
                        'class': 'author-content'}).find_all('a', href=True)[0]  # nome do autor
                    # sinopse da história
                    s = novel.find(
                        'div', attrs={'class': 'summary__content'})
                    sinopse = s.find('p').get_text()

                    i = novel.find('div', attrs={'class': 'summary_image'}
                                   ).find_all('img', {'class': 'img-responsive'})[0]  # img novel
                    img = i.get('data-src')

                    emb = discord.Embed(
                        title="📢 NOVA OBRA PUBLICADA 📢",
                        url=link,
                        color=discord.Color.green()
                    ).set_author(
                        name=author.get_text(),
                        url=author['href'],
                        icon_url="https://kiniga.com/wp-content/uploads/fbrfg/favicon-32x32.png"
                    ).set_thumbnail(
                        url="https://kiniga.com/wp-content/uploads/fbrfg/favicon-32x32.png"
                    ).add_field(
                        name="Nome:",
                        value=titulo,
                        inline=False
                    ).add_field(
                        name="Sinopse:",
                        value=sinopse,
                        inline=False
                    ).set_footer(
                        text="Kiniga.com - O limite é a sua imaginação"
                    ).set_image(
                        url=img
                    )

                    try:
                        oldEmb = await checkRelease(self, interaction)

                        # print("*" * 20)
                        # print( oldEmb.get('url') )
                        # print("*" * 20)
                        # print( emb.to_dict().get('url') )
                        if emb.to_dict().get('url') == oldEmb.to_dict().get('url'):
                            return discord.Embed(
                                title="Ops",
                                description="História já publicada.",
                                color=0x00ff33).set_author(
                                name="Kiniga Brasil",
                                url='https://kiniga.com/',
                                icon_url='https://kiniga.com/wp-content/uploads/fbrfg/favicon-32x32.png'
                            ).set_footer(text='Qualquer coisa, marque o Shuichi! :D')

                    except Exception as a:

                        return discord.Embed(
                            title=f"Erro",
                            description=str(a),
                            color=0x00ff33).set_author(
                            name="Kiniga Brasil",
                            url='https://kiniga.com/',
                            icon_url='https://kiniga.com/wp-content/uploads/fbrfg/favicon-32x32.png'
                        ).set_footer(text='Qualquer coisa, marque o Shuichi! :D')

                    return emb

                except Exception as i:
                    await interaction.user.send("Não foi possível prosseguir por conta do seguinte erro: \n\n"
                                                "```{}``` \n\nPor favor, fale com o Shuichi".format(i))
        except Exception as u:
            await interaction.user.send("Não foi possível prosseguir por conta do seguinte erro: \n\n"
                                        "```{}``` \n\nPor favor, fale com o Shuichi".format(u))


async def getfile(message):
    fileInfo = []
    attach = message.attachments
    for i, value in enumerate(attach):

        # Por enquanto, só quero 1 arquivo. Porém, se precisar de mais, o código está pronto
        if i >= 1:
            break
        try:
            fileInfo.append(
                [attach[1].url,
                 attach[1].filename]
            )
        except Exception as err:
            fileInfo.append(
                [attach[0].url,
                 attach[0].filename]
            )

    res = None
    try:
        url = fileInfo[0][0]
        filename = fileInfo[0][1]
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open('./_temp/h/%s' % (filename), 'w') as f:
            f.write(r.text)
            f.close()
        res = r.text

    except Exception as e:
        raise (e)
    return filename, res
