import json
import requests
import os
import uuid

from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


# * Créditos: IVI
# * https://stackoverflow.com/questions/36588126/uuid-is-not-json-serializable#:~:text=import%20json%0Afrom%20uuid%20import%20UUID%0A%0A%0Aclass%20UUIDEncoder(json.JSONEncoder)%3A%0A%20%20%20%20def%20default(self%2C%20obj)%3A%0A%20%20%20%20%20%20%20%20if%20isinstance(obj%2C%20UUID)%3A%0A%20%20%20%20%20%20%20%20%20%20%20%20%23%20if%20the%20obj%20is%20uuid%2C%20we%20simply%20return%20the%20value%20of%20uuid%0A%20%20%20%20%20%20%20%20%20%20%20%20return%20obj.hex%0A%20%20%20%20%20%20%20%20return%20json.JSONEncoder.default(self%2C%20obj)
class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


class fontPath():
    _path = os.path.abspath('_temp')

    exist = os.path.exists(_path)
    if not exist:
        os.mkdir(_path)
    pathMonserrat = os.path.abspath('src/fonts/Montserrat/')
    pathOpen = os.path.abspath('src/fonts/Opensans/')

    if not os.path.exists(pathMonserrat):
        print("Não consegui encontrar o caminho para %s" % (pathMonserrat))

    if not os.path.exists(pathOpen):
        print("Não consegui encontrar o caminho para %s" % (pathOpen))


class Gradient():
    def __init__(**kwargs):
        super().__init__(kwargs)

    # GRANDIENT
    BLACK, DARKGRAY, GRAY = ((0, 0, 0), (63, 63, 63), (127, 127, 127))
    LIGHTGRAY, WHITE = ((191, 191, 191), (255, 255, 255))
    BLUE, GREEN, RED = ((0, 0, 255), (0, 255, 0), (255, 0, 0))

    def gradient_color(minval, maxval, val, color_palette):
        """ Computes intermediate RGB color of a value in the range of minval
            to maxval (inclusive) based on a color_palette representing the range.
        """
        max_index = len(color_palette) - 1
        delta = maxval - minval
        if delta == 0:
            delta = 1
        v = float(val - minval) / delta * max_index
        i1, i2 = int(v), min(int(v) + 1, max_index)
        (r1, g1, b1), (r2, g2, b2) = color_palette[i1], color_palette[i2]
        f = v - i1
        return int(r1 + f * (r2 - r1)), int(g1 + f * (g2 - g1)), int(b1 + f * (b2 - b1))

    def horz_gradient(draw, rect, color_func, color_palette):
        minval, maxval = 1, len(color_palette)
        delta = maxval - minval
        width = float(rect.width)  # Cache.
        for x in range(rect.min.x, rect.max.x + 1):
            f = (x - rect.min.x) / width
            val = minval + f * delta
            color = color_func(minval, maxval, val, color_palette)
            draw.line([(x, rect.min.y), (x, rect.max.y)], fill=color)

    def vert_gradient(draw, rect, color_func, color_palette):
        minval, maxval = 1, len(color_palette)
        delta = maxval - minval
        height = float(rect.height)  # Cache.
        for y in range(rect.min.y, rect.max.y + 1):
            f = (y - rect.min.y) / height
            val = minval + f * delta
            color = color_func(minval, maxval, val, color_palette)
            draw.line([(rect.min.x, y), (rect.max.x, y)], fill=color)


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


