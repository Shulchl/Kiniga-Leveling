# coding: utf-8
"""
    base.functions
    ~~~~~~~~~~~~~

    Funções para facilitar meu trabalho.
"""

import discord
import os
import aiohttp
import random
import requests
import asyncpg
import json
import sys
import datetime
import time
import ast

from io import BytesIO
from urllib.request import urlopen
from typing import Optional, Literal, Dict, Union, List
from bs4 import BeautifulSoup

from base.struct import Config
from base.utilities import utilities
from asyncpg.pgproto.pgproto import UUID

from discord.utils import format_dt
from discord.ext import commands
from discord import app_commands


from base import log, cfg

__all__ = []


def __init__(self, bot) -> None:
    self.bot = bot
    self.db = utilities.database(self.bot.loop)
    self.log = log
    self.cfg = cfg

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
    if  interaction.response.type == discord.InteractionResponseType.channel_message:
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
    log.exception(error)
    admin = self.bot.get_user(int(self.cfg.report_to))

    embed = discord.Embed(title="Relatório de erros", color=0xe01b24)
    embed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
    embed.add_field(name=error.command.name, value=error.__cause__, inline=False)
    embed.set_footer(text=datetime.datetime.now())

    await admin.send(embed=embed)

async def initiate_user(self, member_id, member_name):
    user_ = await self.db.execute(
        """
            INSERT INTO users (id, rank, xp, xptotal, user_name) 
            VALUES (\'%s\', 0, 5, 5, \'%s\')
            ON CONFLICT (id) DO NOTHING
            RETURNING *;
        """ % (str(member_id), message.author.name, )
    )

    user_id, rank, xp, xptotal, info, spark, ori, iventory_id, birth, rank_id, user_name, email = user_
    # id, rank, xp, xptotal, info, spark, ori, iventory_id, birth, rank_id, user_name, email

    await self.db.execute("""
            INSERT INTO iventory (  iventory_id, itens ) 
            VALUES ( \'%s\',  '%s' )
            ON CONFLICT (iventory_id) DO NOTHING
            RETURNING moldura, car, banner, badge::jsonb

        """ % ( iventory_id,
            '{"Badge": {"rank": {"ids": {}}, "equipe": {"ids": {}}, "moldura": {"ids": {}}, "apoiador": {"ids": {}}}, "Carro": {"ids": {}}, "Banner": {"ids": {}}, "Moldura": {"rank": {"ids": {}}, "equipe": {"ids": {}}, "moldura": {"ids": {}}, "apoiador": {"ids": {}}}, "Utilizavel": {"ids": {}}}', 
        )
    )

    return user_

