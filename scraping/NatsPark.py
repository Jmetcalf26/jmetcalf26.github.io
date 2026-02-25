from bs4 import BeautifulSoup
#from Venue import Venue
from USP import USP

URL_EXT="nats-park/"
NAME="NatsPark"

class NatsPark(USP):
    def __init__(self):
        super().__init__(usp_ext=URL_EXT, usp_name=NAME)
