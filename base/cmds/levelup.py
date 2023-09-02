from random import randint

import discord
from discord import Message
from discord.ext import commands

from base.Spinovelbot import SpinovelBot
from base.classes.functions.drawFunctions.level import neededxp
from base.functions import get_profile_info


# CLASS LEVELING


class Levelup(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot: SpinovelBot) -> None:
        self.bot = bot
        self.database = self.bot.database
        self.cd_mapping = commands.CooldownMapping.from_cooldown(
            1, 0.1, commands.BucketType.member)

        self.config = self.bot.config["other"]

    async def has_db(message):
        a = await SpinovelBot.database.select("users", "name", f"id={message.author.id}", None, 1)
        SpinovelBot.log(message="\n\nuser check\n\n", name="cmds.levelup")
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

            user_ = await get_profile_info(self.bot, member_id, message.author.name)
            user_id, user_name, email, info, user_rank, user_xp, xptotal, spark, ori, birth, created_at, updated_at = user_

            if user_rank >= 80:
                return

            lvUpChannel = self.bot.get_channel(1009074998889164880)

            spark = randint(self.config["coinsmin"], self.config["coinsmax"])
            expectedXP = randint(self.config["min_message_xp"],
                                 self.config["max_message_xp"])
            current_xp = user_xp + expectedXP

            if current_xp >= neededxp(user_rank):
                try:
                    await self.database.dict_increment(
                        "users",
                        {"rank": 1, "xptotal": expectedXP, "spark": spark},
                        f"id={member_id}"
                    )
                    '''
                    await self.database.query(f"""
                        UPDATE users 
                        SET rank = {user_rank + 1}, 
                            xptotal = ( xptotal + {expectedXP} ), 
                            spark = ( spark + {spark} ) 
                        WHERE id = ( {member_id} )
                    """)
                    '''
                    rank = await self.database.select("users", "rank", f"id={message.author.id}")

                    await lvUpChannel.send(
                        "> %s__, você subiu para o nível %s!__ \n> `+%s sparks +%s pontos de experiência.`"
                        % (message.author.mention, rank[0][0], spark, expectedXP,), delete_after=10)
                    rankNames = await self.database.select(
                        "ranks",
                        "name",
                        f"lvmin <= {rank[0][0]}",
                        "lvmin DESC;")
                    nextRank = discord.utils.find(
                        lambda r: r.name == rankNames[0][0],
                        message.guild.roles
                    )
                    prevRank = [
                        x[0] for x in rankNames if x[0] in self.config["ranks"] and str(x[0]) != str(nextRank.name)
                    ]
                    try:
                        if nextRank not in message.author.roles:
                            await message.author.add_roles(nextRank)

                        if not prevRank:
                            return

                        prevRank = [
                            discord.utils.find(
                                lambda r: r.name == i, message.guild.roles
                            ) for i in prevRank
                        ]

                        if not prevRank:
                            return
                        for r in prevRank:
                            if r in message.author.roles:
                                await message.author.remove_roles(r)

                    except Exception as i:
                        if isinstance(i, commands.MissingPermissions):
                            await lvUpChannel.send(
                                "> %s `Eu não tenho permissão para adicionar/remover cargos, reporte à um ADM.`"
                                % (message.author.mention,)
                            )
                            raise i
                        elif isinstance(i, commands.RoleNotFound):
                            await lvUpChannel.send(
                                "> %s `Não consegui encontrar o cargo, favor, reporte à um ADM.`"
                                % (message.author.mention,)
                            )
                        raise i
                except Exception as e:
                    await lvUpChannel.send(f"{e}")
                    raise e
            else:
                await self.bot.database.dict_increment(
                    "users",
                    {"xp": f"{expectedXP}", "xptotal": f"{expectedXP}", "spark": f"{spark}"},
                    f"id={member_id}"
                )
                '''
                await self.bot.database.query(f"""
                    UPDATE users 
                    SET xp=({current_xp}), 
                        xptotal=(xptotal + {current_xp + expectedXP}), 
                        spark=(spark + {spark}) 
                    WHERE id={member_id}
                """)
                '''


async def setup(bot: SpinovelBot) -> None:
    # , guilds=[ discord.Object(id=943170102759686174), discord.Object(id=1010183521907789977)]
    await bot.add_cog(Levelup(bot), guilds=[discord.Object(id=943170102759686174)])
