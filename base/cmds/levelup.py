import json
import discord
import sys

from random import randint
from discord.ext import commands

from base.utilities import utilities
from base.functions import get_profile_info

from discord.ext.commands.errors import MissingPermissions, RoleNotFound

from base import cfg, log

# CLASS LEVELING


class Levelup(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = utilities.database(self.bot.loop)
        self.cd_mapping = commands.CooldownMapping.from_cooldown(
            1, 0.1, commands.BucketType.member)

        self.cfg = cfg

        #self.brake = []
    def cog_load(self):
        sys.stdout.write(f'Cog carregada: {self.__class__.__name__}\n')
        sys.stdout.flush()

    def cog_unload(self):
        sys.stdout.write(f'Cog descarregada: {self.__class__.__name__}\n')
        sys.stdout.flush()

    async def has_db(message):
        a = await self.db.fetch(
            """
                SELECT name FROM users WHERE id=%s LIMIT 1
            """ % (message.author.id)
        )
        log.error("\n\nuser check\n\n", flush=True)
        return a != None

    @commands.before_invoke(has_db)
    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        if message.author.bot:
            return
        if message.author.id == self.bot.user.id:
            return

        bucket = self.cd_mapping.get_bucket(message)

        if not bucket.update_rate_limit():
            member_id = message.author.id

            user_ = await get_profile_info(self, member_id, message.author.name)

            user_id, user_rank, user_xp, user_xptotal, info, spark, ori, user_iventory_id, birth, rank_id, user_name, email = user_

            if user_rank >= 80:
                return
            
            lvUpChannel = self.bot.get_channel(1009074998889164880)
            spark = randint(self.cfg.coinsmin, self.cfg.coinsmax)
            # result = await self.db.fetch(f"SELECT rank, xp, xptotal FROM users WHERE id=('{member_id}')")
            expectedXP = randint(self.cfg.min_message_xp,
                                 self.cfg.max_message_xp)
            current_xp = user_xp + expectedXP

            if current_xp >= utilities.rankcard.neededxp(user_rank):
                try:
                    rank = await self.db.fetchval("""
                        UPDATE users 
                        SET rank = %s, 
                            xptotal = ( xptotal + %s ), 
                            spark = ( spark + %s ) 
                        WHERE id = ( \'%s\' )
                        RETURNING rank
                    """ % (user_rank + 1, expectedXP, spark, member_id, ))

                    await lvUpChannel.send(
                        "> %s__, você subiu para o nível %s!__ \n> `+%s sparks +%s pontos de experiência.`"
                        % (message.author.mention, rank, spark, expectedXP, ), delete_after=10)

                    rankNames = await self.db.fetch("""
                        SELECT name 
                        FROM ranks 
                        WHERE lvmin <= %s 
                        ORDER BY lvmin DESC
                    """ % (rank, ))

                    nextRank = discord.utils.find(
                        lambda r: r.name == rankNames[0][0], 
                            message.guild.roles
                    ) or rankNames[0][0]
                    # print([x[0] for x in rankNames])
                    prevRank = [
                        x[0] for x in rankNames if x[0] in self.cfg.ranks and x[0] != (
                        rankNames[0][0] if rankNames[0][0] != "Novato" else "qualquercoisa")
                    ]
                    # print(prevRank)
                    try:
                        if nextRank in message.author.roles:
                            # await self.lvUpChannel.send("> `%s, você tem um cargo que não deveria ter... (≖_≖ ) `" % (message.author.mention, ), delete_after=10)
                            return

                        await message.author.add_roles(nextRank)

                        if len(prevRank) == 0:
                            return

                        # await self.lvUpChannel.send("+"*10+prevRole +"+"*10)
                        prevRank = [
                            discord.utils.find(
                                lambda r: r.name == i, message.guild.roles
                            ) for i in prevRank
                        ]

                        for r in prevRank:
                            if r in message.author.roles:
                                await message.author.remove_roles(r)

                    except Exception as i:
                        if isinstance(i, commands.MissingPermissions):
                            return await lvUpChannel.send(
                                "> %s `Eu não tenho permissão para adicionar/remover cargos, reporte à um ADM.`"
                                % (message.author.mention, )
                            )
                        elif isinstance(i, commands.RoleNotFound):
                            return await lvUpChannel.send(
                                "> %s `Não consegui encontrar o cargo, favor, reporte à um ADM.`"
                                % (message.author.mention, )
                            )
                        else:
                            raise i
                    # else:
                    #    print("Cargos adicionados/removidos com sucesso.")
                        # rank2 = await self.db.fetch(f'SELECT lv, name, r, g, b FROM ranks WHERE lv <={
                        # user_rank} ORDER BY lv DESC')
                except Exception as e:
                    raise e
            else:
                await self.db.execute("""
                    UPDATE users 
                    SET xp=(%s), 
                        xptotal=(xptotal + %s), 
                        spark=(spark + %s) 
                    WHERE id=\'%s\'
                """ % (current_xp, current_xp + expectedXP, spark, member_id, ))

            # self.brake.append(message.author.id)
            #await asyncsleep(randint(0, 5))  #
            # self.brake.remove(message.author.id)


async def setup(bot: commands.Bot) -> None:
    # , guilds=[ discord.Object(id=943170102759686174), discord.Object(id=1010183521907789977)]
    await bot.add_cog(Levelup(bot), guilds=[discord.Object(id=943170102759686174)])
