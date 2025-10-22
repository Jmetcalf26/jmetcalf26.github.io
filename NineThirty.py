from bs4 import BeautifulSoup
from Venue import Venue

#url = 'https://www.930.com'

class NineThirty(Venue):
    def __init__(self, url, name=""):
        super().__init__(url, name)

    def parse(self, soup):
        upcoming_shows = soup.select(".list-view-item")

        for a in upcoming_shows:
            show = {}
            dates = a.find('span', class_="dates")
            if dates is not None:
                date = dates.text.strip().split()
                print("Date:", date)
                show['dayOfWeek'] = date[0]
                show['day'] = date[1]
                show['month'] = date[2]
            
            doors = a.find('span', class_="doors")
            if doors is not None:
                doors = doors.text.strip()
                print("Doors:", doors)
                show['doors'] = doors
            artist_info = a.find(class_="headliners")
            supports = a.find(class_="supports")
            if artist_info is not None:
                ai = artist_info.text.strip()
                print("Artist:", ai)
                show['artist'] = ai
            if supports is not None:
                opener = supports.text.strip()
                print("Opener:", opener)
                show['opener'] = opener
            ticket_price = a.find("section", class_="ticket-price")
            sold_out = a.find(class_="sold-out")
            if sold_out is not None:
                print("SOLD OUT:", sold_out)
            elif ticket_price is not None:
                ticket_link = ticket_price.a['href']
                print("Ticket link:", ticket_link)
                show['link'] = ticket_link
            self.shows.append(show)
