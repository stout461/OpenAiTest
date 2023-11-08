import requests
import json
from bs4 import BeautifulSoup
from bs4.element import Comment
from tabulate import tabulate
import aiohttp
import asyncio

stop_words_set = set({"a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as",
                      "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot",
                      "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each",
                      "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd",
                      "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
                      "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me",
                      "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
                      "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's",
                      "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
                      "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
                      "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're",
                      "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who",
                      "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're",
                      "you've", "your", "yours", "yourself", "yourselves"})

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
        if element.name in ['div', 'span']:
            return True  # Include div and span tags that might contain relevant content
        return True  # Include other elements by default

    @staticmethod
    def text_from_html(body):
        soup = BeautifulSoup(body, 'lxml')  # Change parser method to 'lxml' or 'html5lib'
        texts = soup.find_all(text=True)
        visible_texts = filter(GoogleSearchResults.tag_visible, texts)
        return " ".join(t.strip() for t in visible_texts)

class KeyWordFinder:
    def __init__(self, soup, rank, search_query):
        self.soup = soup.lower()  # Convert content to lowercase
        self.rank = rank
        self.search = list(set(search_query.lower().split()))  # Convert search query to lowercase set
        self.count = 0
        self.key_word_occurrences = {}
        self.stop_words = stop_words_set  # Assuming 'stop_words' as defined

        search_list = self.soup.split()
        key_word_occurrences_temp = {}
        for word in search_list:
            if word in self.search and word not in self.stop_words:
                self.count += 1
                key_word_occurrences_temp[word] = key_word_occurrences_temp.get(word, 0) + 1
        self.key_word_occurrences = key_word_occurrences_temp


    def print_map_pretty(self):
        printstring = '\nWord Frequency List: \n'
        for word, count in self.key_word_occurrences.items():
            printstring += f'   {word}:{count}\n'
        return printstring

    def __str__(self):
        return '-------------------------------------------------------\n' + 'PageRank: ' + str(self.rank) + self.print_map_pretty()

class GoogleSearchManager:
    async def get_keyword_finders(self, session, results):
        keyword_finders = []
        tasks = []
        for idx, url in enumerate(results.urlArray):
            task = asyncio.ensure_future(self.get_word_count(session, url, idx + 1, results.search_query))
            tasks.append(task)
        keyword_finders = await asyncio.gather(*tasks)
        return keyword_finders

    async def get_word_count(self, session, url, rank, search_query):
        async with session.get(url) as response:
            body = await response.text()
            soup = BeautifulSoup(body, 'html.parser')
            visible_texts = filter(self.tag_visible, soup.find_all(text=True))
            visible_text = " ".join(t.strip() for t in visible_texts)
            return KeyWordFinder(visible_text, rank, search_query)

    @staticmethod
    def tag_visible(element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    async def run(self, api_key_file, search_engine_id_file, search_query, num_results=5):
        async with aiohttp.ClientSession() as session:
            results = GoogleSearchResults(api_key_file, search_engine_id_file, search_query, num_results)
            keyword_finders = await self.get_keyword_finders(session, results)
            for finder in keyword_finders:
                print(str(finder))

class MultipleSearchQueriesManager:
    async def get_search_results(self, session, api_key_file, search_engine_id_file, query, num_results=5):
        results = GoogleSearchResults(api_key_file, search_engine_id_file, query, num_results)
        search_manager = GoogleSearchManager()
        return await search_manager.get_keyword_finders(session, results)

    async def run_queries(self, api_key_file, search_engine_id_file, search_queries, num_results=5):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for query in search_queries:
                task = asyncio.ensure_future(self.get_search_results(session, api_key_file, search_engine_id_file, query, num_results))
                tasks.append(task)
            results = await asyncio.gather(*tasks)
            for query, keyword_finders in zip(search_queries, results):
                print(f"Results for search query: '{query}'")
                for finder in keyword_finders:
                    print(str(finder))
                print("\n")

search_queries = [
    'how to make money',
    'Get rich now'
    # Add more search queries as needed
]
async def main():
    manager = MultipleSearchQueriesManager()
    await manager.run_queries('API_KEY', 'SEARCH_ENGINE_ID', search_queries)

asyncio.run(main())