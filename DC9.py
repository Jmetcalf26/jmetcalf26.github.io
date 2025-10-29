from bs4 import BeautifulSoup
from Venue import Venue

URL="https://www.dc9.club/events/"
NAME="DC9"
COOLDOWN=10

class DC9(Venue):
    def __init__(self):
        super().__init__(url=URL, name=NAME, cooldown=COOLDOWN)

    def parse(self, soup):
        upcoming_shows = soup.select(".listings-block-list__listing")
        for show in upcoming_shows:
            print(show)
            self.shows.append(self.parse_show(show))

    def parse_show(self, show):
        show_dict = {}
        dates = show.find(class_="listingDateTime.listing-date-time.listingMeta.meta")
        if dates.span is not None:
            date = dates.span.text.strip().split()
            show_dict['dayOfWeek'] = date[0]
            show_dict['day'] = date[2]
            show_dict['month'] = date[1]
        
        doors = show.find(class_="listing-doors.listingMeta.meta")
        if doors is not None:
            doors = doors.text.strip()
            if doors != "":
                ds = doors.split()
                show_dict['doors'] = ds[1]

        artist_info = show.find(class_="listing__description")
        print(artist_info)
        #supports = show.find(class_="supports")
        if artist_info is not None:
            ai = artist_info.text.strip()
            show_dict['artist'] = ai
        #if supports is not None:
            #opener = supports.text.strip()
            #show_dict['opener'] = opener

        ticket_price = show.find(class_="listing__titleLink")
        if ticket_price is not None:
            ticket_link = ticket_price['href']
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
