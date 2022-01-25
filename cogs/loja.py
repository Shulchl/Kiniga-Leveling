from __future__ import annotations
from asyncio import sleep as asyncsleep
from base.utilities import utilities
import discord, aiohttp, re
from random import randint
from io import BytesIO
from discord import File as dFile
from discord import Member as dMember
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.errors import BadArgument, MissingRequiredArgument

# CLASS SHOP
class Shop(commands.Cog, name='Loja', description='Comandos de Opções Loja'):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = utilities.database(self.bot.loop, self.bot.cfg.postgresql_user, self.bot.cfg.postgresql_password)

    #   LOJA
    #@commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.command(name='loja', help='Ao digitar s.loja, mostra a loja, com diversas molduras e títulos para comprar!', aliases=["shop", "lojinha"])
    async def loja(self, ctx, page:int=None, member: dMember=None) -> None:
        if member:
            uMember = member
        else:
            uMember = ctx.author
            
        total = await self.db.fetch('SELECT COUNT(id) FROM itens')
        async with aiohttp.ClientSession() as session:
                async with session.get(f'{uMember.avatar_url_as(format="png", size=512)}') as resp:
                    userImg = await resp.read()
        for t in total:
            d = re.sub(r"\D", "", str(t))
            total = int(d)
            if  total > 0:
                rows = await self.db.fetch('SELECT id, name, type, value, img, imgd, lvmin, dest FROM itens WHERE canbuy = True ORDER BY dest Desc')
                if rows:
                    if page == None or page == 1 or page == 2:
                        count = 0
                    else:
                        await ctx.message.delete()
                        #if (total/3) > int(total/3):
                        #    return await ctx.send(f"O limite de páginas é {int(total/3)}", delete_after=5)
                        #elif (total/3) < int(total/3):
                        #    return await ctx.send(f"O limite de páginas é {int(total/3)+1}", delete_after=5)
                    
                    itens = []
                    while count < total:
                        try:
                            itens[count].append({
                                        "id" : str(rows[count][0]),
                                        "name" : str(rows[count][1]),
                                        "type" : str(rows[count][2]),
                                        "value" : str(rows[count][3]),
                                        "img" : str(rows[count][4]),
                                        "imgs" : str(rows[count][5]),
                                        "lvmin" : str(rows[count][6]),
                                        "dest" : str(rows[count][7])
                                        })
                        except:
                            itens.append({count:{
                                "id" : str(rows[count][0]),
                                "name" : str(rows[count][1]),
                                "type" : str(rows[count][2]),
                                "value" : str(rows[count][3]),
                                "img" : str(rows[count][4]),
                                "imgs" : str(rows[count][5]),
                                "lvmin" : str(rows[count][6]),
                                "dest" : str(rows[count][7])
                            }})
                            
                        count += 1
                        
                    for coin in await self.db.fetch(f'SELECT coin FROM users WHERE id = (\'{uMember.id}\')'):
                        if coin[0] == None:
                            coin[0] = 0
                        coin = coin[0]

                        buffer = utilities.shop.drawloja(total, itens, page, coin, BytesIO(userImg)) #byteImg

                    await ctx.reply(file=dFile(fp=buffer, filename='lojinha.png'), delete_after=30)
                    await ctx.message.delete()

                else:    
                    await ctx.reply(f'{uMember.mention}, parece que ainda não temos nenhum item comprável.', delete_after=5)
    @loja.error
    async def loja_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("```Só um usuário pode usar esse comando por vez, por favor aguarde 3 segundos.```", delete_after=5) 
    
    
    #   Comprar
    @commands.command(name='comprar', help='Ao digitar s.comprar <ID-DO-ITEM>, efetua a compra de um item utilizando o ID deste na loja.', aliases=["buy", "compra"])
    async def comprar(self, ctx, id:int) -> None:
        #await ctx.message.delete()
        item = await self.db.fetch(f'SELECT id, name, value, type, lvmin FROM itens WHERE id=\'{id}\' and canbuy = True')
        if item:
            item_id = item[0][0]
            item_name = item[0][1]
            item_value = item[0][2]
            item_type = item[0][3]
            lvmin = item[0][4]
            try:
                inv = await self.db.fetch(f'SELECT coin, inv, rank FROM users WHERE id = (\'{ctx.author.id}\')')
                if inv:
                    if  int(lvmin-9) <= int(inv[0][2]):
                        if int(inv[0][0]) >= int(item_value):
                            if item_type == 'Moldura':
                                tipo = "a moldura"
                                esstipo = "essa moldura"
                            elif item_type == 'Titulo':
                                tipo = "o título"
                                esstipo = "esse título"
                            elif item_type == 'Ticket':
                                tipo = "o ticket"
                                esstipo = "esse ticket"
                            
                            emb = discord.Embed(title='Bela compra!',
                                        description=f'Você acaba de comprar {tipo} {item_name}!',
                                        color=discord.Color.green()).set_footer(
                                            text='Para equipar em seu perfil, basta digitar:\n'
                                                's.equipar')
                                
                            if inv[0][1] is not None:
                                invent = str(inv[0][1])
                                if str(id) in invent.split(","):
                                    return await ctx.send(f"Você já tem {esstipo}.", delete_after=5)
                                else:
                                    await self.db.fetch(f'UPDATE users SET inv = (\'{str(invent) +","+ str(item_id)}\'), coin = ({int(inv[0][0]) - int(item_value)})  WHERE id=\'{ctx.author.id}\'')
                                    if item_type == 'Ticket':
                                        ticketid = item_name.strip("Ticket #")
                                        users = await self.db.fetch(f"SELECT users FROM tickets WHERE id='{int(ticketid)}'")
                                        if users[0][0] is not None:
                                            await self.db.fetch(f'UPDATE tickets SET users = (\'{str(users[0][0]) +","+ str(ctx.author.id)}\')')
                                            return await ctx.send("Agora você pode participar do sorteio!", delete_after=5)
                                        else:
                                            await self.db.fetch(f'UPDATE tickets SET users = (\'{str(ctx.author.id)}\')')
                                            return await ctx.send("Agora você pode participar do sorteio!", delete_after=5)
                            else:
                                await self.db.fetch(f'UPDATE users SET inv = (\'{item_id}\'), coin = ({int(inv[0][0]) - int(item_value)}) WHERE id=\'{ctx.author.id}\'')
                            return await ctx.send('',embed=emb, delete_after=10)
                        else:
                            return await ctx.send("Você é pobre, vá trabalhar.", delete_after=5)
                    else:
                        return await ctx.send("Você não tem nível para comprar isso.", delete_after=5)
                else:
                    return await ctx.send("Aconteceu algo enquanto eu tentava buscar as informações do usuário. Tente novamente mais tarde.", delete_after=5)
            except:
                raise
        else:
            return await ctx.send(f'{ctx.author.mention}, ou não existe um item com esse número(ID) ou o item não está disponível para compra.', delete_after=5)
    #

    #   Equipar
    @commands.command(name='equipar', help='Ao digitar s.equipar <ID-DO-ITEM>, equipa em seu s.perfil, um item do seu inventário, utilizando o ID deste.')
    async def equipar(self, ctx, id:int):
        await ctx.message.delete()
        item = await self.db.fetch(f"SELECT name, type FROM itens WHERE id='{id}'")
        if item:
            name = item[0][0]
            type = item[0][1]
            
            inv = await self.db.fetch(f"SELECT inv FROM users WHERE id='{ctx.author.id}'")
            if inv:
                inv = str(inv[0][0]).split(",")
                if str(id) in inv:
                    if str(type).upper() == "MOLDURA":
                        await self.db.fetch(f"UPDATE users SET mold=(\'{id}\') WHERE id='{ctx.author.id}'")
                        await ctx.send("{} {} equipada!".format(type.capitalize(), name.title()), delete_after=5)
                    if str(type).upper() == "TITULO":
                        await self.db.fetch(f"UPDATE users SET title=(\'{id}\') WHERE id='{ctx.author.id}'")
                        await ctx.send("{} {} equipada!".format(type.capitalize(), name.title()), delete_after=5)
            else:
                raise MissingRequiredArgument   
        else:
            raise BadArgument
        
    @equipar.error
    async def equipar_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("```Esse item não existe.```", delete_after=5)
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("```Você não tem esse item.```", delete_after=5)          
                  
        
def setup(bot) -> None:
    bot.add_cog(Shop(bot))

