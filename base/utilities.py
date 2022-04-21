from __future__ import annotations

import asyncio
import json
import requests
from io import BytesIO
from lib2to3.pytree import convert
from typing import List

import asyncpg
from PIL import Image, ImageColor, ImageDraw, ImageFilter, ImageFont, ImageOps

from base.struct import Config


class Database:
    def __init__(self, loop, user: str, password: str) -> None:
        self.user = user
        self.password = password
        self.host = '127.0.0.1'
        loop.create_task(self.connect())

    async def connect(self) -> None:
        self.conn = await asyncpg.connect(user=self.user, password=self.password, host=self.host)
        try:
            assert not await self.conn.fetch('SELECT datname FROM pg_catalog.pg_database WHERE '
                                             'datname=\'discordleveling\'')
            await self.conn.fetch('CREATE DATABASE discordleveling')
            await self.conn.close()
        except:
            pass
        self.conn = await asyncpg.connect(user=self.user, password=self.password, database='discordleveling',
                                          host=self.host)

        # users
        await self.conn.fetch("CREATE TABLE IF NOT EXISTS users (id TEXT NOT NULL, rank INT NOT NULL, xp INT NOT "
                              "NULL, xptotal INT NOT NULL, title TEXT UNIQUE, mold TEXT UNIQUE, info TEXT, "
                              "coin INT DEFAULT 0, inv TEXT, birth TEXT DEFAULT '???')")
        # ranks
        await self.conn.fetch("CREATE TABLE IF NOT EXISTS ranks (lv INT NOT NULL, name TEXT NOT NULL UNIQUE, "
                              "r INT NOT NULL, g INT NOT NULL, b INT NOT NULL, roleid TEXT, imgxp TEXT)")

        # await self.conn.fetch("INSERT INTO ranks (lv, name, role, r, g, b) VALUES (0, 'Novato', 'Novato', 189, 142,
        # 71), (1, 'Soldado Nadir', 'Soldado Nadir',221, 180,100), (11, 'Sargento Aurora','Sargento Aurora', 101,
        # 187, 254), (21, 'Tenente Zenite','Tenente Zenite', 193, 134, 250),(31, 'Capitão Solar', 'Capitão Solar',
        # 253, 153, 123), (41, 'Major Solar', 'Major Solar', 255, 174, 80), (51, 'Coronel Umbra', 'Coronel Umbra',
        # 153, 197, 155), (61, 'General Blazar', 'General Blazar', 240, 114, 90), (71, 'Marechal Quasar',
        # 'Marechal Quasar', 197, 141, 248)") itens
        await self.conn.fetch("CREATE TABLE IF NOT EXISTS itens (id SERIAL PRIMARY KEY, name TEXT NOT NULL UNIQUE, "
                              "type TEXT NOT NULL, value INT, img TEXT NOT NULL, imgd TEXT, img_profile TEXT NOT "
                              "NULL, lvmin INT DEFAULT 0, canbuy BOOLEAN DEFAULT TRUE, dest BOOLEAN DEFAULT FALSE, "
                              "limitedTime TEXT, details TEXT)")
        # sorteios await self.conn.fetch("CREATE TABLE IF NOT EXISTS sorteios (id SERIAL PRIMARY KEY, name TEXT NOT
        # NULL, endtime TEXT NOT NULL, idticket TEXT NOT NULL)") tickets await self.conn.fetch("CREATE TABLE IF NOT
        # EXISTS tickets (id SERIAL PRIMARY KEY, idticket TEXT NOT NULL, price INT, rank INT, img TEXT DEFAULT
        # 'src\imgs\extra\ticket.png', users TEXT)")
        try:
            await self.conn.fetch("INSERT INTO itens (name, type, value, img, imgd, img_profile, lvmin) VALUES ( "
                                  "'Novato',           'Moldura', 1000,        'src/molduras-loja/#1.png', "
                                  "'src/molduras/#1E.png', 'src/molduras/#1.png', 0, ) ON CONFLICT (name) DO NOTHING")

            await self.conn.fetch("INSERT INTO itens (name, type, value, img, imgd, img_profile, lvmin) VALUES ("
                                  "'Soldado Nadir',    'Moldura', 500000,      'src/molduras-loja/#1.png', "
                                  "'src/molduras/#1E.png', 'src/molduras/#1.png', 10) ON CONFLICT (name) DO NOTHING")

            await self.conn.fetch('INSERT INTO itens (name, type, value, img, imgd, img_profile, lvmin) VALUES ( '
                                  '\'Sargento Aurora\',  \'Moldura\', 1000000,     \'src/molduras-loja/#2.png\', '
                                  '\'src/molduras/#2E.png\', \'src/molduras/#2.png\', 20) ON CONFLICT (name) DO NOTHING')

            await self.conn.fetch('INSERT INTO itens (name, type, value, img, imgd, img_profile, lvmin) VALUES ('
                                  '\'Tenente Zênite\',   \'Moldura\', 2500,        \'src/molduras-loja/#3.png\', '
                                  '\'src/molduras/#3E.png\', \'src/molduras/#3.png\', 30) ON CONFLICT (name) DO NOTHING')

            await self.conn.fetch("INSERT INTO itens (name, type, value, img, imgd, img_profile, lvmin) VALUES ("
                                  "'Capitão Solar',    'Moldura', 4000000,     'src/molduras-loja/#4.png', "
                                  "'src/molduras/#4E.png', 'src/molduras/#4.png', 40) ON CONFLICT (name) DO NOTHING")

            await self.conn.fetch("INSERT INTO itens (name, type, value, img, imgd, img_profile, lvmin) VALUES ("
                                  "'Major Solar',      'Moldura', 6500000,     'src/molduras-loja/#5.png', "
                                  "'src/molduras/#5E.png', 'src/molduras/#5.png', 50) ON CONFLICT (name) DO NOTHING")

            await self.conn.fetch("INSERT INTO itens (name, type, value, img, imgd, img_profile, lvmin) VALUES ("
                                  "'Coronel Umbra',    'Moldura', 8000000,     'src/molduras-loja/#6.png', "
                                  "'src/molduras/#6E.png', 'src/molduras/#6.png', 60) ON CONFLICT (name) DO NOTHING")

            await self.conn.fetch("INSERT INTO itens (name, type, value, img, imgd, img_profile, lvmin) VALUES ("
                                  "'General Blazar',   'Moldura', 100000000,   'src/molduras-loja/#7.png', "
                                  "'src/molduras/#7E.png', 'src/molduras/#7.png', 70) ON CONFLICT (name) DO NOTHING")

            await self.conn.fetch("INSERT INTO itens (name, type, value, img, imgd, img_profile, lvmin) VALUES ("
                                  "'Marechal Quasar',  'Moldura', 100000000,   'src/molduras-loja/#8.png', "
                                  "'src/molduras/#8E.png', 'src/molduras/#8.png', 80) ON CONFLICT (name) DO NOTHING")

            await self.conn.fetch("INSERT INTO itens (name, type, value, img, imgd, img_profile, lvmin) VALUES ("
                                  "'COMRADE',          'Titulo', 2500,         'src/titulos/#1.png',       '',        "
                                  "             '',                     0) ON CONFLICT (name) DO NOTHING")
        except:
            pass

    async def fetch(self, sql: str) -> list:
        return await self.conn.fetch(sql)

    async def fetchList(self, sql: str) -> list:
        return '\n\n'.join([json.dumps(dict(x), ensure_ascii=False) for x in (await self.conn.fetch(sql))])


