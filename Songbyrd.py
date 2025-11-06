from bs4 import BeautifulSoup
from Venue import Venue

URL="https://api.dice.fm/venue_profiles/slug/songbyrd-r58r"
NAME="Songbyrd"
COOLDOWN=10

class Songbyrd(Venue):
    def __init__(self):
        super().__init__(url=URL, name=NAME, cooldown=COOLDOWN, isAPI=True)

    def parse(self, soup):
        for show in soup:
            if 'sections' in soup:
                if 'items' in soup['sections']:
                    print(soup['sections']['items'])
            self.shows.append(self.parse_show(show))

    def parse_show(self, show):
        show_dict = {}
        dates = show.find('span', class_="dates")
        if dates is not None:
            date = dates.text.strip().split()
            show_dict['dayOfWeek'] = date[0]
            show_dict['day'] = date[1]
            show_dict['month'] = date[2]
        
        doors = show.find('span', class_="doors")
        if doors is not None:
            doors = doors.text.strip()
            if doors != "":
                ds = doors.split()
                show_dict['doors'] = ds[1] + ds[2]

        artist_info = show.find(class_="headliners")
        supports = show.find(class_="supports")
        if artist_info is not None:
            ai = artist_info.text.strip()
            show_dict['artist'] = ai
        if supports is not None:
            opener = supports.text.strip()
            show_dict['opener'] = opener

        ticket_price = show.find("section", class_="ticket-price")
        if ticket_price is not None:
            ticket_link = ticket_price.a['href']
            show_dict['link'] = ticket_link

        return show_dict

    def print(self):
        for show in self.shows:
            self.print_show(show)

    def print_show(self, show):
        date = ""
        try:
            date += show['dayOfWeek'] + " "
        except KeyError:
            pass
        try:
            date += show['day'] + " "
        except KeyError:
            pass
        try:
            date += show['month'] + " "
        except KeyError:
            pass
        if date != "":
            print("Date:", date)
        
        try:
            print("Doors:", show['doors'])
        except KeyError:
            print("Doors: N/A")
        try:
            print("Artist:", show['artist'])
        except KeyError:
            print("Artist: N/A")
        try:
            print("Opener:", show['opener'])
        except KeyError:
            print("Opener: N/A")
        try:
            print("Ticket link:", show['link'])
        except KeyError:
            print("SOLD OUT")
