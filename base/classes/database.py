import aiomysql
import asyncio

from datetime import datetime, date
from typing import Any, Optional

class MixedTypes():
    def __init__(self, value: Any) -> None:
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

class DataSQL():
    def __init__(self, bot, host: str = "localhost", port: int = 3306, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        self.bot, self.loop, self.host, self.port = bot, loop, host, port

    async def auth(self, user: str = "root", password: str = '', database: str = "mysql", autocommit: bool = True) -> None:
        self.__authUser, self.__authPassword, self.__authDatabase, self.__authAutocommit = user, password, database, autocommit
        self.pool: aiomysql.pool.Pool = await aiomysql.create_pool(
            host=self.host, 
            port=self.port, 
            user=user, 
            password=password, 
            db=database, 
            loop=self.loop, 
            autocommit=autocommit
        )

        if not await self.select("{}".format(self.bot.config["bot"]["prefix_table"]["table"]), "*"):
            await self.query("""
                CREATE TABLE IF NOT EXISTS `table_prefix` ( 
                    `guild_id` BIGINT unsigned NOT NULL, 
                    `guild_prefix` varchar(256), 
                    UNIQUE(`guild_id`) 
                );
            """)

    async def query(self, query: str) -> tuple:
        async with self.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                try:
                    await cursor.execute(query)
                    response = await cursor.fetchall()
                    return response

                except aiomysql.OperationalError as e:
                    if e.args[0] == 2013: #Lost connection to SQL server during query
                        await self.auth(self.__authUser, self.__authPassword, self.__authDatabase, self.__authAutocommit)
                        return await self.query(query)
                    return self.bot.log(message=f"{e}", name="DataSQL.query")
                
                except Exception as e:
                    return self.bot.log(message=f"{e}", name="DataSQL.query")
                """
                except pymysql.err.OperationalError as e:
                    if e.args[0] == 1044: #Access denied
                        return self.bot.log(message=f"{e}", name="DataSQL.query")
                """

    def __toKindFormat(self, value: Any) -> Any:
        keeper = value
        if isinstance(value, (str)): value = f"'{value}'"
        elif isinstance(value, date): value = f"'{value.strftime('%Y-%m-%d')}'"
        elif isinstance(value, datetime): value = f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'"

        if value != keeper: return value

    def __to_insert_variables_values(self, dictionnary: dict) -> tuple[str, str]:
        variables, values = '', ''
        for i, items in enumerate(dictionnary.items()):
            variable, value = items[0], items[1]
            
            variables += f"`{variable}`, " if i+1 < len(dictionnary) else f"`{variable}`"

            kindFormat = self.__toKindFormat(value)
            if kindFormat: value = kindFormat
            
            values += f"{value}, " if i+1 < len(dictionnary) else f"{value}"    

        return variables, values

    def __to_update_variables_values(self, dictionnary: dict) -> str:
        assignment = ''
        for i, items in enumerate(dictionnary.items()):
            variable, value = items[0], items[1]

            kindFormat = self.__toKindFormat(value)
            if kindFormat: value = kindFormat
            
            assignment += f"`{variable}`={value}, " if i+1 < len(dictionnary) else f"`{variable}`={value}"    

        return assignment

    def __query_insert(self, table: str, dictionnary: dict, close: bool = True) -> str:
        query = f"INSERT INTO `{table}` ("

        variables, values = self.__to_insert_variables_values(dictionnary)
        query += f"{variables} ) VALUES ({values})"	 

        if close: query += ';'
        return query
    
    def __query_update(self, table: str, dictionnary: dict, condition: Optional[str] = None, close: bool = True) -> str:
        query = f"UPDATE `{table}` SET "

        assignement = self.__to_update_variables_values(dictionnary)
        query += assignement

        if condition: query += f" WHERE {condition}"

        if close: query += ';'
        return query

    async def insert(self, table: str, dictionnary: dict): # return query()
        query = self.__query_insert(table, dictionnary)
        return await self.query(query)

    async def insert_onduplicate(self, table: str, insert_dict: dict, update_dict: Optional[dict] = None): # return query()
        if not update_dict: update_dict = insert_dict

        insert_query = self.__query_insert(table, insert_dict, close=False)
        assignment = self.__to_update_variables_values(update_dict)

        query = f"{insert_query} ON DUPLICATE KEY UPDATE {assignment};"

        return await self.query(query)

    async def update(self, table: str, dictionnary: dict, condition: Optional[str] = None): # return query()
        query = self.__query_update(table, dictionnary, condition)
        return await self.query(query)
    
    async def delete(self, table: str, condition: Optional[str] = None): # return query()
        query = f"DELETE FROM `{table}` WHERE {condition};"
        return await self.query(query + ';')

    async def increment(self, table: str, target: str, value: int = 1, condition: Optional[str] = None): # return update()
        await self.update(table, {target: MixedTypes(f"{target} + {value}")}, condition)

    async def dict_increment(self, table: str, dict_increment : dict, condition: Optional[str] = None):  # return update()
        final_dict = {}
        for key, value in dict_increment.items():
            final_dict[key] = MixedTypes(f"{key} + {value}")
        await self.update(table, final_dict, condition)

    async def select(self, table: str, target: str, condition: Optional[str] = None, order: Optional[str] = None, limit: Optional[str] = None): # return query()
        query = f"SELECT {target} FROM {table}"
        if condition: query += f" WHERE {condition}"
        if order: query += f" ORDER BY {order}"
        if limit: query += f" LIMIT {limit}"
        self.bot.log(f"{query + ';'}", name="func.select")
        return await self.query(query + ';')

    async def count(self, table: str, what: str, condition: Optional[str] = None): # return select()
        return await self.select(table, f"COUNT({what})", condition)

    async def lookup(self, table: str, target: str, dictionnary: dict): # return select()
        condition = ''
        for i, items in enumerate(dictionnary.items()):
            key, value = items
            condition += f"`{key}` = {self.__toKindFormat(value)} AND" if i+1 < len(dictionnary) else f"`{key}` = {self.__toKindFormat(value)}"

        return await self.select(table, target, condition)
    
    async def exist(self, table: str, target: str, condition: Optional[str] = None) -> bool:
        response = await self.count(table, target, condition)
        return response[0][0] > 0

    async def close(self) -> None:
        self.pool.close()
        await self.pool.wait_closed()