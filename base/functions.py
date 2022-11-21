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
import re
import numpy as np
import asyncpg
import ast
import json

from typing import final

from io import BytesIO
from pkg_resources import EmptyProvider

from base.struct import Config
from base.utilities import utilities

from urllib.request import urlopen

from psycopg2 import OperationalError, errorcodes, errors
from base.db.database import print_psycopg2_exception as pycopg_exception

from typing import Optional, Literal

from bs4 import BeautifulSoup


__all__ = ['Functions']


def __init__(self, bot) -> None:
    self.bot = bot
    self.db = utilities.database(
        self.bot.loop, self.bot.cfg.postgresql_user, self.bot.cfg.postgresql_password)

    with open('config.json', 'r') as f:
        self.cfg = Config(json.loads(f.read()))


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

    classes = self.bot.cfg.ranks
    # x = []
    colors = self.bot.cfg.colors
    count = 0
    for i, value in enumerate(classes):

        if i >= len(classes):
            break

        z = colors[i]
        # x = tuple((z[0], z[1], z[2]))
        # ''.join((f"{z[0]}, {z[1]}, {z[2]}"))
        rankRole = discord.utils.find(lambda r: r.name == value, msg.guild.roles) or await msg.guild.create_role(
            name=str(value), color=discord.Colour.from_rgb(z[0], z[1], z[2]))
        try:
            await self.db.fetch(
                "INSERT INTO ranks (lv, name, r, g, b, badges, roleid, imgxp) VALUES "
                f" ({count}, \'{value}\', {z[ 0 ]}, {z[ 1 ]}, {z[ 2 ]}, \'src/imgs/badges/#{i}.png\', "
                f" {rankRole.id}, \'src/imgs/molduras/molduras-perfil/xp-bar/#{i}xp.png\')"
            )
        except Exception as o:
            await msg.channel.send(f"`{o}`")
        count += 10


