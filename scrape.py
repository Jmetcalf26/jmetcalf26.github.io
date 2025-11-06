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
from MiracleTheatre import MiracleTheatre
from CapitalTurnaround import CapitalTurnaround
from NatsPark import NatsPark
from PieShop import PieShop
from DC9 import DC9
from Songbyrd import Songbyrd

def scrape(venues):
    for venue in venues:
        v = venue()
        v_soup = v.getData()
        v.parse(v_soup)
        v.print()

if __name__=="__main__":
    # TODO Add argument parsing to enable certain venues
    #  Ex. python3 scrape.py --930 --Atlantis
    venues = [Songbyrd]
    scrape(venues)
