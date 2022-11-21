import asyncpg
import asyncio
import json
import requests
import os
import uuid

from io import BytesIO
from lib2to3.pytree import convert
from typing import List
from PIL import Image, ImageColor, ImageDraw, ImageFilter, ImageFont, ImageOps
from base.struct import Config
from base.db.database import print_psycopg2_exception as pycopg_exception

import line_profiler

import math

# import the error handling libraries for psycopg2
from psycopg2 import OperationalError, errorcodes, errors

# import the psycopg2 library's __version__ string
from psycopg2 import __version__ as psycopg2_version

path = r'.\_temp'

isExist = os.path.exists(path)
if not isExist:
    os.mkdir(path)

pathMonserrat = "src/fonts/Montserrat/"
pathOpen = "src/fonts/Opensans/"


class Database:
    def __init__(self, loop, user: str, password: str) -> None:
        self.user = user
        self.password = password
        self.host = '127.0.0.1'
        loop.create_task(self.connect())

    async def connect(self) -> None:
        self.conn = await asyncpg.connect(user=self.user, password=self.password, host=self.host)
        try:
            await self.conn.fetch('CREATE DATABASE spinovelleveling')
        except:
            pass
        else:
            await self.conn.close()

        try:
            self.conn = await asyncpg.connect(user=self.user, password=self.password, database='spinovelleveling',
                                              host=self.host)
            await self.conn.fetch("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
        except OperationalError as err:
            # pass exception to function
            pycopg_exception(err)

            # set the connection to 'None' in case of error
            self.conn = None

        try:

            await self.conn.fetch("""
                CREATE TABLE IF NOT EXISTS public.badges
                (
                    name text COLLATE pg_catalog."default" NOT NULL,
                    img text COLLATE pg_catalog."default" NOT NULL,
                    canbuy boolean DEFAULT true,
                    value integer DEFAULT 0,
                    type text DEFAULT 'Badge',
                    id uuid DEFAULT uuid_generate_v4(),
                    unique(id)
                )
            """)
            await self.conn.fetch("""
                CREATE TABLE IF NOT EXISTS public.banners
                (
                    name text COLLATE pg_catalog."default" NOT NULL,
                    img_loja text COLLATE pg_catalog."default" NOT NULL,
                    img_perfil text COLLATE pg_catalog."default" NOT NULL,
                    canbuy boolean DEFAULT true,
                    value integer DEFAULT 0,
                    type_ text DEFAULT 'Banner',
                    id uuid DEFAULT uuid_generate_v4(),
                    unique(name),
                    unique(id)
                )
            """)
            await self.conn.fetch("""
                CREATE TABLE IF NOT EXISTS public.cars
                (
                    name text COLLATE pg_catalog."default" NOT NULL,
                    localimg text COLLATE pg_catalog."default" NOT NULL,
                    canbuy boolean DEFAULT true,
                    value integer DEFAULT 0,
                    type_ text DEFAULT 'Carro',
                    id uuid DEFAULT uuid_generate_v4(),
                    unique(name),
                    unique(id)
                )
            """)
            await self.conn.fetch("""
                CREATE TABLE IF NOT EXISTS public.molds
                (
                    id uuid DEFAULT uuid_generate_v4(),
                    name text COLLATE pg_catalog."default" NOT NULL,
                    img text COLLATE pg_catalog."default" NOT NULL,
                    imgxp text,
                    img_bdg text NOT NULL,
                    type_ text DEFAULT 'Moldura',
                    img_profile text NOT NULL,
                    value integer DEFAULT 0,
                    canbuy boolean DEFAULT True,
                    img_mold_title text,
                    lvmin int DEFAULT 0,
                    unique(name),
                    unique(id)
                )
            """)
            await self.conn.fetch("""
                CREATE TABLE IF NOT EXISTS public.titles
                (
                    id uuid DEFAULT uuid_generate_v4(),
                    name text COLLATE pg_catalog."default" NOT NULL,
                    localimg text COLLATE pg_catalog."default" NOT NULL,
                    canbuy boolean DEFAULT true,
                    type_ text DEFAULT 'Titulo',
                    value integer DEFAULT 0,
                    unique(name),
                    unique(id)
                )
            """)
            await self.conn.fetch("""
                CREATE TABLE IF NOT EXISTS public.utilizaveis
                (
                    id uuid DEFAULT uuid_generate_v4(),
                    name text NOT NULL,
                    canbuy boolean DEFAULT true,
                    value integer DEFAULT 0,
                    type_ text DEFAULT 'Utilizavel',
                    img text NOT NULL
                )
            """)
            await self.conn.fetch("""
                CREATE TABLE IF NOT EXISTS public.itens
                (
                    id SERIAL PRIMARY KEY,
                    name text COLLATE pg_catalog."default" NOT NULL,
                    type_ text COLLATE pg_catalog."default" NOT NULL,
                    value integer,
                    img text COLLATE pg_catalog."default" NOT NULL,
                    imgd text COLLATE pg_catalog."default",
                    img_profile text COLLATE pg_catalog."default",
                    lvmin integer,
                    canbuy boolean,
                    dest boolean,
                    limitedtime timestamp without time zone,
                    details CHAR,
                    item_type_id uuid DEFAULT uuid_generate_v4(),
                    CONSTRAINT unique_id UNIQUE (item_type_id)
                )
            """)
            await self.conn.fetch("""
                CREATE TABLE IF NOT EXISTS public.ranks
                (
                    lv integer NOT NULL,
                    name text COLLATE pg_catalog."default" NOT NULL,
                    r integer NOT NULL,
                    g integer NOT NULL,
                    b integer NOT NULL,
                    badges text COLLATE pg_catalog."default",
                    roleid text COLLATE pg_catalog."default",
                    imgxp text COLLATE pg_catalog."default",
                    id bigint,
                    unique(name),
                    unique(id)
                )
            """)
            await self.conn.fetch("""
                CREATE TABLE IF NOT EXISTS public.setup
                (
                    guild text COLLATE pg_catalog."default" NOT NULL,
                    message_id text COLLATE pg_catalog."default" NOT NULL,
                    role_id text COLLATE pg_catalog."default" NOT NULL,
                    owner_id integer NOT NULL,
                    unique(guild)
                )
            """)
            await self.conn.fetch("""
                CREATE TABLE IF NOT EXISTS public.shop
                (
                    id bigint,
                    name text COLLATE pg_catalog."default" NOT NULL,
                    value integer,
                    lvmin integer,
                    dest boolean,
                    limitedtime timestamp without time zone,
                    img text COLLATE pg_catalog."default",
                    details text COLLATE pg_catalog."default",
                    type_ text,
                    unique(id)
                )
            """)
            await self.conn.fetch("""
                CREATE TABLE IF NOT EXISTS public.users
                (
                    id text COLLATE pg_catalog."default" NOT NULL,
                    rank integer NOT NULL,
                    xp integer NOT NULL,
                    xptotal integer NOT NULL,
                    info text COLLATE pg_catalog."default",
                    spark integer DEFAULT 0,
                    inventory_id uuid DEFAULT uuid_generate_v4(),
                    birth text DEFAULT '???',
                    ori integer DEFAULT 0,
                    rank_id bigint,
                    user_name text NOT NULL,
                    unique(id)
                )
            """)
            await self.conn.fetch("""
                CREATE TABLE IF NOT EXISTS public.iventory
                (
                    ivent_id uuid,
                    itens jsonpath,
                    car uuid,
                    title uuid,
                    mold uuid,
                    banner uuid,
                    badge json,
                    unique(ivent_id)
                )
            """)
            # END CREATE
        except Exception as err:
            if isinstance(err, asyncpg.exceptions.PostgresSyntaxError):
                # pass exception to function
                pycopg_exception(err)
            else:
                pycopg_exception(err)

    async def fetch(self, sql: str) -> list:
        try:
            return await self.conn.fetch(sql)
        except Exception as err:
            if isinstance(err, asyncpg.exceptions.PostgresSyntaxError):
                # pass exception to function
                pycopg_exception(err)
            else:
                pycopg_exception(err)

    async def fetchList(self, sql: str) -> list:
        return '\n\n'.join([json.dumps(dict(x), ensure_ascii=False) for x in (await self.conn.fetch(sql))])


# GRANDIENT
BLACK, DARKGRAY, GRAY = ((0, 0, 0), (63, 63, 63), (127, 127, 127))
LIGHTGRAY, WHITE = ((191, 191, 191), (255, 255, 255))
BLUE, GREEN, RED = ((0, 0, 255), (0, 255, 0), (255, 0, 0))


class Point(object):
    def __init__(self, x, y):
        self.x, self.y = x, y


class Rect(object):
    def __init__(self, x1, y1, x2, y2):
        minx, maxx = (x1, x2) if x1 < x2 else (x2, x1)
        miny, maxy = (y1, y2) if y1 < y2 else (y2, y1)
        self.min = Point(minx, miny)
        self.max = Point(maxx, maxy)

    width = property(lambda self: self.max.x - self.min.x)
    height = property(lambda self: self.max.y - self.min.y)


def gradient_color(minval, maxval, val, color_palette):
    """ Computes intermediate RGB color of a value in the range of minval
        to maxval (inclusive) based on a color_palette representing the range.
    """
    max_index = len(color_palette)-1
    delta = maxval - minval
    if delta == 0:
        delta = 1
    v = float(val-minval) / delta * max_index
    i1, i2 = int(v), min(int(v)+1, max_index)
    (r1, g1, b1), (r2, g2, b2) = color_palette[i1], color_palette[i2]
    f = v - i1
    return int(r1 + f*(r2-r1)), int(g1 + f*(g2-g1)), int(b1 + f*(b2-b1))


def horz_gradient(draw, rect, color_func, color_palette):
    minval, maxval = 1, len(color_palette)
    delta = maxval - minval
    width = float(rect.width)  # Cache.
    for x in range(rect.min.x, rect.max.x+1):
        f = (x - rect.min.x) / width
        val = minval + f * delta
        color = color_func(minval, maxval, val, color_palette)
        draw.line([(x, rect.min.y), (x, rect.max.y)], fill=color)


def vert_gradient(draw, rect, color_func, color_palette):
    minval, maxval = 1, len(color_palette)
    delta = maxval - minval
    height = float(rect.height)  # Cache.
    for y in range(rect.min.y, rect.max.y+1):
        f = (y - rect.min.y) / height
        val = minval + f * delta
        color = color_func(minval, maxval, val, color_palette)
        draw.line([(rect.min.x, y), (rect.max.x, y)], fill=color)
#


class Rank:

    def __init__(self) -> None:
        # PERFIL
        self.class_font_semibold = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratSemiBold.ttf'), 36)

        self.class_font_bold_name = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratBold.ttf'), 72)

        self.class_font_bold_id = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratMedium.ttf'), 42)

        self.class_font_bold_info_sans = ImageFont.truetype(
            os.path.join(pathOpen, 'OpenSansRegular.ttf'), 36)

        self.class_font_bold_xp = ImageFont.truetype(
            os.path.join(pathOpen, 'OpenSansBold.ttf'), 48)

        self.class_font_bold_info = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratBold.ttf'), 36)

        self.class_font_montserrat = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratRegular.ttf'), 36)

        self.class_font_montserrat_bday = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratMedium.ttf'), 36)

        self.class_font_bold_ori_bday = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratBold.ttf'), 42)

        self.class_font_role = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratBold.ttf'), 30)

        self.RadiateSansBoldCondensed = ImageFont.truetype(
            os.path.join(pathOpen, 'OpenSansCondensedBold.ttf'), 65)

        # NIVEL
        # "LOJA"
        self.montserrat_extrabold_loja = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratExtraBold.ttf'), 50)

        # COINS TITLE TEXT
        self.montserrat_medium_coins = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratMedium.ttf'), 23)

        # COINS VALUE TEXT
        self.montserrat_bold_coins = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratBold.ttf'), 28)

        # Nome do item
        self.montserrat_bold_name = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratBold.ttf'), 20)

        # Tipo do item
        self.montserrat_bold_type = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratBold.ttf'), 22)

        # Valor
        self.montserrat_blackitalic_value = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratBlackItalic.ttf'), 40)

        # Categoria do item
        self.montserrat_semibold_category = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratSemiBold.ttf'), 20)

        # "Página"
        self.montserrat_semibold = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratSemiBold.ttf'), 30)

        # Número da página
        self.montserrat_extrabold_pageNumb = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratExtraBold.ttf'), 30)

        # /equipar #ID [diff]
        self.montserrat_extrabolditalic_equip = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratExtraBoldItalic.ttf'), 25)
       # antigas 
        
        self.class_font_montserrat_regular_nivel = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratRegular.ttf'), 30)
        
        self.XPRadiateSansBoldCondensed = ImageFont.truetype(
            os.path.join(pathOpen, 'RadiateSansBoldCondensed.ttf'), 85)
    def add_corners(self, im, rad):
        size = im.size
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0) + size, radius=rad, fill=255)
        im_ = im.copy()
        im_.putalpha(mask)

        output = ImageOps.fit(im_, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)

        return output

    def text_wrap(self, text, font, max_width):

        lines = []
        # If the width of the text is smaller than image width
        # we don't need to split it, just add it to the lines array
        # and return
        if font.getsize(text)[0] <= max_width:
            lines.append(text)
        else:
            # split the line by spaces to get words
            words = text.split(' ')
            i = 0
            # append every word to a line while its width is shorter than image width
            while i < len(words):
                line = ''
                while i < len(words) and font.getsize(line + words[i])[0] <= max_width:
                    line = line + words[i] + " "
                    i += 1
                if not line:
                    line = words[i]
                    i += 1
                # when the line gets longer than the max width do not append the word,
                # add the line to the lines array
                lines.append(line)
        return lines

    #   Gradiente
    def gradient(self, img_baixo, img_cima, colors, gradient=1.2, initial_opacity=1):
        #input_im = Image.open(src)
        if img_cima == None:

            bg_draw = ImageDraw.Draw(img_baixo)
            bg_draw.ellipse(
                (-600, int(650/2 - 20), int(1280 + 600), int(1280/1.5 - 150)), fill=colors[1])
            bg_draw.rounded_rectangle(
                (-70, 0, int(1280 + 70), int(1280/2 + 40)), 0, fill=colors[0])
            bg_draw.rounded_rectangle(
                (-70, int(650/1.5 - 20), int(1280 + 70), int(1280/2 + 40)), 700, fill=colors[1])
            bg_draw.rounded_rectangle(
                (-5, int(650/2 - 20), int(1280 + 5), int(1280/2)), 35, fill=colors[1])
            return img_baixo

        #input_im = Image.new(mode="RGB", size=bg.size, color=colors[0])

        input_im = img_cima.size

        input_im = Image.new(mode="RGB", size=(input_im), color=(0, 45, 62))

        mask = Image.new('L', (img_cima.size))
        bg_draw = ImageDraw.Draw(mask)
        bg_draw.ellipse((-600, int(650/2 - 20), int(1280 + 600),
                        int(1280/1.5 - 150)), fill=("white"))
        bg_draw.rounded_rectangle(
            (-70, 0, int(1280 + 70), int(1280/2 + 40)), 0, fill=("black"))
        bg_draw.rounded_rectangle(
            (-70, int(650/1.5 - 20), int(1280 + 70), int(1280/2 + 40)), 700, fill=("white"))
        bg_draw.rounded_rectangle(
            (-5, int(650/2 - 20), int(1280 + 5), int(1280/2)), 35, fill=("white"))

        gradient = 1
        initial_opacity = 2

        if input_im.mode != 'RGBA':
            input_im = input_im.convert('RGBA')
        width, height = input_im.size

        alpha_gradient = Image.new('L', (1, height), color=0xFF)
        for x in range(height):
            a = int((initial_opacity * 255.) *
                    (1. - gradient * float(x)/height))

            if a > 0:
                alpha_gradient.putpixel((0, -x), a)
            else:
                alpha_gradient.putpixel((0, -x), 0)
        alpha = alpha_gradient.resize(input_im.size)
        alpha.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

        black_im = Image.new('RGBA', (width, height), color=0)
        black_im = black_im.resize(input_im.size)
        black_im.putalpha(alpha)
        img_cima.paste(img_baixo, (0, int(650/2 - 20)))

        output = Image.composite(input_im, img_cima, black_im)

        # make composite with original image

        return output

    def draw_mask(self, banner):
        bg = Image.new('RGBA', (1280, 1280), (0, 33, 46, 255))

        banner_bg = banner

        bg_copy = Image.new('RGBA', (1280, 1280), (0, 45, 62, 255))

        banner_bg_cima = banner_bg.crop(
            (0, 0, 1280, int(banner_bg.size[1]/2)))

        banner_bg_baixo = banner_bg.crop(
            (0, int(banner_bg.size[1]/2 - 20), 1280, 1280))
        banner_bg_baixo = banner_bg_baixo.filter(
            ImageFilter.GaussianBlur(radius=10))

        bg.paste(banner_bg_cima, (0, 0), banner_bg_cima)
        #bg_copy.paste(banner_bg_baixo, (0, int(650/2 - 20)))

        mask = Image.new('L', (bg.size))

        image = self.gradient(img_baixo=mask, img_cima=None,
                              colors=[("black"), ("white")])

        back = Image.composite(bg_copy, bg, image)
        #bg.paste(image, (0, int(650/2 - 20)), image)

        image2 = self.gradient(img_baixo=banner_bg_baixo, img_cima=bg,
                               colors=[None])

        bg = Image.composite(image2, back, image)

        # bg_cima = self.gradient(
        #    img_baixo=banner_bg_baixo, img_cima=banner_bg_cima, colors=[(0, 45, 62)])

        #bg = Image.composite(banner_bg_baixo, image2, image)

        #bg = Image.composite(image2, bg, image)

        return bg

    def draw(self, user: str, userRank: str, userXp: str, titleImg: str,
             moldName: str, moldImage: str, moldRounded: str, userInfo: str,
             userSpark: int, userBirth: str, staff: None, rankName, rankR: str,
             rankG: str, rankB: str, rankImgxp, profile_bytes: BytesIO
             ) -> BytesIO:

        profile_bytes = Image.open(profile_bytes)

        if profile_bytes.mode != 'RGBA':
            profile_bytes = profile_bytes.convert('RGBA')

        profile_bytes_imenso = profile_bytes.copy()

        # if moldImg == None:
        profile_bytes = profile_bytes.resize((269, 269))
        prof_elipse = 92

        # else:
        #    profile_bytes = profile_bytes.resize((209, 209))
        #    prof_elipse = 130

        bigsize = (profile_bytes.size[0] * 3, profile_bytes.size[1] * 3)

        mask = Image.new('L', bigsize, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(profile_bytes.size, Image.ANTIALIAS)
        profile_bytes.putalpha(mask)

        output = ImageOps.fit(profile_bytes, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)

        bg = Image.new('RGBA', (1280, 1280), (0, 45, 62, 255))
        bg_draw = ImageDraw.Draw(bg)

        profile_bytes_imenso = profile_bytes_imenso.resize((1280, 1280))
        profile_bytes_imenso = profile_bytes_imenso.crop(
            (0, 420, 1280, 1280 + 420))
        mask = Image.new("L", (profile_bytes_imenso.size), 90)

        profileFundo = Image.composite(profile_bytes_imenso, bg, mask)
        profileBlur = profileFundo.filter(ImageFilter.GaussianBlur(radius=30))
        bg.paste(profileBlur, (0, 0))

        # user
        bg_draw.rounded_rectangle(
            (25, 27, 420 + 25, 625 + 27), 50, fill=(0, 45, 62))

        splitUsername = user.split('#')
        username = splitUsername[0]
        string_encode = username.encode("ascii", "ignore")
        username = string_encode.decode()
        userid = (f"#{splitUsername[ 1 ]}")
        bg_draw.text((488, 32), username, font=self.class_font_bold_name, fill=(
            219, 239, 255), spacing=5)
        bg_draw.text((488, 104), userid, font=self.class_font_bold_id,
                     fill=(175, 191, 204), spacing=5)

        user_border = (profile_bytes.size[0] +
                       prof_elipse + 15, profile_bytes.size[1] + 185 + 15)

        rolePosition = 488
        spacing = 10
        role_top = 168
        if rankName == None:
            rank_text = "Novato"
            cor = (167, 141, 116)
        else:
            rank_text = rankName.upper()
            cor = (int(rankR), int(rankG), int(rankB))
        if staff:
            staff.reverse()
            # classe
            bg_draw.ellipse([prof_elipse, 185, user_border],
                            fill=(list(staff[0].values())[0]['color']))

            bg_draw.rounded_rectangle(
                [(54, 548), (418, 625)], 37, fill=(list(staff[0].values())[0]['color']))
            count = 0
            while count <= len(staff) - 1 and count <= 2:
                list_roles = list(staff[count].values())

                # info
                largText, altText = self.class_font_role.getsize(
                    list_roles[0]['name'])
                if rolePosition + largText + 22 > 1280:
                    role_top = 230
                    rolePosition = 488

                bg_draw.rounded_rectangle(
                    [(rolePosition - 5 if rolePosition == 488 else rolePosition + spacing, role_top - 5),
                     (rolePosition + largText + 22 + 5 if rolePosition == 488 else rolePosition + largText + 22 +
                     spacing, role_top + 44 + 5)], 28,
                    fill=(list_roles[0]['color']),
                    width=3)
                bg_draw.text((
                    rolePosition + largText + 12 if rolePosition == 488 else rolePosition +
                    largText + 12 + spacing,
                    role_top + 32), list_roles[0]['name'],
                    font=self.class_font_role,
                    fill=(
                    0, 45, 62), anchor="rs", spacing=5)

                rolePosition = rolePosition + largText + 32
                count += 1

        else:

            # info
            largText, altText = self.class_font_role.getsize("Membro")
            bg_draw.rounded_rectangle(
                [(rolePosition, 168), (rolePosition + largText + 22, 224)], 28, fill=(133, 133, 133), width=3)
            bg_draw.text((rolePosition + largText + 12, 206), "Membro", font=self.class_font_role, fill=(
                0, 45, 62), anchor="rs", spacing=5)

            rolePosition = rolePosition + 166

            # classe
            # r, g, b = bytes.fromhex(color[1:])
            # bg_draw.ellipse([prof_elipse, 185, user_border], fill=f"rgb({r}, {g}, {b})")
            if moldImage != None:
                border_im = Image.open(r"{}".format(moldImage))
                # border_im = border_im.resize((profile_bytes.size[0] +
                #       prof_elipse+15, profile_bytes.size[1]+prof_elipse+15), Image.NEAREST)
                # border_im = border_im.resize((profile_bytes.size[0],  profile_bytes.size[1]), Image.NEAREST)
                # print(profile_bytes.size[0],  profile_bytes.size[1])
                rank_rounded = Image.open(r"{}".format(moldRounded))
                bg.paste(rank_rounded, (54, 548), rank_rounded)

            elif moldImage == None:
                bg_draw.ellipse([prof_elipse, 185, user_border],
                                fill=(cor))
                bg_draw.rounded_rectangle(
                    [(54, 548), (418, 625)], 37, fill=(cor))

        if titleImg != None:
            title_img = Image.open(r"{}".format(titleImg))
            title_img = title_img.resize((340, 70), Image.NEAREST)
            tsize = (title_img.size[0], title_img.size[1]+5)
            bg.paste(
                title_img, (int((420 - tsize[0]) / 2) + 25, 70), title_img)

        if moldName != None:
            rank_text = moldName.upper()
            bg_draw.text((235, 603), rank_text, font=self.class_font_barlow_bold, fill=(
                0, 28, 38), anchor="ms", spacing=5)
        else:

            bg_draw.text((235, 603), rank_text, font=self.class_font_barlow_bold, fill=(
                0, 28, 38), anchor="ms", spacing=5)

        # info
        bg_draw.rounded_rectangle(
            [(488, 250), (488 + 764, 262 + 230)], 25, fill=(0, 45, 62))
        bg_draw.text((516, 270), 'Biografia:', font=self.class_font_montserrat, fill=(
            161, 177, 191), spacing=5)

        if not userInfo:
            userInfo = "Não há o que bisbilhotar aqui."

        lines = self.text_wrap(userInfo, self.class_font_bold_info_sans, 600)
        line_height = self.class_font_bold_info.getsize(userInfo)[1]
        x = 516
        y = 330

        for line in lines:
            # draw the line on the image
            bg_draw.text((x, y), line, font=self.class_font_bold_info,
                         fill=(219, 239, 255), spacing=5)
            # update the y position so that we can use it for next line
            y = y + line_height + 15

        # ori
        bg_draw.rounded_rectangle(
            [(488, 530), (488 + 407, 490 + 162)], 25, fill=(0, 45, 62))  # ori

        ori = Image.open("src\imgs\extra\ori.png")
        ori = ori.resize((95, 95), Image.NEAREST)
        bg.paste(ori, (510, 548), ori)
        value = f"{int(userSpark):,}".replace(",", ".")
        bg_draw.text((620, 548), "Oris",
                     font=self.class_font_montserrat, fill=(212, 255, 236))
        bg_draw.text((620, 583), value,
                     font=self.class_font_bold_ori_bday, fill=(0, 247, 132))

        # Bday
        bg_draw.rounded_rectangle(
            [(913, 530), (913 + 339, 490 + 162)], 25, fill=(0, 45, 62))  # Bday

        if userBirth != "???":
            userBirth = userBirth.split("/")
            dia = userBirth[0]
            mes = userBirth[1]
            userBirth = f"{dia}/{mes}"
        else:
            userBirth = "??/??"

        cake = Image.open("src\imgs\extra\cake.png")
        cake = cake.resize((62, 84), Image.NEAREST)
        bg.paste(cake, (934, 548), cake)
        value = f"{int(userSpark):,}".replace(",", ".")
        bg_draw.text((1015, 548), "Aniversário",
                     font=self.class_font_montserrat, fill=(255, 212, 216))
        bg_draw.text((1015, 583), userBirth,
                     font=self.class_font_bold_ori_bday, fill=(214, 83, 96))

        # xp_text = f'Faltam {} para chegar ao Nível {}:'.format(xp_remain, at_rank-1)

        bg_draw.rounded_rectangle(
            [(190, 699), (1089, 728)], 15, fill=(0, 45, 62))

        # xp_in = self.gradientLeft()
        # xp_im = Image.open(r"src/bg/xpFill-background.png")
        # im1 = xp_im.crop((0, 0, ((int(xp/needed_xp*100))*6), 81))
        # bg.paste(im1, (488, 558), im1)
        #
        # bg_draw.text((515, 503), xp_text, font=self.class_font_semibold, fill=(161, 177, 191))
        # bg_draw.text((870, 618), f"{xp}/{needed_xp}", font=self.class_font_bold_xp, anchor="ms", fill=(219, 239, 255))

        needed_xp = self.neededxp(userRank)

        # Pré
        bg_draw.text((80, 723), "NÍVEL ",
                     font=self.class_font_montserrat_regular_nivel, anchor="ms", fill=(219, 239, 255))
        bg_draw.text((150, 723), f"{userRank}",
                     font=self.class_font_role, anchor="ms", fill=(219, 239, 255))

        # Middle
        bg_draw.text((640, 785),
                     f"Faltam {int(needed_xp - userXp):,} de XP para chegar ao Nível {userRank + 1}".replace(
                         ",", "."),
                     font=self.class_font_role, anchor="ms", fill=(219, 239, 255))

        # Pós
        bg_draw.text((1089 + 70, 723), "NÍVEL ",
                     font=self.class_font_montserrat_regular_nivel, anchor="ms", fill=(219, 239, 255))
        bg_draw.text((1089 + 140, 723), f"{userRank + 1}",
                     font=self.class_font_role, anchor="ms", fill=(219, 239, 255))

        # img user

        bg.paste(output, (100, 193), output)

        if moldImage is None:
            bg_draw.rounded_rectangle((190, 698, 190 + ((int(userXp / needed_xp * 100)) * 6), 698 + 30), fill=(cor),
                                      radius=25)
            # bg_draw.rounded_rectangle((190, 698, 190, 698+148), fill=(0, 45, 62))
        else:

            xp_im = Image.open(rf"{rankImgxp}")
            im1 = xp_im.crop((0, 0, ((int(userXp / needed_xp * 100)) * 6), 80))
            bg.paste(im1, (190, 698), im1)

        if staff:
            pass
        else:
            if moldImage is not None:
                moldImage = Image.open(moldImage)
                bsize = (moldImage.size[0], moldImage.size[1])
                bg.paste(
                    moldImage, (int((478 - bsize[0]) / 2), 100), moldImage)
                # bg.paste(moldImg, (105, 189), moldImg)
            else:
                pass

        mask = Image.open(
            "src/imgs/extra/perfil/Discord-Border.png").convert("L")
        color_palette = [(186, 162, 125), (189, 142, 71)]
        region = Rect(0, 0, mask.size[0], mask.size[1])
        width, height = region.max.x+1, region.max.y+1
        image = Image.new("RGB", (width, height), WHITE)
        draw = ImageDraw.Draw(image)
        horz_gradient(draw, region, gradient_color, color_palette)
        image = image.resize(mask.size, Image.NEAREST).convert("RGBA")
        bg = Image.composite(image, bg, mask)
        #bg.paste(image, (0, 0))
        #bg.paste(gradient, (0, 0), gradient)

        buffer = BytesIO()
        bg.save(buffer, 'png')
        buffer.seek(0)

        mask.close()
        bg.close()

        return buffer

    def draw_new(self, user: str, badge_images, banner: str,
                 moldImage: str, userInfo: str,
                 userSpark: int, userOri: int, userBirth: str, staff: None, rankName, rankR: str,
                 rankG: str, rankB: str, profile_bytes: BytesIO
                 ) -> BytesIO:

        profile_bytes = Image.open(profile_bytes)

        if profile_bytes.mode != 'RGBA':
            profile_bytes = profile_bytes.convert('RGBA')

        banner = Image.open(banner).convert("RGBA")

        # if moldImg == None:
        profile_bytes = profile_bytes.resize((269, 269))
        prof_elipse = 91

        # else:
        #    profile_bytes = profile_bytes.resize((209, 209))
        #    prof_elipse = 130

        bigsize = (profile_bytes.size[0] * 3, profile_bytes.size[1] * 3)

        mask = Image.new('L', bigsize, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(profile_bytes.size, Image.Resampling.LANCZOS)
        profile_bytes.putalpha(mask)

        output = ImageOps.fit(profile_bytes, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)

        bg = self.draw_mask(banner)

        bg_draw = ImageDraw.Draw(bg)

        #banner = banner.resize((1280, 1280))
        # banner = banner.crop(
        #    (0, 420, 1280, 1280 + 420))
        mask = Image.new("L", (bg.size), 90)

    # BORDA DO CARALHO
        ma = Image.open(
            "src/imgs/extra/perfil/Discord-Border.png").convert("L")

        mask = Image.new("L", (1280, 1280))
        mask.paste(ma, (0, int(banner.size[1]/2 - 20)))
        color_palette = [(186, 162, 125), (189, 142, 71)]
        region = Rect(0, 0, mask.size[0], mask.size[1])
        width, height = region.max.x+1, region.max.y+1
        image = Image.new("RGB", (width, height), WHITE)
        draw = ImageDraw.Draw(image)
        horz_gradient(draw, region, gradient_color, color_palette)
        image = image.resize(
            mask.size, Image.Resampling.NEAREST).convert("RGBA")
        image = Image.composite(image, bg, mask)
        bg.paste(image, (0, 0))

        # user
        # bg_draw.rounded_rectangle(
        #    (25, 27, 420 + 25, 625 + 27), 50, fill=(0, 45, 62))
        splitUsername = user.split('#')
        username = splitUsername[0]
        string_encode = username.encode("ascii", "ignore")
        username = string_encode.decode()
        userid = (f"#{splitUsername[ 1 ]}")

        bg_draw.text((105, 603), username, font=self.class_font_bold_name,
                     fill=(219, 239, 255), anchor="ls", spacing=5)
        bg_draw.text((105, 653), userid, font=self.class_font_bold_id,
                     fill=(175, 191, 204), anchor="ls", spacing=5)

        user_border = (profile_bytes.size[0] +
                       prof_elipse + 12, profile_bytes.size[1] + 185 + 12)

        rolePosition = 870
        spacing = 10
        role_top = 513
        if rankName == None:
            rank_text = "Novato"
            cor = (167, 141, 116)
        else:
            rank_text = rankName.upper()
            cor = (int(rankR), int(rankG), int(rankB))
        if staff:
            staff.reverse()
            # classe
            bg_draw.ellipse([prof_elipse, 188, user_border],
                            fill=(list(staff[0].values())[0]['color']))

            count = 0
            while count <= len(staff) - 1 and count <= 2:
                list_roles = list(staff[count].values())

                # info
                largText, altText = self.class_font_role.getsize(
                    list_roles[0]['name'])
                if rolePosition + largText + 22 > 1280:
                    role_top = 575
                    rolePosition = 870

                bg_draw.rounded_rectangle(
                    [(rolePosition if rolePosition == 870 else rolePosition + spacing + 50, role_top - int(spacing+15)),
                        (rolePosition + int(largText + 60) + spacing if rolePosition == 870 else rolePosition + int(largText + 60) +
                         spacing + 50, role_top + int(spacing+15))], 28,
                    fill=(list_roles[0]['color']), width=3)
                bg_draw.text((
                    rolePosition + largText + 33 if rolePosition == 870 else rolePosition + largText + 33 + spacing + 50, role_top + spacing),
                    list_roles[0]['name'], font=self.class_font_role, fill=(0, 45, 62), anchor="rs", spacing=5)

                rolePosition = rolePosition + largText + 32
                count += 1
        else:
            largText, altText = self.class_font_role.getsize("Membro")
            bg_draw.rounded_rectangle(
                [(rolePosition, 488), (rolePosition + largText + 22, 513+25)], 28, fill=(133, 133, 133), width=3)
            bg_draw.text((rolePosition + largText + 15, 525), "Membro", font=self.class_font_role, fill=(
                0, 45, 62), anchor="rs", spacing=5)

            rolePosition = rolePosition + 166

            if moldImage == None:
                bg_draw.ellipse([prof_elipse, 188, user_border],
                                fill=(cor))

    # BADGES
        if len(badge_images) > 0:
            count = 0
            inic_larg = int(banner.size[0] - 150)
            inic_alt = int(banner.size[1]/2)

            for badge in badge_images:
                badge = Image.open(badge)
                badge = badge.resize(
                    (int(badge.size[0]/4), int(badge.size[1]/4)), Image.Resampling.NEAREST)
                bg.paste(badge, (inic_larg, inic_alt), badge)
                inic_larg -= (badge.size[0] + 10)

        # img user
        bg.paste(output, (97, 193), output)

        # info
        bg_draw.rounded_rectangle(
            [(480, int(1280-524)), (480 + 764, int(1280-215))], 25, fill=(0, 45, 62))
        bg_draw.text((516, 776), 'Biografia:', font=self.class_font_montserrat_bday, fill=(
            161, 177, 191), spacing=5)

        if not userInfo:
            userInfo = "Não há o que bisbilhotar aqui."

        lines = self.text_wrap(userInfo, self.class_font_bold_info_sans, 600)
        line_height = self.class_font_bold_info.getsize(userInfo)[1]
        x = 516
        y = 820

        for line in lines:
            # draw the line on the image
            bg_draw.text((x, y), line, font=self.class_font_bold_info,
                         fill=(219, 239, 255), spacing=5)
            # update the y position so that we can use it for next line
            y = y + line_height + 15

    # spark
        bg_draw.rounded_rectangle(
            [(35, int(1280-524)), (int(1280-840), int(1280-387))], 25, fill=(0, 45, 62))  # spark

        spark = Image.open("src\imgs\extra\spark.png")
        spark = spark.resize((110, 110), Image.Resampling.NEAREST)
        bg.paste(spark, (45, int(1280-504)), spark)
        value = f"{int(userSpark):,}".replace(",", ".")
        bg_draw.text((170, int(1280-508)), "Sparks",
                     font=self.class_font_montserrat_bday, fill=(153, 177, 191))
        bg_draw.text((170, int(1280-458)), value,
                     font=self.class_font_bold_ori_bday, fill=(219, 239, 255))

    # ori
        bg_draw.rounded_rectangle(
            [(35, int(1280-352)), (int(1280-840), int(1280-215))], 25, fill=(0, 53, 49))  # ori

        ori = Image.open("src\imgs\extra\ori.png")
        ori = ori.resize((100, 100), Image.Resampling.NEAREST)
        bg.paste(ori, (50, int(1280-330)), ori)
        value = f"{int(userOri):,}".replace(",", ".")
        bg_draw.text((170, int(1280-335)), "Oris",
                     font=self.class_font_montserrat_bday, fill=(212, 255, 236))
        bg_draw.text((170, int(1280-285)), value,
                     font=self.class_font_bold_ori_bday, fill=(0, 247, 132))

    # Bday
        bg_draw.rounded_rectangle(
            [(35, int(1280-178)), (int(1280-840), int(1280-40))], 25, fill=(54, 46, 59))  # Bday

        if userBirth != "???":
            userBirth = userBirth.split("/")
            dia = userBirth[0]
            mes = userBirth[1]
            userBirth = f"{dia}/{mes}"
        else:
            userBirth = "??/??"

        # image
        cake = Image.open("src\imgs\extra\cake.png")
        cake = cake.resize((70, 92), Image.Resampling.NEAREST)
        bg.paste(cake, (65, int(1280-155)), cake)

        # text
        value = f"{int(userSpark):,}".replace(",", ".")
        bg_draw.text((170, int(1280-165)), "Aniversário",
                     font=self.class_font_montserrat_bday, fill=(255, 212, 216))
        bg_draw.text((int(170), int(1280-110)), userBirth,
                     font=self.class_font_bold_ori_bday, fill=(214, 83, 96))

    # CARS
        cars_position = 525
        car_border = (187, 165, 16)
        cars_bg = [(37, 62, 52)]
        for i in range(4):
            if i >= 1:
                car_border = (0, 33, 46, 255)
                cars_bg = [(0, 38, 53)]

            bg_draw.rounded_rectangle(
                [(cars_position, int(1280-178)),
                 (cars_position + 140, int(1280-40))],
                radius=30, fill=cars_bg[0], outline=(car_border), width=2)

            bg_draw.text((cars_position+70, int(1280-185) + 120), "?",
                         font=self.class_font_bold_name, anchor="md", fill=(0, 45, 62))
            cars_position += 180

        # xp_text = f'Faltam {} para chegar ao Nível {}:'.format(xp_remain, at_rank-1)

        # xp_in = self.gradientLeft()
        # xp_im = Image.open(r"src/bg/xpFill-background.png")
        # im1 = xp_im.crop((0, 0, ((int(xp/needed_xp*100))*6), 81))
        # bg.paste(im1, (488, 558), im1)
        #
        # bg_draw.text((515, 503), xp_text, font=self.class_font_semibold, fill=(161, 177, 191))
        # bg_draw.text((870, 618), f"{xp}/{needed_xp}", font=self.class_font_bold_xp, anchor="ms", fill=(219, 239, 255))

        if staff != None:
            pass
        else:
            if moldImage is not None:
                moldImage = Image.open(moldImage)
                bsize = (moldImage.size[0], moldImage.size[1])
                bg.paste(
                    moldImage, (int((478 - bsize[0]) / 2), 100), moldImage)
                # bg.paste(moldImg, (105, 189), moldImg)
            else:
                pass

        #bg.paste(image, (0, 0))
        #bg.paste(gradient, (0, 0), gradient)
        # bg.show()
        buffer = BytesIO()
        bg.save(buffer, 'png')
        buffer.seek(0)

        mask.close()
        bg.close()

        return buffer

    def rank(self, rank: str, xp: str, xptotal: str,
             moldName: str, moldImg: str, imgxp: str,
             profile_bytes) -> BytesIO:
        profile_bytes = Image.open(str(profile_bytes))
        profile_bytes_imenso = profile_bytes.copy()

        # profile_bytes = profile_bytes.resize((1270, 1270))

        bigsize = (profile_bytes.size[0] * 3, profile_bytes.size[1] * 3)
        mask = Image.new('L', bigsize, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(profile_bytes.size, Image.ANTIALIAS)
        profile_bytes.putalpha(mask)

        output = ImageOps.fit(profile_bytes, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)

        bg = Image.new('RGBA', (1270, 892), (0, 45, 62, 255))
        bg_draw = ImageDraw.Draw(bg)

        profile_bytes_imenso = profile_bytes_imenso.resize((1270, 892))
        # profile_bytes_imenso = profile_bytes_imenso.crop(
        #    (0, 420, 1280, 823+420))
        mask = Image.new("L", (profile_bytes_imenso.size), 90)

        profileFundo = Image.composite(profile_bytes_imenso, bg, mask)
        profileBlur = profileFundo.filter(ImageFilter.GaussianBlur(radius=30))
        bg.paste(profileBlur, (0, 0))

        # xp_text = f'Faltam {} para chegar ao Nível {}:'.format(xp_remain, at_rank-1)

        bg_draw.rounded_rectangle(
            [(190, 768), (1089, 768 + 28)], 15, fill=(0, 45, 62))

        # xp_in = self.gradientLeft()
        # xp_im = Image.open(r"src/bg/xpFill-background.png")
        # im1 = xp_im.crop((0, 0, ((int(xp/needed_xp*100))*6), 81))
        # bg.paste(im1, (488, 558), im1)
        #
        # bg_draw.text((515, 503), xp_text, font=self.class_font_semibold, fill=(161, 177, 191))
        # bg_draw.text((870, 618), f"{xp}/{needed_xp}", font=self.class_font_bold_xp, anchor="ms", fill=(219, 239, 255))

        needed_xp = self.neededxp(rank)

        # Pré
        bg_draw.text((80, 797), "NÍVEL ",
                     font=self.class_font_montserrat_regular_nivel, anchor="ms", fill=(219, 239, 255))
        bg_draw.text((150, 797), f"{rank}",
                     font=self.class_font_role, anchor="ms", fill=(219, 239, 255))

        # Middle
        bg_draw.text((640, 855),
                     f"Faltam {int(needed_xp - xp):,} de XP para chegar ao Nível {rank + 1}".replace(
                         ",", "."),
                     font=self.class_font_role, anchor="ms", fill=(219, 239, 255))

        # Pós
        bg_draw.text((1089 + 70, 797), "NÍVEL ",
                     font=self.class_font_montserrat_regular_nivel, anchor="ms", fill=(219, 239, 255))
        bg_draw.text((1089 + 140, 797), f"{rank + 1}",
                     font=self.class_font_role, anchor="ms", fill=(219, 239, 255))

        xp_im = Image.open(rf"{imgxp}")
        im1 = xp_im.crop((0, 0, ((int(xp / needed_xp * 100)) * 6), 81))
        bg.paste(im1, (190, 767), im1)

        color = xp_im.getpixel(((xp_im.size[0]) - 5, 7))

        if moldName != None:
            rank_text = moldName.upper()
            bg_draw.text((635, 622), rank_text, font=self.RadiateSansBoldCondensed, fill=(
                color), anchor="ms", spacing=5)

        bg_draw.text((695, 730), f"{int(xptotal):,}".replace(",", "."),
                     font=self.XPRadiateSansBoldCondensed, anchor="rs", fill=(219, 239, 255))
        bg_draw.text((705, 730), "XP TOTAL",
                     font=self.class_font_montserrat_regular_nivel, anchor="ls", fill=(219, 239, 255))

        border_im = Image.open(r"{}".format(moldImg))
        bsize = (border_im.size[0], border_im.size[1])
        bg.paste(
            border_im, (int((1270 - bsize[0]) / 2) + 2, (int((892 - bsize[1]) / 2) - 150)), border_im)

        buffer = BytesIO()
        bg.save(buffer, 'png')
        buffer.seek(0)

        mask.close()
        bg.close()

        return buffer

    def drawiventory(self, banner, spark, ori, items, total) -> BytesIO:

        # STATIC IMAGES
        spark_img = Image.open("src/imgs/extra/Spark.png")
        ori_img = Image.open("src/imgs/extra/Ori.png")

        icon = Image.open(
            "src/imgs/extra/inventario/Inventory-Icon-Spinovel.png")

        # ITEM CATEGORIE IMAGES
        comumCat_image = Image.open(
            "src/imgs/extra/inventario/Loja-Comum.png")
        raroCat_image = Image.open(
            "src/imgs/extra/inventario/Loja-Raro.png")
        lendCat_image = Image.open(
            "src/imgs/extra/inventario/Loja-Lendario.png")

        total_page = total/6 if total/6 == int() else int(total/6+0.5)

        images = []
        count = 0
        for i in range(total_page):

            plain = Image.new('RGBA', (1280, 1280), (0, 45, 62, 255))
            banner = Image.open(banner)

            banner_Big = banner.resize((1280+630, 650+630))
            banner_Big = banner_Big.crop((300, 0, 1580, 1280))
            mask = Image.new("L", banner_Big.size, 90)

            bannerFundo = Image.composite(banner_Big, plain, mask)
            bannerBlur = bannerFundo.filter(
                ImageFilter.GaussianBlur(radius=10))

            plain.paste(bannerBlur, (0, 0))
            bg_draw = ImageDraw.Draw(plain)

        # SHOPING TITLE
            plain.paste(icon, (45, 80), icon)
            bg_draw.text((115, 75), "INVENTÁRIO", font=self.montserrat_extrabold_loja,
                         anchor="la", fill=(219, 239, 255))

        # SHOPING COINS

            # SPARK AREA
            bg_draw.rounded_rectangle(
                [(695, 50), (959, 140)], 22, fill=(0, 45, 62))

            bg_draw.text((770, 60), "Sparks",
                         font=self.montserrat_medium_coins, fill=(153, 177, 191))

            spark_value = f"{int(spark):,}".replace(",", ".")
            bg_draw.text((770, 90), spark_value,
                         font=self.montserrat_bold_coins, fill=(219, 239, 255))

            # ORI AREA
            bg_draw.rounded_rectangle(
                [(985, 50), (1249, 140)], 22, fill=(0, 53, 49))

            bg_draw.text((1065, 60), "Oris",
                         font=self.montserrat_medium_coins, fill=(203, 246, 228))

            ori_value = f"{int(ori):,}".replace(",", ".")

            bg_draw.text((1065, 90), ori_value,
                         font=self.montserrat_bold_coins, fill=(0, 247, 132))

            # IMAGES
            spark_img = spark_img.resize((70, 80), Image.Resampling.NEAREST)
            plain.paste(spark_img, (700, 55), spark_img)

            ori_img = ori_img.resize((67, 67), Image.Resampling.NEAREST)
            plain.paste(ori_img, (993, 58), ori_img)

        # FOOTER
            # PAGE AREA
            bg_draw.text((630, 1240), "Página",
                         font=self.montserrat_semibold, anchor="md", fill=(0, 247, 132))

            bg_draw.text((700, 1240), "%s" % (i+1, ),
                         font=self.montserrat_extrabold_pageNumb, anchor="md", fill=(0, 247, 132))

        # PAGE CREATE LOOP
            ccount = 0
            tcount = 1
            try:
                largura = 0
                altura = 195
                for t in range(12):
                    if count >= total:
                        break
                    list_itens = list(items[count].values())
                    #print (list_itens)

                    if str(list_itens[0]['type']) == "Banner":
                        itemImg = Image.open(
                            list_itens[0]['img']).convert("RGBA")
                        itemImg = itemImg.resize(
                            (235, 105), Image.Resampling.NEAREST)
                        itemImg = self.add_corners(itemImg, 20)

                    elif str(list_itens[0]['type']) == "Utilizavel":
                        itemImg = Image.open(
                            list_itens[0]['img']).convert("RGBA")
                        itemImg = itemImg.resize(
                            (128, 128), Image.Resampling.NEAREST)

                    elif str(list_itens[0]['type']) == "Badge":
                        itemImg = Image.open(
                            list_itens[0]['img']).convert("RGBA")
                        itemImg = itemImg.resize(
                            (int(itemImg.size[0]/2.5), int(itemImg.size[1]/2.5)), Image.Resampling.NEAREST)
                    elif str(list_itens[0]['type']) == "Titulo":
                        itemImg = Image.open(
                            list_itens[0]['img']).convert("RGBA")

                    else:
                        itemImg = Image.open(
                            list_itens[0]['img']).convert("RGBA")
                        lar = (itemImg.size[0], itemImg.size[1])

                        itemImg = itemImg.resize(
                            (int(itemImg.size[0]/2.5), int(itemImg.size[1]/2.5)), Image.Resampling.NEAREST)

                    if list_itens[0]['category'] == "Comum":
                        img = comumCat_image
                    elif list_itens[0]['category'] == "Raro":
                        img = raroCat_image
                    elif list_itens[0]['category'] == "Lendário":
                        img = lendCat_image
                    else:
                        img = comumCat_image

                    lar = (itemImg.size[0], itemImg.size[1])

                    # print(list_itens)

                    if largura > 1200:
                        ccount = 0
                        tcount += 1
                        altura = int((img.size[0] - 18) * tcount)

                    largura = ((img.size[0] + 35) * ccount) + \
                        (35 if ccount == 0 else 35)

                    if altura > 1280:
                        break

                    largura = ((img.size[0] + 35) * ccount) + \
                        (35 if ccount == 0 else 35)

                # ROW BACKGROUND IMAGE 1
                    plain.paste(img, (largura, altura), img)

                    # ROW ITEM IMAGE 1
                    plain.paste(
                        itemImg, (int(largura + int((img.size[0] - lar[0])/2)),
                                  int(altura + int((img.size[1] - lar[1])/2)) - 40), itemImg)
                # TEXTS
                    # ITEM TYPE
                    bg_draw.text((90 + largura, altura),
                                 list_itens[0]['type'], fill=(0, 45, 62), anchor="ma", font=self.montserrat_bold_type)

                    # ITEM NAME
                    bg_draw.text((int(largura + int((img.size[0]/2))),
                                  int(altura + int((img.size[1]/2))) + 50),
                                 list_itens[0]['name'], fill=(215, 235, 251), anchor="ma",
                                 font=self.montserrat_bold_name)

                    # ITEM EQUIP
                    bg_draw.text((int(largura + int((img.size[0]/2))),
                                  int(altura + int((img.size[1]/2))) + 103),
                                 "/equipar %s" % (list_itens[0]['id'], ), fill=(0, 45, 62), anchor="ma",
                                 font=self.montserrat_extrabolditalic_equip)

                    ccount += 1
                    count += 1
            except Exception as a:
                raise a
            plain = plain.convert('RGB')
            try:
                u = uuid.uuid4().hex

                plain.save(f'{os.path.join(path, u)}.jpg',
                           'JPEG', optimize=True)
                # buffer.seek(0)

            except Exception as i:
                raise i
            else:
                images.append(f"{u}.jpg")
        return images

    @staticmethod
    def neededxp(level: str) -> int:
        return 100 + level * 300


class Shop:

    def __init__(self) -> None:
        self.class_font_montbold = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratBold.ttf'), 72)
        self.class_font_montbold_ori = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratBold.ttf'), 27)
        self.class_font_montbold_ori_menor = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratBold.ttf'), 22)
        self.class_font_opensans = ImageFont.truetype(
            os.path.join(pathOpen, 'OpenSansRegular.ttf'), 30)
        self.class_font_opensansmold = ImageFont.truetype(
            os.path.join(pathOpen, 'OpenSansRegular.ttf'), 33)
        self.class_font_opensansbold = ImageFont.truetype(
            os.path.join(pathOpen, 'OpenSansBold.ttf'), 33)
        self.class_font_montserrat = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratRegular.ttf'), 27)

#
#  GRADIENTE
    #   Gradiente para a esquerda
    # def gradientLeft(self, gradient, initial_opacity, bg):
    #    #input_im = Image.open(src)

    #    input_im = Image.new(mode = "RGB", size = (311, 110), color = (0, 65, 89))

    #    gradient= 1.2
    #    initial_opacity=1

    #    if input_im.mode != 'RGBA':
    #        input_im = input_im.convert('RGBA')
    #    width, height = input_im.size

    #    alpha_gradient = Image.new('L', (width, 1), color=0xFF)
    #    for x in range(width):
    #        a = int((initial_opacity * 255.) * (1. - gradient * float(x)/width))
    #
    #        if a > 0:
    #            alpha_gradient.putpixel((x, 0), a)
    #        else:
    #            alpha_gradient.putpixel((x, 0), 0)
    #    alpha = alpha_gradient.resize(input_im.size)

    #    black_im = Image.new('RGBA', (width, height), color=0)
    #    black_im.putalpha(alpha)

    #    #make composite with original image
    #    output_im = Image.composite(input_im, bg, black_im)
    #    bg.paste(output_im, (0, 30), output_im)
    #
    #    return

    #   Gradiente para a direita
    # def gradientRight(self, gradient, initial_opacity, bg):
    #    #input_im = Image.open(src)
    #    input_im = Image.new(mode = "RGB", size = bg.size, color = (0, 65, 89))

    #    gradient= 1.2
    #    initial_opacity=1

    #    if input_im.mode != 'RGBA':
    #        input_im = input_im.convert('RGBA')
    #    width, height = input_im.size

    #    alpha_gradient = Image.new('L', (width, 1), color=0xFF)
    #    for x in range(width):
    #        a = int((initial_opacity * 255.) * (1. - gradient * float(x)/width))
    #
    #        if a > 0:
    #            alpha_gradient.putpixel((-x, 0), a)
    #        else:
    #            alpha_gradient.putpixel((-x, 0), 0)
    #    alpha = alpha_gradient.resize(input_im.size)

    #    black_im = Image.new('RGBA', (width, height), color=0)
    #    black_im.putalpha(alpha)

    #    input_im.transpose(Image.FLIP_LEFT_RIGHT)
    #    output_im = Image.composite(input_im, bg, black_im)
    #    input_im.crop((3, 0, 311, 124))
    #    bg.paste(input_im, (969, 30), black_im)
    #
    #    return
    #
#
    # LOJA ANTIGA
    def drawloja(self, total, itens, coin: int, userImg: BytesIO) -> BytesIO:

        # plain = Image.open(byteImg)
        plain = Image.open(userImg)

        if plain.mode != 'RGBA':
            plain = plain.convert('RGBA')

        userImg_Big = plain.copy()

        oriOriginal = Image.open(r"src\imgs\extra\ori.png")
        starOriginal = Image.open(r"src\imgs\extra\Pin-Star.png")

        total_page = total/6 if total/6 == int() else int(total/6+1)
        images = []
        count = 0
        for i in range(total_page):
            bg = Image.new('RGBA', (1280, 950), (0, 45, 62, 255))
            bg_draw = ImageDraw.Draw(bg)

            userImg_Big = userImg_Big.resize((1280, 1280))
            userImg_Big = userImg_Big.crop((0, 330, 1280, 950 + 330))
            mask = Image.new("L", userImg_Big.size, 90)

            profileFundo = Image.composite(userImg_Big, bg, mask)
            profileBlur = profileFundo.filter(
                ImageFilter.GaussianBlur(radius=10))
            bg.paste(profileBlur, (0, 0))
            bg_draw.text((640, 90), "LOJA", font=self.class_font_montbold,
                         anchor="ms", fill=(219, 239, 255))

            tcount = 0
            ccount = 0
            if tcount == 3:
                tcount = 0
                ccount = 0

            for t in range(7):

                if count < t:
                    list_itens = list(itens[count].values())

                    if int(list_itens[0]['value']) <= int(coin):
                        valueColor = (0, 247, 132)
                    else:
                        valueColor = (228, 45, 45)

                    if str(list_itens[0]['type']) == "Banner":
                        itemImg = Image.open(list_itens[0]['img']).resize(
                            (330, 185), Image.NEAREST)
                        print("Banner")
                    elif str(list_itens[0]['type']) == "Utilizavel":
                        itemImg = Image.open(list_itens[0]['img']).resize(
                            (128, 128), Image.NEAREST)
                        print("Util")
                    else:
                        itemImg = Image.open(list_itens[0]['img'])

                    lar = (itemImg.size[0], itemImg.size[1])
                    # print(list_itens)

                    altura = 180
                    largura = 382

                    larg_inic = 420 * ccount
                    larg_baixo = 420 * tcount

                    ori_pos = 420 * ccount
                    ori_pos_baixo = 420 * tcount

                    if larg_baixo > 840:
                        break

                    if larg_inic <= 840:
                        # 1 row
                        bg_draw.rounded_rectangle(
                            [(37 + larg_inic, altura),
                             ((larg_inic + largura - 2), 320 + altura)], 25,
                            fill=(0, 247, 132))  # bg verde
                        bg_draw.rounded_rectangle(
                            [(35 + larg_inic, altura), ((larg_inic + largura), 315 + altura)], 25, fill=(0, 45, 62))  # bg
                        bg_draw.rounded_rectangle(
                            [(30 + larg_inic, altura),
                             ((larg_inic + largura) + 5, 95 + altura)], 25,
                            fill=(0, 56, 76))  # titulo

                        if list_itens[0]['dest'] == "False":
                            color = (161, 177, 191)
                        else:
                            color = (255, 182, 0)
                            star = starOriginal.resize((40, 41), Image.NEAREST)
                            bg.paste(star, (19 + larg_inic, altura - 15), star)

                        # details
                        value = f"{int(list_itens[ 0 ][ 'value' ]):,}"

                        value = value.replace(",", ".")

                        largText, altText = self.class_font_montbold_ori.getsize(
                            list_itens[0]['value'])

                        largID, altID = self.class_font_montbold_ori.getsize(
                            f"ID: #{list_itens[ 0 ][ 'id' ]}")

                        bg_draw.rounded_rectangle(
                            [(larg_inic + largText + 100, 480), (larg_inic +
                                                                 largText + largID + 140, 43 + 480)], 15,
                            fill=(0, 52, 71))  # id
                        bg_draw.rounded_rectangle(
                            [(larg_inic + 30, 473),
                             (larg_inic + largText + 120, 54 + 473)], 20,
                            fill=(0, 56, 76))  # price

                        bg_draw.text((larg_inic + 27 + (largura) / 2, 260),
                                     list_itens[0]['name'], font=self.class_font_opensansbold, anchor="ms",
                                     fill=(color))
                        bg_draw.text((larg_inic + 27 + (largura) / 2, 215),
                                     list_itens[0]['type'], font=self.class_font_opensansmold, anchor="ms",
                                     fill=(color))
                        # print(itens[t]['value'])

                        bg_draw.text((larg_inic + 90, 483), value,
                                     font=self.class_font_montbold_ori, fill=(valueColor))
                        bg_draw.text((larg_inic + largText + 130, 485),
                                     f"ID: ", font=self.class_font_montbold_ori_menor, fill=(0, 198, 244))
                        bg_draw.text((larg_inic + largText + 135, 483),
                                     f"    #{list_itens[ 0 ][ 'id' ]}", font=self.class_font_montbold_ori,
                                     fill=(0, 198, 244))

                        # print(lar)
                        if list_itens[0]['type'] == "Titulo":
                            bg.paste(
                                itemImg,
                                (int((larg_inic + 20) +
                                 ((largura - lar[0]) / 2)), 350),
                                itemImg
                            )
                        elif list_itens[0]['type'] == "Banner":
                            bg.paste(itemImg, (int((larg_inic + 20) + ((largura - lar[0]) / 2)),
                                               int((95 + altura))))
                        else:
                            bg.paste(
                                itemImg, (35 + 105 + larg_inic, 300), itemImg)

                        ori = oriOriginal.resize((70, 71), Image.NEAREST)
                        bg.paste(ori, (ori_pos, 467), ori)
                        ccount += 1

                    elif larg_baixo <= 840:

                        altura = 570

                        bg_draw.rounded_rectangle(
                            [(37 + larg_baixo, altura),
                             ((larg_baixo + largura - 2), 320 + altura)], 25,
                            fill=(0, 247, 132))
                        bg_draw.rounded_rectangle(
                            [(35 + larg_baixo, altura), ((larg_baixo + largura), 315 + altura)], 25, fill=(0, 45, 62))
                        bg_draw.rounded_rectangle(
                            [(30 + larg_baixo, altura), ((larg_baixo + largura) + 5, 95 + altura)], 25, fill=(0, 56, 76))

                        if list_itens[0]['dest'] == "False":
                            color = (161, 177, 191)
                        else:
                            color = (255, 182, 0)
                            star = starOriginal.resize((40, 41), Image.NEAREST)
                            bg.paste(
                                star, (19 + larg_baixo, altura - 15), star)
                        value = f"{int(list_itens[ 0 ][ 'value' ]):,}"
                        value = value.replace(",", ".")

                        largText, altText = self.class_font_montbold_ori.getsize(
                            list_itens[0]['value'])

                        largID, altID = self.class_font_montbold_ori.getsize(
                            f"ID: #{list_itens[ 0 ][ 'id' ]}")

                        bg_draw.rounded_rectangle(
                            [(larg_baixo + largText + 100, 865),
                             (larg_baixo + largText + largID + 140, 43 + 865)], 15,
                            fill=(0, 52, 71))
                        bg_draw.rounded_rectangle(
                            [(larg_baixo + 30, 860), (larg_baixo + largText + 120, 54 + 860)], 20, fill=(0, 56, 76))

                        bg_draw.text((larg_baixo + 27 + (largura) / 2, 650),
                                     list_itens[0]['name'], font=self.class_font_opensansbold, anchor="ms",
                                     fill=(color))
                        bg_draw.text((larg_baixo + 27 + (largura) / 2, 605),
                                     list_itens[0]['type'], font=self.class_font_opensansmold, anchor="ms",
                                     fill=(color))
                        bg_draw.text((larg_baixo + 90, 868), value,
                                     font=self.class_font_montbold_ori, fill=(valueColor))
                        bg_draw.text((larg_baixo + largText + 130, 870),
                                     f"ID: ", font=self.class_font_montbold_ori_menor, fill=(0, 198, 244))
                        bg_draw.text((larg_baixo + largText + 135, 868),
                                     f"    #{list_itens[ 0 ][ 'id' ]}", font=self.class_font_montbold_ori,
                                     fill=(0, 198, 244))

                        if list_itens[0]['type'] == "Titulo":
                            bg.paste(
                                itemImg,
                                (int((larg_baixo + 20) +
                                 ((largura - lar[0]) / 2)), 735),
                                itemImg
                            )
                        elif list_itens[0]['type'] == "Banner":
                            bg.paste(itemImg, (int((larg_baixo + 20) + ((largura - lar[0]) / 2)),
                                               int(95 + altura)))
                        else:
                            bg.paste(
                                itemImg, (35 + 110 + larg_baixo, 682), itemImg)

                        ori = oriOriginal.resize((70, 71), Image.NEAREST)
                        bg.paste(ori, (ori_pos_baixo, 855), ori)
                        tcount += 1

                    count += 1
            bg_draw.text((100, 54), "Suas oris",
                         font=self.class_font_montserrat, fill=(212, 255, 236))

            value = f"{int(coin):,}".replace(",", ".")
            bg_draw.text((100, 90), value,
                         font=self.class_font_montserrat, fill=(0, 247, 132))

            bg_draw.text((1063, 55), "Página Atual",
                         font=self.class_font_montserrat, fill=(161, 177, 191))

            bg_draw.text((1200, 90), "{}".format(i+1),
                         font=self.class_font_montbold_ori, fill=(219, 239, 255))
            # SUBTITLE
            bg_draw.text((630, 135), "Use os botões abaixo par navegar entre as páginas.",
                         font=self.class_font_opensans, anchor="ms", fill=(219, 239, 255))

            #bg.paste(output, (100, 193), output)

            #buffer = BytesIO()

            # Tá bem feito, mas é só tirar esse convert, mudar jpg pra png e tirar o optimize do save
            bg = bg.convert('RGB')
            try:
                u = uuid.uuid4().hex

                bg.save(f'{os.path.join(path, u)}.jpg', 'JPEG', optimize=True)
                # buffer.seek(0)

            except Exception as i:
                raise i
            else:
                images.append(f"{u}.jpg")
        return images

# NOVA LOJA


class shopNew:
    def __init__(self) -> None:

        # "LOJA"
        self.montserrat_extrabold_loja = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratExtraBold.ttf'), 50
        )

        # COINS TITLE TEXT
        self.montserrat_medium_coins = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratMedium.ttf'), 23
        )

        # COINS VALUE TEXT
        self.montserrat_bold_coins = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratBold.ttf'), 28
        )

        # /comprar #ID
        self.montserrat_semibolditalic_buy = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratSemiBoldItalic.ttf'), 25
        )

        # Nome do item
        self.montserrat_bold_name = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratBold.ttf'), 25
        )

        # Tipo do item
        self.montserrat_bold_type = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratBold.ttf'), 22
        )

        # Valor
        self.montserrat_blackitalic_value = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratBlackItalic.ttf'), 40
        )

        # Categoria do item
        self.montserrat_semibold_category = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratSemiBold.ttf'), 20
        )

        # "Página"
        self.montserrat_semibold = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratSemiBold.ttf'), 30
        )

        # Número da página
        self.montserrat_extrabold_pageNumb = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratExtraBold.ttf'), 30
        )

    def add_corners(self, im, rad):
        size = im.size
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0) + size, radius=rad, fill=255)
        im_ = im.copy()
        im_.putalpha(mask)

        output = ImageOps.fit(im_, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)

        return output

    def drawloja(self, total, spark, ori, items, banner=None) -> BytesIO:
        spark_img = Image.open("src/imgs/extra/Spark.png")
        ori_img = Image.open("src/imgs/extra/Ori.png")
        shopCar_img = Image.open(
            "src/imgs/extra/loja/Carrinho-Loja-Colorido.png")

        # ITEM CATEGORIE IMAGES
        comumCat_image = Image.open("src/imgs/extra/loja/Loja-Comum.png")
        raroCat_image = Image.open("src/imgs/extra/loja/Loja-Raro.png")
        lendCat_image = Image.open("src/imgs/extra/loja/Loja-Lendario.png")

        comumCategory_value, raroCategory_value, lendCategory_value = 100000, 1000000, 100000000

        if not banner:
            banner = Image.open(
                "src/imgs/extra/loja/banners/Fy-no-Planeta-Magnético.png")
        else:
            banner = Image.open(banner)

        plain = Image.new(
            'RGBA', (1280, 1280), (0, 45, 62, 255))

        banner_Big = banner.resize((1280+630, 650+630))
        banner_Big = banner_Big.crop((300, 0, 1580, 1280))
        mask = Image.new("L", banner_Big.size, 90)

        bannerFundo = Image.composite(banner_Big, plain, mask)
        bannerBlur = bannerFundo.filter(ImageFilter.GaussianBlur(radius=10))

        total_page = total/6 if total/6 == int() else int(total/6+0.5)

        images = []
        count = 0
        for i in range(total_page):
            bg_draw = ImageDraw.Draw(plain)
            plain.paste(bannerBlur, (0, 0))

        # SHOPING TITLE
            plain.paste(shopCar_img, (45, 80), shopCar_img)
            bg_draw.text((115, 75), "LOJA", font=self.montserrat_extrabold_loja,
                         anchor="la", fill=(219, 239, 255))

        # SHOPING COINS

            # SPARK AREA
            bg_draw.rounded_rectangle(
                [(695, 50), (959, 140)], 22, fill=(0, 45, 62))

            bg_draw.text((770, 60), "Sparks",
                         font=self.montserrat_medium_coins, fill=(153, 177, 191))

            spark_value = f"{int(spark):,}".replace(",", ".")
            bg_draw.text((770, 90), spark_value,
                         font=self.montserrat_bold_coins, fill=(219, 239, 255))

            # ORI AREA
            bg_draw.rounded_rectangle(
                [(985, 50), (1249, 140)], 22, fill=(0, 53, 49))

            bg_draw.text((1065, 60), "Oris",
                         font=self.montserrat_medium_coins, fill=(203, 246, 228))

            ori_value = f"{int(ori):,}".replace(",", ".")

            bg_draw.text((1065, 90), ori_value,
                         font=self.montserrat_bold_coins, fill=(0, 247, 132))

            # IMAGES
            spark_img = spark_img.resize((70, 80), Image.NEAREST)
            plain.paste(spark_img, (700, 55), spark_img)

            ori_img = ori_img.resize((67, 67), Image.NEAREST)
            plain.paste(ori_img, (993, 58), ori_img)

        # FOOTER
            # PAGE AREA
            bg_draw.text((630, 1240), "Página",
                         font=self.montserrat_semibold, anchor="md", fill=(0, 247, 132))

            bg_draw.text((700, 1240), "%s" % (i+1, ),
                         font=self.montserrat_extrabold_pageNumb, anchor="md", fill=(0, 247, 132))

        # PAGE CREATE LOOP
            tcount = 0
            ccount = 0
            if tcount == 3:
                tcount = 0
                ccount = 0

            for t in range(7):
                if count >= total:
                    break
                # ITENS OPTIONS
                largura = 382

                larg_cima = 420 * ccount
                larg_baixo = 420 * tcount

                list_itens = list(items[count].values())
                #print (list_itens)

                if str(list_itens[0]['type']) == "Banner":
                    itemImg = Image.open(list_itens[0]['img']).convert(
                        "RGBA").resize((330, 185), Image.NEAREST)
                    itemImg = self.add_corners(itemImg, 20)
                elif str(list_itens[0]['type']) == "Utilizavel":
                    itemImg = Image.open(list_itens[0]['img']).convert(
                        "RGBA").resize((128, 128), Image.NEAREST)
                elif str(list_itens[0]['type']) == "Badge":
                    itemImg = Image.open(list_itens[0]['img']).convert("RGBA")
                    itemImg = itemImg.resize(
                        (int(itemImg.size[0]/2), int(itemImg.size[1]/2)), Image.NEAREST)
                elif str(list_itens[0]['type']) == "Titulo":
                    itemImg = Image.open(list_itens[0]['img']).convert("RGBA")
                else:
                    itemImg = Image.open(list_itens[0]['img']).convert("RGBA")
                    lar = (itemImg.size[0], itemImg.size[1])
                    itemImg = itemImg.resize(
                        (int(lar[0]*1.5), int(lar[1]*1.5)), Image.NEAREST
                    )

                if int(list_itens[0]['value']) <= comumCategory_value:
                    img = comumCat_image
                elif int(list_itens[0]['value']) <= raroCategory_value:
                    img = raroCat_image
                elif int(list_itens[0]['value']) <= lendCategory_value:
                    img = lendCat_image

                lar = (itemImg.size[0], itemImg.size[1])

                # print(list_itens)

                if larg_baixo > 840:
                    # ROW 1
                    break

                if larg_cima <= 840:
                    # IMAGES
                    altura = 195

                    # ROW BACKGROUND IMAGE 1
                    plain.paste(img, (25 + larg_cima, altura), img)

                    # ROW ITEM IMAGE 1
                    plain.paste(
                        itemImg, (int(25 + larg_cima + int((img.size[0] - lar[0])/2)),
                                  int(altura + int((img.size[1] - lar[1])/2)) - 70), itemImg)
                # TEXTS
                    # ITEM TYPE
                    bg_draw.text((135 + larg_cima, altura),
                                 list_itens[0]['type'], fill=(0, 45, 62), anchor="ma", font=self.montserrat_bold_type)

                    # ITEM NAME
                    bg_draw.text((int(25 + larg_cima + int((img.size[0]/2))),
                                  int(altura + int((img.size[1]/2))) + 70),
                                 list_itens[0]['name'], fill=(215, 235, 251), anchor="ma",
                                 font=self.montserrat_bold_name)

                    # ITEM BUY
                    bg_draw.text((int(25 + larg_cima + int((img.size[0]/2))),
                                  int(altura + int((img.size[1]/2))) + 130),
                                 "/comprar %s" % (list_itens[0]['id'], ), fill=(0, 45, 62), anchor="ma",
                                 font=self.montserrat_semibolditalic_buy)

                    # ITEM VALUE
                    value = f"{int(list_itens[0][ 'value' ]):,}".replace(
                        ",", ".")
                    bg_draw.text((int(25 + larg_cima + int((img.size[0]/2))),
                                  int(altura + int((img.size[1]/2))) + 160),
                                 value, fill=(0, 45, 62), anchor="ma",
                                 font=self.montserrat_extrabold_pageNumb)

                    ccount += 1

                elif larg_baixo <= 840:
                    altura = 685

                    # ROW BACKGROUND IMAGE 2
                    plain.paste(img, (25 + larg_baixo, altura), img)

                    # ROW ITEM IMAGE 2
                    plain.paste(
                        itemImg, (int(25 + larg_baixo + int((img.size[0] - lar[0])/2)),
                                  int(altura + int((img.size[1] - lar[1])/2)) - 70), itemImg)

                # TEXTS
                    # ITEM TYPE
                    bg_draw.text((135 + larg_baixo, altura),
                                 list_itens[0]['type'], fill=(0, 45, 62), anchor="ma", font=self.montserrat_bold_type)

                    # ITEM NAME
                    bg_draw.text((int(25 + larg_baixo + int((img.size[0]/2))),
                                  int(altura + int((img.size[1]/2))) + 70),
                                 list_itens[0]['name'], fill=(215, 235, 251), anchor="ma",
                                 font=self.montserrat_bold_name)

                    # ITEM BUY
                    bg_draw.text((int(25 + larg_baixo + int((img.size[0]/2))),
                                  int(altura + int((img.size[1]/2))) + 130),
                                 "/comprar %s" % (list_itens[0]['id'], ), fill=(0, 45, 62), anchor="ma",
                                 font=self.montserrat_semibolditalic_buy)

                    # ITEM VALUE
                    value = f"{int(list_itens[0][ 'value' ]):,}".replace(
                        ",", ".")
                    bg_draw.text((int(25 + larg_baixo + int((img.size[0]/2))),
                                  int(altura + int((img.size[1]/2))) + 160),
                                 value, fill=(0, 45, 62), anchor="ma",
                                 font=self.montserrat_extrabold_pageNumb)

                    tcount += 1

                count += 1

            plain = plain.convert('RGB')
            try:
                u = uuid.uuid4().hex

                plain.save(f'{os.path.join(path, u)}.png', 'PNG')
                # buffer.seek(0)

            except Exception as i:
                raise i
            else:
                images.append(f"{u}.png")
        return images


