import requests
from bs4 import BeautifulSoup
from NineThirty import NineThirty

def scrape():
    nt = NineThirty(url='https://www.930.com/#upcoming-shows-title', name="930")
    print(nt.name)
    print(nt.url)
    nt_soup = nt.getHTML()
    nt.parse(nt_soup)

#if __name__=="__main__":
scrape()