async def starterItens(self):
    """
    Adiciona os itens criados à loja
    {Muuita preguiça de fazer loop pra tudo, só usei os que eu já tinha }

    """
    banners = [filename for filename in os.listdir(
        'src/imgs/banners') if filename.endswith('.png')]
    titles = [filename for filename in os.listdir(
        'src/imgs/titulos') if filename.endswith('.png')]
    title_value = [12000, 25000, 69000, 70000, 125000, 178000, 200000]
    print(banners)
    print(titles)

    try:
        # START MOLDS INSERT
        await self.db.fetch("""
            INSERT INTO molds (
                    name, img, imgxp, img_bdg, img_profile, 
                    lvmin, value, img_mold_title, canbuy
                ) VALUES ('Novato',
                        'src/imgs/molduras/molduras-loja/#0.png',
                        'src/imgs/molduras/molduras-perfil/xp-bar/#0xp.png',
                        'src/imgs/badges/#0.png',
                        'src/imgs/molduras/molduras-perfil/bordas/#0.png', 
                        0, 1000,
                        'src/imgs/molduras/molduras-perfil/titulos/#0E.png', 
                        False
                ) ON CONFLICT (name) DO NOTHING
        """)
        await self.db.fetch("""
            INSERT INTO molds (
                    name, img, imgxp, img_bdg, img_profile, 
                    lvmin, value, img_mold_title
                ) VALUES ('Soldado Nadir',
                        'src/imgs/molduras/molduras-loja/#1.png',
                        'src/imgs/molduras/molduras-perfil/xp-bar/#1xp.png',
                        'src/imgs/badges/#0.png',
                        'src/imgs/molduras/molduras-perfil/bordas/#1.png', 
                        10, 500000,
                        'src/imgs/molduras/molduras-perfil/titulos/#1E.png' 
                ) ON CONFLICT (name) DO NOTHING
        """)
        await self.db.fetch("""
            INSERT INTO molds (
                    name, img, imgxp, img_bdg, img_profile, 
                    lvmin, value, img_mold_title
                ) VALUES ('Sargento Aurora',
                        'src/imgs/molduras/molduras-loja/#2.png',
                        'src/imgs/molduras/molduras-perfil/xp-bar/#2xp.png',
                        'src/imgs/badges/#0.png',
                        'src/imgs/molduras/molduras-perfil/bordas/#2.png', 
                        20, 1000000,
                        'src/imgs/molduras/molduras-perfil/titulos/#2E.png' 
                ) ON CONFLICT (name) DO NOTHING
        """)
        await self.db.fetch("""
            INSERT INTO molds (
                    name, img, imgxp, img_bdg, img_profile, 
                    lvmin, value, img_mold_title
                ) VALUES ('Tenente Zênite',
                        'src/imgs/molduras/molduras-loja/#3.png',
                        'src/imgs/molduras/molduras-perfil/xp-bar/#3xp.png',
                        'src/imgs/badges/#0.png',
                        'src/imgs/molduras/molduras-perfil/bordas/#3.png', 
                        30, 2000000,
                        'src/imgs/molduras/molduras-perfil/titulos/#3E.png' 
                ) ON CONFLICT (name) DO NOTHING
        """)
        await self.db.fetch("""
            INSERT INTO molds (
                    name, img, imgxp, img_bdg, img_profile, 
                    lvmin, value, img_mold_title
                ) VALUES ('Capitão Solar',
                        'src/imgs/molduras/molduras-loja/#4.png',
                        'src/imgs/molduras/molduras-perfil/xp-bar/#4xp.png',
                        'src/imgs/badges/#0.png',
                        'src/imgs/molduras/molduras-perfil/bordas/#4.png', 
                        40, 4000000,
                        'src/imgs/molduras/molduras-perfil/titulos/#4E.png' 
                ) ON CONFLICT (name) DO NOTHING
        """)
        await self.db.fetch("""
            INSERT INTO molds (
                    name, img, imgxp, img_bdg, img_profile, 
                    lvmin, value, img_mold_title
                ) VALUES ('Major Solar',
                        'src/imgs/molduras/molduras-loja/#5.png',
                        'src/imgs/molduras/molduras-perfil/xp-bar/#5xp.png',
                        'src/imgs/badges/#0.png',
                        'src/imgs/molduras/molduras-perfil/bordas/#5.png', 
                        50, 6500000,
                        'src/imgs/molduras/molduras-perfil/titulos/#5E.png' 
                ) ON CONFLICT (name) DO NOTHING
        """)
        await self.db.fetch("""
            INSERT INTO molds (
                    name, img, imgxp, img_bdg, img_profile, 
                    lvmin, value, img_mold_title
                ) VALUES ('Coronel Umbra',
                        'src/imgs/molduras/molduras-loja/#6.png',
                        'src/imgs/molduras/molduras-perfil/xp-bar/#6xp.png',
                        'src/imgs/badges/#0.png',
                        'src/imgs/molduras/molduras-perfil/bordas/#6.png', 
                        60, 8000000,
                        'src/imgs/molduras/molduras-perfil/titulos/#6E.png' 
                ) ON CONFLICT (name) DO NOTHING
        """)
        await self.db.fetch("""
            INSERT INTO molds (
                    name, img, imgxp, img_bdg, img_profile, 
                    lvmin, value, img_mold_title
                ) VALUES ('General Blazar',
                        'src/imgs/molduras/molduras-loja/#7.png',
                        'src/imgs/molduras/molduras-perfil/xp-bar/#7xp.png',
                        'src/imgs/badges/#0.png',
                        'src/imgs/molduras/molduras-perfil/bordas/#7.png', 
                        70, 100000000,
                        'src/imgs/molduras/molduras-perfil/titulos/#7E.png' 
                ) ON CONFLICT (name) DO NOTHING
        """)
        await self.db.fetch("""
            INSERT INTO molds (
                    name, img, imgxp, img_bdg, img_profile, 
                    lvmin, value, img_mold_title
                ) VALUES ('Marechal Quasar',
                        'src/imgs/molduras/molduras-loja/#8.png',
                        'src/imgs/molduras/molduras-perfil/xp-bar/#8xp.png',
                        'src/imgs/badges/#0.png',
                        'src/imgs/molduras/molduras-perfil/bordas/#8.png', 
                        80, 100000000,
                        'src/imgs/molduras/molduras-perfil/titulos/#8E.png' 
                ) ON CONFLICT (name) DO NOTHING
        """)
        # END MOLDS INSERT

        # START BANNERS INSERT
        await self.db.fetch(f"""
            INSERT INTO banners (name, img_loja,
                img_perfil, canbuy, value
                ) VALUES ('Explosão Solar',
                            'src/imgs/banners/{banners[0]}',
                            'src/imgs/banners/{banners[0]}',
                            true, 55000
                ) ON CONFLICT (name) DO NOTHING
        """)
        await self.db.fetch(f"""
            INSERT INTO banners (name, img_loja,
                img_perfil, canbuy, value
                ) VALUES ('Explosão Negativa',
                            'src/imgs/banners/{banners[1]}',
                            'src/imgs/banners/{banners[1]}',
                            true, 5500000
                ) ON CONFLICT (name) DO NOTHING
        """)
        await self.db.fetch(f"""
            INSERT INTO banners (name, img_loja,
                img_perfil, canbuy, value
                ) VALUES ('Plenata Magnético',
                            'src/imgs/banners/{banners[2]}',
                            'src/imgs/banners/{banners[2]}',
                            true, 5500000
                ) ON CONFLICT (name) DO NOTHING
        """)
        # END BANNERS INSERT

        # START TITLES INSERT
        count = 0
        for i in titles:
            # START TITLES INSERT
            nome = re.search(r'\-(.*?).png', i).group(1)
            print(nome, i, title_value[int(titles.index(i))])

            await self.db.fetch(f"""
                INSERT INTO titles (
                    name, localimg, canbuy, value
                ) VALUES ('{nome}', 
                        'src/imgs/titulos/{i}',
                        true, {title_value[int(titles.index(i))]}
                ) ON CONFLICT (name) DO NOTHING
            """)
            count += 1
        # END TITLES INSERT

        # START ALTER
        await self.db.fetch("""
            ALTER TABLE IF EXISTS public.itens
            ADD CONSTRAINT banners_detail FOREIGN KEY 
            (name, item_type_id)
            REFERENCES public.banners 
            (name, id) MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
            NOT VALID
        """)
        await self.db.fetch("""
            ALTER TABLE IF EXISTS public.itens
            ADD CONSTRAINT molds_detail FOREIGN KEY 
            (name, item_type_id)
            REFERENCES public.molds 
            (name, id) MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
            NOT VALID
        """)
        await self.db.fetch("""
            ALTER TABLE IF EXISTS public.itens
            ADD CONSTRAINT titles_detail FOREIGN KEY (name, item_type_id)
            REFERENCES public.titles (name, id) MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
            NOT VALID
        """)
        await self.db.fetch("""
            ALTER TABLE IF EXISTS public.itens
            ADD CONSTRAINT utili_detail FOREIGN KEY (name, id)
            REFERENCES public.utilizaveis (name, id) MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
            NOT VALID;
        """)
        await self.db.fetch("""
            ALTER TABLE IF EXISTS public.ranks
            ADD FOREIGN KEY (name, badges)
            REFERENCES public.molds (name, img_bdg) MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
            NOT VALID;
        """)
        await self.db.fetch("""
            ALTER TABLE IF EXISTS public.setup
            ADD CONSTRAINT owner_id FOREIGN KEY (owner_id)
            REFERENCES public.users (id) MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
            NOT VALID;
        """)
        await self.db.fetch("""
            ALTER TABLE IF EXISTS public.shop
            ADD CONSTRAINT itens_details FOREIGN KEY (id)
            REFERENCES public.itens (id) MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
            NOT VALID;
        """)
        await self.db.fetch("""
            ALTER TABLE IF EXISTS public.users
            ADD CONSTRAINT rank_id FOREIGN KEY (rank_id)
            REFERENCES public.ranks (id) MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
            NOT VALID;
        """)
        await self.db.fetch("""
            ALTER TABLE IF EXISTS public.users
            ADD CONSTRAINT ivent_id FOREIGN KEY (inventory_id)
            REFERENCES public.iventory (ivent_id) MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
            NOT VALID;
        """)
        await self.db.fetch("""
            ALTER TABLE IF EXISTS public.iventory
            ADD CONSTRAINT banner FOREIGN KEY (banner)
            REFERENCES public.banners (id) MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
            NOT VALID;
        """)
        await self.db.fetch("""
            ALTER TABLE IF EXISTS public.iventory
            ADD CONSTRAINT title FOREIGN KEY (title)
            REFERENCES public.titles (id) MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
            NOT VALID;
        """)
        await self.db.fetch("""
            ALTER TABLE IF EXISTS public.iventory
            ADD CONSTRAINT mold FOREIGN KEY (mold)
            REFERENCES public.molds (id) MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
            NOT VALID;
        """)
        await self.db.fetch("""
            ALTER TABLE IF EXISTS public.iventory
            ADD CONSTRAINT car FOREIGN KEY (car)
            REFERENCES public.cars (id) MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
            NOT VALID;
        """)

        # ADD BADGES
        try:
            await self.db.fetch("""
                insert into badges(name, img, lvmin) select name, img_bdg, lvmin from molds on conflict (name) do nothing;
            """)

        except Exception as e:
            return "`Não foi possível inserir as badges nos itens, provavelmente porque não tem nenhuma moldura ainda. \n %s`" % (e, )

    except Exception as err:
        if isinstance(err, asyncpg.exceptions.PostgresSyntaxError):
            # pass exception to function
            pycopg_exception(err)
        else:
            pycopg_exception(err)


