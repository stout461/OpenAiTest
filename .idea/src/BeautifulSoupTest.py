import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from FindKeyWords import KeyWordFinder
## Test to grab all the HTML from a specific URL. https://pypi.org/project/beautifulsoup4/
## Note for aarush- the google search library you were already using was just searching a term in google then using this library to parse the search result page.

URL = "https://blog.hubspot.com/website/how-to-start-coding"
r = requests.get(URL)

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

search = 'How to learn to code'
soup = text_from_html(r.content)

SearchList = KeyWordFinder(soup,search)
print(SearchList.search)
print(SearchList.soup)
print(SearchList.keyWordOccurences)





