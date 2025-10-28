import requests
import time
from bs4 import BeautifulSoup
from Venue import Venue
from NineThirty import NineThirty
from Atlantis import Atlantis
from PearlStreet import PearlStreet
from UnionStage import UnionStage
from JamminJava import JamminJava
from TheHoward import TheHoward

def scrape(venues):
    for venue in venues:
        v = venue()
        v_soup = v.getHTML()
        v.parse(v_soup)
        v.print()

if __name__=="__main__":
    # TODO Add argument parsing to enable certain venues
    #  Ex. python3 scrape.py --930 --Atlantis
    venues = [TheHoward]
    scrape(venues)
