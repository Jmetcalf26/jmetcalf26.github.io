import requests
from bs4 import BeautifulSoup

class Venue:
    def __init__(self, url, name=""):
        self.url = url
        self.name = name
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
        }
        self.shows = []
    def getHTML(self):
        r = requests.get(self.url, headers=self.headers)

        with open('pages/'+self.name+'.html', 'wb') as of:
            of.write(r.content)

        return BeautifulSoup(r.content, 'html.parser')
        
    def parse(self, soup):
        pass
    
    def print(self):
        pass
