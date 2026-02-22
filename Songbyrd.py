from bs4 import BeautifulSoup
from Venue import Venue
from datetime import datetime
import requests
import json

URL="https://songbyrddc.com/events/"
NAME="Songbyrd"
COOLDOWN=10

class Songbyrd(Venue):
    def __init__(self):
        super().__init__(url=URL, name=NAME, cooldown=COOLDOWN, isAPI=False)

    def parse(self, soup):
        # The events are contained in divs with classes like "wpem-event-box-col"
        event_divs = soup.find_all('div', class_='wpem-event-box-col')
        for event in event_divs:
            show_dict = {}
            
            # Artist / Title
            title_div = event.find('div', class_='wpem-event-title')
            if title_div and title_div.h3:
                show_dict['artist'] = title_div.h3.get_text(strip=True)
            else:
                # Fallback: try finding any heading or prominent text in the wrapper
                continue

            # Supporting Acts (Openers)
            openers_div = event.find('div', class_='wpem-event-supporting-acts')
            if openers_div and openers_div.p:
                openers_text = openers_div.p.get_text(strip=True)
                if ":" in openers_text:
                    openers_text = openers_text.split(":", 1)[1].strip()
                if openers_text:
                    show_dict['opener'] = openers_text

            # Date
            date_div = event.find('div', class_='wpem-from-date')
            if date_div:
                dotw = date_div.find('div', class_='wpem-dotw')
                day = date_div.find('div', class_='wpem-date')
                month = date_div.find('div', class_='wpem-month')
                
                if dotw: show_dict['dayOfWeek'] = dotw.get_text(strip=True)
                if day: show_dict['day'] = day.get_text(strip=True)
                if month: show_dict['month'] = month.get_text(strip=True)

            # Doors
            door_div = event.find('div', class_='wpem-event-door-time')
            if door_div and door_div.p:
                door_text = door_div.p.get_text(strip=True)
                if ":" in door_text:
                    door_text = door_text.split(":", 1)[1].strip()
                if door_text:
                    show_dict['doors'] = door_text

            # Ticket Link
            action_links = event.find_all('a', class_='wpem-event-action-url')
            link = None
            for alink in action_links:
                if 'href' in alink.attrs:
                    href = alink['href']
                    # Prioritize dice.fm links
                    if 'dice.fm' in href:
                        link = href
                        break
                    # If we don't have a link yet, take the first one (usually songbyrddc.com/event/...)
                    if not link:
                        link = href
            
            if link:
                show_dict['link'] = link

            self.shows.append(show_dict)

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