async def get_profile_info(self, member_id, member_name):
    user_ = await self.db.fetchrow(
        """
            SELECT * 
            FROM users
            WHERE id=($1)
        """, str(member_id)
    )
    if not user_:
        user_ = await self.initiate_user(str(member_id), member_name)

    return user_

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
    with open(os.path.join('./base/db', 'tables.sql'), 'r') as e:
        try:
            await self.db.execute(e.read())

        except Exception as f:
            log.exception(f)
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


    classes = self.cfg.ranks
    # x = []
    colors = self.cfg.colors
    count = 0

    if not classes:
        return f"Parece que você não inseriu nenhuma classe nas configurações."
    
    if not colors:
        return f"Parece que você não inseriu nenhuma cor nas configurações."

    if len(classes) != len(colors):
        return f"Toda classe precisa ter uma cor e toda cor precisa ter uma classe. "
        " Verifique se o número de cor é o mesmo que o de classes."
        f"\n\nNúmero de classes/cor: {len(classes)}/{len(colors)}"        

    # await self.db.execute("""
    #     insert into ranks(name, badges, lvmin) select name, img_bdg, lvmin from molds on conflict (name) do nothing returning lvmin;
    # """)

    for i, value in enumerate(classes):

        z = colors[i]
        # x = tuple((z[0], z[1], z[2]))
        # ''.join((f"{z[0]}, {z[1]}, {z[2]}"))
        rankRole = discord.utils.find(lambda r: r.name == value, msg.guild.roles) or await msg.guild.create_role(
            name=str(value), color=discord.Colour.from_rgb(z[0], z[1], z[2]))
        imgPathName = '-'.join(value.split())
        try:

            await self.db.execute("""
                INSERT INTO ranks (
                    name, lvmin, r, g, b, roleid, badges, imgxp
                )
                VALUES (
                    '%(rank_name)s', %(lv)s, %(r)s, %(g)s, %(b)s, 
                    '%(roleid)s', '%(badges)s', '%(imgxp)s' 
                )
            """ % {
                'rank_name': str(value),
                'lv': int(count),
                'r': int(z[0]),
                'g': int(z[1]),
                'b': int(z[2]),
                'roleid': str(rankRole.id),
                'badges': 'src/imgs/badges/rank/%s.png' % (imgPathName,),
                'imgxp': 'src/imgs/molduras/molduras-perfil/xp-bar/%s.png' % (imgPathName,), })

            # await self.db.fetch("""
            #    INSERT INTO ranks
            #     (lv, name, r, g, b, roleid, badges, imgxp) VALUES
            #     (%s, \'%s\', %s, %s, %s, %s,
            #     \'src/imgs/badges/rank/#%s.png\',
            #     \'src/imgs/molduras/molduras-perfil/xp-bar/#%sxp.png\')
            # """ % (i*10 if i != 0 else 10, value, z[0], z[1], z[2], rankRole.id, i, i))

        except Exception as o:
            await msg.channel.send(f"`{o}`")
            raise (o)
        else:
            print_progress_bar(
                i, len(classes), " progresso de badges criadas")
        finally:
            count += 10
    return "Todas as classes foram criadas"


