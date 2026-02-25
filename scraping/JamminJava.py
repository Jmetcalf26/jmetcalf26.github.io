from bs4 import BeautifulSoup
#from Venue import Venue
from USP import USP

URL_EXT="jammin-java/"
NAME="JamminJava"

class JamminJava(USP):
    def __init__(self):
        super().__init__(usp_ext=URL_EXT, usp_name=NAME)
