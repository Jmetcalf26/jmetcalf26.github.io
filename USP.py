from bs4 import BeautifulSoup
from Venue import Venue

URL="https://www.unionstagepresents.com/"
NAME="USP"
COOLDOWN=10

class USP(Venue):
    def __init__(self, usp_ext="", usp_name=NAME):
        super().__init__(url=URL+usp_ext, name=usp_name, cooldown=COOLDOWN, isUSP=True)

    def parse(self, soup):
        # Overarching shows HTML: row row-cols-1 row-cols-md-2 row-cols-lg-3 row-cols-xl-3 g-4 tessera-card-deck
        # Individual shows: <div class="col">
        upcoming_shows = soup.select(".col")
        for show in upcoming_shows:
            if "text-center" not in show["class"]:
                s = self.parse_show(show)
                if "Private Event" not in s['artist']:
                    self.shows.append(s)

    def parse_show(self, show):
        show_dict = {}
        dates = show.find(class_="date")
        if dates is not None:
            date = dates.text.strip().split()
            show_dict['day'] = date[1]
            show_dict['month'] = date[0]
        
        doors = show.find(class_="tessera-showTimes")
        if doors is not None:
            doors = doors.text.strip()
            show_dict['doors'] = doors.split()[1]

        artist_info = show.find(class_="card-title")
        supports = show.find(class_="tessera-additionalArtists")
        if artist_info is not None:
            ai = artist_info.text.strip()
            show_dict['artist'] = ai
        if supports is not None:
            opener = supports.text.strip()
            show_dict['opener'] = opener

        sold_out = show.find("text", id="sold-out")
        if sold_out is None:
            ticket_price = show.find(class_="buy-now")
            if ticket_price is not None:
                if ticket_price.find("a") is not None:
                    ticket_link = ticket_price.a['href']
                    show_dict['link'] = ticket_link
                else:
                    show_dict['link'] = "N/A"

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