class Top:
    def __init__(self) -> None:
        self.opensans_bold_name = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratBold.ttf'), 40)
        self.opensans_regular_lilname = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratRegular.ttf'), 27)
        self.opensans_bold_coin = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratMedium.ttf'), 40)
        self.opensans_bold_count = ImageFont.truetype(
            os.path.join(pathMonserrat, 'MontserratBold.ttf'), 18)

    async def topdraw(self, user_id, ranking, user_position, profile_bytes: BytesIO) -> BytesIO:

        ori = Image.open("src/imgs/extra/ori.png")
        rankFundo = Image.open("src/imgs/extra/bg/rankFundo.png")

        oriCopy = ori.copy()

        plain = Image.new(
            'RGBA', (rankFundo.size[0], rankFundo.size[1]), (37, 150, 190))
        bg_draw = ImageDraw.Draw(plain)

        plain.paste(rankFundo, (0, 0), rankFundo)

        count = 0
        icount = 0
        size = 100
        big_size = size + 100

        infos = []

        for e in ranking:
            users = list(ranking[count].values())
            try:
                response = requests.get(users[0]['avatar_url'])
                user_img = Image.open(BytesIO(response.content))
            except:
                user_img = Image.open("src/imgs/extra/spark.png")

            if user_img.mode != 'RGBA':
                user_img = user_img.convert('RGBA')

            user_img = user_img.resize((90, 90))

            user_font_color = [(0, 30, 41, 255), (65, 84, 88, 255)]
            user_coin_bg = (0, 45, 62, 255)
            if count == 0:
                color = (255, 216, 84, 255)
            elif count == 1:
                color = (222, 222, 222, 255)
            elif count == 2:
                color = (242, 171, 113, 255)
            else:
                color = (0, 52, 71, 255)
                user_font_color = [(219, 239, 255), (169, 185, 198)]
                if users[0]['type'] == "Ori":
                    user_coin_bg = (0, 63, 63, 255)
                if users[0]['type'] == "Nivel":
                    user_coin_bg = (0, 38, 53, 255)

            # row rectangle
            bg_draw.rounded_rectangle(
                [(50, size), (1230, big_size + 5)], 25,
                fill=color)

            # username
            text_name = users[0]['name']
            line_height = self.opensans_bold_name.getsize(text_name)[1]
            name, cod = text_name.split('#')
            bg_draw.text(((user_img.size[1]*2) + 70, size+50), name,
                         font=self.opensans_bold_name, fill=(user_font_color[0]), anchor='ls')
            bg_draw.text(((user_img.size[1]*2) + 70, size+80),
                         f"#{cod}", font=self.opensans_regular_lilname, fill=(user_font_color[1]), anchor='ls')

            # mask to round image
            bigsize = (user_img.size[0] * 3, user_img.size[1] * 3)

            mask = Image.new('L', bigsize, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + bigsize, fill=255)
            mask = mask.resize(user_img.size, Image.ANTIALIAS)
            user_img.putalpha(mask)

            output = ImageOps.fit(user_img, mask.size, centering=(0.5, 0.5))
            output.putalpha(mask)

            plain.paste(output, (110, size+10), output)

            # count circle
            bg_draw.ellipse([(105, size+10), (135, size+40)],
                            fill=(255, 255, 255, 255))
            bg_draw.text((121, size+32), str(count+1),
                         font=self.opensans_bold_count, fill=(0, 30, 41, 255), anchor='ms')

            # rounded value
            bg_draw.rounded_rectangle(
                [(880, size+20), (1200, size + 80)], 15, fill=(user_coin_bg))

            value = users[0]['value']
            tipo = str(users[0]['type'])

            if tipo.title() == "Ori":
                value = f"{int(users[ 0 ][ 'value' ]):,}"
                value = value.replace(",", ".")

                txt_color = (0, 247, 132, 255)
                bg_draw.text(
                    (1060, size+72), value, font=self.opensans_bold_coin, fill=txt_color, anchor='md')

                ori = oriCopy.resize((85, 85), Image.NEAREST)
                plain.paste(ori, (860, size+10), ori)

                bg_draw.text((100, 70),
                             f"Confira os 10 usuários com a maior quantidade de {users[ 0 ][ 'type' ]} do servidor.",
                             font=self.opensans_regular_lilname, fill=(0, 247, 132), anchor='ls')
                bg_draw.text((rankFundo.size[0] - 100, rankFundo.size[1]-15),
                             f"Você está na {user_position}ª Colocação.",
                             font=self.opensans_regular_lilname, fill=(0, 247, 132), anchor='rs')

            elif tipo.title() == "Nivel":

                txt_color = (219, 239, 255, 255)
                bg_draw.text(
                    (1060, size+72), value, font=self.opensans_bold_coin, fill=txt_color, anchor='md')

                rank_img = Image.open(users[0]['rank_image'])
                rank_img = rank_img.resize((85, 85), Image.NEAREST)
                plain.paste(rank_img, (860, size+10), rank_img)

                bg_draw.text((100, 70),
                             f"Confira os 10 usuários com a maior quantidade de {users[ 0 ][ 'type' ]} do servidor.",
                             font=self.opensans_regular_lilname, fill=(0, 247, 132), anchor='ls')
                bg_draw.text((rankFundo.size[0] - 100, rankFundo.size[1]-15),
                             f"Você está na {user_position}ª Colocação.",
                             font=self.opensans_regular_lilname, fill=(0, 247, 132), anchor='rs')

            size = big_size + 20
            big_size = size + 100
            count += 1

        buffer = BytesIO()
        plain.save(buffer, 'png')
        buffer.seek(0)
        return buffer


class Utilities:
    def __init__(self):
        self.database = Database
        self.rankcard = Rank()
        self.shop = Shop()
        self.shopnew = shopNew()
        self.topcard = Top()


utilities = Utilities()