async def starterItens(self):
    """
    Adiciona os itens criados à loja
    {Muuita preguiça de fazer loop pra tudo, só usei os que eu já tinha }

    """
    # titles = [filename for filename in os.listdir(
    #     'src/imgs/titulos') if filename.endswith('.png')]
    # title_value = [12000, 25000, 69000, 70000, 125000, 178000, 200000]

    banners = [filename for filename in os.listdir(
        'src/imgs/banners') if filename.endswith('.png')]

    molduras_rank = [filename for filename in os.listdir(
        'src/imgs/molduras/molduras-loja') if filename.endswith('.png')]
    molduras_extra = [filename for filename in os.listdir(
        'src/imgs/molduras/molduras-perfil/bordas/extra') if filename.endswith('.png')]
    sys.stdout.write(str(molduras_extra))
    sys.stdout.flush()
    # START MOLDS INSERT
    for i, item in enumerate(molduras_rank):
        item_name = ' '.join(item.split('-'))[0:-4]
        try:
            '''
                - moldura loja
                - barra de xp
                - badge
                - moldura perfil
                - barra em que fica o nome do rank
            '''
            await self.db.execute("""
                INSERT INTO molds (
                    name, lvmin, canbuy, 
                    img, 
                    imgxp, 
                    img_bdg, 
                    img_profile, 
                    img_mold_title
                ) VALUES ('%(name)s', 0, True,
                    'src/imgs/molduras/molduras-loja/%(item)s',
                    'src/imgs/molduras/molduras-perfil/xp-bar/%(item)s',
                    'src/imgs/badges/rank/%(item)s',
                    'src/imgs/molduras/molduras-perfil/bordas/rank/%(item)s', 
                    'src/imgs/molduras/molduras-perfil/titulos/%(item)s'
                ) ON CONFLICT (name) DO NOTHING
            """ % {'name': item_name, 'item': item, })
        except Exception as o:
            if isinstance(o, asyncpg.exceptions.PostgresSyntaxError):
                continue
            else:
                raise o
        else:
            print_progress_bar(
                i, len(molduras_rank), " progresso de molduras de rank criadas")
    # Molduras "extra""
    for i, item in enumerate(molduras_extra):
        item_name = ' '.join(item.split('-'))[0:-4]
        sys.stdout.write(item_name)
        sys.stdout.flush()
        sys.stdout.write(item)
        sys.stdout.flush()
        try:

            await self.db.execute("""
                INSERT INTO molds (
                    name, lvmin, canbuy, 
                    group_, category,
                    img, 
                    img_profile
                ) VALUES (
                    '%(name)s', 0, True, 
                    'moldura', 'Lendário',
                    'src/imgs/molduras/molduras-perfil/bordas/extra/%(item)s',
                    'src/imgs/molduras/molduras-perfil/bordas/extra/%(item)s'
                ) ON CONFLICT (name) DO NOTHING
            """ % {'name': item_name, 'item': item, })
            print_progress_bar(i, len(molduras_extra), " progresso de molduras 'extras' criadas")
        except Exception as f:
            if isinstance(f, asyncpg.exceptions.PostgresSyntaxError):
                continue
            else:
                raise f

    sys.stdout.write("\nAtualizando lvmin das badges...")
    sys.stdout.flush()
    await self.db.fetch(
        """
            UPDATE badges SET lvmin = (
                SELECT lvmin FROM ranks WHERE ranks.name = badges.name
            )
        """
    )
    sys.stdout.write("\nAtualizando lvmin das molduras...")
    sys.stdout.flush()
    await self.db.fetch(
        """
            UPDATE molds SET lvmin = (
                SELECT lvmin FROM ranks WHERE ranks.name = molds.name
            )
        """
    )
    sys.stdout.write("\nTodas as molduras e badges foram criadas e atualizadas")
    sys.stdout.flush()
    # END MOLDS INSERT

    # START BANNERS INSERT

    for i, item in enumerate(banners):
        item_name = ' '.join(item.split('-'))[0:-4]
        await self.db.execute("""
            INSERT INTO banners (
                name, 
                canbuy,
                img_loja, 
                img_perfil 
            ) 
            VALUES (
                '%(name)s', true,
                'src/imgs/banners/%(item)s',
                'src/imgs/banners/%(item)s' ) 
            ON CONFLICT (name) DO NOTHING 
        """ % {'name': item_name, 'item': item, })
        print_progress_bar(i, len(banners), " progresso de banners criadas")
    sys.stdout.write("\nTodas os banners foram criadas")
    sys.stdout.flush()

    # END BANNERS INSERT

    # ADD BADGES INSERT
    await self.db.execute("""
        insert into badges(name, img, lvmin) select name, img_bdg, lvmin from molds on conflict (name) do nothing;
    """)
    sys.stdout.write("\nTodas as badges foram criadas")
    sys.stdout.flush()

    # UTILIZAVEIS
    boost_path = "src/imgs/utilizaveis/boost"
    for i, file in enumerate(os.path.abspath(boost_path)):
        if file.endswith('.png'):
            await self.db.execute(
                """
                    INSERT INTO utilizaveis (
                        name, 
                        img, 
                        value
                    ) VALUES (
                        file[:-4],
                        os.path.join(boost_path, file),
                        90000 * ((i+1)*2)

                    ) ON CONFLICT name DO NOTHING

                """
            )
            sys.stdout.write("\nItem %s criado." % (file[:-4]))
            sys.stdout.flush()

    # CONSUMABLE ITENS
    consummable_path = "src/imgs/utilizaveis"
    for i, file in enumerate(os.path.abspath(boost_path)):
        if file.endswith('.png'):
            await self.db.execute(
                """
                    INSERT INTO utilizaveis (
                        name, canbuy, value, img
                    ) VALUES (
                        '%s', %s, %s, '%s'
                    ) ON CONFLICT name DO NOTHING
                """ % (file[:-4], True, 15000, os.path.join(consummable_path, file))
            )
            sys.stdout.write("\nItem consumível %s criado." % (file[:-4]))
            sys.stdout.flush()

    # TITULOS NÃO SÃO MAIS SUPORTADOS

    # count = 0
    # for i in titles:
    #     # START TITLES INSERT
    #     nome = re.search(r'\-(.*?).png', i).group(1)
    #     print(nome, i, title_value[int(titles.index(i))])
    #     await self.db.execute(f"""
    #         INSERT INTO titles (
    #             name, localimg, canbuy, value
    #         ) VALUES ('{nome}',
    #                 'src/imgs/titulos/{i}',
    #                 true, {title_value[int(titles.index(i))]}
    #         ) ON CONFLICT (name) DO NOTHING
    #     """)
    #     count += 1
    # END TITLES INSERT