async def get_roles(member: discord.Member, guild, roles=[

    855117820814688307
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

        # print(staff)
        return staff


def saveImage(url, fpath):
    contents = urlopen(url)
    try:
        f = open(fpath, 'w')
        os.path.splitext(f.write(contents.read()))
        f.close()
    except Exception:
        raise


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
    id = await self.db.fetch("""
        SELECT itens::jsonb FROM iventory WHERE ivent_id=(
                SELECT inventory_id FROM users WHERE id = ('%s')
        )
    """ % (memberId, )
    )
    return id[0][0]


async def user_inventory(self, member, opt: Optional[Literal["get", "remove", "add"]], iventory_key: list = None, newValue: list = None):
    iventoryId = await self.db.fetch("SELECT inventory_id FROM users WHERE id = (\'%s\')" % (member, ))
    if iventoryId:
        iventoryId = iventoryId[0][0]

    if iventory_key is not None:
        itens = [f"itens::jsonb->'{i}'" for i in iventory_key]
        itens = ",".join(itens)
    else:
        itens = "itens::jsonb"

    if opt == "get":
        if "Badge" or "Moldura" in iventory_key:
            res = await self.db.fetch("""
                    SELECT * FROM jsonb_each_text(
                        (
                            SELECT %s FROM iventory
                            WHERE ivent_id=(\'%s\')
                        )
                    );
                """ % (str(itens), iventoryId, )
            )
        else:
            res = await self.db.fetch("""
                SELECT * FROM jsonb_each_text(
                    (
                        SELECT %s FROM iventory WHERE ivent_id=(\'%s\')
                    )
                )
                    
            """ % (
                str(itens),
                iventoryId, )
            )

    elif opt == "remove":
        res - await self.db.fetch("""
            SELECT to_jsonb(
                SELECT %s FROM iventory WHERE ivent_id=(\'%s\')
            )
            - '%s'::jsonb
        
        """ % (str(itens), iventoryId, newValue)
        )
    elif opt == "add":
        itens = [f"{i}" for i in iventory_key]
        itensId = [i for i in newValue]
        print(itens[0])
        if itens[0] == 'Badge' or itens[0] == 'Moldura':
            if itens[0] == 'Badge':
                item_find = 'badges'
            elif itens[0] == 'Moldura':
                item_find = 'molds'
            else:
                item_find = itens[0]
            # Get banner group
            item_group = await self.db.fetch("""
                SELECT group_ FROM %s WHERE id=(\'%s\')
            """ % (f"{item_find}s" if item_find == "Banner" else item_find, itensId[0], ))
            try:
                res = await self.db.fetch("""
                    UPDATE iventory SET itens = (
                        SELECT jsonb_insert(
                            
                            itens::jsonb,
                            '{%s, %s, %s}',
                            '1',
                            true
                        )
                    ) WHERE ivent_id=('%s')

                    RETURNING itens::jsonb;
                """ % (itens[0], item_group[0][0], itensId[0], iventoryId)
                )
            except Exception as error:
                if (isinstance(error, AttributeError)):
                    res = await self.db.fetch("""
                        UPDATE iventory SET itens = (
                            SELECT jsonb_set(
                                itens::jsonb,
                                '{%s, %s, %s}'::text[],
                                (SELECT 
                                    (
                                        SELECT CAST(
                                            itens::jsonb->'%s'->'%s'->'%s' as INTEGER
                                        ) + 1 as %s_rank FROM iventory 
                                        WHERE ivent_id=('%s')
                                    )::text

                                )::jsonb
                            )
                        ) WHERE ivent_id=(
                            '%s'
                        )

                        RETURNING itens::jsonb;
                    """ % (itens[0], item_group[0][0], itensId[0],
                           itens[0], item_group[0][0], itensId[0],
                           itens[0], iventoryId, iventoryId)
                    )
                else:
                    raise error

        else:
            for i in range(len(itens)):
                try:
                    res = await self.db.fetch("""
                        UPDATE iventory SET itens = (
                            SELECT jsonb_insert(
                                itens::jsonb,
                                '{%s, ids, %s}'::text[],
                                '1'::jsonb,
                                true
                            )
                        ) WHERE ivent_id=(\'%s\')
                        
                        RETURNING itens::json->'%s'
                    """ % (str(itens[i]), itensId[i], iventoryId, str(itens[i]), )
                    )
                except Exception as error:
                    if (isinstance(error, AttributeError)):
                        res = await self.db.fetch("""
                            UPDATE iventory SET itens = (
                                SELECT jsonb_insert(
                                    itens::jsonb,
                                    '{%s, ids, %s}'::text[],
                                    (SELECT 
                                        (
                                            SELECT CAST(
                                                itens::jsonb->'%s'->'ids'->'%s' as INTEGER
                                            ) + 1 as %s_rank FROM iventory 
                                            WHERE ivent_id=('%s')
                                        )::text

                                    )::jsonb,
                                    true
                                )
                            ) WHERE ivent_id=(\'%s\')
                            
                            RETURNING itens::json->'%s'
                        """ % (str(itens[i]), itensId[i], str(itens[i]), itensId[i], str(itens[i]), iventoryId)
                        )
    return res


# FUNÇÕES DE NOVO AUTOR

async def sendEmb(user, author):
    try:
        # to author
        welcome = discord.Embed(title=f"{user.name}, meus parabéns por se tornar um autor da Kiniga!",
                                description="\n Leia as informações abaixo sobre como publicar capítulos "
                                            "no site e à quem recorrer para você não ficar perdido caso precise de ajuda.",
                                color=0x00ff33).set_author(name="Kiniga Brasil",
                                                           url='https://kiniga.com/',
                                                           icon_url='https://kiniga.com/wp-content/uploads/fbrfg/favicon-32x32.png').set_footer(text='Espero que seja muito produtivo escrevendo!')
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
                                ).set_image(url='https://media4.giphy.com/media/pURSYHBjYBEUhr04XQ/giphy.gif?cid=790b7611ecb81458c0064e87d5413028a19bfe17a95ed280&rid=giphy.gif&ct=g')
        #  novo projeto
        newProject = discord.Embed(title='Não entendeu como criar uma tag?',
                                   description='Siga o passo a passo abaixo para entender como solicitar a criação de uma tag '
                                   'para a sua história.',
                                   color=0x00ff33).set_image(url='https://media0.giphy.com/media/1IY0E9XoHQ2iJeLNwx/giphy.gif?cid=790b7611ed4435131498a759f83547158e2d9029c5e9b083&rid=giphy.gif&ct=g')

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
            c = message.embeds[0] if len(message.embeds) >= 1 else message.content
        
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
                    author = novel.find('div', attrs={'class': 'author-content'}).find_all('a', href=True)[0]  # nome do autor
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
                            emb = discord.Embed(
                                title="Ops",
                                description="Essa história Já Foi Publicada!",
                                color=0x00ff33).set_author(
                                name="Kiniga Brasil",
                                url='https://kiniga.com/',
                                icon_url='https://kiniga.com/wp-content/uploads/fbrfg/favicon-32x32.png'
                            ).set_footer(text='Qualquer coisa, marque o Shuichi! :D')

                        return emb

                    except Exception as a:

                        print(f"Ocorreu um erro no embed\n\n{a}")
                        interaction.user.send(embed = discord.Embed(
                            title=f"Erro!",
                            description="\nUm erro ocorreu devido ao seguinte problema: \n\n{}.".format(a),
                            color=0x00ff33).set_author(
                            name="Kiniga Brasil",
                            url='https://kiniga.com/',
                            icon_url='https://kiniga.com/wp-content/uploads/fbrfg/favicon-32x32.png'
                        ).set_footer(text='Qualquer coisa, marque o Shuichi! :D'))
                except Exception as i:
                    await interaction.user.send("Não foi possível prosseguir por conta do seguinte erro: \n\n"
                                                "```{}``` \n\nPor favor, fale com o Shuichi".format(i))
        except Exception as u:
            await interaction.user.send("Não foi possível prosseguir por conta do seguinte erro: \n\n"
                                        "```{}``` \n\nPor favor, fale com o Shuichi".format(u))