class Rank:
    def __init__(self) -> None:
        self.class_font_semibold = ImageFont.truetype(
            'src/fonts/MontserratSemiBold.ttf', 36)
        self.class_font_extrabold = ImageFont.truetype(
            'src/fonts/MontserratExtraBold.ttf', 48)
        self.class_font_bold_name = ImageFont.truetype(
            'src/fonts/MontserratBold.ttf', 72)
        self.class_font_bold_id = ImageFont.truetype(
            'src/fonts/MontserratSemiBold.ttf', 42)
        self.class_font_bold_role = ImageFont.truetype(
            'src/fonts/MontserratMedium.ttf', 30)
        self.class_font_bold_info_sans = ImageFont.truetype(
            'src/fonts/OpenSansRegular.ttf', 36)
        self.class_font_bold_xp = ImageFont.truetype(
            'src/fonts/OpenSansBold.ttf', 48)
        self.class_font_bold_info = ImageFont.truetype(
            'src/fonts/MontserratBold.ttf', 36)
        self.class_font_montserrat = ImageFont.truetype(
            'src/fonts/MontserratRegular.ttf', 36)
        self.class_font_bold_ori_bday = ImageFont.truetype(
            'src/fonts/MontserratBold.ttf', 45)
        self.class_font_barlow_bold = ImageFont.truetype(
            'src/fonts/BarlowSemiCondensedBold.ttf', 42)
        self.class_font_role = ImageFont.truetype(
            'src/fonts/MontserratBold.ttf', 30)
        self.class_font_montserrat_regular_nivel = ImageFont.truetype(
            'src/fonts/MontserratRegular.ttf', 30)
        self.class_font_sans_regular_nivel = ImageFont.truetype(
            'src/fonts/OpenSansRegular.ttf', 30)
        self.RadiateSansBoldCondensed = ImageFont.truetype(
            'src/fonts/RadiateSansBoldCondensed.ttf', 65)
        self.XPRadiateSansBoldCondensed = ImageFont.truetype(
            'src/fonts/RadiateSansBoldCondensed.ttf', 85)

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

    def draw(self, user: str, rank: str, xp: str, titleImg: str, moldName: str, moldImg: str, moldImgR: str, info: str,
             coin: int, birth: str, staff: None, rank_name, r: str, g: str, b: str, imgxp,
             profile_bytes: BytesIO) -> BytesIO:
        profile_bytes = Image.open(profile_bytes)
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

        bg = Image.new('RGBA', (1280, 823), (0, 45, 62, 255))
        bg_draw = ImageDraw.Draw(bg)

        profile_bytes_imenso = profile_bytes_imenso.resize((1280, 1280))
        profile_bytes_imenso = profile_bytes_imenso.crop(
            (0, 420, 1280, 823 + 420))
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
        userid = (f"#{splitUsername[1]}")
        bg_draw.text((488, 32), username, font=self.class_font_bold_name, fill=(
            219, 239, 255), spacing=5)
        bg_draw.text((488, 104), userid, font=self.class_font_bold_id,
                     fill=(122, 137, 145), spacing=5)

        user_border = (profile_bytes.size[0] +
                       prof_elipse + 15, profile_bytes.size[1] + 185 + 15)

        rolePosition = 488
        role_top = 168
        if rank_name == None:
            rank_text = "Novato"
            cor = (167, 141, 116)
        else:
            rank_text = rank_name.upper()
            cor = (int(r), int(g), int(b))
        if staff:
            staff.reverse()
            # classe
            bg_draw.ellipse([prof_elipse, 185, user_border],
                            fill=(list(staff[0].values())[0]['color']))

            bg_draw.rounded_rectangle(
                [(54, 548), (418, 625)], 37, fill=(list(staff[0].values())[0]['color']))
            count = 0
            while count <= len(staff) - 1:
                list_roles = list(staff[count].values())

                # info
                largText, altText = self.class_font_role.getsize(
                    list_roles[0]['name'])
                if rolePosition + largText + 22 > 1280:
                    role_top = 230
                    rolePosition = 488

                bg_draw.rounded_rectangle(
                    [(rolePosition, role_top), (rolePosition + largText + 22, role_top + 44)], 28, fill=(list_roles[0]['color']),
                    width=3)
                bg_draw.text((rolePosition + largText + 12, role_top+31), list_roles[0]['name'], font=self.class_font_role,
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
            roleTextPosition = rolePosition + 92

            # classe
            # r, g, b = bytes.fromhex(color[1:])
            # bg_draw.ellipse([prof_elipse, 185, user_border], fill=f"rgb({r}, {g}, {b})")
            if moldImg != None:
                border_im = Image.open(r"{}".format(moldImg))
                # border_im = border_im.resize((profile_bytes.size[0] +
                #       prof_elipse+15, profile_bytes.size[1]+prof_elipse+15), Image.NEAREST)
                # border_im = border_im.resize((profile_bytes.size[0],  profile_bytes.size[1]), Image.NEAREST)
                # print(profile_bytes.size[0],  profile_bytes.size[1])
                rank_rounded = Image.open(r"{}".format(moldImgR))
                bg.paste(rank_rounded, (54, 548), rank_rounded)

            elif moldImg == None:
                border_im = None
                bg_draw.ellipse([prof_elipse, 185, user_border],
                                fill=(cor))
                bg_draw.rounded_rectangle(
                    [(54, 548), (418, 625)], 37, fill=(cor))

        if titleImg != None:
            title_img = Image.open(r"{}".format(titleImg))
            tsize = (title_img.size[0], title_img.size[1])
            bg.paste(title_img, (int((420 - tsize[0]) / 2) + 25, 64), title_img)

        if moldName != None:
            rank_text = moldName.upper()
            bg_draw.text((235, 603), rank_text, font=self.class_font_barlow_bold, fill=(
                0, 28, 38), anchor="ms", spacing=5)
        else:

            bg_draw.text((235, 603), rank_text, font=self.class_font_barlow_bold, fill=(
                0, 28, 38), anchor="ms", spacing=5)

        # info
        bg_draw.rounded_rectangle(
            [(488, 286), (488 + 764, 262 + 185)], 25, fill=(0, 45, 62))
        bg_draw.text((516, 300), "Info:", font=self.class_font_montserrat, fill=(
            161, 177, 191), spacing=5)

        if not info:
            info = "Não há o que bisbilhotar aqui."

        lines = self.text_wrap(info, self.class_font_bold_info_sans, 600)
        line_height = self.class_font_bold_info.getsize(info)[1]
        x = 516
        y = 350

        for line in lines:
            # draw the line on the image
            bg_draw.text((x, y), line, font=self.class_font_bold_info,
                         fill=(219, 239, 255), spacing=5)
            # update the y position so that we can use it for next line
            y = y + line_height

        # ori
        bg_draw.rounded_rectangle(
            [(488, 490), (488 + 407, 490 + 162)], 25, fill=(0, 45, 62))  # ori

        ori = Image.open("src\imgs\extra\ori.png")
        #ori = ori.resize((140, 140), Image.NEAREST)
        bg.paste(ori, (490, 505), ori)
        value = f"{int(coin):,}".replace(",", ".")
        bg_draw.text((637, 525), "Oris",
                     font=self.class_font_montserrat, fill=(212, 255, 236))
        bg_draw.text((637, 575), value,
                     font=self.class_font_bold_ori_bday, fill=(0, 247, 132))

        # Bday
        bg_draw.rounded_rectangle(
            [(913, 490), (913 + 339, 490 + 162)], 25, fill=(0, 45, 62))  # Bday

        if birth != "???":
            birth = birth.split("/")
            dia = birth[0]
            mes = birth[1]
            birth = f"{dia}/{mes}"
        else:
            birth = "??/??"

        cake = Image.open("src\imgs\extra\cake.png")
        cake = cake.resize((62, 84), Image.NEAREST)
        bg.paste(cake, (934, 530), cake)
        value = f"{int(coin):,}".replace(",", ".")
        bg_draw.text((1015, 525), "Aniversário",
                     font=self.class_font_montserrat, fill=(255, 212, 216))
        bg_draw.text((1015, 575), birth,
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

        needed_xp = self.neededxp(rank)

        # Pré
        bg_draw.text((80, 723), "NÍVEL ",
                     font=self.class_font_montserrat_regular_nivel, anchor="ms", fill=(219, 239, 255))
        bg_draw.text((150, 723), f"{rank}",
                     font=self.class_font_role, anchor="ms", fill=(219, 239, 255))

        # Middle
        bg_draw.text((640, 785),
                     f"Faltam {int(needed_xp - xp):,} de XP para chegar ao Nível {rank + 1}".replace(",", "."),
                     font=self.class_font_role, anchor="ms", fill=(219, 239, 255))

        # Pós
        bg_draw.text((1089 + 70, 723), "NÍVEL ",
                     font=self.class_font_montserrat_regular_nivel, anchor="ms", fill=(219, 239, 255))
        bg_draw.text((1089 + 140, 723), f"{rank + 1}",
                     font=self.class_font_role, anchor="ms", fill=(219, 239, 255))

        # img user
        if moldImg == None:
            bg.paste(profile_bytes, (100, 193), profile_bytes)
            bg_draw.rounded_rectangle((190, 698, 190 + ((int(xp/needed_xp*100))*6), 698 + 30), fill=(cor),
                                      radius=25)
            # bg_draw.rounded_rectangle((190, 698, 190, 698+148), fill=(0, 45, 62))
        else:
            bg.paste(profile_bytes, (100, 193), profile_bytes)
            xp_im = Image.open(rf"{imgxp}")
            im1 = xp_im.crop((0, 0, ((int(xp/needed_xp*100))*6), 80))
            bg.paste(im1, (190, 698), im1)

        if staff:
            pass
        else:
            if moldImg != None:
                bsize = (moldImg.size[0], moldImg.size[1])
                bg.paste(moldImg, (int((478 - bsize[0]) / 2) + 2, 100), moldImg)
                # bg.paste(moldImg, (105, 189), moldImg)
            else:
                pass

        buffer = BytesIO()
        bg.save(buffer, 'png')
        buffer.seek(0)

        return buffer

    def rank(self, rank: str, xp: str, xptotal: str, moldName: str, moldImg: str, imgxp: str,
             profile_bytes: BytesIO) -> BytesIO:
        profile_bytes = Image.open(profile_bytes)
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
                     f"Faltam {int(needed_xp - xp):,} de XP para chegar ao Nível {rank + 1}".replace(",", "."),
                     font=self.class_font_role, anchor="ms", fill=(219, 239, 255))

        # Pós
        bg_draw.text((1089 + 70, 797), "NÍVEL ",
                     font=self.class_font_montserrat_regular_nivel, anchor="ms", fill=(219, 239, 255))
        bg_draw.text((1089 + 140, 797), f"{rank + 1}",
                     font=self.class_font_role, anchor="ms", fill=(219, 239, 255))

        bg_draw.rounded_rectangle(
            [(190, 768), (1089, 768 + 30)], 15, fill=(0, 45, 62))

        if moldName != None:

            xp_im = Image.open(rf"{imgxp}")
            im1 = xp_im.crop((0, 0, ((int((needed_xp / xp) * 100)) * 8), 81))
            bg.paste(im1, (190, 767), im1)

            color = xp_im.getpixel(((xp_im.size[0]) - 5, 7))

            rank_text = moldName.title()
            bg_draw.text((635, 622), rank_text, font=self.RadiateSansBoldCondensed, fill=(
                color), anchor="ms", spacing=5)
            border_im = Image.open(r"{}".format(moldImg))
            bsize = (border_im.size[0], border_im.size[1])
            bg.paste(
                border_im, (int((1270 - bsize[0]) / 2) + 2, (int((892 - bsize[1]) / 2) - 150)), border_im)

        else:
            ## user img circle

            profile_bytes = profile_bytes.resize((420, 420))
            prof_elipse = 92
            user_border = (int((1270 / 2) - (profile_bytes.size[0] / 2)), profile_bytes.size[1] + 190)

            bg_draw.ellipse(
                [(user_border[0] - 10, 130), (user_border[0] + profile_bytes.size[1] + 10, user_border[0] + 145)],
                fill=(167, 141, 116))

            ##
            bg.paste(profile_bytes, (user_border[0], (int((892 - user_border[1]) / 2))), profile_bytes)

            bg_draw.rounded_rectangle((190, 768, 190 + ((int((needed_xp / xp) * 100)) * 8), 768 + 30),
                                      fill=(167, 141, 116), radius=25)

        bg_draw.text((695, 730), f"{int(xptotal):,}".replace(",", "."),
                     font=self.XPRadiateSansBoldCondensed, anchor="rs", fill=(219, 239, 255))
        bg_draw.text((705, 730), "XP TOTAL",
                     font=self.class_font_montserrat_regular_nivel, anchor="ls", fill=(219, 239, 255))

        buffer = BytesIO()
        bg.save(buffer, 'png')
        buffer.seek(0)

        return buffer

    @staticmethod
    def neededxp(level: str) -> int:
        return 100 + level * 345


class Shop:
    def __init__(self) -> None:
        self.class_font_montsemibold = ImageFont.truetype(
            'src/fonts/MontserratSemiBold.ttf', 36)
        self.class_font_montbold = ImageFont.truetype(
            'src/fonts/MontserratBold.ttf', 72)
        self.class_font_montbold_ori = ImageFont.truetype(
            'src/fonts/MontserratBold.ttf', 27)
        self.class_font_montbold_ori_menor = ImageFont.truetype(
            'src/fonts/MontserratBold.ttf', 22)
        self.class_font_opensans = ImageFont.truetype(
            'src/fonts/OpenSansRegular.ttf', 30)
        self.class_font_opensansmold = ImageFont.truetype(
            'src/fonts/OpenSansRegular.ttf', 33)
        self.class_font_opensansbold = ImageFont.truetype(
            'src/fonts/OpenSansBold.ttf', 33)
        self.class_font_montserrat = ImageFont.truetype(
            'src/fonts/MontserratRegular.ttf', 27)

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

    #   Gradiente para a esquerda
    # def gradientRight(self, gradient, initial_opacity, bg):
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

    def drawloja(self, total, itens, page: int, coin: int, userImg: BytesIO) -> BytesIO:

        # plain = Image.open(byteImg)
        plain = Image.open(userImg)

        userImg_Big = plain.copy()
        userImg = plain.resize((342, 342))

        bigsize = (userImg.size[0] * 3, userImg.size[1] * 3)
        mask = Image.new('L', bigsize, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(userImg.size, Image.ANTIALIAS)
        userImg.putalpha(mask)

        output = ImageOps.fit(userImg, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)

        bg = Image.new('RGBA', (1280, 950), (0, 45, 62, 255))
        bg_draw = ImageDraw.Draw(bg)

        userImg_Big = userImg_Big.resize((1280, 1280))
        userImg_Big = userImg_Big.crop((0, 330, 1280, 950 + 330))
        mask = Image.new("L", (userImg_Big.size), 90)

        profileFundo = Image.composite(userImg_Big, bg, mask)
        profileBlur = profileFundo.filter(ImageFilter.GaussianBlur(radius=10))
        bg.paste(profileBlur, (0, 0))

        # self.gradientLeft(1.2, 1, bg)
        # self.gradientRight(1.2, 1, bg)
        # quad1 = Image.new(mode = "RGB", size = (311, 110), color = (0, 56, 76))
        # bg.paste(quad1, (0, 30))
        # quad2 = Image.new(mode = "RGB", size = (311, 110), color = (0, 56, 76))
        # bg.paste(quad2, (969, 30))

        # bg_draw.rounded_rectangle([(25, 30), (1245, 150)], 25, fill=(0, 56, 76))

        # Titles
        bg_draw.text((640, 90), "LOJA", font=self.class_font_montbold,
                     anchor="ms", fill=(219, 239, 255))

        # Itens

        largura = 382
        # altura = 190*3
        if page == None or page == 1:
            count = 1
            ccount = 0
            while count <= 6:
                list_itens = list(itens[count - 1].values())

                if int(list_itens[0]['value']) <= int(coin):
                    valueColor = (0, 247, 132)
                else:
                    valueColor = (228, 45, 45)

                itemImg = Image.open(list_itens[0]['img']).resize((128, 128), Image.NEAREST) if str(
                    list_itens[0]['name']) == "Chave" else Image.open(list_itens[0]['img'])
                lar = (itemImg.size[0], itemImg.size[1])
                # print(list_itens)
                if count == 1:
                    ori_pos = 15
                    altura = 180
                    larg_inic = 0
                else:
                    larg_inic = 420 * (count - 1)
                    altura = 180
                    if count == 3:
                        ori_pos = 422 * (count - 1)
                    else:
                        ori_pos = 436 * (count - 1)

                if larg_inic <= 840:
                    # 1 row
                    bg_draw.rounded_rectangle(
                        [(37 + larg_inic, altura), ((larg_inic + largura - 2), 320 + altura)], 25,
                        fill=(0, 247, 132))  # bg verde
                    bg_draw.rounded_rectangle(
                        [(35 + larg_inic, altura), ((larg_inic + largura), 315 + altura)], 25, fill=(0, 45, 62))  # bg
                    bg_draw.rounded_rectangle(
                        [(30 + larg_inic, altura), ((larg_inic + largura) + 5, 95 + altura)], 25,
                        fill=(0, 56, 76))  # titulo

                    if list_itens[0]['dest'] == "False":
                        color = (161, 177, 191)
                    else:
                        color = (255, 182, 0)
                        star = Image.open("src\imgs\extra\Pin-Star.png")
                        star = star.resize((40, 41), Image.NEAREST)
                        bg.paste(star, (19 + larg_inic, altura - 15), star)

                    # details
                    value = f"{int(list_itens[0]['value']):,}"

                    value = value.replace(",", ".")

                    largText, altText = self.class_font_montbold_ori.getsize(
                        list_itens[0]['value'])

                    largID, altID = self.class_font_montbold_ori.getsize(
                        f"ID: #{list_itens[0]['id']}")

                    bg_draw.rounded_rectangle(
                        [(larg_inic + largText + 100, 480), (larg_inic + largText + largID + 140, 43 + 480)], 15,
                        fill=(0, 52, 71))  # id
                    bg_draw.rounded_rectangle(
                        [(larg_inic + 30, 473), (larg_inic + largText + 120, 54 + 473)], 20, fill=(0, 56, 76))  # price

                    bg_draw.text((larg_inic + 27 + (largura) / 2, 260),
                                 list_itens[0]['name'], font=self.class_font_opensansbold, anchor="ms", fill=(color))
                    bg_draw.text((larg_inic + 27 + (largura) / 2, 215),
                                 list_itens[0]['type'], font=self.class_font_opensansmold, anchor="ms", fill=(color))
                    # print(itens[count]['value'])

                    bg_draw.text((larg_inic + 100, 480), value,
                                 font=self.class_font_montbold_ori, fill=(valueColor))
                    bg_draw.text((larg_inic + largText + 130, 483),
                                 f"ID: ", font=self.class_font_montbold_ori_menor, fill=(0, 198, 244))
                    bg_draw.text((larg_inic + largText + 135, 480),
                                 f"    #{list_itens[0]['id']}", font=self.class_font_montbold_ori, fill=(0, 198, 244))




                    # print(lar)
                    if lar[0] > 250:
                        bg.paste(
                            itemImg, (int((larg_inic + 20) + ((largura - lar[0]) / 2)), 350), itemImg)
                    else:
                        bg.paste(itemImg, (35 + 105 + larg_inic, 290), itemImg)

                    ori = Image.open("src\imgs\extra\ori.png")

                    ori = ori.resize((70, 71), Image.NEAREST)
                    bg.paste(ori, (ori_pos, 467), ori)

                    count += 1
                elif larg_inic > 840 and ccount <= 3:

                    if count == 4:
                        larg_baixo = 0
                        ori_pos_baixo = 15
                    else:
                        larg_baixo = 420 * (ccount)
                        if count == 6:
                            ori_pos_baixo = 422 * 2
                        else:
                            ori_pos_baixo = 436 * (ccount)

                    altura = 570

                    bg_draw.rounded_rectangle(
                        [(37 + larg_baixo, altura), ((larg_baixo + largura - 2), 320 + altura)], 25, fill=(0, 247, 132))
                    bg_draw.rounded_rectangle(
                        [(35 + larg_baixo, altura), ((larg_baixo + largura), 315 + altura)], 25, fill=(0, 45, 62))
                    bg_draw.rounded_rectangle(
                        [(30 + larg_baixo, altura), ((larg_baixo + largura) + 5, 95 + altura)], 25, fill=(0, 56, 76))

                    if list_itens[0]['dest'] == "False":
                        color = (161, 177, 191)
                    else:
                        color = (255, 182, 0)
                        star = Image.open("src\imgs\extra\Pin-Star.png")
                        star = star.resize((40, 41), Image.NEAREST)
                        bg.paste(star, (19 + larg_baixo, altura - 15), star)
                    value = f"{int(list_itens[0]['value']):,}"
                    value = value.replace(",", ".")

                    largText, altText = self.class_font_montbold_ori.getsize(
                        list_itens[0]['value'])

                    largID, altID = self.class_font_montbold_ori.getsize(
                        f"ID: #{list_itens[0]['id']}")

                    bg_draw.rounded_rectangle(
                        [(larg_baixo + largText + 100, 865), (larg_baixo + largText + largID + 140, 43 + 865)], 15,
                        fill=(0, 52, 71))
                    bg_draw.rounded_rectangle(
                        [(larg_baixo + 30, 860), (larg_baixo + largText + 120, 54 + 860)], 20, fill=(0, 56, 76))

                    bg_draw.text((larg_baixo + 27 + (largura) / 2, 650),
                                 list_itens[0]['name'], font=self.class_font_opensansbold, anchor="ms", fill=(color))
                    bg_draw.text((larg_baixo + 27 + (largura) / 2, 605),
                                 list_itens[0]['type'], font=self.class_font_opensansmold, anchor="ms", fill=(color))
                    bg_draw.text((larg_baixo + 100, 865), value,
                                 font=self.class_font_montbold_ori, fill=(valueColor))
                    bg_draw.text((larg_baixo + largText + 130, 868),
                                 f"ID: ", font=self.class_font_montbold_ori_menor, fill=(0, 198, 244))
                    bg_draw.text((larg_baixo + largText + 135, 865),
                                 f"    #{list_itens[0]['id']}", font=self.class_font_montbold_ori, fill=(0, 198, 244))

                    if lar[0] > 250:
                        bg.paste(
                            itemImg, (int((larg_baixo + 20) + ((largura - lar[0]) / 2)), 735), itemImg)
                    else:
                        bg.paste(itemImg, (35 + 110 + larg_baixo, 682), itemImg)

                    ori = Image.open("src\imgs\extra\ori.png")
                    ori = ori.resize((70, 71), Image.NEAREST)
                    bg.paste(ori, (ori_pos_baixo, 855), ori)

                    count += 1
                    ccount += 1
        if page != None and page > 1:
            truecount = 6
            count = 1
            ccount = 0
            while truecount < total:
                list_itens = list(itens[truecount].values())

                if int(list_itens[0]['value']) <= int(coin):
                    valueColor = (0, 247, 132)
                else:
                    valueColor = (228, 45, 45)

                itemImg = Image.open(list_itens[0]['img']).resize((128, 128), Image.NEAREST) if str(
                    list_itens[0]['name']) == "Chave" else Image.open(list_itens[0]['img'])
                lar = (itemImg.size[0], itemImg.size[1])

                # print(list_itens)
                if count == 1:
                    ori_pos = 15
                    altura = 180
                    larg_inic = 0
                else:
                    larg_inic = 420 * (count - 1)
                    altura = 180
                    if count == 3 or count == 6:
                        ori_pos = 422 * (count - 1)
                    else:
                        ori_pos = 436 * (count - 1)

                if larg_inic <= 840:
                    # 1 row
                    bg_draw.rounded_rectangle(
                        [(37 + larg_inic, altura), ((larg_inic + largura - 2), 320 + altura)], 25,
                        fill=(0, 247, 132))  # bg verde
                    bg_draw.rounded_rectangle(
                        [(35 + larg_inic, altura), ((larg_inic + largura), 315 + altura)], 25, fill=(0, 45, 62))  # bg
                    bg_draw.rounded_rectangle(
                        [(30 + larg_inic, altura), ((larg_inic + largura) + 5, 95 + altura)], 25,
                        fill=(0, 56, 76))  # titulo

                    if list_itens[0]['dest'] == "False":
                        color = (161, 177, 191)
                    else:
                        color = (255, 182, 0)
                        star = Image.open("src\imgs\extra\Pin-Star.png")
                        star = star.resize((40, 41), Image.NEAREST)
                        bg.paste(star, (19 + larg_inic, altura - 15), star)

                    # details
                    value = f"{int(list_itens[0]['value']):,}"

                    value = value.replace(",", ".")

                    largText, altText = self.class_font_montbold_ori.getsize(
                        list_itens[0]['value'])
                    # print(largText, altText)
                    # bg_draw.rounded_rectangle([(larg_inic+largText+35, 480), (larg_inic+largText+245, 43+480)], 15, fill=(0, 52, 71)) #price
                    bg_draw.rounded_rectangle(
                        [(larg_inic + largText + 35, 480), (larg_inic + largText + 245, 43 + 480)], 15,
                        fill=(0, 52, 71))  # price
                    bg_draw.rounded_rectangle(
                        [(larg_inic + 30, 473), (larg_inic + largText + 120, 54 + 473)], 20, fill=(0, 56, 76))  # price

                    bg_draw.text((larg_inic + 27 + (largura) / 2, 260),
                                 list_itens[0]['name'], font=self.class_font_opensansbold, anchor="ms", fill=(color))
                    bg_draw.text((larg_inic + 27 + (largura) / 2, 215),
                                 list_itens[0]['type'], font=self.class_font_opensansmold, anchor="ms", fill=(color))
                    # print(itens[count]['value'])

                    bg_draw.text((larg_inic + 100, 480), value,
                                 font=self.class_font_montbold_ori, fill=(valueColor))
                    bg_draw.text((larg_inic + largText + 130, 483),
                                 f"ID: ", font=self.class_font_montbold_ori_menor, fill=(0, 198, 244))
                    bg_draw.text((larg_inic + largText + 135, 480),
                                 f"    #{list_itens[0]['id']}", font=self.class_font_montbold_ori, fill=(0, 198, 244))

                    # print(lar)
                    if lar[0] > 250:
                        bg.paste(
                            itemImg, (int((larg_inic) + ((largura - lar[0]) / 2)), 350), itemImg)
                    else:
                        bg.paste(itemImg, (int((larg_inic) + ((largura - lar[0]) / 2) + 27), 290), itemImg)

                    ori = Image.open("src\imgs\extra\ori.png")

                    ori = ori.resize((70, 71), Image.NEAREST)
                    bg.paste(ori, (ori_pos, 467), ori)

                    count += 1
                    truecount += 1
                elif larg_inic > 840 and ccount <= 3:

                    if count == 4:
                        larg_baixo = 0
                        ori_pos_baixo = 15
                    else:
                        larg_baixo = 420 * (ccount)
                        if count == 3 or count == 6:
                            ori_pos_baixo = 422 * (count - 1)
                        else:
                            ori_pos_baixo = 436 * (count - 1)

                    altura = 570

                    bg_draw.rounded_rectangle(
                        [(37 + larg_baixo, altura), ((larg_baixo + largura - 2), 320 + altura)], 25, fill=(0, 247, 132))
                    bg_draw.rounded_rectangle(
                        [(35 + larg_baixo, altura), ((larg_baixo + largura), 315 + altura)], 25, fill=(0, 45, 62))
                    bg_draw.rounded_rectangle(
                        [(30 + larg_baixo, altura), ((larg_baixo + largura) + 5, 95 + altura)], 25, fill=(0, 56, 76))

                    if list_itens[0]['dest'] == "False":
                        color = (161, 177, 191)
                    else:
                        color = (255, 182, 0)
                        star = Image.open("src\imgs\extra\Pin-Star.png")
                        star = star.resize((40, 41), Image.NEAREST)
                        bg.paste(star, (19 + larg_baixo, altura - 15), star)
                    value = f"{int(list_itens[0]['value']):,}"
                    value = value.replace(",", ".")

                    largText, altText = self.class_font_montbold_ori.getsize(
                        list_itens[0]['value'])

                    bg_draw.rounded_rectangle(
                        [(larg_baixo + largText + 27, 865), (larg_baixo + largText + 245, 43 + 865)], 15,
                        fill=(0, 52, 71))
                    bg_draw.rounded_rectangle(
                        [(larg_baixo + 30, 860), (larg_baixo + largText + 120, 54 + 860)], 20, fill=(0, 56, 76))

                    bg_draw.text((larg_baixo + 27 + (largura) / 2, 650),
                                 list_itens[0]['name'], font=self.class_font_opensansbold, anchor="ms", fill=(color))
                    bg_draw.text((larg_baixo + 27 + (largura) / 2, 605),
                                 list_itens[0]['type'], font=self.class_font_opensansmold, anchor="ms", fill=(color))
                    bg_draw.text((larg_baixo + 100, 865), value,
                                 font=self.class_font_montbold_ori, fill=(valueColor))
                    bg_draw.text((larg_baixo + largText + 130, 868),
                                 f"ID: ", font=self.class_font_montbold_ori_menor, fill=(0, 198, 244))
                    bg_draw.text((larg_baixo + largText + 135, 865),
                                 f"    #{list_itens[0]['id']}", font=self.class_font_montbold_ori, fill=(0, 198, 244))

                    if lar[0] > 250:
                        bg.paste(
                            itemImg, (int((larg_baixo) + ((largura - lar[0]) / 2)), 735), itemImg)
                    else:
                        bg.paste(itemImg, (int((larg_baixo + 20) + ((largura - lar[0]) / 2)), 682), itemImg)

                    ori = Image.open("src\imgs\extra\ori.png")
                    ori = ori.resize((70, 71), Image.NEAREST)
                    bg.paste(ori, (ori_pos_baixo, 855), ori)

                    count += 1
                    ccount += 1
                    truecount += 1

        bg_draw.text((100, 54), "Suas oris",
                     font=self.class_font_montserrat, fill=(212, 255, 236))
        bg.paste(ori, (25, 56), ori)
        value = f"{int(coin):,}".replace(",", ".")
        bg_draw.text((100, 90), value,
                     font=self.class_font_montserrat, fill=(0, 247, 132))

        bg_draw.text((1063, 55), "Página Atual",
                     font=self.class_font_montserrat, fill=(161, 177, 191))

        bg_draw.text((1200, 90), "{}".format(page),
                     font=self.class_font_montbold_ori, fill=(219, 239, 255))
        # SUBTITLE
        bg_draw.text((630, 135), "Use os botões abaixo par navegar entre as páginas.",
                     font=self.class_font_opensans, anchor="ms", fill=(219, 239, 255))

        buffer = BytesIO()
        bg.save(buffer, 'png')
        buffer.seek(0)
        return buffer


class Utilities:
    def __init__(self):
        self.database = Database
        self.rankcard = Rank()
        self.shop = Shop()


utilities = Utilities()
