import json
import os
import aiohttp
import discord
import asyncio

from discord.ext import commands

from base import log, cfg


#import matplotlib
#print(matplotlib.get_configdir(), flush=True)

TEST_GUILD = discord.Object(id=943170102759686174)

class SpinovelBot(commands.Bot):
    def __init__(self, **kwargs) -> None:
        
        super().__init__(
            intents=kwargs.pop("intents"),
            command_prefix=commands.when_mentioned_or(kwargs.pop("prefix")),
            description=kwargs.pop("description"),
            activity=kwargs.pop("activity"),
            case_insensitive = True,
        )

        log.info('Excluindo arquivos temporários...\n')
        buffer_total, buffer_result = self.buffer_remove()
        log.info('%s/%s Arquivos removidos.\n' % (buffer_total, buffer_result))

    def buffer_remove(self) -> None:
        total = 0
        file = os.listdir('./_temp')
        for filename in file:
            if filename.endswith(".png") or filename.endswith(".jpg"):
                os.remove('./_temp/%s' % (filename,))
                total = total + 1
        return len(file), total

        self.session = None

    async def load_cogs(self) -> None:
        for filename in os.listdir('./base/cmds'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'base.cmds.{filename[:-3]}')
                except Exception as e:
                    log.error(f'Ocorreu um erro enquanto a cog "{filename}" carregava.\n{e}')

    async def setup_hook(self) -> None:
        # discord.utils.setup_logging()
        log.info(f'Logado como {self.user} (ID: {self.user.id}) usando discord.py {discord.__version__}')
        await self.load_cogs()
        # self.tree.copy_global_to(guild=TEST_GUILD)
        # await self.tree.sync(guild=TEST_GUILD)

    async def close(self) -> None:
        log.info("desligando o bot...")
        await super().close()
        await self.session.close()


async def main() -> None:
    bot = SpinovelBot(
        prefix = cfg.prefix, 
        description = cfg.description, 
        activity = discord.Activity(
            type=discord.ActivityType.watching, name="Spinovel"
        ),
        intents = discord.Intents.all()
    )
    async with aiohttp.ClientSession() as session, bot:
        bot.session = session
        await bot.start(cfg.bot_token)


async def warn() -> None:
    return log.info("bot foi desligado usando ctrl+c no terminal!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(warn())
