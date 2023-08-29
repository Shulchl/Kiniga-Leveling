import os

from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
from base.classes.functions.admFunctions import fontPath


class drawLevel:
    def __init__(self):
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

        self.class_font_montserrat_regular_nivel = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratRegular.ttf'), 30)

        self.XPRadiateSansBoldCondensed = ImageFont.truetype(
            os.path.join(fontPath.pathOpen, 'RadiateSansBoldCondensed.ttf'), 85)

    @staticmethod
    def neededxp(level: int) -> int:
        return ((level * level) * 300) + 100

    def level(
            self,
            rank: str,
            xp: str,
            xptotal: str,
            moldName: str,
            moldImg: str,
            imgxp: str,
            profile_bytes
    ) -> BytesIO:
        profile_bytes = Image.open(str(profile_bytes))
        profile_bytes_imenso = profile_bytes.copy()

        # profile_bytes = profile_bytes.resize((1270, 1270))

        bigsize = (profile_bytes.size[0] * 3, profile_bytes.size[1] * 3)
        mask = Image.new('L', bigsize, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(profile_bytes.size, Image.Resampling.LANCZOS)
        profile_bytes.putalpha(mask)

        output = ImageOps.fit(profile_bytes, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)

        bg = Image.new('RGBA', (1270, 892), (0, 45, 62, 255))
        bg_draw = ImageDraw.Draw(bg)

        profile_bytes_imenso = profile_bytes_imenso.resize((1270, 892))
        # profile_bytes_imenso = profile_bytes_imenso.crop(
        #    (0, 420, 1280, 823+420))
        mask = Image.new("L", profile_bytes_imenso.size, 90)

        profileFundo = Image.composite(profile_bytes_imenso, bg, mask)
        profileBlur = profileFundo.filter(ImageFilter.GaussianBlur(radius=30))
        bg.paste(profileBlur, (0, 0))

        # xp_text = f'Faltam {} para chegar ao Nível {}:'.format(xp_remain, at_rank-1)

        bg_draw.rounded_rectangle(
            ((190, 768), (1089, 768 + 28)), 15, fill=(0, 45, 62))

        # xp_in = self.gradientLeft()
        # xp_im = Image.open(r"src/bg/xpFill-background.png")
        # im1 = xp_im.crop((0, 0, ((int(xp/needed_xp*100))*6), 81))
        # bg.paste(im1, (488, 558), im1)
        #
        # bg_draw.text((515, 503), xp_text, font=self.class_font_semibold, fill=(161, 177, 191))
        # bg_draw.text((870, 618), f"{xp}/{needed_xp}", font=self.class_font_bold_xp, anchor="ms", fill=(219, 239, 255))

        needed_xp = self.neededxp(int(rank))

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
        # ((already_earned / to_reach) * 100)

        # print(xp_im.size[0])
        # print(int((xp / needed_xp) * xp_im.size[0]))
        # print(xp / needed_xp)

        im1 = xp_im.crop((0, 0, int((xp / needed_xp) * xp_im.size[0]), 81))
        bg.paste(im1, (190, 767), im1)

        color = xp_im.getpixel(((xp_im.size[0]) - 5, 7))

        if moldName is not None:
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


drawlevel = drawLevel().level
neededxp = drawLevel().neededxp
