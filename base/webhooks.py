import requests
import json
from base.struct import Config
from requests.exceptions import HTTPError


class addCard():
    
    def __init__(self) -> None:
        
        with open('config.json', 'r') as f:
            self.cfg = Config(json.loads(f.read()))

    def get_response(novelId: str, desc: str, trelloList, trelloKey, trelloToken):
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


        # Python pretty print JSON
        #json_formatted_str = json.dumps(response.json(), indent=4, ensure_ascii=False)
        # return json_formatted_str

# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
#data = '{\n  "key": "{APIKey}",\n  "callbackURL": "http://www.mywebsite.com/trelloCallback",\n  "idModel":"4d5ea62fd76aa1136000000c",\n  "description": "My first webhook"\n}'
#response = requests.post('https://api.trello.com/1/tokens/{APIToken}/webhooks/', headers=headers, data=data)
