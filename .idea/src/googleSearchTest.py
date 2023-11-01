import requests
import json

API_KEY = open('API_KEY').read()
SEARCH_ENGINE_ID = open('SEARCH_ENGINE_ID').read()

print(API_KEY)

search_query = 'How to learn to code'

url = 'https://customsearch.googleapis.com/customsearch/v1'

params = {
    'q': search_query,
    'key': API_KEY,
    'cx': SEARCH_ENGINE_ID,
    'start': 0,
    'num': 5
}

response = requests.get(url,params=params)
formatting_results = response.text

print(formatting_results)