class Rank:

    def __init__(self) -> None:
        # PERFIL
        self.class_font_semibold = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratSemiBold.ttf'), 36)

        self.class_font_bold_name = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratBold.ttf'), 72)

        self.class_font_bold_id = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratMedium.ttf'), 42)

        self.class_font_bold_info_sans = ImageFont.truetype(
            os.path.join(fontPath.pathOpen, 'OpenSansRegular.ttf'), 36)

        self.class_font_bold_xp = ImageFont.truetype(
            os.path.join(fontPath.pathOpen, 'OpenSansBold.ttf'), 48)

        self.class_font_bold_info = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratBold.ttf'), 36)

        self.class_font_montserrat = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratRegular.ttf'), 36)

        self.class_font_montserrat_bday = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratMedium.ttf'), 36)

        self.class_font_bold_ori_bday = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratBold.ttf'), 42)

        self.class_font_role = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratBold.ttf'), 30)

        self.RadiateSansBoldCondensed = ImageFont.truetype(
            os.path.join(fontPath.pathOpen, 'OpenSansCondensedBold.ttf'), 65)

        # NIVEL
        # "LOJA"
        self.montserrat_extrabold_loja = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratExtraBold.ttf'), 50)

        # COINS TITLE TEXT
        self.montserrat_medium_coins = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratMedium.ttf'), 23)

        # COINS VALUE TEXT
        self.montserrat_bold_coins = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratBold.ttf'), 28)

        # Nome do item
        self.montserrat_bold_name = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratBold.ttf'), 20)

        # Tipo do item
        self.montserrat_bold_type = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratBold.ttf'), 22)

        # Valor
        self.montserrat_blackitalic_value = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratBlackItalic.ttf'), 40)

        # Categoria do item
        self.montserrat_semibold_category = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratSemiBold.ttf'), 20)

        # "Página"
        self.montserrat_semibold = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratSemiBold.ttf'), 30)

        # Número da página
        self.montserrat_extrabold_pageNumb = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratExtraBold.ttf'), 30)

        # /equipar #ID [diff]
        self.montserrat_extrabolditalic_equip = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratExtraBoldItalic.ttf'), 25)
        # antigas

        self.class_font_montserrat_regular_nivel = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratRegular.ttf'), 30)

        self.XPRadiateSansBoldCondensed = ImageFont.truetype(
            os.path.join(fontPath.pathOpen, 'RadiateSansBoldCondensed.ttf'), 85)

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
        if font.getbbox(text)[2] <= max_width:
            lines.append(text)
        else:
            # split the line by spaces to get words
            words = text.split(' ')
            i = 0
            # append every word to a line while its width is shorter than image width
            while i < len(words):
                line = ''
                while i < len(words) and font.getbbox(line + words[i])[2] <= max_width:
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
        # input_im = Image.open(src)
        if img_cima == None:
            bg_draw = ImageDraw.Draw(img_baixo)
            bg_draw.ellipse(
                (-600, int(650 / 2 - 20), int(1280 + 600), int(1280 / 1.5 - 150)), fill=colors[1])
            bg_draw.rounded_rectangle(
                (-70, 0, int(1280 + 70), int(1280 / 2 + 40)), 0, fill=colors[0])
            bg_draw.rounded_rectangle(
                (-70, int(650 / 1.5 - 20), int(1280 + 70), int(1280 / 2 + 40)), 700, fill=colors[1])
            bg_draw.rounded_rectangle(
                (-5, int(650 / 2 - 20), int(1280 + 5), int(1280 / 2)), 35, fill=colors[1])
            return img_baixo

        # input_im = Image.new(mode="RGB", size=bg.size, color=colors[0])

        input_im = img_cima.size

        input_im = Image.new(mode="RGB", size=(input_im), color=(0, 45, 62))

        mask = Image.new('L', (img_cima.size))
        bg_draw = ImageDraw.Draw(mask)
        bg_draw.ellipse((-600, int(650 / 2 - 20), int(1280 + 600),
                         int(1280 / 1.5 - 150)), fill=("white"))
        bg_draw.rounded_rectangle(
            (-70, 0, int(1280 + 70), int(1280 / 2 + 40)), 0, fill=("black"))
        bg_draw.rounded_rectangle(
            (-70, int(650 / 1.5 - 20), int(1280 + 70), int(1280 / 2 + 40)), 700, fill=("white"))
        bg_draw.rounded_rectangle(
            (-5, int(650 / 2 - 20), int(1280 + 5), int(1280 / 2)), 35, fill=("white"))

        gradient = 1
        initial_opacity = 2

        if input_im.mode != 'RGBA':
            input_im = input_im.convert('RGBA')
        width, height = input_im.size

        alpha_gradient = Image.new('L', (1, height), color=0xFF)
        for x in range(height):
            a = int((initial_opacity * 255.) *
                    (1. - gradient * float(x) / height))

            if a > 0:
                alpha_gradient.putpixel((0, -x), a)
            else:
                alpha_gradient.putpixel((0, -x), 0)
        alpha = alpha_gradient.resize(input_im.size)
        alpha.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

        black_im = Image.new('RGBA', (width, height), color=0)
        black_im = black_im.resize(input_im.size)
        black_im.putalpha(alpha)
        img_cima.paste(img_baixo, (0, int(650 / 2 - 20)))

        output = Image.composite(input_im, img_cima, black_im)

        # make composite with original image

        return output

    def draw_mask(self, banner):
        bg = Image.new('RGBA', (1280, 1280), (0, 33, 46, 255))

        banner_bg = banner

        bg_copy = Image.new('RGBA', (1280, 1280), (0, 45, 62, 255))

        banner_bg_cima = banner_bg.crop(
            (0, 0, 1280, int(banner_bg.size[1] / 2)))

        banner_bg_baixo = banner_bg.crop(
            (0, int(banner_bg.size[1] / 2 - 20), 1280, 1280))
        banner_bg_baixo = banner_bg_baixo.filter(
            ImageFilter.GaussianBlur(radius=10))

        bg.paste(banner_bg_cima, (0, 0), banner_bg_cima)
        # bg_copy.paste(banner_bg_baixo, (0, int(650/2 - 20)))

        mask = Image.new('L', (bg.size))

        image = self.gradient(img_baixo=mask, img_cima=None,
                              colors=[("black"), ("white")])

        back = Image.composite(bg_copy, bg, image)
        # bg.paste(image, (0, int(650/2 - 20)), image)

        image2 = self.gradient(img_baixo=banner_bg_baixo, img_cima=bg,
                               colors=[None])

        bg = Image.composite(image2, back, image)

        # bg_cima = self.gradient(
        #    img_baixo=banner_bg_baixo, img_cima=banner_bg_cima, colors=[(0, 45, 62)])

        # bg = Image.composite(banner_bg_baixo, image2, image)

        # bg = Image.composite(image2, bg, image)

        return bg

    def draw(
            self,
            user: str,
            userRank: str,
            userXp: str,
            titleImg: str,
            moldName: str,
            moldImage: str,
            moldRounded: str,
            userInfo: str,

            userSpark: int,
            userBirth: str,
            staff: None,
            rankName,
            rankR: str,

            rankG: str,
            rankB: str,
            rankImgxp,
            profile_bytes: BytesIO
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
        mask = mask.resize(profile_bytes.size, Image.Resampling.LANCZOS)
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
        userid = (f"#{splitUsername[1]}")
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
                e, d, largText, altText = self.class_font_role.getbbox(
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
                    fill=(0, 45, 62), anchor="rs", spacing=5)

                rolePosition = rolePosition + largText + 32
                count += 1

        else:

            # info
            e, d, largText, altText = self.class_font_role.getbbox("Membro")
            bg_draw.rounded_rectangle(
                [(rolePosition, 168), (rolePosition + largText + 22, 224)], 28, fill=(133, 133, 133), width=3)
            bg_draw.text((rolePosition + largText + 12, 206), "Membro", font=self.class_font_role, fill=(0, 45, 62),
                         anchor="rs", spacing=5)

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
            tsize = (title_img.size[0], title_img.size[1] + 5)
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
        line_height = self.class_font_bold_info.getbbox(userInfo)[3]
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

        ori = Image.open("src/imgs/extra/ori.png")
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

        cake = Image.open("src/imgs/extra/cake.png")
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
        width, height = region.max.x + 1, region.max.y + 1
        image = Image.new("RGB", (width, height), Gradient.WHITE)
        draw = ImageDraw.Draw(image)
        Gradient.horz_gradient(draw, region, Gradient.gradient_color, color_palette)
        image = image.resize(mask.size, Image.NEAREST).convert("RGBA")
        bg = Image.composite(image, bg, mask)
        # bg.paste(image, (0, 0))
        # bg.paste(gradient, (0, 0), gradient)

        buffer = BytesIO()
        bg.save(buffer, 'png')
        buffer.seek(0)

        mask.close()
        bg.close()

        return buffer

    # PERFIL

    def drawiventory(self, banner, spark, ori, items, total) -> BytesIO:

        # STATIC IMAGES
        spark_img = Image.open("src/imgs/extra/spark.png")
        ori_img = Image.open("src/imgs/extra/ori.png")

        icon = Image.open(
            "src/imgs/extra/inventario/Inventory-Icon-Spinovel.png")

        # ITEM CATEGORIE IMAGES
        comumCat_image = Image.open(
            "src/imgs/extra/inventario/Loja-Comum.png")
        raroCat_image = Image.open(
            "src/imgs/extra/inventario/Loja-Raro.png")
        lendCat_image = Image.open(
            "src/imgs/extra/inventario/Loja-Lendario.png")

        total_page = total / 12 if total / 12 == int() else int(total / 12 + 0.9)

        images = []
        count = 0

        if total_page > 12:
            total_page = total_page + 1
        print(total_page)

        try:
            for i in range(total_page):

                plain = Image.new('RGBA', (1280, 1280), (0, 45, 62, 255))
                banner_ = Image.open(banner)
                banner_Big = banner_.resize((1280 + 630, 650 + 630))
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

                bg_draw.text((700, 1240), "%s" % (i + 1,),
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

                        itemImg = Image.open(
                            list_itens[0]['img']).convert("RGBA")
                        if str(list_itens[0]['type']) == "Banner":

                            itemImg = itemImg.resize(
                                (235, 105), Image.Resampling.NEAREST)
                            itemImg = self.add_corners(itemImg, 20)

                        elif str(list_itens[0]['type']) == "Utilizavel":
                            itemImg = itemImg.resize(
                                (128, 128), Image.Resampling.NEAREST)

                        elif str(list_itens[0]['type']) == "Badge":
                            itemImg = itemImg.resize(
                                (
                                    int(itemImg.size[0] / 2.5),
                                    int(itemImg.size[1] / 2.5)
                                ),
                                Image.Resampling.NEAREST
                            )

                        elif str(list_itens[0]['type']) == "Titulo":
                            pass
                        else:
                            lar = (itemImg.size[0], itemImg.size[1])
                            itemImg = itemImg.resize(
                                (int(itemImg.size[0] / 2.5), int(itemImg.size[1] / 2.5)), Image.Resampling.NEAREST)

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

                        if largura > 660:
                            ccount = 0
                            tcount += 1
                            altura = int((img.size[0] - 18) * tcount)
                            if altura == 777:
                                altura += 64

                        largura = ((img.size[0] + 35) * ccount) + \
                                  (35 if ccount == 0 else 35)

                        if altura > 1280:
                            break

                        # ROW BACKGROUND IMAGE 1
                        plain.paste(img, (largura, altura), img)

                        # ROW ITEM IMAGE 1
                        plain.paste(
                            itemImg, (int(largura + int((img.size[0] - lar[0]) / 2)),
                                      int(altura + int((img.size[1] - lar[1]) / 2)) - 40), itemImg)
                        # TEXTS
                        # ITEM TYPE
                        bg_draw.text((90 + largura, altura),
                                     list_itens[0]['type'], fill=(0, 45, 62), anchor="ma",
                                     font=self.montserrat_bold_type)

                        # ITEM NAME
                        bg_draw.text((int(largura + int((img.size[0] / 2))),
                                      int(altura + int((img.size[1] / 2))) + 50),
                                     list_itens[0]['name'], fill=(215, 235, 251), anchor="ma",
                                     font=self.montserrat_bold_name)

                        # ITEM EQUIP
                        bg_draw.text(
                            (int(largura + int((img.size[0] / 2))),
                             int(altura + int((img.size[1] / 2))) + 103),
                            "%s %s" % (
                                "/equipar" if list_itens[0]['type'].upper() != "UTILIZAVEL" else "/usar",
                                list_itens[0]['id'],
                            ), fill=(0, 45, 62),
                            anchor="ma",
                            font=self.montserrat_extrabolditalic_equip
                        )

                        ccount += 1
                        count += 1
                except Exception as a:
                    print(a)
                    raise a
                plain = plain.convert('RGB')
                try:
                    u = uuid.uuid4().hex

                    plain.save(f'{os.path.join("_temp", u)}.jpg',
                               'JPEG')  # optimize=True
                    # buffer.seek(0)

                except Exception as i:
                    print(i)
                    raise i
                else:
                    images.append(f"{u}.jpg")
            return images
        except Exception as f:
            print(f)
            raise f


class Top:
    def __init__(self) -> None:
        self.opensans_bold_name = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratBold.ttf'), 40)
        self.opensans_regular_lilname = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratRegular.ttf'), 27)
        self.opensans_bold_coin = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratMedium.ttf'), 40)
        self.opensans_bold_count = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratBold.ttf'), 18)

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
            line_height = self.opensans_bold_name.getbbox(text_name)[3]
            name, cod = text_name.split('#')
            bg_draw.text(((user_img.size[1] * 2) + 70, size + 50), name,
                         font=self.opensans_bold_name, fill=(user_font_color[0]), anchor='ls')
            bg_draw.text(((user_img.size[1] * 2) + 70, size + 80),
                         f"#{cod}", font=self.opensans_regular_lilname, fill=(user_font_color[1]), anchor='ls')

            # mask to round image
            bigsize = (user_img.size[0] * 3, user_img.size[1] * 3)

            mask = Image.new('L', bigsize, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + bigsize, fill=255)
            mask = mask.resize(user_img.size, Image.Resampling.LANCZOS)
            user_img.putalpha(mask)

            output = ImageOps.fit(user_img, mask.size, centering=(0.5, 0.5))
            output.putalpha(mask)

            plain.paste(output, (110, size + 10), output)

            # count circle
            bg_draw.ellipse([(105, size + 10), (135, size + 40)],
                            fill=(255, 255, 255, 255))
            bg_draw.text((121, size + 32), str(count + 1),
                         font=self.opensans_bold_count, fill=(0, 30, 41, 255), anchor='ms')

            # rounded value
            bg_draw.rounded_rectangle(
                [(880, size + 20), (1200, size + 80)], 15, fill=(user_coin_bg))

            value = users[0]['value']
            tipo = str(users[0]['type'])

            if tipo.title() == "Ori":
                value = f"{int(users[0]['value']):,}"
                value = value.replace(",", ".")

                txt_color = (0, 247, 132, 255)
                bg_draw.text(
                    (1060, size + 72), value, font=self.opensans_bold_coin, fill=txt_color, anchor='md')

                ori = oriCopy.resize((85, 85), Image.NEAREST)
                plain.paste(ori, (860, size + 10), ori)

                bg_draw.text((100, 70),
                             f"Confira os 10 usuários com a maior quantidade de {users[0]['type']} do servidor.",
                             font=self.opensans_regular_lilname, fill=(0, 247, 132), anchor='ls')
                bg_draw.text((rankFundo.size[0] - 100, rankFundo.size[1] - 15),
                             f"Você está na {user_position}ª Colocação.",
                             font=self.opensans_regular_lilname, fill=(0, 247, 132), anchor='rs')

            elif tipo.title() == "Nivel":

                txt_color = (219, 239, 255, 255)
                bg_draw.text(
                    (1060, size + 72), value, font=self.opensans_bold_coin, fill=txt_color, anchor='md')

                rank_img = Image.open(users[0]['rank_image'])
                rank_img = rank_img.resize((85, 85), Image.NEAREST)
                plain.paste(rank_img, (860, size + 10), rank_img)

                bg_draw.text((100, 70),
                             f"Confira os 10 usuários com a maior quantidade de {users[0]['type']} do servidor.",
                             font=self.opensans_regular_lilname, fill=(0, 247, 132), anchor='ls')
                bg_draw.text((rankFundo.size[0] - 100, rankFundo.size[1] - 15),
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
        self.rankcard = Rank()
        self.topcard = Top()


utilities = Utilities()
