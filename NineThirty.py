from bs4 import BeautifulSoup
from Venue import Venue

URL="https://www.930.com"
NAME="930"
COOLDOWN=10

class NineThirty(Venue):
    def __init__(self):
        super().__init__(url=URL, name=NAME, cooldown=COOLDOWN)

    def parse(self, soup):
        # Only taking the first index on skips the "Up Next" item
        # That is formatted differently and is repeated.
        upcoming_shows = soup.select(".list-view-item")[1:]
        for show in upcoming_shows:
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
            show_dict['doors'] = doors

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
