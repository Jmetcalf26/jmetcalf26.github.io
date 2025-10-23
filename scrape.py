import requests
import time
from bs4 import BeautifulSoup
from Venue import Venue
from NineThirty import NineThirty
from Atlantis import Atlantis

# TODO: Add Atlantis parsing once it is ready
def scrape(venues):
    for venue in venues:
        v = venue()
        v_soup = v.getHTML()
        v.parse(v_soup)
        v.print()
        time.sleep(10)

if __name__=="__main__":
    # TODO Add argument parsing to enable certain venues
    #  Ex. python3 scrape.py --930 --Atlantis
    venues = [NineThirty, Atlantis]
    scrape(venues)
