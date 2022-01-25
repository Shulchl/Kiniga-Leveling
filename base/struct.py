from __future__ import annotations

class Config:
    def __init__(self, cfg: dict) -> None:
        self.bot_token = cfg['bot_token']
        self.postgresql_user = cfg['postgresql_user']
        self.postgresql_password = cfg['postgresql_password']
        self.min_message_xp = cfg['min_message_xp']
        self.max_message_xp = cfg['max_message_xp']
        self.coinsmin = cfg['coinsmin']
        self.coinsmax = cfg['coinsmax']
        self.lucky = cfg['lucky']
        self.prefix = cfg['prefix']
        self.bdayloop = cfg['bdayloop']
        self.guild = cfg['guild']
        self.chat_cmds = cfg['chat_cmds']
        self.coin_max = cfg['coin_max']
        self.setup = cfg['setup']
        self.ranks = cfg['ranks']
        self.colors = cfg['colors']
        self.trash = cfg['trash']
        
