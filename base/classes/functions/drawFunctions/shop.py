import os
import uuid

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
from base.classes.functions.admFunctions import fontPath


def add_corners(im, rad):
    size = im.size
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0) + size, radius=rad, fill=255)
    im_ = im.copy()
    im_.putalpha(mask)

    output = ImageOps.fit(im_, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)

    return output


class drawShop:
    def __init__(self) -> None:
        # "LOJA"
        self.montserrat_extrabold_loja = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratExtraBold.ttf'), 50
        )

        # COINS TITLE TEXT
        self.montserrat_medium_coins = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratMedium.ttf'), 23
        )

        # COINS VALUE TEXT
        self.montserrat_bold_coins = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratBold.ttf'), 28
        )

        # /comprar #ID
        self.montserrat_semibolditalic_buy = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratSemiBoldItalic.ttf'), 25
        )

        # Nome do item
        self.montserrat_bold_name = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratBold.ttf'), 25
        )

        # Tipo do item
        self.montserrat_bold_type = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratBold.ttf'), 22
        )

        # Valor
        self.montserrat_blackitalic_value = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratBlackItalic.ttf'), 40
        )

        # Categoria do item
        self.montserrat_semibold_category = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratSemiBold.ttf'), 20
        )

        # "Página"
        self.montserrat_semibold = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratSemiBold.ttf'), 30
        )

        # Número da página
        self.montserrat_extrabold_pageNumb = ImageFont.truetype(
            os.path.join(fontPath.pathMonserrat, 'MontserratExtraBold.ttf'), 30
        )

    def shop(self, total, spark, ori, items, banner=None) -> list[str]:
        try:
            spark_img = Image.open("src/imgs/extra/spark.png")
            ori_img = Image.open("src/imgs/extra/ori.png")
            shopCar_img = Image.open(
                "src/imgs/extra/loja/Carrinho-Loja-Colorido.png")

            # ITEM CATEGORIE IMAGES
            comumCat_image = Image.open("src/imgs/extra/loja/Loja-Comum.png")
            raroCat_image = Image.open("src/imgs/extra/loja/Loja-Raro.png")
            lendCat_image = Image.open("src/imgs/extra/loja/Loja-Lendario.png")

            if not banner:
                banner = Image.open(
                    "src/imgs/extra/loja/banners/Fy-no-Planeta-Magnético.png")
            else:
                banner = Image.open(banner)

            plain = Image.new(
                'RGBA', (1280, 1280), (0, 45, 62, 255))

            banner_Big = banner.resize((1280 + 630, 650 + 630))
            banner_Big = banner_Big.crop((300, 0, 1580, 1280))
            mask = Image.new("L", banner_Big.size, 90)

            bannerFundo = Image.composite(banner_Big, plain, mask)
            bannerBlur = bannerFundo.filter(ImageFilter.GaussianBlur(radius=10))

            total_page = total / 6 if total / 6 == int() else int(total / 6 + 0.5)

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
                    ((695, 50), (959, 140)), 22, fill=(0, 45, 62))

                bg_draw.text((770, 60), "Sparks",
                             font=self.montserrat_medium_coins, fill=(153, 177, 191))

                spark_value = f"{int(spark):,}".replace(",", ".")
                bg_draw.text((770, 90), spark_value,
                             font=self.montserrat_bold_coins, fill=(219, 239, 255))

                # ORI AREA
                bg_draw.rounded_rectangle(
                    ((985, 50), (1249, 140)), 22, fill=(0, 53, 49))

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

                bg_draw.text((700, 1240), "%s" % (i + 1,),
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

                    if str(list_itens[0]['category']) == "Comum":
                        img = comumCat_image
                    elif str(list_itens[0]['category']) == "Raro":
                        img = raroCat_image
                    elif str(list_itens[0]['category']) == "Lendário":
                        img = lendCat_image

                    itemImg = Image.open(list_itens[0]['img']).convert("RGBA")

                    if str(list_itens[0]['type']) == "Banner":
                        itemImg = itemImg.resize((330, 185), Image.NEAREST)
                        itemImg = add_corners(itemImg, 20)
                    elif str(list_itens[0]['type']) == "Utilizavel":
                        itemImg = itemImg.resize((128, 128), Image.NEAREST)
                    elif str(list_itens[0]['type']) == "Badge":
                        itemImg = itemImg.resize(
                            (int(itemImg.size[0] * 0.5), int(itemImg.size[1] * 0.5)), Image.NEAREST)

                    elif str(list_itens[0]['type']) == "Titulo":
                        itemImg = itemImg
                    elif str(list_itens[0]['type']) == "Moldura":
                        itemImg = itemImg
                        if itemImg.size[0] <= 460:
                            lar_x, alt_y = (int(itemImg.size[0] * 0.6), int(itemImg.size[1] * 0.6))
                            itemImg = itemImg.resize(
                                (lar_x, alt_y), Image.NEAREST
                            )
                        else:
                            lar_x, alt_y = (int(itemImg.size[0] * 0.5), int(itemImg.size[1] * 0.5))
                            itemImg = itemImg.resize(
                                (lar_x, alt_y), Image.NEAREST
                            )

                    lar = (itemImg.size[0], itemImg.size[1])

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
                            itemImg, (int(25 + larg_cima + int((img.size[0] - lar[0]) / 2)),
                                      int(altura + int((img.size[1] - lar[1]) / 2)) - 70), itemImg)
                        # TEXTS
                        # ITEM TYPE
                        bg_draw.text((135 + larg_cima, altura),
                                     list_itens[0]['type'], fill=(0, 45, 62), anchor="ma",
                                     font=self.montserrat_bold_type)

                        # ITEM NAME
                        bg_draw.text((int(25 + larg_cima + int((img.size[0] / 2))),
                                      int(altura + int((img.size[1] / 2))) + 70),
                                     list_itens[0]['name'], fill=(215, 235, 251), anchor="ma",
                                     font=self.montserrat_bold_name)

                        # ITEM BUY
                        bg_draw.text((int(25 + larg_cima + int((img.size[0] / 2))),
                                      int(altura + int((img.size[1] / 2))) + 130),
                                     "/comprar %s" % (list_itens[0]['id'],), fill=(0, 45, 62), anchor="ma",
                                     font=self.montserrat_semibolditalic_buy)

                        # ITEM VALUE
                        value = f"{int(list_itens[0]['value']):,}".replace(
                            ",", ".")
                        bg_draw.text((int(25 + larg_cima + int((img.size[0] / 2))),
                                      int(altura + int((img.size[1] / 2))) + 160),
                                     value, fill=(0, 45, 62), anchor="ma",
                                     font=self.montserrat_extrabold_pageNumb)

                        ccount += 1

                    elif larg_baixo <= 840:
                        altura = 685

                        # ROW BACKGROUND IMAGE 2
                        plain.paste(img, (25 + larg_baixo, altura), img)

                        # ROW ITEM IMAGE 2
                        plain.paste(
                            itemImg, (int(25 + larg_baixo + int((img.size[0] - lar[0]) / 2)),
                                      int(altura + int((img.size[1] - lar[1]) / 2)) - 70), itemImg)

                        # TEXTS
                        # ITEM TYPE
                        bg_draw.text((135 + larg_baixo, altura),
                                     list_itens[0]['type'], fill=(0, 45, 62), anchor="ma",
                                     font=self.montserrat_bold_type)

                        # ITEM NAME
                        bg_draw.text((int(25 + larg_baixo + int((img.size[0] / 2))),
                                      int(altura + int((img.size[1] / 2))) + 70),
                                     list_itens[0]['name'], fill=(215, 235, 251), anchor="ma",
                                     font=self.montserrat_bold_name)

                        # ITEM BUY
                        bg_draw.text((int(25 + larg_baixo + int((img.size[0] / 2))),
                                      int(altura + int((img.size[1] / 2))) + 130),
                                     "/comprar %s" % (list_itens[0]['id'],), fill=(0, 45, 62), anchor="ma",
                                     font=self.montserrat_semibolditalic_buy)

                        # ITEM VALUE
                        value = f"{int(list_itens[0]['value']):,}".replace(
                            ",", ".")
                        bg_draw.text((int(25 + larg_baixo + int((img.size[0] / 2))),
                                      int(altura + int((img.size[1] / 2))) + 160),
                                     value, fill=(0, 45, 62), anchor="ma",
                                     font=self.montserrat_extrabold_pageNumb)

                        tcount += 1

                    count += 1

                plain = plain.convert('RGB')
                try:
                    u = uuid.uuid4().hex

                    plain.save(f'{os.path.join(fontPath._path, u)}.png', 'PNG')
                    # buffer.seek(0)

                except Exception as i:
                    raise i
                else:
                    images.append(f"{u}.png")
            return images
        except Exception as e:
            print(e)
            raise e


drawshop = drawShop().shop