async def get_roles(
        member: discord.Member,
        guild,
        roles=[
            855117820814688307
        ]
):
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
    contents = urlopen(url)
    try:
        f = open(fpath, 'w')
        os.path.splitext(f.write(contents.read()))
        f.close()
    except Exception as o:
        raise (o)


async def get_userBanner_func(self, member: discord.Member):
    uMember = member
    uMember_id = member.id
    if uMember.is_avatar_animated:
        req = await self.bot.http.request(discord.http.Route("GET", "/users/{uid}", uid=uMember_id))
        banner_id = req["banner"]
        return BytesIO(requests.get(
            f"https://cdn.discordapp.com/banners/{uMember.id}/{banner_id}?size=2048")
                       .content).getvalue()


async def get_userAvatar_func(member: discord.Member):
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
        rows = await self.db.fetch("""
            SELECT * FROM jsonb_each_text(
                (
                    SELECT itens::jsonb FROM iventory
                    WHERE iventory_id=(
                        SELECT iventory_id FROM users WHERE id = ('%s')
                    )
                )
            );
        """ % (memberId,)
                                   )
        item_ids = []
        if rows:
            # transform item_type | item_groups_and_ids in list 
            items_list = [[i[0], i[1]] for i in rows]
            for row in items_list:
                items_key = row[0]
                items_value_ids = ast.literal_eval(row[1])
                list_value = []
                # separate groups ans keys
                for key, value in items_value_ids.items():
                    if key != 'ids':
                        value = ast.literal_eval(str(value))

                    # print(check_value_type)
                    # print(type(check_value_type))
                    for k, v in value.items():

                        new_value = None

                        if k == 'ids':
                            new_value = v
                        else:
                            new_value = value

                        if not new_value:
                            continue

                        list_value.append(new_value)

                item_ids.append([items_key, ast.literal_eval(str(list_value))])

        print(time.time() - start_time, flush=True)
        return item_ids

    except Exception as e:
        raise e


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
    elif a == "UTILIZAVEL":
        itype = 'utilizaveis'

    return itype

