import requests
import json
from bs4 import BeautifulSoup
from bs4.element import Comment

class GoogleSearchResults:
    def __init__(self, api_key_file, search_engine_id_file, search_query, num_results=5):
        self.API_KEY = open(api_key_file).read()
        self.SEARCH_ENGINE_ID = open(search_engine_id_file).read()
        self.search_query = search_query
        self.num = num_results
        self.url = 'https://customsearch.googleapis.com/customsearch/v1'
        self.urlArray = []
        self._get_search_results()

    def _get_search_results(self):
        params = {
            'q': self.search_query,
            'key': self.API_KEY,
            'cx': self.SEARCH_ENGINE_ID,
            'start': 0,
            'num': self.num
        }
        response = requests.get(self.url, params=params)
        data = response.json()
        temp = data['items']
        self.urlArray = [temp[i]['link'] for i in range(0, self.num)]

    @staticmethod
    def tag_visible(element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    @staticmethod
    def text_from_html(body):
        soup = BeautifulSoup(body, 'html.parser')
        texts = soup.findAll(text=True)
        visible_texts = filter(GoogleSearchResults.tag_visible, texts)
        return u" ".join(t.strip() for t in visible_texts)

class KeyWordFinder:
    def __init__(self, soup, search, rank):
        self.soup = soup
        self.rank = rank
        self.search = list(set(search.split()))
        count = 0
        search_list = list(self.soup.split())
        key_word_occurrences_temp = dict.fromkeys(self.search, 0)
        for x in search_list:
            if x in key_word_occurrences_temp:
                count += 1
                key_word_occurrences_temp[x] = key_word_occurrences_temp.get(x) + 1
        self.count = count
        self.key_word_occurrences = key_word_occurrences_temp

    def print_map_pretty(self):
        printstring = '\nWord Frequency List: \n'
        for x in self.search:
            printstring += '   ' + x + ":" + str(self.key_word_occurrences.get(x)) + '\n'
        return printstring

    def __str__(self):
        return '-------------------------------------------------------\n' + 'PageRank: ' + str(self.rank) + self.print_map_pretty()

class GoogleSearchManager:
    def __init__(self, api_key_file, search_engine_id_file, search_query, num_results=5):
        self.results = GoogleSearchResults(api_key_file, search_engine_id_file, search_query, num_results)
        self.keyword_finders = [KeyWordFinder(GoogleSearchResults.text_from_html(requests.get(url).content), search_query, idx+1) for idx, url in enumerate(self.results.urlArray)]

    def print_keyword_finder_results(self):
        for finder in self.keyword_finders:
            print(str(finder))

# Usage
search_manager = GoogleSearchManager('API_KEY', 'SEARCH_ENGINE_ID', 'how to make money')
search_manager.print_keyword_finder_results()




