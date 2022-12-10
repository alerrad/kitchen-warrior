import re
import requests

class API_handler:
    URL = 'https://api.spoonacular.com/recipes/'

    def __init__(self, api_key: str, default_amount: int) -> None:
        self.amount = default_amount
        self.key = api_key

    def get_by_tag(self, tag: str) -> list:
        if tag == 'popular': tag = ''
        res = requests.get(self.URL + f'random?apiKey={self.key}&tags={tag}&number={self.amount}')
        return res.json()['recipes']

    def get_by_name(self, query: str) -> list:
        res = requests.get(self.URL + f'complexSearch?apiKey={self.key}&query={query}')
        return res.json()['results']

    def get_by_id(self, rcp_id: str) -> dict:
        res = requests.get(self.URL + f'{rcp_id}/information?apiKey={self.key}')
        return res.json()

    def get_random(self) -> dict:
        res = requests.get(self.URL + f'random?apiKey={self.key}&number=1')
        return res.json()['recipes'][0]

    @staticmethod
    def remove_tags(text: str) -> str:
        cleaner = re.compile(r'<.*?>')
        return cleaner.sub(' ', text)