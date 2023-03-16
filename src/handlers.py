import re
import requests

class API_handler:
    URL = 'https://api.spoonacular.com/recipes/'

    def __init__(self, api_key: str, default_amount: int) -> None:
        self.amount = default_amount
        self.key = api_key

    async def get_by_tag(self, tag: str) -> list[dict]:
        if tag == 'popular': tag = ''
        res = requests.get(API_handler.URL + f'random?apiKey={self.key}&tag={tag}&number={self.amount}')
        return res.json()['recipes']

    async def get_by_name(self, query: str) -> list[dict]:
        res = requests.get(API_handler.URL + f'complexSearch?apiKey={self.key}&query={query}')
        return res.json()['results']

    async def get_by_id(self, rcp_id: str) -> dict:
        res = requests.get(API_handler.URL + f'{rcp_id}/information?apiKey={self.key}')
        return res.json()

    async def get_random(self) -> dict:
        res = requests.get(API_handler.URL + f'random?apiKey={self.key}&number=1')
        return res.json()['recipes'][0]

    @staticmethod
    def remove_tags(text: str) -> str:
        cleaner = re.compile(r'<.*?>')
        return cleaner.sub(' ', text)