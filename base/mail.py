from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib
import ssl
import os
import json

from base.struct import Config


class Mail():

    def __init__(self, email, mailhtml, mailtxt) -> None:
        
        with open('config.json', 'r') as f:
            self.cfg = Config(json.loads(f.read()))

        self.smtp_server = self.cfg.bot_mailhost
        self.port = 587  # For starttls
        self.sender_email = self.cfg.bot_mail
        self.password = self.cfg.bot_mailpass

        self.email = email
        self.mailhtml = mailhtml
        self.mailtxt = mailtxt

    async def sendMail(self) -> None:

        receiver_email = self.email

        # Create the plain-text and HTML version of your message
        html = self.mailhtml

        message = MIMEMultipart("alternative")
        message["Subject"] = "E-mail de Resposta!"
        message["From"] = self.sender_email
        message["To"] = receiver_email #','.join(receiver_email)

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(MIMEText(html, "html"))

        # add images
        # files = ['image-1.png',
        #         'image-2.png',
        #         'image-3.png',
        #         'image-4.png',
        #         'image-5.png',
        #         'image-6.png']
        # Get the files/images you want to add.
        img_dir = "src\imgs\other\mail"
        images = [os.path.join(img_dir, i) for i in os.listdir(img_dir)]

        # Added a enumerate loop around the whole procedure.
        # Reference to cid:image_id_"j", which you will attach to the email later.
        for j, val in enumerate(images):

            with open('{}'.format(val), "rb") as attachment:
                msgImage = MIMEImage(attachment.read(), filename='filename')

            # print(j, val, '<image{}>'.format(j+1))
            # Define the image's ID with counter as you will reference it.
            msgImage.add_header('Content-ID', '<image%s>' % (j+1, ))
            message.attach(msgImage)

        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            # server.set_debuglevel(1)
            server.ehlo()
            server.login(self.sender_email, self.password)
            server.sendmail(
                self.sender_email, receiver_email, message.as_string()
            )

    def getEmailMessage(status):
        if status == 'accept':
            email = """\
                <!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Transitional //EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
                <html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
                <head>
                <!--[if gte mso 9]>
                <xml>
                <o:OfficeDocumentSettings>
                    <o:AllowPNG/>
                    <o:PixelsPerInch>96</o:PixelsPerInch>
                </o:OfficeDocumentSettings>
                </xml>
                <![endif]-->
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta name="x-apple-disable-message-reformatting">
                <!--[if !mso]><!--><meta http-equiv="X-UA-Compatible" content="IE=edge"><!--<![endif]-->
                <title></title>
                
                    <style type="text/css">
                    @media only screen and (min-width: 620px) {
                .u-row {
                    width: 600px !important;
                }
                .u-row .u-col {
                    vertical-align: top;
                }

                .u-row .u-col-100 {
                    width: 600px !important;
                }

                }

                @media (max-width: 620px) {
                .u-row-container {
                    max-width: 100% !important;
                    padding-left: 0px !important;
                    padding-right: 0px !important;
                }
                .u-row .u-col {
                    min-width: 320px !important;
                    max-width: 100% !important;
                    display: block !important;
                }
                .u-row {
                    width: calc(100% - 40px) !important;
                }
                .u-col {
                    width: 100% !important;
                }
                .u-col > div {
                    margin: 0 auto;
                }
                }
                body {
                margin: 0;
                padding: 0;
                }

                table,
                tr,
                td {
                vertical-align: top;
                border-collapse: collapse;
                }

                p {
                margin: 0;
                }

                .ie-container table,
                .mso-container table {
                table-layout: fixed;
                }

                * {
                line-height: inherit;
                }

                a[x-apple-data-detectors='true'] {
                color: inherit !important;
                text-decoration: none !important;
                }

                table, td { color: #000000; } #u_body a { color: #0000ee; text-decoration: underline; } @media (max-width: 480px) { #u_content_image_1 .v-src-width { width: auto !important; } #u_content_image_1 .v-src-max-width { max-width: 38% !important; } #u_content_image_2 .v-src-width { width: auto !important; } #u_content_image_2 .v-src-max-width { max-width: 100% !important; } }
                    </style>
                
                

                <!--[if !mso]><!--><link href="https://fonts.googleapis.com/css?family=Lato:400,700&display=swap" rel="stylesheet" type="text/css"><link href="https://fonts.googleapis.com/css?family=Montserrat:400,700&display=swap" rel="stylesheet" type="text/css"><!--<![endif]-->

                </head>

                <body class="clean-body u_body" style="margin: 0;padding: 0;-webkit-text-size-adjust: 100%;background-color: #ecf0f1;color: #000000">
                <!--[if IE]><div class="ie-container"><![endif]-->
                <!--[if mso]><div class="mso-container"><![endif]-->
                <table id="u_body" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;min-width: 320px;Margin: 0 auto;background-color: #ecf0f1;width:100%" cellpadding="0" cellspacing="0">
                <tbody>
                <tr style="vertical-align: top">
                    <td style="word-break: break-word;border-collapse: collapse !important;vertical-align: top">
                    <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td align="center" style="background-color: #ecf0f1;"><![endif]-->
                    

                <div class="u-row-container" style="padding: 0px;background-color: transparent">
                <div class="u-row" style="Margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: #264653;">
                    <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-color: transparent;">
                    <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px;"><tr style="background-color: #264653;"><![endif]-->
                    
                <!--[if (mso)|(IE)]><td align="center" width="600" style="width: 600px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;" valign="top"><![endif]-->
                <div class="u-col u-col-100" style="max-width: 320px;min-width: 600px;display: table-cell;vertical-align: top;">
                <div style="height: 100%;width: 100% !important;">
                <!--[if (!mso)&(!IE)]><!--><div style="height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;"><!--<![endif]-->
                
                <table id="u_content_image_1" style="font-family:'Montserrat',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                <tbody>
                    <tr>
                    <td style="overflow-wrap:break-word;word-break:break-word;padding:20px 10px;font-family:'Montserrat',sans-serif;" align="left">
                        
                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                    <td style="padding-right: 0px;padding-left: 0px;" align="center">
                    <a href="https://kiniga.com/" target="_blank">
                    <img align="center" border="0" src="cid:image3" alt="Logo" title="Logo" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: inline-block !important;border: none;height: auto;float: none;width: 21%;max-width: 121.8px;" width="121.8" class="v-src-width v-src-max-width"/>
                    </a>
                    </td>
                </tr>
                </table>

                    </td>
                    </tr>
                </tbody>
                </table>

                <!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
                </div>
                </div>
                <!--[if (mso)|(IE)]></td><![endif]-->
                    <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
                    </div>
                </div>
                </div>



                <div class="u-row-container" style="padding: 0px;background-color: transparent">
                <div class="u-row" style="Margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: #ffffff;">
                    <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-color: transparent;">
                    <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px;"><tr style="background-color: #ffffff;"><![endif]-->
                    
                <!--[if (mso)|(IE)]><td align="center" width="600" style="width: 600px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;" valign="top"><![endif]-->
                <div class="u-col u-col-100" style="max-width: 320px;min-width: 600px;display: table-cell;vertical-align: top;">
                <div style="height: 100%;width: 100% !important;">
                <!--[if (!mso)&(!IE)]><!--><div style="height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;"><!--<![endif]-->
                
                <table id="u_content_image_2" style="font-family:'Montserrat',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                <tbody>
                    <tr>
                    <td style="overflow-wrap:break-word;word-break:break-word;padding:15px 0px 10px;font-family:'Montserrat',sans-serif;" align="left">
                        
                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                    <td style="padding-right: 0px;padding-left: 0px;" align="center">
                    
                    <img align="center" border="0" src="cid:image5" alt="Hero Image" title="Hero Image" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: inline-block !important;border: none;height: auto;float: none;width: 77%;max-width: 462px;" width="462" class="v-src-width v-src-max-width"/>
                    
                    </td>
                </tr>
                </table>

                    </td>
                    </tr>
                </tbody>
                </table>

                <!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
                </div>
                </div>
                <!--[if (mso)|(IE)]></td><![endif]-->
                    <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
                    </div>
                </div>
                </div>



                <div class="u-row-container" style="padding: 0px;background-color: transparent">
                <div class="u-row" style="Margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: #ffffff;">
                    <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-color: transparent;">
                    <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px;"><tr style="background-color: #ffffff;"><![endif]-->
                    
                <!--[if (mso)|(IE)]><td align="center" width="600" style="width: 600px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;" valign="top"><![endif]-->
                <div class="u-col u-col-100" style="max-width: 320px;min-width: 600px;display: table-cell;vertical-align: top;">
                <div style="height: 100%;width: 100% !important;">
                <!--[if (!mso)&(!IE)]><!--><div style="height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;"><!--<![endif]-->
                
                <table style="font-family:'Montserrat',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                <tbody>
                    <tr>
                    <td style="overflow-wrap:break-word;word-break:break-word;padding:0px 10px;font-family:'Montserrat',sans-serif;" align="left">
                        
                <h1 style="margin: 0px; color: #264653; line-height: 140%; text-align: center; word-wrap: break-word; font-weight: normal; font-family: arial,helvetica,sans-serif; font-size: 38px;">
                    <strong>Parabéns!</strong>
                </h1>

                    </td>
                    </tr>
                </tbody>
                </table>

                <table style="font-family:'Montserrat',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                <tbody>
                    <tr>
                    <td style="overflow-wrap:break-word;word-break:break-word;padding:0px 10px 20px;font-family:'Montserrat',sans-serif;" align="left">
                        
                <div style="line-height: 140%; text-align: center; word-wrap: break-word;">
                    <p style="font-size: 14px; line-height: 140%;"><span style="font-size: 22px; line-height: 30.8px; color: #2a9d8f;"><strong>Você foi aceito(a).</strong></span></p>
                </div>

                    </td>
                    </tr>
                </tbody>
                </table>

                <!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
                </div>
                </div>
                <!--[if (mso)|(IE)]></td><![endif]-->
                    <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
                    </div>
                </div>
                </div>



                <div class="u-row-container" style="padding: 0px;background-color: transparent">
                <div class="u-row" style="Margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: #bfedd2;">
                    <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-color: transparent;">
                    <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px;"><tr style="background-color: #bfedd2;"><![endif]-->
                    
                <!--[if (mso)|(IE)]><td align="center" width="600" style="width: 600px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;" valign="top"><![endif]-->
                <div class="u-col u-col-100" style="max-width: 320px;min-width: 600px;display: table-cell;vertical-align: top;">
                <div style="height: 100%;width: 100% !important;">
                <!--[if (!mso)&(!IE)]><!--><div style="height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;"><!--<![endif]-->
                
                <table style="font-family:'Montserrat',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                <tbody>
                    <tr>
                    <td style="overflow-wrap:break-word;word-break:break-word;padding:25px 10px 0px 30px;font-family:'Montserrat',sans-serif;" align="left">
                        
                <div style="color: #264653; line-height: 140%; text-align: left; word-wrap: break-word;">
                    <p style="line-height: 140%; font-size: 14px;"><span style="line-height: 19.6px; font-size: 14px;"><span style="font-size: 16px; line-height: 22.4px;"><strong>Olá, você</strong></span><strong style="font-size: 16px;">, tudo bem? </strong></span></p>
                </div>

                    </td>
                    </tr>
                </tbody>
                </table>

                <table style="font-family:'Montserrat',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                <tbody>
                    <tr>
                    <td style="overflow-wrap:break-word;word-break:break-word;padding:10px 30px;font-family:'Montserrat',sans-serif;" align="left">
                        
                <div style="color: #264653; line-height: 160%; text-align: left; word-wrap: break-word;">
                    <p style="font-size: 14px; line-height: 160%; text-align: justify;">Estou enviando esta resposta pois recebemos a sua história e temos o prazer de anunciar que <strong>aceitamos </strong>ela na <span style="text-decoration: underline; font-size: 14px; line-height: 22.4px;"><span style="color: #2dc26b; font-size: 14px; line-height: 22.4px; text-decoration: underline;">Kiniga</span></span>!</p>
                <p style="font-size: 14px; line-height: 160%; text-align: justify;">Peço que não pule esta mensagem, pois ela é de <strong>extrema importância</strong> para que sua história seja publicada sem que ocorra nenhum problema. </p>
                </div>

                    </td>
                    </tr>
                </tbody>
                </table>

                <table style="font-family:'Montserrat',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                <tbody>
                    <tr>
                    <td style="overflow-wrap:break-word;word-break:break-word;padding:10px 10px 0px 30px;font-family:'Montserrat',sans-serif;" align="left">
                        
                <div style="color: #264653; line-height: 140%; text-align: left; word-wrap: break-word;">
                    <p style="font-size: 14px; line-height: 140%;"><strong>O que fazer</strong></p>
                </div>

                    </td>
                    </tr>
                </tbody>
                </table>

                <table style="font-family:'Montserrat',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                <tbody>
                    <tr>
                    <td style="overflow-wrap:break-word;word-break:break-word;padding:0px 20px 10px 30px;font-family:'Montserrat',sans-serif;" align="left">
                        
                <div style="color: #264653; line-height: 180%; text-align: left; word-wrap: break-word;">
                    <p style="font-size: 14px; line-height: 180%; text-align: justify;">Supondo que você já tenha lido todas as nossas <span style="color: #2dc26b; font-size: 14px; line-height: 25.2px;"><a rel="noopener" href="https://politicas.kiniga.com/" target="_blank" style="color: #2dc26b;">Políticas</a></span>, que também é de extrema importância, decidimos criar um <a rel="noopener" href="https://docs.google.com/document/d/1Yrj84cdIQQwFMkmCZ8k9YLgLkA4dngI57yl3TtfxqaE/edit?usp=sharing" target="_blank"><span style="color: #2dc26b; font-size: 14px; line-height: 25.2px;">FAQ</span></a> para sanar qualquer dúvida relacionada ao processo de avaliação e publicação de histórias, bem como acontecimentos deste servidor, como são aplicadas punições, feitos os anúncios, e mais. Fora isso, sugiro que siga as instruções abaixo para que sua história não perca o lugar na fila de publicação. </p>
                </div>

                    </td>
                    </tr>
                </tbody>
                </table>

                <table style="font-family:'Montserrat',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                <tbody>
                    <tr>
                    <td style="overflow-wrap:break-word;word-break:break-word;padding:10px 10px 0px 30px;font-family:'Montserrat',sans-serif;" align="left">
                        
                <div style="color: #264653; line-height: 140%; text-align: left; word-wrap: break-word;">
                    <p style="font-size: 14px; line-height: 140%;"><strong>Não saia do servidor</strong></p>
                </div>

                    </td>
                    </tr>
                </tbody>
                </table>

                <table style="font-family:'Montserrat',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                <tbody>
                    <tr>
                    <td style="overflow-wrap:break-word;word-break:break-word;padding:0px 20px 10px 30px;font-family:'Montserrat',sans-serif;" align="left">
                        
                <div style="color: #264653; line-height: 180%; text-align: left; word-wrap: break-word;">
                    <p style="font-size: 14px; line-height: 180%; text-align: justify;">Para que nosso sistema de publicação funcione sem problemas, é preciso que o autor ou autora esteja no servidor. Assim, poderemos avisá-los do <strong>lançamento</strong>, explicar como poderão <strong>publicar </strong>seus capítulos, <strong>criar a tag</strong> da história e quais canais usar para coisas específicas, como anúncios sobre a história.</p>
                </div>

                    </td>
                    </tr>
                </tbody>
                </table>

                <table style="font-family:'Montserrat',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                <tbody>
                    <tr>
                    <td style="overflow-wrap:break-word;word-break:break-word;padding:10px 10px 0px 30px;font-family:'Montserrat',sans-serif;" align="left">
                        
                <div style="color: #264653; line-height: 140%; text-align: left; word-wrap: break-word;">
                    <p style="font-size: 14px; line-height: 140%;"><strong>Não mude o seu ID.</strong></p>
                </div>

                    </td>
                    </tr>
                </tbody>
                </table>

                <table style="font-family:'Montserrat',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                <tbody>
                    <tr>
                    <td style="overflow-wrap:break-word;word-break:break-word;padding:0px 20px 10px 30px;font-family:'Montserrat',sans-serif;" align="left">
                        
                <div style="color: #264653; line-height: 180%; text-align: left; word-wrap: break-word;">
                    <p style="font-size: 14px; line-height: 180%; text-align: justify;">Com o mesmo objetivo de melhor funcionamento do sistema, pedimos para que não alterem seu ID do Discord — o mesmo que você inseriu no formulário. Ex: Shuichi#6999</p>
                <p style="font-size: 14px; line-height: 180%; text-align: justify;"> </p>
                <p style="font-size: 14px; line-height: 180%; text-align: justify;">Não estamos falando do seu <strong>apelido </strong>no servidor, mas sim seu ID. Após a publicação da sua história e se você já tiver criado a TAG da sua história, você poderá alterar seu ID se desejar. Mas, até lá, pedimos que permaneça com o mesmo que foi inserido no formulário.</p>
                <p style="font-size: 14px; line-height: 180%; text-align: justify;"> </p>
                <p style="font-size: 14px; line-height: 180%; text-align: justify;"><span style="background-color: #c2e0f4; font-size: 14px; line-height: 25.2px;">Caso você não tenha alternativa além dalterar seu ID, ou por algum motivo teve que mudar de conta, pedimos que marque o <strong>@Jonathan (O Budista)</strong> no canal <strong>֎・chat-geral-sério</strong> contando seu problema em detalhes. </span></p>
                </div>

                    </td>
                    </tr>
                </tbody>
                </table>

                <table style="font-family:'Montserrat',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                <tbody>
                    <tr>
                    <td style="overflow-wrap:break-word;word-break:break-word;padding:10px 10px 0px 30px;font-family:'Montserrat',sans-serif;" align="left">
                        
                <div style="color: #264653; line-height: 140%; text-align: left; word-wrap: break-word;">
                    <p style="font-size: 14px; line-height: 140%;"><strong>Forneça o link do capítulo corretamente.</strong></p>
                </div>

                    </td>
                    </tr>
                </tbody>
                </table>

                <table style="font-family:'Montserrat',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                <tbody>
                    <tr>
                    <td style="overflow-wrap:break-word;word-break:break-word;padding:0px 20px 10px 30px;font-family:'Montserrat',sans-serif;" align="left">
                        
                <div style="color: #264653; line-height: 180%; text-align: left; word-wrap: break-word;">
                    <p style="font-size: 14px; line-height: 180%; text-align: justify;">Se a história for aceita, os Editores entram em contato solicitando o capítulo da história que será publicado no lançamento. Esse link deve ser o de um serviço de armazenamento online, como o <span style="text-decoration: underline; font-size: 14px; line-height: 25.2px;">Google Drive</span>, <span style="text-decoration: underline; font-size: 14px; line-height: 25.2px;">One Drive</span>, <span style="text-decoration: underline; font-size: 14px; line-height: 25.2px;">Dropbox</span>, etc. É <strong>essencial </strong>que o Editor(a) possa acessar o arquivo para que ele(a) possa publicar a história, e se o arquivo não estiver com a opção de compartilhamento com, pelo menos, <strong>permissão para ler</strong>, isso não será possível. </p>
                </div>

                    </td>
                    </tr>
                </tbody>
                </table>

                <table style="font-family:'Montserrat',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                <tbody>
                    <tr>
                    <td style="overflow-wrap:break-word;word-break:break-word;padding:10px 10px 0px 30px;font-family:'Montserrat',sans-serif;" align="left">
                        
                <div style="color: #264653; line-height: 140%; text-align: left; word-wrap: break-word;">
                    <p style="font-size: 14px; line-height: 140%;"><strong>Consequência.</strong></p>
                </div>

                    </td>
                    </tr>
                </tbody>
                </table>

                <table style="font-family:'Montserrat',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                <tbody>
                    <tr>
                    <td style="overflow-wrap:break-word;word-break:break-word;padding:0px 20px 10px 30px;font-family:'Montserrat',sans-serif;" align="left">
                        
                <div style="color: #264653; line-height: 180%; text-align: left; word-wrap: break-word;">
                    <p style="font-size: 14px; line-height: 180%; text-align: justify;">Se qualquer uma das coisas acima acontecer, a sua história perderá o lugar na fila. O que significa que, quando algum Editor tentar publicá-la e não for possível, sua história passará a ser a última a ser publicada. Portanto, mantenha isso em mente e tente não bobear. Caso tenha sido reportado à um Editor/Administrador, e o problema tenha sido solucionado, não haverá consequência. </p>
                </div>

                    </td>
                    </tr>
                </tbody>
                </table>

                <table style="font-family:'Montserrat',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                <tbody>
                    <tr>
                    <td style="overflow-wrap:break-word;word-break:break-word;padding:10px 10px 0px 30px;font-family:'Montserrat',sans-serif;" align="left">
                        
                <div style="color: #264653; line-height: 140%; text-align: left; word-wrap: break-word;">
                    <p style="font-size: 14px; line-height: 140%;"><span style="font-size: 14px; line-height: 19.6px; background-color: #f8cac6;"><strong>ATENÇÃO!</strong></span></p>
                </div>

                    </td>
                    </tr>
                </tbody>
                </table>

                <table style="font-family:'Montserrat',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                <tbody>
                    <tr>
                    <td style="overflow-wrap:break-word;word-break:break-word;padding:0px 20px 10px 30px;font-family:'Montserrat',sans-serif;" align="left">
                        
                <div style="color: #264653; line-height: 180%; text-align: left; word-wrap: break-word;">
                    <p style="font-size: 14px; line-height: 180%; text-align: justify;"><span style="background-color: #f8cac6; font-size: 14px; line-height: 25.2px;">Todas as suas dúvidas, e mais, podem ser </span><span style="background-color: #f8cac6; font-size: 14px; line-height: 25.2px;">respondidas ao ler o FAQ. </span></p>
                </div>

                    </td>
                    </tr>
                </tbody>
                </table>

                <table style="font-family:'Montserrat',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                <tbody>
                    <tr>
                    <td style="overflow-wrap:break-word;word-break:break-word;padding:10px 30px;font-family:'Montserrat',sans-serif;" align="left">
                        
                <div style="color: #264653; line-height: 160%; text-align: left; word-wrap: break-word;">
                    <p style="font-size: 14px; line-height: 160%;"><strong><span style="font-family: Lato, sans-serif; font-size: 14px; line-height: 22.4px; color: #264653;">Se você tiver alguma dúvida, contate-nos pelo Discord.<span style="color: #34495e; font-size: 14px; line-height: 22.4px;"></span></span></strong></p>
                </div>

                    </td>
                    </tr>
                </tbody>
                </table>

                <!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
                </div>
                </div>
                <!--[if (mso)|(IE)]></td><![endif]-->
                    <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
                    </div>
                </div>
                </div>



                <div class="u-row-container" style="padding: 0px;background-color: transparent">
                <div class="u-row" style="Margin: 0 auto;min-width: 320px;max-width: 600px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: #264653;">
                    <div style="border-collapse: collapse;display: table;width: 100%;height: 100%;background-color: transparent;">
                    <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px;"><tr style="background-color: #264653;"><![endif]-->
                    
                <!--[if (mso)|(IE)]><td align="center" width="600" style="width: 600px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;" valign="top"><![endif]-->
                <div class="u-col u-col-100" style="max-width: 320px;min-width: 600px;display: table-cell;vertical-align: top;">
                <div style="height: 100%;width: 100% !important;">
                <!--[if (!mso)&(!IE)]><!--><div style="height: 100%; padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;"><!--<![endif]-->
                
                <table style="font-family:'Montserrat',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                <tbody>
                    <tr>
                    <td style="overflow-wrap:break-word;word-break:break-word;padding:30px 10px 0px;font-family:'Montserrat',sans-serif;" align="left">
                        
                <h1 style="margin: 0px; color: #ffffff; line-height: 140%; text-align: center; word-wrap: break-word; font-weight: normal; font-family: trebuchet ms,geneva; font-size: 22px;">
                    <strong>Sobre Nós</strong>
                </h1>

                    </td>
                    </tr>
                </tbody>
                </table>

                <table style="font-family:'Montserrat',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                <tbody>
                    <tr>
                    <td style="overflow-wrap:break-word;word-break:break-word;padding:10px;font-family:'Montserrat',sans-serif;" align="left">
                        
                <div style="line-height: 140%; text-align: center; word-wrap: break-word;">
                    <p style="font-size: 14px; line-height: 140%;"><span style="color: #ffffff; font-size: 14px; line-height: 19.6px;">W W W . K I N I G A . C O M</span></p>
                </div>

                    </td>
                    </tr>
                </tbody>
                </table>

                <table style="font-family:'Montserrat',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                <tbody>
                    <tr>
                    <td style="overflow-wrap:break-word;word-break:break-word;padding:10px;font-family:'Montserrat',sans-serif;" align="left">
                        
                <div align="center">
                <div style="display: table; max-width:167px;">
                <!--[if (mso)|(IE)]><table width="167" cellpadding="0" cellspacing="0" border="0"><tr><td style="border-collapse:collapse;" align="center"><table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse; mso-table-lspace: 0pt;mso-table-rspace: 0pt; width:167px;"><tr><![endif]-->
                
                    
                    <!--[if (mso)|(IE)]><td width="32" style="width:32px; padding-right: 10px;" valign="top"><![endif]-->
                    <table align="left" border="0" cellspacing="0" cellpadding="0" width="32" height="32" style="width: 32px !important;height: 32px !important;display: inline-block;border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;margin-right: 10px">
                    <tbody><tr style="vertical-align: top"><td align="left" valign="middle" style="word-break: break-word;border-collapse: collapse !important;vertical-align: top">
                        <a href="https://www.facebook.com/kinigabrasil" title="Facebook" target="_blank">
                        <img src="cid:image1" alt="Facebook" title="Facebook" width="32" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: block !important;border: none;height: auto;float: none;max-width: 32px !important">
                        </a>
                    </td></tr>
                    </tbody></table>
                    <!--[if (mso)|(IE)]></td><![endif]-->
                    
                    <!--[if (mso)|(IE)]><td width="32" style="width:32px; padding-right: 10px;" valign="top"><![endif]-->
                    <table align="left" border="0" cellspacing="0" cellpadding="0" width="32" height="32" style="width: 32px !important;height: 32px !important;display: inline-block;border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;margin-right: 10px">
                    <tbody><tr style="vertical-align: top"><td align="left" valign="middle" style="word-break: break-word;border-collapse: collapse !important;vertical-align: top">
                        <a href="https://twitter.com/KinigaBrasil" title="Twitter" target="_blank">
                        <img src="cid:image2" alt="Twitter" title="Twitter" width="32" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: block !important;border: none;height: auto;float: none;max-width: 32px !important">
                        </a>
                    </td></tr>
                    </tbody></table>
                    <!--[if (mso)|(IE)]></td><![endif]-->
                    
                    <!--[if (mso)|(IE)]><td width="32" style="width:32px; padding-right: 10px;" valign="top"><![endif]-->
                    <table align="left" border="0" cellspacing="0" cellpadding="0" width="32" height="32" style="width: 32px !important;height: 32px !important;display: inline-block;border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;margin-right: 10px">
                    <tbody><tr style="vertical-align: top"><td align="left" valign="middle" style="word-break: break-word;border-collapse: collapse !important;vertical-align: top">
                        <a href="https://www.instagram.com/p/CAp_qaQHEuM/" title="Instagram" target="_blank">
                        <img src="cid:image4" alt="Instagram" title="Instagram" width="32" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: block !important;border: none;height: auto;float: none;max-width: 32px !important">
                        </a>
                    </td></tr>
                    </tbody></table>
                    <!--[if (mso)|(IE)]></td><![endif]-->
                    
                    <!--[if (mso)|(IE)]><td width="32" style="width:32px; padding-right: 0px;" valign="top"><![endif]-->
                    <table align="left" border="0" cellspacing="0" cellpadding="0" width="32" height="32" style="width: 32px !important;height: 32px !important;display: inline-block;border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;margin-right: 0px">
                    <tbody><tr style="vertical-align: top"><td align="left" valign="middle" style="word-break: break-word;border-collapse: collapse !important;vertical-align: top">
                        <a href="https://discord.gg/QMKHU8y" title="Discord" target="_blank">
                        <img src="cid:image6" alt="Discord" title="Discord" width="32" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: block !important;border: none;height: auto;float: none;max-width: 32px !important">
                        </a>
                    </td></tr>
                    </tbody></table>
                    <!--[if (mso)|(IE)]></td><![endif]-->
                    
                    
                    <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
                </div>
                </div>

                    </td>
                    </tr>
                </tbody>
                </table>

                <table style="font-family:'Montserrat',sans-serif;" role="presentation" cellpadding="0" cellspacing="0" width="100%" border="0">
                <tbody>
                    <tr>
                    <td style="overflow-wrap:break-word;word-break:break-word;padding:10px 10px 15px;font-family:'Montserrat',sans-serif;" align="left">
                        
                <div style="color: #ffffff; line-height: 160%; text-align: center; word-wrap: break-word;">
                    <p style="font-size: 14px; line-height: 160%;">©️ 2022 – Todos os direitos reservados<br /><span style="color: #ffffff; font-size: 14px; line-height: 22.4px;"><a rel="noopener" href="https://politicas.kiniga.com/termos-de-servico/" target="_blank" style="color: #ffffff;">Termos de Serviço</a></span> | <span style="color: #ffffff; font-size: 14px; line-height: 22.4px;"><a rel="noopener" href="https://politicas.kiniga.com/politicas-de-privacidade/" target="_blank" style="color: #ffffff;">Política de Privacidade</a></span></p>
                </div>

                    </td>
                    </tr>
                </tbody>
                </table>

                <!--[if (!mso)&(!IE)]><!--></div><!--<![endif]-->
                </div>
                </div>
                <!--[if (mso)|(IE)]></td><![endif]-->
                    <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
                    </div>
                </div>
                </div>


                    <!--[if (mso)|(IE)]></td></tr></table><![endif]-->
                    </td>
                </tr>
                </tbody>
                </table>
                <!--[if mso]></div><![endif]-->
                <!--[if IE]></div><![endif]-->
                </body>

                </html>


            """
            emailtxt = """\
                
                ESTA É UMA MENSAGEM AUTOMÁTICA. NÃO RESPONDA.
                
                Olá, você, tudo bem? 

                Estou enviando esta resposta pois recebemos a sua história e temos o prazer de anunciar que aceitamos ela na Kiniga!

                Peço que não pule esta mensagem, pois ela é de extrema importância para que sua história seja publicada sem que ocorra nenhum problema. 

                O que fazer

                Supondo que você já tenha lido todas as nossas Políticas (https://politicas.kiniga.com/), que também é de extrema importância, decidimos criar um FAQ (https://docs.google.com/document/d/1Yrj84cdIQQwFMkmCZ8k9YLgLkA4dngI57yl3TtfxqaE/edit?usp=sharing) para sanar qualquer dúvida relacionada ao processo de avaliação e publicação de histórias, bem como acontecimentos de nosso servidor, como são aplicadas punições, feitos os anúncios, e mais. Fora isso, sugiro que siga as instruções abaixo para que sua história não perca o lugar na fila de publicação. 

                Não saia do servidor

                Para que nosso sistema de publicação funcione sem problemas, é preciso que o autor ou autora esteja no servidor. Assim, poderemos avisá-los do lançamento, explicar como poderão publicar seus capítulos, criar a tag da história e quais canais usar para coisas específicas, como anúncios sobre a história.

                Não mude o seu ID.

                Com o mesmo objetivo de melhor funcionamento do sistema, pedimos para que não alterem seu ID do Discord — o mesmo que você inseriu no formulário. Ex: Shuichi#6996

                

                Não estamos falando do seu apelido no servidor, mas sim seu ID. Após a publicação da sua história e se você já tiver criado a TAG da sua história, você poderá alterar seu ID se desejar. Mas, até lá, pedimos que permaneça com o mesmo que foi inserido no formulário.

                

                Caso você não tenha alternativa além de alterar seu ID, ou por algum motivo teve que mudar de conta, pedimos que marque o @Jonathan (O Budista) no canal ֎・chat-geral-sério contando seu problema em detalhes. 

                Forneça o link do capítulo corretamente.

                Se a história for aceita, os Editores entram em contato solicitando o capítulo da história que será publicado no lançamento. Esse link deve ser o de um serviço de armazenamento online, como o Google Drive, One Drive, Dropbox, etc. É essencial que o Editor(a) possa acessar o arquivo para que ele(a) possa publicar a história, e se o arquivo não estiver com a opção de compartilhamento com, pelo menos, permissão para ler, isso não será possível. 

                Consequência.

                Se qualquer uma das coisas acima acontecer, a sua história perderá o lugar na fila. O que significa que, quando algum Editor tentar publicá-la e não for possível, sua história passará a ser a última a ser publicada. Portanto, mantenha isso em mente e tente não bobear. Caso tenha sido reportado à um Editor/Administrador, e o problema tenha sido solucionado, não haverá consequência. 

                ATENÇÃO!

                Todas essas informações, e mais, podem ser
                encontradas no FAQ. Então, mesmo que não consiga ler esta mensagem novamente, você ainda poderá essas informações lá. 

                Se você tiver alguma dúvida, contate-nos pelo Discord.

                Att,
                Equipe Kiniga Brasil.
                
            """
        elif status == 'refuse':
            email = """\
                <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional //EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
                <html
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:v="urn:schemas-microsoft-com:vml"
                xmlns:o="urn:schemas-microsoft-com:office:office"
                >
                <head>
                    <!--[if gte mso 9]>
                    <xml>
                        <o:OfficeDocumentSettings>
                        <o:AllowPNG />
                        <o:PixelsPerInch>96</o:PixelsPerInch>
                        </o:OfficeDocumentSettings>
                    </xml>
                    <![endif]-->
                    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
                    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                    <meta name="x-apple-disable-message-reformatting" />
                    <!--[if !mso]><!-->
                    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
                    <!--<![endif]-->
                    <title></title>

                    <style type="text/css">
                    @media only screen and (min-width: 620px) {
                        .u-row {
                        width: 600px !important;
                        }

                        .u-row .u-col {
                        vertical-align: top;
                        }

                        .u-row .u-col-100 {
                        width: 600px !important;
                        }
                    }

                    @media (max-width: 620px) {
                        .u-row-container {
                        max-width: 100% !important;
                        padding-left: 0px !important;
                        padding-right: 0px !important;
                        }

                        .u-row .u-col {
                        min-width: 320px !important;
                        max-width: 100% !important;
                        display: block !important;
                        }

                        .u-row {
                        width: calc(100% - 40px) !important;
                        }

                        .u-col {
                        width: 100% !important;
                        }

                        .u-col > div {
                        margin: 0 auto;
                        }
                    }

                    body {
                        margin: 0;
                        padding: 0;
                    }

                    table,
                    tr,
                    td {
                        vertical-align: top;
                        border-collapse: collapse;
                    }

                    p {
                        margin: 0;
                    }

                    .ie-container table,
                    .mso-container table {
                        table-layout: fixed;
                    }

                    * {
                        line-height: inherit;
                    }

                    a[x-apple-data-detectors="true"] {
                        color: inherit !important;
                        text-decoration: none !important;
                    }

                    table,
                    td {
                        color: #000000;
                    }

                    #u_body a {
                        color: #0000ee;
                        text-decoration: underline;
                    }

                    @media (max-width: 480px) {
                        #u_content_image_1 .v-src-width {
                        width: auto !important;
                        }

                        #u_content_image_1 .v-src-max-width {
                        max-width: 38% !important;
                        }

                        #u_content_image_2 .v-src-width {
                        width: auto !important;
                        }

                        #u_content_image_2 .v-src-max-width {
                        max-width: 100% !important;
                        }
                    }
                    </style>

                    <!--[if !mso]><!-->
                    <link
                    href="https://fonts.googleapis.com/css?family=Lato:400,700&display=swap"
                    rel="stylesheet"
                    type="text/css"
                    />
                    <link
                    href="https://fonts.googleapis.com/css?family=Montserrat:400,700&display=swap"
                    rel="stylesheet"
                    type="text/css"
                    />
                    <!--<![endif]-->
                </head>

                <body
                    class="clean-body u_body"
                    style="
                    margin: 0;
                    padding: 0;
                    -webkit-text-size-adjust: 100%;
                    background-color: #ecf0f1;
                    color: #000000;
                    "
                >
                    <!--[if IE]><div class="ie-container"><![endif]-->
                    <!--[if mso]><div class="mso-container"><![endif]-->
                    <table
                    id="u_body"
                    style="
                        border-collapse: collapse;
                        table-layout: fixed;
                        border-spacing: 0;
                        mso-table-lspace: 0pt;
                        mso-table-rspace: 0pt;
                        vertical-align: top;
                        min-width: 320px;
                        margin: 0 auto;
                        background-color: #ecf0f1;
                        width: 100%;
                    "
                    cellpadding="0"
                    cellspacing="0"
                    >
                    <tbody>
                        <tr style="vertical-align: top">
                        <td
                            style="
                            word-break: break-word;
                            border-collapse: collapse !important;
                            vertical-align: top;
                            "
                        >
                            <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td align="center" style="background-color: #ecf0f1;"><![endif]-->

                            <div
                            class="u-row-container"
                            style="padding: 0px; background-color: transparent"
                            >
                            <div
                                class="u-row"
                                style="
                                margin: 0 auto;
                                min-width: 320px;
                                max-width: 600px;
                                overflow-wrap: break-word;
                                word-wrap: break-word;
                                word-break: break-word;
                                background-color: #264653;
                                "
                            >
                                <div
                                style="
                                    border-collapse: collapse;
                                    display: table;
                                    width: 100%;
                                    height: 100%;
                                    background-color: transparent;
                                "
                                >
                                <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px;"><tr style="background-color: #264653;"><![endif]-->

                                <!--[if (mso)|(IE)]><td align="center" width="600" style="width: 600px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;" valign="top"><![endif]-->
                                <div
                                    class="u-col u-col-100"
                                    style="
                                    max-width: 320px;
                                    min-width: 600px;
                                    display: table-cell;
                                    vertical-align: top;
                                    "
                                >
                                    <div style="height: 100%; width: 100% !important">
                                    <!--[if (!mso)&(!IE)]><!-->
                                    <div
                                        style="
                                        height: 100%;
                                        padding: 0px;
                                        border-top: 0px solid transparent;
                                        border-left: 0px solid transparent;
                                        border-right: 0px solid transparent;
                                        border-bottom: 0px solid transparent;
                                        "
                                    >
                                        <!--<![endif]-->
                                        <table
                                        id="u_content_image_1"
                                        style="font-family: 'Montserrat', sans-serif"
                                        role="presentation"
                                        cellpadding="0"
                                        cellspacing="0"
                                        width="100%"
                                        border="0"
                                        >
                                        <tbody>
                                            <tr>
                                            <td
                                                style="
                                                overflow-wrap: break-word;
                                                word-break: break-word;
                                                padding: 20px 10px;
                                                font-family: 'Montserrat', sans-serif;
                                                "
                                                align="left"
                                            >
                                                <table
                                                width="100%"
                                                cellpadding="0"
                                                cellspacing="0"
                                                border="0"
                                                >
                                                <tr>
                                                    <td
                                                    style="
                                                        padding-right: 0px;
                                                        padding-left: 0px;
                                                    "
                                                    align="center"
                                                    >
                                                    <a
                                                        href="https://kiniga.com/"
                                                        target="_blank"
                                                    >
                                                        <img
                                                        align="center"
                                                        border="0"
                                                        src="cid:image3"
                                                        alt="Logo"
                                                        title="Logo"
                                                        style="
                                                            outline: none;
                                                            text-decoration: none;
                                                            -ms-interpolation-mode: bicubic;
                                                            clear: both;
                                                            display: inline-block !important;
                                                            border: none;
                                                            height: auto;
                                                            float: none;
                                                            width: 21%;
                                                            max-width: 121.8px;
                                                        "
                                                        width="121.8"
                                                        class="v-src-width v-src-max-width"
                                                        />
                                                    </a>
                                                    </td>
                                                </tr>
                                                </table>
                                            </td>
                                            </tr>
                                        </tbody>
                                        </table>

                                        <!--[if (!mso)&(!IE)]><!-->
                                    </div>
                                    <!--<![endif]-->
                                    </div>
                                </div>
                                <!--[if (mso)|(IE)]></td><![endif]-->
                                <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
                                </div>
                            </div>
                            </div>

                            <div
                            class="u-row-container"
                            style="padding: 0px; background-color: transparent"
                            ></div>

                            <div
                            class="u-row-container"
                            style="padding: 0px; background-color: transparent"
                            >
                            <div
                                class="u-row"
                                style="
                                margin: 0 auto;
                                min-width: 320px;
                                max-width: 600px;
                                overflow-wrap: break-word;
                                word-wrap: break-word;
                                word-break: break-word;
                                background-color: #ffffff;
                                "
                            >
                                <div
                                style="
                                    border-collapse: collapse;
                                    display: table;
                                    width: 100%;
                                    height: 100%;
                                    background-color: transparent;
                                "
                                >
                                <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px;"><tr style="background-color: #ffffff;"><![endif]-->

                                <!--[if (mso)|(IE)]><td align="center" width="600" style="width: 600px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;" valign="top"><![endif]-->

                                <!--[if (mso)|(IE)]></td><![endif]-->
                                <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
                                </div>
                            </div>
                            </div>

                            <div
                            class="u-row-container"
                            style="padding: 0px; background-color: transparent"
                            >
                            <div
                                class="u-row"
                                style="
                                margin: 0 auto;
                                min-width: 320px;
                                max-width: 600px;
                                overflow-wrap: break-word;
                                word-wrap: break-word;
                                word-break: break-word;
                                background-color: #bfedd2;
                                "
                            >
                                <div
                                style="
                                    border-collapse: collapse;
                                    display: table;
                                    width: 100%;
                                    height: 100%;
                                    background-color: transparent;
                                "
                                >
                                <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px;"><tr style="background-color: #bfedd2;"><![endif]-->

                                <!--[if (mso)|(IE)]><td align="center" width="600" style="width: 600px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;" valign="top"><![endif]-->
                                <div
                                    class="u-col u-col-100"
                                    style="
                                    max-width: 320px;
                                    min-width: 600px;
                                    display: table-cell;
                                    vertical-align: top;
                                    "
                                >
                                    <div style="height: 100%; width: 100% !important">
                                    <!--[if (!mso)&(!IE)]><!-->
                                    <div
                                        style="
                                        height: 100%;
                                        padding: 0px;
                                        border-top: 0px solid transparent;
                                        border-left: 0px solid transparent;
                                        border-right: 0px solid transparent;
                                        border-bottom: 0px solid transparent;
                                        "
                                    >
                                        <!--<![endif]-->
                                        <table
                                        style="font-family: 'Montserrat', sans-serif"
                                        role="presentation"
                                        cellpadding="0"
                                        cellspacing="0"
                                        width="100%"
                                        border="0"
                                        >
                                        <tbody>
                                            <tr>
                                            <td
                                                style="
                                                overflow-wrap: break-word;
                                                word-break: break-word;
                                                padding: 25px 10px 0px 30px;
                                                font-family: 'Montserrat', sans-serif;
                                                "
                                                align="left"
                                            >
                                                <div
                                                style="
                                                    color: #264653;
                                                    line-height: 140%;
                                                    text-align: left;
                                                    word-wrap: break-word;
                                                "
                                                >
                                                <p style="line-height: 140%; font-size: 14px">
                                                    <span
                                                    style="
                                                        line-height: 19.6px;
                                                        font-size: 14px;
                                                    "
                                                    ><span
                                                        style="
                                                        font-size: 16px;
                                                        line-height: 22.4px;
                                                        "
                                                        ><strong>Olá, você</strong></span
                                                    ><strong style="font-size: 16px"
                                                        >, tudo bem? </strong
                                                    ></span
                                                    >
                                                </p>
                                                </div>
                                            </td>
                                            </tr>
                                        </tbody>
                                        </table>

                                        <table
                                        style="font-family: 'Montserrat', sans-serif"
                                        role="presentation"
                                        cellpadding="0"
                                        cellspacing="0"
                                        width="100%"
                                        border="0"
                                        >
                                        <tbody>
                                            <tr>
                                            <td
                                                style="
                                                overflow-wrap: break-word;
                                                word-break: break-word;
                                                padding: 10px 30px;
                                                font-family: 'Montserrat', sans-serif;
                                                "
                                                align="left"
                                            >
                                                <div
                                                style="
                                                    color: #264653;
                                                    line-height: 160%;
                                                    text-align: left;
                                                    word-wrap: break-word;
                                                "
                                                >
                                                <p
                                                    style="
                                                    font-size: 14px;
                                                    line-height: 160%;
                                                    text-align: justify;
                                                    "
                                                >
                                                    Estou enviando esta resposta pois recebemos
                                                    a sua história, porém ela foi recusada
                                                    na
                                                    <span
                                                    style="
                                                        text-decoration: underline;
                                                        font-size: 14px;
                                                        line-height: 22.4px;
                                                    "
                                                    ><span
                                                        style="
                                                        color: #2dc26b;
                                                        font-size: 14px;
                                                        line-height: 22.4px;
                                                        text-decoration: underline;
                                                        "
                                                        >Kiniga</span
                                                    ></span
                                                    >.
                                                </p>

                                                
                                                </div>
                                            </td>
                                            </tr>
                                        </tbody>
                                        </table>

                                        <br />

                                        <table
                                        style="font-family: 'Montserrat', sans-serif"
                                        role="presentation"
                                        cellpadding="0"
                                        cellspacing="0"
                                        width="100%"
                                        border="0"
                                        >
                                        <tbody>
                                            <tr>
                                            <td
                                                style="
                                                overflow-wrap: break-word;
                                                word-break: break-word;
                                                padding: 10px 10px 0px 30px;
                                                font-family: 'Montserrat', sans-serif;
                                                "
                                                align="left"
                                            >
                                                <div
                                                style="
                                                    color: #264653;
                                                    line-height: 140%;
                                                    text-align: left;
                                                    word-wrap: break-word;
                                                "
                                                >
                                                <p style="font-size: 14px; line-height: 140%">
                                                    <span
                                                    style="
                                                        font-size: 14px;
                                                        line-height: 19.6px;
                                                        background-color: #f8cac6;
                                                    "
                                                    ><strong>ATENÇÃO!</strong></span
                                                    >
                                                </p>
                                                </div>
                                            </td>
                                            </tr>
                                        </tbody>
                                        </table>

                                        <table
                                        style="font-family: 'Montserrat', sans-serif"
                                        role="presentation"
                                        cellpadding="0"
                                        cellspacing="0"
                                        width="100%"
                                        border="0"
                                        >
                                        <tbody>
                                            <tr>
                                            <td
                                                style="
                                                overflow-wrap: break-word;
                                                word-break: break-word;
                                                padding: 0px 20px 10px 30px;
                                                font-family: 'Montserrat', sans-serif;
                                                "
                                                align="left"
                                            >
                                                <div
                                                style="
                                                    color: #264653;
                                                    line-height: 180%;
                                                    text-align: left;
                                                    word-wrap: break-word;
                                                "
                                                >
                                                <p
                                                    style="
                                                    font-size: 14px;
                                                    line-height: 180%;
                                                    text-align: justify;
                                                    "
                                                >
                                                    <span
                                                    style="
                                                        background-color: #f8cac6;
                                                        font-size: 14px;
                                                        line-height: 25.2px;
                                                    "
                                                    >Todas as suas dúvidas, e mais, podem
                                                    ser</span
                                                    ><span
                                                    style="
                                                        background-color: #f8cac6;
                                                        font-size: 14px;
                                                        line-height: 25.2px;
                                                    "
                                                    >respondidas ao ler o
                                                    <a
                                                        rel="noopener"
                                                        href="https://docs.google.com/document/d/1Yrj84cdIQQwFMkmCZ8k9YLgLkA4dngI57yl3TtfxqaE/edit?usp=sharing"
                                                        target="_blank"
                                                        ><span
                                                        style="
                                                            color: #2dc26b;
                                                            font-size: 14px;
                                                            line-height: 25.2px;
                                                        "
                                                        >FAQ</span
                                                        ></a
                                                    >. </span
                                                    >
                                                </p>
                                                </div>
                                            </td>
                                            </tr>
                                        </tbody>
                                        </table>

                                        <table
                                        style="font-family: 'Montserrat', sans-serif"
                                        role="presentation"
                                        cellpadding="0"
                                        cellspacing="0"
                                        width="100%"
                                        border="0"
                                        >
                                        <tbody>
                                            <tr>
                                            <td
                                                style="
                                                overflow-wrap: break-word;
                                                word-break: break-word;
                                                padding: 10px 30px;
                                                font-family: 'Montserrat', sans-serif;
                                                "
                                                align="left"
                                            >
                                                <div
                                                style="
                                                    color: #264653;
                                                    line-height: 160%;
                                                    text-align: left;
                                                    word-wrap: break-word;
                                                "
                                                >
                                                <p style="font-size: 14px; line-height: 160%">
                                                    <strong
                                                    ><span
                                                        style="
                                                        font-family: Lato, sans-serif;
                                                        font-size: 14px;
                                                        line-height: 22.4px;
                                                        color: #264653;
                                                        "
                                                        >Mas, se você tiver alguma dúvida,
                                                        contate-nos pelo Discord.<span
                                                        style="
                                                            color: #34495e;
                                                            font-size: 14px;
                                                            line-height: 22.4px;
                                                        "
                                                        ></span></span
                                                    ></strong>
                                                </p>
                                                </div>
                                            </td>
                                            </tr>
                                        </tbody>
                                        </table>

                                        <!--[if (!mso)&(!IE)]><!-->
                                    </div>
                                    <!--<![endif]-->
                                    </div>
                                </div>
                                <!--[if (mso)|(IE)]></td><![endif]-->
                                <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
                                </div>
                            </div>
                            </div>

                            <div
                            class="u-row-container"
                            style="padding: 0px; background-color: transparent"
                            >
                            <div
                                class="u-row"
                                style="
                                margin: 0 auto;
                                min-width: 320px;
                                max-width: 600px;
                                overflow-wrap: break-word;
                                word-wrap: break-word;
                                word-break: break-word;
                                background-color: #264653;
                                "
                            >
                                <div
                                style="
                                    border-collapse: collapse;
                                    display: table;
                                    width: 100%;
                                    height: 100%;
                                    background-color: transparent;
                                "
                                >
                                <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding: 0px;background-color: transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px;"><tr style="background-color: #264653;"><![endif]-->

                                <!--[if (mso)|(IE)]><td align="center" width="600" style="width: 600px;padding: 0px;border-top: 0px solid transparent;border-left: 0px solid transparent;border-right: 0px solid transparent;border-bottom: 0px solid transparent;" valign="top"><![endif]-->
                                <div
                                    class="u-col u-col-100"
                                    style="
                                    max-width: 320px;
                                    min-width: 600px;
                                    display: table-cell;
                                    vertical-align: top;
                                    "
                                >
                                    <div style="height: 100%; width: 100% !important">
                                    <!--[if (!mso)&(!IE)]><!-->
                                    <div
                                        style="
                                        height: 100%;
                                        padding: 0px;
                                        border-top: 0px solid transparent;
                                        border-left: 0px solid transparent;
                                        border-right: 0px solid transparent;
                                        border-bottom: 0px solid transparent;
                                        "
                                    >
                                        <!--<![endif]-->
                                        <table
                                        style="font-family: 'Montserrat', sans-serif"
                                        role="presentation"
                                        cellpadding="0"
                                        cellspacing="0"
                                        width="100%"
                                        border="0"
                                        >
                                        <tbody>
                                            <tr>
                                            <td
                                                style="
                                                overflow-wrap: break-word;
                                                word-break: break-word;
                                                padding: 30px 10px 0px;
                                                font-family: 'Montserrat', sans-serif;
                                                "
                                                align="left"
                                            >
                                                <h1
                                                style="
                                                    margin: 0px;
                                                    color: #ffffff;
                                                    line-height: 140%;
                                                    text-align: center;
                                                    word-wrap: break-word;
                                                    font-weight: normal;
                                                    font-family: trebuchet ms, geneva;
                                                    font-size: 22px;
                                                "
                                                >
                                                <strong>Sobre Nós</strong>
                                                </h1>
                                            </td>
                                            </tr>
                                        </tbody>
                                        </table>

                                        <table
                                        style="font-family: 'Montserrat', sans-serif"
                                        role="presentation"
                                        cellpadding="0"
                                        cellspacing="0"
                                        width="100%"
                                        border="0"
                                        >
                                        <tbody>
                                            <tr>
                                            <td
                                                style="
                                                overflow-wrap: break-word;
                                                word-break: break-word;
                                                padding: 10px;
                                                font-family: 'Montserrat', sans-serif;
                                                "
                                                align="left"
                                            >
                                                <div
                                                style="
                                                    line-height: 140%;
                                                    text-align: center;
                                                    word-wrap: break-word;
                                                "
                                                >
                                                <p style="font-size: 14px; line-height: 140%">
                                                    <span
                                                    style="
                                                        color: #ffffff;
                                                        font-size: 14px;
                                                        line-height: 19.6px;
                                                    "
                                                    >W W W . K I N I G A . C O M</span
                                                    >
                                                </p>
                                                </div>
                                            </td>
                                            </tr>
                                        </tbody>
                                        </table>

                                        <table
                                        style="font-family: 'Montserrat', sans-serif"
                                        role="presentation"
                                        cellpadding="0"
                                        cellspacing="0"
                                        width="100%"
                                        border="0"
                                        >
                                        <tbody>
                                            <tr>
                                            <td
                                                style="
                                                overflow-wrap: break-word;
                                                word-break: break-word;
                                                padding: 10px;
                                                font-family: 'Montserrat', sans-serif;
                                                "
                                                align="left"
                                            >
                                                <div align="center">
                                                <div style="display: table; max-width: 167px">
                                                    <!--[if (mso)|(IE)]><table width="167" cellpadding="0" cellspacing="0" border="0"><tr><td style="border-collapse:collapse;" align="center"><table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse; mso-table-lspace: 0pt;mso-table-rspace: 0pt; width:167px;"><tr><![endif]-->

                                                    <!--[if (mso)|(IE)]><td width="32" style="width:32px; padding-right: 10px;" valign="top"><![endif]-->
                                                    <table
                                                    align="left"
                                                    border="0"
                                                    cellspacing="0"
                                                    cellpadding="0"
                                                    width="32"
                                                    height="32"
                                                    style="
                                                        width: 32px !important;
                                                        height: 32px !important;
                                                        display: inline-block;
                                                        border-collapse: collapse;
                                                        table-layout: fixed;
                                                        border-spacing: 0;
                                                        mso-table-lspace: 0pt;
                                                        mso-table-rspace: 0pt;
                                                        vertical-align: top;
                                                        margin-right: 10px;
                                                    "
                                                    >
                                                    <tbody>
                                                        <tr style="vertical-align: top">
                                                        <td
                                                            align="left"
                                                            valign="middle"
                                                            style="
                                                            word-break: break-word;
                                                            border-collapse: collapse !important;
                                                            vertical-align: top;
                                                            "
                                                        >
                                                            <a
                                                            href="https://www.facebook.com/kinigabrasil"
                                                            title="Facebook"
                                                            target="_blank"
                                                            >
                                                            <img
                                                                src="cid:image1"
                                                                alt="Facebook"
                                                                title="Facebook"
                                                                width="32"
                                                                style="
                                                                outline: none;
                                                                text-decoration: none;
                                                                -ms-interpolation-mode: bicubic;
                                                                clear: both;
                                                                display: block !important;
                                                                border: none;
                                                                height: auto;
                                                                float: none;
                                                                max-width: 32px !important;
                                                                "
                                                            />
                                                            </a>
                                                        </td>
                                                        </tr>
                                                    </tbody>
                                                    </table>
                                                    <!--[if (mso)|(IE)]></td><![endif]-->

                                                    <!--[if (mso)|(IE)]><td width="32" style="width:32px; padding-right: 10px;" valign="top"><![endif]-->
                                                    <table
                                                    align="left"
                                                    border="0"
                                                    cellspacing="0"
                                                    cellpadding="0"
                                                    width="32"
                                                    height="32"
                                                    style="
                                                        width: 32px !important;
                                                        height: 32px !important;
                                                        display: inline-block;
                                                        border-collapse: collapse;
                                                        table-layout: fixed;
                                                        border-spacing: 0;
                                                        mso-table-lspace: 0pt;
                                                        mso-table-rspace: 0pt;
                                                        vertical-align: top;
                                                        margin-right: 10px;
                                                    "
                                                    >
                                                    <tbody>
                                                        <tr style="vertical-align: top">
                                                        <td
                                                            align="left"
                                                            valign="middle"
                                                            style="
                                                            word-break: break-word;
                                                            border-collapse: collapse !important;
                                                            vertical-align: top;
                                                            "
                                                        >
                                                            <a
                                                            href="https://twitter.com/KinigaBrasil"
                                                            title="Twitter"
                                                            target="_blank"
                                                            >
                                                            <img
                                                                src="cid:image2"
                                                                alt="Twitter"
                                                                title="Twitter"
                                                                width="32"
                                                                style="
                                                                outline: none;
                                                                text-decoration: none;
                                                                -ms-interpolation-mode: bicubic;
                                                                clear: both;
                                                                display: block !important;
                                                                border: none;
                                                                height: auto;
                                                                float: none;
                                                                max-width: 32px !important;
                                                                "
                                                            />
                                                            </a>
                                                        </td>
                                                        </tr>
                                                    </tbody>
                                                    </table>
                                                    <!--[if (mso)|(IE)]></td><![endif]-->

                                                    <!--[if (mso)|(IE)]><td width="32" style="width:32px; padding-right: 10px;" valign="top"><![endif]-->
                                                    <table
                                                    align="left"
                                                    border="0"
                                                    cellspacing="0"
                                                    cellpadding="0"
                                                    width="32"
                                                    height="32"
                                                    style="
                                                        width: 32px !important;
                                                        height: 32px !important;
                                                        display: inline-block;
                                                        border-collapse: collapse;
                                                        table-layout: fixed;
                                                        border-spacing: 0;
                                                        mso-table-lspace: 0pt;
                                                        mso-table-rspace: 0pt;
                                                        vertical-align: top;
                                                        margin-right: 10px;
                                                    "
                                                    >
                                                    <tbody>
                                                        <tr style="vertical-align: top">
                                                        <td
                                                            align="left"
                                                            valign="middle"
                                                            style="
                                                            word-break: break-word;
                                                            border-collapse: collapse !important;
                                                            vertical-align: top;
                                                            "
                                                        >
                                                            <a
                                                            href="https://www.instagram.com/p/CAp_qaQHEuM/"
                                                            title="Instagram"
                                                            target="_blank"
                                                            >
                                                            <img
                                                                src="cid:image4"
                                                                alt="Instagram"
                                                                title="Instagram"
                                                                width="32"
                                                                style="
                                                                outline: none;
                                                                text-decoration: none;
                                                                -ms-interpolation-mode: bicubic;
                                                                clear: both;
                                                                display: block !important;
                                                                border: none;
                                                                height: auto;
                                                                float: none;
                                                                max-width: 32px !important;
                                                                "
                                                            />
                                                            </a>
                                                        </td>
                                                        </tr>
                                                    </tbody>
                                                    </table>
                                                    <!--[if (mso)|(IE)]></td><![endif]-->

                                                    <!--[if (mso)|(IE)]><td width="32" style="width:32px; padding-right: 0px;" valign="top"><![endif]-->
                                                    <table
                                                    align="left"
                                                    border="0"
                                                    cellspacing="0"
                                                    cellpadding="0"
                                                    width="32"
                                                    height="32"
                                                    style="
                                                        width: 32px !important;
                                                        height: 32px !important;
                                                        display: inline-block;
                                                        border-collapse: collapse;
                                                        table-layout: fixed;
                                                        border-spacing: 0;
                                                        mso-table-lspace: 0pt;
                                                        mso-table-rspace: 0pt;
                                                        vertical-align: top;
                                                        margin-right: 0px;
                                                    "
                                                    >
                                                    <tbody>
                                                        <tr style="vertical-align: top">
                                                        <td
                                                            align="left"
                                                            valign="middle"
                                                            style="
                                                            word-break: break-word;
                                                            border-collapse: collapse !important;
                                                            vertical-align: top;
                                                            "
                                                        >
                                                            <a
                                                            href="https://discord.gg/QMKHU8y"
                                                            title="Discord"
                                                            target="_blank"
                                                            >
                                                            <img
                                                                src="cid:image6"
                                                                alt="Discord"
                                                                title="Discord"
                                                                width="32"
                                                                style="
                                                                outline: none;
                                                                text-decoration: none;
                                                                -ms-interpolation-mode: bicubic;
                                                                clear: both;
                                                                display: block !important;
                                                                border: none;
                                                                height: auto;
                                                                float: none;
                                                                max-width: 32px !important;
                                                                "
                                                            />
                                                            </a>
                                                        </td>
                                                        </tr>
                                                    </tbody>
                                                    </table>
                                                    <!--[if (mso)|(IE)]></td><![endif]-->

                                                    <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
                                                </div>
                                                </div>
                                            </td>
                                            </tr>
                                        </tbody>
                                        </table>

                                        <table
                                        style="font-family: 'Montserrat', sans-serif"
                                        role="presentation"
                                        cellpadding="0"
                                        cellspacing="0"
                                        width="100%"
                                        border="0"
                                        >
                                        <tbody>
                                            <tr>
                                            <td
                                                style="
                                                overflow-wrap: break-word;
                                                word-break: break-word;
                                                padding: 10px 10px 15px;
                                                font-family: 'Montserrat', sans-serif;
                                                "
                                                align="left"
                                            >
                                                <div
                                                style="
                                                    color: #ffffff;
                                                    line-height: 160%;
                                                    text-align: center;
                                                    word-wrap: break-word;
                                                "
                                                >
                                                <p style="font-size: 14px; line-height: 160%">
                                                    ©️ 2022 – Todos os direitos reservados<br /><span
                                                    style="
                                                        color: #ffffff;
                                                        font-size: 14px;
                                                        line-height: 22.4px;
                                                    "
                                                    ><a
                                                        rel="noopener"
                                                        href="https://politicas.kiniga.com/termos-de-servico/"
                                                        target="_blank"
                                                        style="color: #ffffff"
                                                        >Termos de Serviço</a
                                                    ></span
                                                    >
                                                    |
                                                    <span
                                                    style="
                                                        color: #ffffff;
                                                        font-size: 14px;
                                                        line-height: 22.4px;
                                                    "
                                                    ><a
                                                        rel="noopener"
                                                        href="https://politicas.kiniga.com/politicas-de-privacidade/"
                                                        target="_blank"
                                                        style="color: #ffffff"
                                                        >Política de Privacidade</a
                                                    ></span
                                                    >
                                                </p>
                                                </div>
                                            </td>
                                            </tr>
                                        </tbody>
                                        </table>

                                        <!--[if (!mso)&(!IE)]><!-->
                                    </div>
                                    <!--<![endif]-->
                                    </div>
                                </div>
                                <!--[if (mso)|(IE)]></td><![endif]-->
                                <!--[if (mso)|(IE)]></tr></table></td></tr></table><![endif]-->
                                </div>
                            </div>
                            </div>

                            <!--[if (mso)|(IE)]></td></tr></table><![endif]-->
                        </td>
                        </tr>
                    </tbody>
                    </table>
                    <!--[if mso]></div><![endif]-->
                    <!--[if IE]></div><![endif]-->
                </body>
                </html>


            """
            emailtxt = """\
                Esta é uma mensagem automática. Não responda.

                Olá, como você está?


                Viemos informar que recebemos a sua história, mas infelizmente não poderemos aceitá-la no site, pois nela há uma carência dos requisitos mínimos para que uma história seja publicada. Mas não desanime, você pode nos enviar a história novamente quando desejar! E não se esqueça de revisar bem antes de enviar, beleza?

                Caso tenha dúvidas, temos um FAQ, onde você pode ter um contato com nossa equipe. Mande mensagem para os membros da equipe apenas após ir ao FAQ e jamais entre em contato pelo privado (caso seja preciso, um membro irá chamá-lo, nunca o contrário).

                (FAQ fixado no chat geral do nosso servidor do discord)

                Link Kiniga: https://discord.gg/dWGvCr3

                Também temos parceria com o server Novel Brasil, uma comunidade para escritores. Lá você pode encontrar outros autores e pessoas que podem te ajudar a melhorar na escrita, com aulas em calls, conversa com tutores e artigos do blog que eles possuem.

                Link Novel Brasil: https://discord.gg/2yEkSWdM9z

                Em todo caso, espero que tenha um dia muito produtivo escrevendo!
                
                """

        return email, emailtxt
