from bs4 import BeautifulSoup
from Venue import Venue

URL = "https://www.theatlantis.com"
NAME = "atlantis"

class Atlantis(Venue):
    def __init__(self):
        super().__init__(url=URL, name=NAME)

    def parse(self, soup):
        upcoming_shows = soup.select(".event-list-item")
        for show in upcoming_shows:
            self.shows.append(self.parse_show(show))

    def parse_show(self, show):
        show_dict = {}
        dates = show.find('p', class_="item-date").find_all('span')
        if dates is not None:
            show_dict['dayOfWeek'] = dates[0].text.strip()
            dayMonthYear = dates[2].text.strip().split()
            show_dict['day'] = dayMonthYear[1][:-1]
            show_dict['month'] = dayMonthYear[0]
        
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

        ticket_price = show.find("a", class_="event-button-link")
        if ticket_price is not None:
            ticket_link = ticket_price['href']
            show_dict['link'] = ticket_link

        sold_out = show.find("div", class_="event-button--sold-out")
        if sold_out is not None:
            del show_dict['link']

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
