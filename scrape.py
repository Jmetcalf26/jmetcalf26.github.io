import requests
from bs4 import BeautifulSoup
from NineThirty import NineThirty

# TODO: Add Atlantis parsing once it is ready
def scrape():
    nt = NineThirty(url='https://www.930.com', name="930")
    nt_soup = nt.getHTML()
    nt.parse(nt_soup)
    nt.print()

if __name__=="__main__":
    scrape()
