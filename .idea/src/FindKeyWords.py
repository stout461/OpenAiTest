

class KeyWordFinder:
    def __init__(self, soup, search):
        self.soup = soup
        self.search = list(set(search.split()))
        searchList = list(self.soup.split())
        keyWordOccurencesTemp = dict.fromkeys(self.search,0)
        for x in searchList:
            if x in keyWordOccurencesTemp:
                keyWordOccurencesTemp[x] = keyWordOccurencesTemp.get(x) +1
        self.keyWordOccurences = keyWordOccurencesTemp

