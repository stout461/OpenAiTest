import requests
import json
from bs4 import BeautifulSoup
from bs4.element import Comment

API_KEY = open('API_KEY').read()
SEARCH_ENGINE_ID = open('SEARCH_ENGINE_ID').read()
search_query = 'how to make money'
url = 'https://customsearch.googleapis.com/customsearch/v1'
num = 5
params = {
    'q': search_query,
    'key': API_KEY,
    'cx': SEARCH_ENGINE_ID,
    'start': 0,
    'num': num
}
response = requests.get(url,params=params)
data = response.json() # create a json object from the response
temp = data['items']
urlArray = [temp[i]['link'] for i in range(0,num)] #get the list of URL returned.
## Functions to clean up webpage text so that we can read it. (aka returns only the words, and no tags)
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True
def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)

class KeyWordFinder:
    def __init__(self, soup, search, rank):
        self.soup = soup
        self.rank = rank
        self.search = list(set(search.split()))
        count = 0
        searchList = list(self.soup.split())
        keyWordOccurencesTemp = dict.fromkeys(self.search,0)
        for x in searchList:
            if x in keyWordOccurencesTemp:
                count +=1
                keyWordOccurencesTemp[x] = keyWordOccurencesTemp.get(x) +1
        self.count = count
        self.keyWordOccurences = keyWordOccurencesTemp

    def printMapPretty(self):
        printstring = '\nWord Frequency List: \n'
        for x in self.search:
            printstring += '   ' + x + ":" + str(self.keyWordOccurences.get(x)) + '\n'
        return printstring
    def __str__(self):
        return   '-------------------------------------------------------\n' + 'PageRank: ' + str(self.rank) + self.printMapPretty()#'\n Word Frequency List: \n' + str(self.keyWordOccurences.items())




#def keyWordFinder(soup,search):
#    search = list(set(search.split()))
#    searchList = list(soup.split())
#    keyWordOccurences = dict.fromkeys(search,0)
#    count = 0
#    for x in searchList:
#        count += 1
#        if x in keyWordOccurences:
#            keyWordOccurences[x] = keyWordOccurences.get(x) +1
#    print(count)
#    return keyWordOccurences

count = 1;
for x in urlArray:
    #print('-------------------------------------')
    #print("PageRank: " + str(count))
    print(str(KeyWordFinder(text_from_html(requests.get(x).content),search_query,count)))
    count+=1

print(urlArray)




