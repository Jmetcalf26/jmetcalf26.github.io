from bs4 import BeautifulSoup
from Venue import Venue
from datetime import datetime
import requests
import json

URL="https://api.dice.fm/venue_profiles/slug/songbyrd-r58r"
NAME="Songbyrd"
COOLDOWN=10

class Songbyrd(Venue):
    def __init__(self):
        super().__init__(url=URL, name=NAME, cooldown=COOLDOWN, isAPI=True)

    def parse(self, soup):
        if 'sections' in soup:
            if 'items' in soup['sections'][0]:
                for show in soup['sections'][0]['items']:
                    self.shows.append(self.parse_show(show))

    def parse_show(self, show):
        if show['type'] == "event":
            show = show['event']
        show_dict = {}
        print(show)
        dates = show['dates']
        d = None
        if dates is not None:


            da = dates['event_start_date']
            da = da[:da.rfind("-")]
            d = datetime.fromisoformat(da)
            
            show_dict['dayOfWeek'] = d.strftime("%A")[:3]
            show_dict['day'] = d.strftime("%d")
            show_dict['month'] = d.strftime("%m")
        
            show_dict['doors'] = d.strftime("%I%p")

        id = show['id']

        lineup_page = requests.get("https://api.dice.fm/events/" + id + "/lineup", headers=self.headers)
        if lineup_page.text is not None:
            lineup_page = json.loads(lineup_page.text)

        artist_info = lineup_page['lineup'][-1]
        print(artist_info)
        supports = lineup_page['lineup'][:-1] if len(lineup_page['lineup']) > 1 else None
        print(supports)
        if 'title' in artist_info:
            show_dict['artist'] = artist_info['title']
        else:
            show_dict['artist'] = artist_info['name']
        for supporter in supports:
            if 'title' in supporter:
                show_dict['opener'] = supporter['title']
            else:
                show_dict['opener'] = supporter['name']

        if 'status' in show and show['status'] != "sold-out":
            if 'price' in show:
                ticket_link = show['price']
                show_dict['link'] = ticket_link['amount']

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
