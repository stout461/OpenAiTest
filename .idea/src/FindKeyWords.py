

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

