import requests
import json
from bs4 import BeautifulSoup
from bs4.element import Comment
from tabulate import tabulate

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
        return True

    @staticmethod
    def text_from_html(body):
        soup = BeautifulSoup(body, 'html.parser')
        texts = soup.findAll(text=True)
        visible_texts = filter(GoogleSearchResults.tag_visible, texts)
        return u" ".join(t.strip() for t in visible_texts)

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
    def __init__(self, results, num_results=5):
        self.results = results
        self.keyword_finders = [KeyWordFinder(GoogleSearchResults.text_from_html(requests.get(url).content), idx+1, self.results.search_query) for idx, url in enumerate(self.results.urlArray)]

    def print_keyword_finder_results(self):
        for finder in self.keyword_finders:
            print(str(finder))

class MultipleSearchQueriesManager:
    def __init__(self, api_key_file, search_engine_id_file, search_queries, num_results=5):
        self.search_results = {}
        for query in search_queries:
            results = GoogleSearchResults(api_key_file, search_engine_id_file, query, num_results)
            search_manager = GoogleSearchManager(results, num_results)
            self.search_results[query] = search_manager.keyword_finders

    def print_keyword_finder_results(self):
        for query, keyword_finders in self.search_results.items():
            print(f"Results for search query: '{query}'")
            for finder in keyword_finders:
                print(str(finder))
            print("\n")

    def print_keyword_finder_results(self):
        for query, keyword_finders in self.search_results.items():
            print(f"Results for search query: '{query}'")
            headers = ["Word", "Count"]
            for finder in keyword_finders:
                data = [(word, count) for word, count in finder.key_word_occurrences.items()]
                print(tabulate(data, headers=headers, tablefmt="pretty"))
            print("\n")


# Example list of search queries
search_queries = [
    'how to make money',
    'Get rich now'
    # Add more search queries as needed
]

# Create a MultipleSearchQueriesManager instance
multiple_search_queries_manager = MultipleSearchQueriesManager('API_KEY', 'SEARCH_ENGINE_ID', search_queries)

# Print the keyword finder results for each search query
multiple_search_queries_manager.print_keyword_finder_results()