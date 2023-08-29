import requests
import json
from requests.exceptions import HTTPError



class TrelloFunctions():
    
    def __init__(self, bot) -> None:
        self.bot = bot
        self.cfg = self.bot.config

    def add_card(novelId: str, desc: str, trelloList, trelloKey, trelloToken):
        novelId = '#ID ' + str(''.join(novelId.split('#')))

        # PEGA LISTAS
        # response = requests.request(
        #    'GET',
        #    f'https://api.trello.com/1/boards/638f5911ab7045001d5e4159/lists', params=query) # 638f64a6fd438c0154fd7c6f < ID DA LISTA

        # PEGA OS CARDS
        # response = requests.request(
        #    'GET',
        #    f'https://api.trello.com/1/boards/638f5911ab7045001d5e4159/cards', params=query)

        # response = requests.post(
        #     f'https://api.trello.com/1/tokens/{apiToken}/webhooks/', headers=headers, json=json_data)

        # Convert JSON to Python object
        # obj = json.loads()

        query = {
            'name': novelId,
            'desc': desc,
            'idList': trelloList,
            'key': trelloKey,
            'token': trelloToken
        }

        with requests.Session() as s:
            response = s.request(
                'POST',
                f'https://api.trello.com/1/cards', params=query)

            if response.ok:
                res = "%s Card criado." % (
                    novelId)

        return res

    async def get_last_card(self):

        query = {
            'key': self.cfg["other"]["trelloKey"],
            'token': self.cfg["other"]["trelloToken"]
        }
        headers = {'Content-Type': 'application/json'}

        with requests.Session() as s:
            response = s.request(
                'GET',
                'https://api.trello.com/1/lists/' \
                f'{self.cfg["other"]["trelloList"]}/cards?fields=name,labels,shortUrl,desc', 
                params=query,
                headers=headers)

            if response.ok:
                self.bot.log(message="Cards requisitados", name="function.Trello")

        items = []
        item_ = json.loads(response.text)

        for item in item_:

            # Pule a tag de embelezamento

            if item["name"] == "HISTÓRIAS ACEITAS": continue
            
            '''
                Se:
                - Não tiver capa
                - Não estiver curada
                - Não tiver acesso ao link do capítulo
                pule.
            '''

            colors = []
            for i in item["labels"]:
                colors.append(i["color"])
            

            if "yellow" in colors: continue
            if "red_dark" in colors: continue
            if "orange_dark" in colors: continue

            this_item = {}

            this_item["title"] = str(item["name"])

            desc = ' \n'.join([x for x in str(item["desc"]).split("\n") if x != ''])
            #print(desc,flush=True)
            desc = (desc[:4096] + '..') if len(desc) > 4096 else desc
            this_item["description"] = desc
            this_item["url"] = item["shortUrl"]

            this_item = json.dumps(this_item, indent=2)

            items.append(this_item)

        #print(items, flush=True)
        #items = json.dumps(items, indent=2)
        return items


        # Python pretty print JSON
        #json_formatted_str = json.dumps(response.json(), indent=4, ensure_ascii=False)
        # return json_formatted_str

# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
#data = '{\n  "key": "{APIKey}",\n  "callbackURL": "http://www.mywebsite.com/trelloCallback",\n  "idModel":"4d5ea62fd76aa1136000000c",\n  "description": "My first webhook"\n}'
#response = requests.post('https://api.trello.com/1/tokens/{APIToken}/webhooks/', headers=headers, data=data)

#trello = TrelloFunctions()