import os

from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
from base.classes.functions.admFunctions import fontPath


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


class drawProfile:
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
        if img_cima is None:
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

        input_im = Image.new(mode="RGB", size=input_im, color=(0, 45, 62))

        mask = Image.new('L', img_cima.size)
        bg_draw = ImageDraw.Draw(mask)
        bg_draw.ellipse((-600, int(650 / 2 - 20), int(1280 + 600),
                         int(1280 / 1.5 - 150)), fill="white")
        bg_draw.rounded_rectangle(
            (-70, 0, int(1280 + 70), int(1280 / 2 + 40)), 0, fill="black")
        bg_draw.rounded_rectangle(
            (-70, int(650 / 1.5 - 20), int(1280 + 70), int(1280 / 2 + 40)), 700, fill="white")
        bg_draw.rounded_rectangle(
            (-5, int(650 / 2 - 20), int(1280 + 5), int(1280 / 2)), 35, fill="white")

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

        mask = Image.new('L', bg.size)

        image = self.gradient(img_baixo=mask, img_cima=None,
                              colors=["black", "white"])

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

    def profile(
            self,
            user: str,
            badge_images,
            banner: str,
            moldImage: str,
            userInfo: str,
            userSpark: int,
            userOri: int,
            userBirth: str,
            staff: None,
            rankName,
            rankR: str,
            rankG: str,
            rankB: str,
            profile_bytes: BytesIO
    ) -> BytesIO:
        try:
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

            # banner = banner.resize((1280, 1280))
            # banner = banner.crop(
            #    (0, 420, 1280, 1280 + 420))
            mask = Image.new("L", bg.size, 90)

            # BORDA DO CARALHO
            ma = Image.open(
                "src/imgs/extra/perfil/Discord-Border.png").convert("L")

            mask = Image.new("L", (1280, 1280))
            mask.paste(ma, (0, int(banner.size[1] / 2 - 20)))
            color_palette = [(186, 162, 125), (189, 142, 71)]
            region = Rect(0, 0, mask.size[0], mask.size[1])
            width, height = region.max.x + 1, region.max.y + 1
            image = Image.new("RGB", (width, height), Gradient.WHITE)
            draw = ImageDraw.Draw(image)
            Gradient.horz_gradient(draw, region, Gradient.gradient_color, color_palette)
            image = image.resize(
                mask.size, Image.Resampling.NEAREST).convert("RGBA")
            image = Image.composite(image, bg, mask)
            bg.paste(image, (0, 0))

            # user
            # bg_draw.rounded_rectangle(
            #    (25, 27, 420 + 25, 625 + 27), 50, fill=(0, 45, 62))
            username = user.encode("ascii", "ignore")
            username = username.decode()

            bg_draw.text((105, 603), username, font=self.class_font_bold_name,
                         fill=(219, 239, 255), anchor="ls", spacing=5)
            # bg_draw.text((105, 653), userid, font=self.class_font_bold_id,
            #             fill=(175, 191, 204), anchor="ls", spacing=5)

            user_border = (profile_bytes.size[0] +
                           prof_elipse + 12, profile_bytes.size[1] + 185 + 12)

            rolePosition = 870
            spacing = 10
            role_top = 513
            if rankName is None:
                rank_text = "Novato"
                cor = (167, 141, 116)
            else:
                rank_text = rankName.upper()
                cor = (int(rankR), int(rankG), int(rankB))
            if staff:
                staff.reverse()
                # classe
                bg_draw.ellipse([prof_elipse, 188, user_border],
                                fill=staff[0].values()[0]['color'])

                count = 0
                while count <= len(staff) - 1 and count <= 2:
                    list_roles = list(staff[count].values())

                    # info
                    e, d, largText, altText = self.class_font_role.getbbox(
                        list_roles[0]['name'])
                    if rolePosition + largText + 22 > 1280:
                        role_top = 575
                        rolePosition = 870

                    bg_draw.rounded_rectangle(
                        (
                            (
                                rolePosition if rolePosition == 870 else rolePosition + spacing + 50,
                                role_top - int(spacing + 15)
                            ),
                            (
                                rolePosition + int(largText + 60) + spacing if rolePosition == 870 \
                                    else rolePosition + int(largText + 60) + spacing + 50,
                                role_top + int(spacing + 15)
                            )
                        ), 28,
                        fill=(list_roles[0]['color']), width=3)
                    bg_draw.text((
                        rolePosition + largText + 33 if rolePosition == 870 else rolePosition + largText + 33 + spacing + 50,
                        role_top + spacing),
                        list_roles[0]['name'], font=self.class_font_role, fill=(0, 45, 62), anchor="rs", spacing=5)

                    rolePosition = rolePosition + largText + 32
                    count += 1
            else:
                e, d, largText, altText = self.class_font_role.getbbox("Membro")
                bg_draw.rounded_rectangle(
                    ((rolePosition, 488), (rolePosition + largText + 22, 513 + 25)), 28, fill=(133, 133, 133), width=3)
                bg_draw.text((rolePosition + largText + 15, 525), "Membro", font=self.class_font_role, fill=(
                    0, 45, 62), anchor="rs", spacing=5)

                rolePosition = rolePosition + 166

                if moldImage is None:
                    bg_draw.ellipse([prof_elipse, 188, user_border],
                                    fill=cor)
                print("final else staff")
            # BADGES
            if len(badge_images) > 0:
                print("badge_images")
                count = 0
                inic_larg = int(banner.size[0] - 150)
                inic_alt = int(banner.size[1] / 2)

                for badge in badge_images:
                    badge = Image.open(badge)
                    badge = badge.resize(
                        (int(badge.size[0] / 4), int(badge.size[1] / 4)), Image.Resampling.NEAREST)
                    bg.paste(badge, (inic_larg, inic_alt), badge)
                    inic_larg -= (badge.size[0] + 10)
                print("after badge_images")
            # img user
            bg.paste(output, (97, 193), output)

            # info
            bg_draw.rounded_rectangle(
                ((480, int(1280 - 524)), (480 + 764, int(1280 - 215))), 25, fill=(0, 45, 62))
            bg_draw.text((516, 776), 'Biografia:', font=self.class_font_montserrat_bday, fill=(
                161, 177, 191), spacing=5)

            if not userInfo:
                userInfo = "Não há o que bisbilhotar aqui."

            lines = self.text_wrap(userInfo, self.class_font_bold_info_sans, 600)
            line_height = self.class_font_bold_info.getbbox(userInfo)[3]
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
                ((35, int(1280 - 524)), (int(1280 - 840), int(1280 - 387))), 25, fill=(0, 45, 62))  # spark

            spark = Image.open("src/imgs/extra/spark.png")
            spark = spark.resize((110, 110), Image.Resampling.NEAREST)
            bg.paste(spark, (45, int(1280 - 504)), spark)
            value = f"{int(userSpark):,}".replace(",", ".")
            bg_draw.text((170, int(1280 - 508)), "Sparks",
                         font=self.class_font_montserrat_bday, fill=(153, 177, 191))
            bg_draw.text((170, int(1280 - 458)), value,
                         font=self.class_font_bold_ori_bday, fill=(219, 239, 255))
            print("src/imgs/extra/spark")
            # ori
            bg_draw.rounded_rectangle(
                ((35, int(1280 - 352)), (int(1280 - 840), int(1280 - 215))), 25, fill=(0, 53, 49))  # ori

            ori = Image.open("src/imgs/extra/ori.png")
            ori = ori.resize((100, 100), Image.Resampling.NEAREST)
            bg.paste(ori, (50, int(1280 - 330)), ori)
            value = f"{int(userOri):,}".replace(",", ".")
            bg_draw.text((170, int(1280 - 335)), "Oris",
                         font=self.class_font_montserrat_bday, fill=(212, 255, 236))
            bg_draw.text((170, int(1280 - 285)), value,
                         font=self.class_font_bold_ori_bday, fill=(0, 247, 132))

            # Bday
            bg_draw.rounded_rectangle(
                ((35, int(1280 - 178)), (int(1280 - 840), int(1280 - 40))), 25, fill=(54, 46, 59))  # Bday

            if userBirth != "???":
                userBirth = userBirth.split("/")
                dia = userBirth[0]
                mes = userBirth[1]
                userBirth = f"{dia}/{mes}"
            else:
                userBirth = "??/??"

            # image
            cake = Image.open("src/imgs/extra/cake.png")
            cake = cake.resize((70, 92), Image.Resampling.NEAREST)
            bg.paste(cake, (65, int(1280 - 155)), cake)

            # text
            value = f"{int(userSpark):,}".replace(",", ".")
            bg_draw.text((170, int(1280 - 165)), "Aniversário",
                         font=self.class_font_montserrat_bday, fill=(255, 212, 216))
            bg_draw.text((int(170), int(1280 - 110)), userBirth,
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
                    ((cars_position, int(1280 - 178)),
                     (cars_position + 140, int(1280 - 40))),
                    radius=30, fill=cars_bg[0], outline=car_border, width=2)

                bg_draw.text((cars_position + 70, int(1280 - 185) + 120), "?",
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

            # bg.paste(image, (0, 0))
            # bg.paste(gradient, (0, 0), gradient)
            # bg.show()
            buffer = BytesIO()
            bg.save(buffer, 'png')
            buffer.seek(0)

            mask.close()
            bg.close()

            return buffer
        except Exception as e:
            raise e


drawprofile = drawProfile().profile
