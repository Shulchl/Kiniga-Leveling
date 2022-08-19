from __future__ import annotations

from datetime import datetime as dt
from datetime import timedelta
from pydoc import describe
import requests
import shutil
from asyncio import sleep as asyncsleep

import discord
import discord.utils
from discord.ext import commands
from discord import app_commands
from typing import Literal
from typing import Optional
   
## Mod Itens Class
class ModItem(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        
    ## UTILIDADES
    @commands.command(name="ori")
    @commands.has_permissions(administrator=True)
    async def ori(self, ctx, simbol: Optional[Literal['-', '+']], amount: int, member: discord.Member = None):
        member = member or ctx.author
        if member:
            if simbol == '+':
                await self.db.fetch(f"UPDATE users SET coin = ( coin + {amount}) WHERE id= (\'{member.id}\')")
                return await ctx.send(f"Foram adicionadas {amount} oris à {member.mention}!", delete_after=10)
            elif simbol == '-':
                await self.db.fetch(f"UPDATE users SET coin = (coin - {amount}) WHERE id= (\'{member.id}\')")
                return await ctx.send(f"Foram removidas {amount} oris de {member.mention}!", delete_after=10)
        else:
            return await ctx.send("O usuário não está no servidor")

    # Pin/Unpin shop item

    @commands.has_any_role(
        667839130570588190,
        815704339221970985,
        677283492824088576,
        'Administrador',
        'Admin',
        943171518895095869,
        943174476839936010,
        943192163947274341,
        943172687642132591,
        943171893752659979,
        943172687642132591,
        943193084584402975,
        943251043838468127
    )
    @commands.cooldown(1, 300, commands.BucketType.member)
    @commands.command(aliases=[ "destaque" ], name='dest',
                      help='SÓ PARA EQUIPE! \n Ao digitar s.det <ID-DO-ITEM>, destaca o item na loja.')
    async def dest(self, ctx, id):
        await ctx.message.delete()
        result = await self.db.fetch(f'SELECT * FROM itens WHERE id = {int(id)}')
        if result:
            await self.db.fetch(f'UPDATE itens SET dest = True WHERE id={int(id)}')
            emb = discord.Embed(
                description=f'O item foi adicionado aos destaques.',
                color=discord.Color.green()).set_footer(
                text='Use [s.tdestaque ID] para tirar o destaque do item.')
            await ctx.send(f'{ctx.author.mention}', embed=emb)
        else:
            await ctx.send("Não encontrei um item com esse ID", delete_after=5)

    #
    # Tira destaque do item // Unpin shop item

    @commands.has_any_role(
        667839130570588190,
        815704339221970985,
        677283492824088576,
        'Administrador',
        'Admin',
        943171518895095869,
        943174476839936010,
        943192163947274341,
        943172687642132591,
        943171893752659979,
        943172687642132591,
        943193084584402975,
        943251043838468127
    )
    @commands.command(aliases=[ "tirar", "td" ], name='tdest',
                      help='SÓ PARA EQUIPE! \n Ao digitar s.tdet <ID-DO-ITEM>, remove o destaque do item na loja.')
    @commands.cooldown(1, 300, commands.BucketType.member)
    async def tdest(self, ctx, id):
        await ctx.message.delete()
        result = await self.db.fetch(f"SELECT * FROM itens WHERE id = {int(id)}")
        if result:
            await self.db.fetch(f"UPDATE itens SET dest = False WHERE id={int(id)}")
            emb = discord.Embed(
                description=f'O item foi removido dos destaques.',
                color=discord.Color.green()).set_footer(
                text='Use [s.destaque ID] para destacar o item novamente.')
            await ctx.send(f'{ctx.author.mention}', embed=emb)
        else:
            await ctx.send("Não encontrei um item com esse ID", delete_after=5)

    @commands.has_any_role(
        667839130570588190,
        815704339221970985,
        677283492824088576,
        'Administrador',
        'Admin',
        943171518895095869,
        943174476839936010,
        943192163947274341,
        943172687642132591,
        943171893752659979,
        943172687642132591,
        943193084584402975,
        943251043838468127
    )
    @commands.command(aliases=[ "tbuy", "tcomprar" ], name='canotbuy',
                      help='SÓ PARA EQUIPE! \n Ao digitar s.canbuy <ID-DO-ITEM>, remove o item da loja.')
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def canotbuy(self, ctx, id: int):
        await ctx.message.delete()
        result = await self.db.fetch(f'SELECT * FROM itens WHERE id = {id}')
        if result:
            await self.db.fetch(f'UPDATE itens SET canbuy = False WHERE id = {id}')
            emb = discord.Embed(
                description=f'O item foi removido da loja.',
                color=discord.Color.green()).set_footer(
                text='Use [s.canbuy ID] para recolocar o item novamente.')
            await ctx.send(f'{ctx.author.mention}', embed=emb)
        else:
            await ctx.send("Não encontrei um item com esse ID", delete_after=5)

    @commands.command(aliases=[ "cbuy", "ccomprar" ], name='canbuy',
                      help='SÓ PARA EQUIPE! \n Ao digitar s.canbuy <ID-DO-ITEM>, remove o item da loja.')
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def canbuy(self, ctx, id: int):
        await ctx.message.delete()
        result = await self.db.fetch(f'SELECT * FROM itens WHERE id = {id}')
        if result:
            await self.db.fetch(f'UPDATE itens SET canbuy = True WHERE id = {id}')
            emb = discord.Embed(
                description=f'O item foi adicionado à loja.',
                color=discord.Color.green()).set_footer(
                text='Use [s.canotbuy ID] para remover o item novamente.')
            await ctx.send(f'{ctx.author.mention}', embed=emb)
        else:
            await ctx.send("Não encontrei um item com esse ID", delete_after=5)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ModItem(bot), guilds=[ discord.Object(id=943170102759686174) ])
