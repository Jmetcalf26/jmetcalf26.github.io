from bs4 import BeautifulSoup
from Venue import Venue

class Atlantis(Venue):
    def __init__(self, url, name=""):
        super().__init__(url, name)

    def parse(self, soup):
        upcoming_shows = soup.select(".event-list-item")
        for show in upcoming_shows:
            self.shows.append(self.parse_show(show))

    def parse_show(self, show):
        show_dict = {}
        # TODO: Update this parsing to see if every single show has the same
        # 3-span structure and the middle one is just a dot that can be skipped
        dates = show.find('p', class_="item-date")
        if dates is not None:
            show_dict['dayOfWeek'] = dates.text.strip()
        
        doors = show.find('p', class_="item-time")
        if doors is not None:
            doors = doors.text.strip()
            show_dict['doors'] = doors

        artist_info = show.find('h3', class_="item-title")
        supports = show.find('h4', class_="item-supporting")
        if artist_info is not None:
            ai = artist_info.text.strip()
            show_dict['artist'] = ai
        if supports is not None:
            opener = supports.text.strip()
            show_dict['opener'] = opener

        # TODO: Update this section to use different 'div' in order to differentiate
        # between still in stock vs sold out
        ticket_price = show.find("section", class_="ticket-price")
        if ticket_price is not None:
            ticket_link = ticket_price.a['href']
            show_dict['link'] = ticket_link

        return show_dict

    def print(self):
        for show in self.shows:
            self.print_show(show)

    # TODO: Determine if there are any differences here
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
