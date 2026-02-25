from bs4 import BeautifulSoup
from Venue import Venue

URL="https://www.pieshopdc.com/shows/"
NAME="PieShop"
COOLDOWN=10

class PieShop(Venue):
    def __init__(self):
        super().__init__(url=URL, name=NAME, cooldown=COOLDOWN)

    def parse(self, soup):
        upcoming_shows = soup.select(".uui-layout88_item.w-dyn-item")
        for show in upcoming_shows:
            self.shows.append(self.parse_show(show))

    def parse_show(self, show):
        show_dict = {}

        day = show.find(class_="event-day")
        month = show.find(class_="event-month")
        if day is not None:
            show_dict['day'] = day.text.strip()
        if month is not None:
            show_dict['month'] = month.text.strip()
        
        doors = show.find(class_="event-time-new")
        if doors is not None:
            doors = doors.text.strip()
            if doors != "":
                ds = doors.split()
                show_dict['doors'] = ds[0] + ds[1]

        artist_info = show.find(class_="uui-heading-xxsmall-2")
        if artist_info is not None:
            ai_stripped = artist_info.text.strip()
            if "w/" in ai_stripped:
                ai_split = ai_stripped.split("w/")
                show_dict['artist'] = ai_split[0]

                supports = ai_split[1]
                if supports is not None:
                    show_dict['opener'] = supports
            else:
                show_dict['artist'] = ai_stripped

        ticket_price = show.a
        if ticket_price is not None:
            ticket_link = ticket_price['href']
            show_dict['link'] = URL + ticket_link.split("/")[-1]

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