## DO NOT USE
async def user_inventory(
        self,
        member,
        opt: Optional[
            Literal[
                "remove", "add"
            ]
        ],
        iventory_key=None,
        newValue=None
):
    #
    #   ADICIONA/REMOVE ITENS E QUANTIDADES
    #   iventory_key: str = TIPO DO ITEM  (EX: Badge, Moldura, Banner)
    #   newValue: str(uuid) = ID VERDADEIRO DO ITEM
    #

    sys.stdout.flush()
    res = ""
    itensId = newValue
    if isinstance(itensId, list):
        itensId = [i for i in itensId]

    iventoryId = await self.db.fetch("SELECT iventory_id FROM users WHERE id = (\'%s\')" % (member,))
    if iventoryId:
        iventoryId = iventoryId[0][0]

    item_find = checktype_(iventory_key)
    is_badge_mold = False
    item_group = ''
    if iventory_key == 'Badge' or iventory_key == 'Moldura':
        item_group = await self.db.fetch(
            """
                    SELECT group_ FROM %s WHERE id=(\'%s\')
                """ % (
                item_find,
                itensId,
            )
        )
        item_group = str(item_group[0][0])
        is_badge_mold = True

    try:

        if opt == "remove":
            res = 'remove'
            if iventory_key == 'Badge' or iventory_key == 'Moldura':
                # REMOVE 1 UNIDADE DO ITEM
                # REMOVE 1 UNIDADE DO ITEM
                await self.db.fetch(
                    """
                        UPDATE iventory SET itens = jsonb_set(
                            itens::jsonb,
                            '{%(iKEY)s, %(iGROUP)s, ids, %(iID)s}'::text[],
                            (
                                SELECT COALESCE(
                                    (
                                        SELECT CAST(
                                            itens::jsonb->\'%(iKEY)s\'->'%(iGROUP)s'->'ids'->\'%(iID)s\' as INTEGER
                                        ) - 1  FROM iventory
                                        WHERE iventory_id=(\'%(iINV)s\')
                                    ), 0 
                                )::text as _item
                            )::jsonb,
                            true
                        )
                        WHERE iventory_id=(
                            \'%(iINV)s\'
                        )
                        
                    """ % {
                        'iKEY': iventory_key,
                        'iGROUP': item_group,
                        'iID': itensId,
                        'iINV': iventoryId
                    }
                )

                # REMOVE SE UANTIDADE FOR 0 
                # (útil apenas para itens utilizáveis/consumíveis)
                try:
                    print("Tentando pegar valores zerados...")
                    null_values = await self.db.fetch(
                        """
                            SELECT * FROM (
                                SELECT 
                                    iventory_id,
                                    (jsonb_each_text(itens::jsonb->'%(iKEY)s'->\'%(iGROUP)s\'->'ids')).* 
                                FROM
                                    iventory t
                            ) denormalized_values
                            WHERE VALUE < '1' and iventory_id = \'%(iINV)s\'
                        """ % {
                            'iKEY': iventory_key,
                            'iGROUP': item_group,
                            'iINV': iventoryId
                        }
                    )
                    # print(null_values)
                except Exception as e:
                    print(e)
                # print(', '.join(["{%s, %s, %s}" % (iventory_key, 'ids', n[1]) for n in null_values]))

                print("{%s, %s, %s, %s}" % (iventory_key, item_group, 'ids', n[1]) for n in null_values)
                try:
                    t = ["{%s, %s, %s, %s}" % (iventory_key, item_group, 'ids', n[1]) for n in null_values]
                    t = ', '.join(t)
                    print(t)
                    for n in null_values:
                        print("Tentando apagar valores zerados...")
                        query = "SELECT itens::jsonb " + "#-" + " '{%(iKEY)s}'::text[] FROM iventory WHERE iventory_id = ('%(iINV)s')" % {
                            'oKEY': iventory_key,
                            'iKEY': t,
                            'iGROUP': item_group,
                            'iINV': iventoryId
                        }
                        aa = await self.db.fetch(query)
                        print(aa)

                    print("Feito.")
                except Exception as e:
                    print(e)


            else:
                # REMOVE 1 UNIDADE DO ITEM
                await self.db.fetch(
                    """
                        UPDATE iventory SET itens = jsonb_set(
                            itens::jsonb,
                            '{%(iKEY)s, ids, %(iID)s}'::text[],
                            (
                                SELECT COALESCE(
                                    (
                                        SELECT CAST(
                                            itens::jsonb->\'%(iKEY)s\'->'ids'->\'%(iID)s\' as INTEGER
                                        ) - 1  FROM iventory
                                        WHERE iventory_id=(\'%(iINV)s\')
                                    ), 0
                                )::text as _item
                            )::jsonb,
                            true
                        )
                        WHERE iventory_id=(
                            \'%(iINV)s\'
                        )
                    """ % {
                        'iKEY': iventory_key,
                        'iGROUP': item_group,
                        'iID': itensId,
                        'iINV': iventoryId
                    }
                )

                # REMOVE SE UANTIDADE FOR 0 
                # (útil apenas para itens utilizáveis/consumíveis)
                try:
                    print("Tentando pegar valores zerados...")
                    null_values = await self.db.fetch(
                        """
                            SELECT * FROM (
                                SELECT 
                                    iventory_id,
                                    (jsonb_each_text(itens::jsonb->'%(iKEY)s'->'ids')).* 
                                FROM
                                    iventory t
                            ) denormalized_values
                            WHERE VALUE < '1' and iventory_id = \'%(iINV)s\'
                        """ % {
                            'iKEY': iventory_key,
                            'iGROUP': item_group,
                            'iINV': iventoryId
                        }
                    )
                    print(null_values)
                except Exception as e:
                    print(e)
                # print(', '.join(["{%s, %s, %s}" % (iventory_key, 'ids', n[1]) for n in null_values]))
                print((tuple("{%s, %s, %s, %s}") % (iventory_key, item_group, 'ids', n[1]) for n in null_values))
                try:
                    t = ["{%s, %s, %s}" % (iventory_key, 'ids', n[1]) for n in null_values]
                    t = ', '.join(t)
                    for n in null_values:
                        print("Tentando apagar valores zerados...")
                        query = "SELECT itens::jsonb" + " #- " + "'{%(iKEY)s}'::text[] FROM iventory WHERE iventory_id = ('%(iINV)s')" % {
                            'iKEY': t,
                            'iINV': iventoryId
                        }
                        aa = await self.db.fetch(query)
                        print(aa)

                    print("Feito.")
                except Exception as e:
                    print(e)

        elif opt == "add":
            if iventory_key == 'Badge' or iventory_key == 'Moldura':
                res = await self.db.fetch(
                    """
                        UPDATE iventory SET itens = jsonb_set(
                            itens::jsonb,
                            '{%(i)s, %(iGROUP)s, ids, %(iID)s}'::text[],
                            (
                                SELECT COALESCE(
                                    (
                                        SELECT CAST(
                                            itens::jsonb->\'%(iKEY)s\'->'%(iGROUP)s'->'ids'->\'%(iID)s\' as INTEGER
                                        ) + 1  FROM iventory
                                        WHERE iventory_id=(\'%(iINV)s\')
                                    ), 0 
                                )::text as _item
                            )::jsonb,
                            true
                        )
                        WHERE iventory_id=(
                            \'%(iINV)s\'
                        )

                    """ % {
                        'iKEY': iventory_key,
                        'iGROUP': item_group,
                        'iID': itensId,
                        'iINV': iventoryId
                    }
                )

            else:
                res = await self.db.fetch(
                    """
                        UPDATE iventory SET itens = jsonb_set(
                            itens::jsonb,
                            '{%(i)s, ids, %(iID)s}'::text[],
                            (
                                SELECT COALESCE(
                                    (
                                        SELECT CAST(
                                            itens::jsonb->\'%(iKEY)s\'->'ids'->\'%(iID)s\' as INTEGER
                                        ) + 1  FROM iventory
                                        WHERE iventory_id=(\'%(iINV)s\')
                                    ), 0 
                                )::text as _item
                            )::jsonb,
                            true
                        )
                        WHERE iventory_id=(
                            \'%(iINV)s\'
                        )

                    """ % {
                        'iKEY': iventory_key,
                        'iID': itensId,
                        'iINV': iventoryId
                    }
                )
    except Exception as a:
        raise a

    return res


