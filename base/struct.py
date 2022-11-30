from __future__ import annotations


class Config:
    def __init__(self, cfg: dict) -> None:
        # COISAS DA DATABASE 
        self.dbName = cfg['db_Name']
        self.postgresql_user = cfg['postgresql_user']
        self.postgresql_password = cfg['postgresql_password']
        self.postgresql_host = cfg['postgresql_host']
        
        # COISAS DO DISCORD
        self.bot_token = cfg['bot_token']
        
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
        
        self.ranks = cfg['ranks']  # NOMES DE CARGOS DE RANK
        self.colors = cfg['colors'] # CORES DE CARGOS DE RANK
        self.trash = cfg['trash'] # NOME DE ITENS LIXO

        self.eqp_role = cfg['eqp_role'] # CARGO DE EQUIPE
        self.mark_role = cfg['mark_role'] # CARGO SEPARADOR
        self.aut_role = cfg['aut_role'] # CARGO DE AUTOR
        self.creat_role = cfg['creat_role'] # CARGO DE CRIADOR
        
        self.chat_creators = cfg['chat_creators'] # CANAL EXCLUSIVO DE AUTORES
        self.chat_release = cfg['chat_release'] # CANAL EM QUE SERÃO ENVIADOS OS CAPÍTULOS RECENTES

        self.acept_channel = cfg['acept_channel'] # CANAL EM QUE SERÁ ENVIADO OSS PROJETOS ACEITOS 
        self.refuse_channel = cfg['refuse_channel'] # CANAL EM QUE SERÁ ENVIADO OSS PROJETOS RECUSADOS
    