## -------
## USE THIS ONE INSTEAD
async def inventory_update_key(self, user_inventory_id, group, sub_group: Optional[Literal[str]], item_id: str,
                               purpose: Optional[Literal['buy', 'use', 'show']],
                               increment: Optional[Literal[0, 1]]) -> str:
    """
    user_inventory_id:
        the id (uuid) of the user's inventory
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

    if item_id:
        if isinstance(item_id, UUID):
            item_id = str(item_id)

    try:
        # Define the query to fetch the current data for the group
        result = await self.db.fetchval(
            """
                SELECT itens::json
                FROM iventory 
                WHERE iventory_id = $1 
                FOR UPDATE
            """, user_inventory_id
        )
        log.info(result)
        data = ast.literal_eval(result)
        print(data, flush=True)
        if purpose == 'show':
            return data
        if group not in data:
            print("inside if", flush=True)
            data[group] = {}
        subkeys = sub_group.split('.')

        current_subkey = data[group]
        print(current_subkey, flush=True)

        if group in ['Moldura', 'Badge']:
            for subkey in subkeys[:-1]:
                if subkey not in current_subkey:
                    current_subkey[subkey] = {"ids": {}}
                current_subkey = current_subkey[subkey]
                if subkey != "ids":
                    current_subkey = current_subkey["ids"]
                    if item_id in current_subkey:
                        return "ITEM_ALREADY_EXISTS"
        else:
            current_subkey = current_subkey[subkeys[-1]]

        print(current_subkey, flush=True)

        # if subkeys[-1] != "ids": # and group == 'Utilizavel' or 'Carro'
        #    if subkeys[-1] not in current_subkey:
        #        current_subkey[subkeys[-1]] = {"ids": {}}
        #    current_subkey = current_subkey[subkeys[-1]]

        # if "ids" not in current_subkey:
        #     current_subkey = {}
        print(current_subkey.get(item_id), flush=True)
        if uuid_value := current_subkey.get(item_id):
            print(uuid_value, flush=True)
            if increment is None:  # or group not in ['Utilizavel', 'Carro']
                return "ITEM_ALREADY_EXISTS"

            current_subkey[item_id] = (uuid_value + increment) if increment == 1 else (uuid_value - 1)
            print("aaa", flush=True)
            print(current_subkey, flush=True)

            if current_subkey[item_id] == 0:
                del current_subkey[item_id]

            print(current_subkey, flush=True)
        else:
            # IF IT DONT EXIST
            if purpose == 'buy':
                print(type(item_id), flush=True)
                current_subkey[item_id] = 1
            elif purpose == 'use':
                if item_id not in current_subkey:
                    return "ITEM_DONT_EXISTS"

        data = json.dumps(data)
        print(data, flush=True)
        await self.db.execute(
            "UPDATE iventory SET itens = \'%s\' WHERE iventory_id = \'%s\'" % (str(data), user_inventory_id))

        return "ITEM_ADDED_SUCCESSFULLY"

    except Exception as f:
        log.exception(f)
        print(repr(f), flush=True)


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
        channel = interaction.guild.get_channel(self.cfg.chat_release)
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
        raise (i)


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

## BOT MENAGEMENT

async def cogs_manager(bot: commands.Bot, mode: str, cogs: list[str]) -> None:
    for cog in cogs:
        try:
            if mode == "unload":
                await bot.unload_extension(cog)
            elif mode == "load":
                await bot.load_extension(cog)
            elif mode == "reload":
                await bot.reload_extension(cog)
            else:
                raise ValueError("Invalid mode.")
            bot.log(f"Cog {cog} {mode}ed.", name="classes.utilities", level=logging.DEBUG)
        except Exception as e:
            raise e

def bot_has_permissions(**perms: bool):
    """A decorator that add specified permissions to Command.extras and add bot_has_permissions check to Command with specified permissions.
    
    Warning:
    - This decorator must be on the top of the decorator stack
    - This decorator is not compatible with commands.check()
    """
    def wrapped(command: Union[app_commands.Command, commands.HybridCommand, commands.Command]) -> Union[app_commands.Command, commands.HybridCommand, commands.Command]:
        if not isinstance(command, (app_commands.Command, commands.hybrid.HybridCommand, commands.Command)):
            raise TypeError(f"Cannot decorate a class that is not a subclass of Command, get: {type(command)} must be Command")

        valid_required_permissions = [
            perm for perm, value in perms.items() if getattr(discord.Permissions.none(), perm) != value
        ]
        command.extras.update({"bot_permissions": valid_required_permissions})

        if isinstance(command, commands.HybridCommand) and command.app_command:
            command.app_command.extras.update({"bot_permissions": valid_required_permissions})

        if isinstance(command, (app_commands.Command, commands.HybridCommand)):
            app_commands.checks.bot_has_permissions(**perms)(command)
        if isinstance(command, (commands.Command, commands.HybridCommand)):
            commands.bot_has_permissions(**perms)(command)

        return command

    return wrapped