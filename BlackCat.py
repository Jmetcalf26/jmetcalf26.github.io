from bs4 import BeautifulSoup
from Venue import Venue
import re

URL="https://www.blackcatdc.com/schedule.html"
NAME="BlackCat"
COOLDOWN=10

class BlackCat(Venue):
    def __init__(self):
        super().__init__(url=URL, name=NAME, cooldown=COOLDOWN, isAPI=False)

    def parse(self, soup):
        show_divs = soup.find_all('div', class_='show')
        for show_div in show_divs:
            show_dict = {}
            
            details = show_div.find('div', class_='show-details')
            if not details:
                continue

            # Date: e.g. "Saturday February 21"
            date_h2 = details.find('h2', class_='date')
            if date_h2:
                date_text = date_h2.get_text(strip=True)
                # Split "Saturday February 21" -> ["Saturday", "February", "21"]
                parts = date_text.split()
                if len(parts) >= 3:
                    show_dict['dayOfWeek'] = parts[0][:3] # "Sat"
                    show_dict['month'] = parts[1][:3]     # "Feb"
                    show_dict['day'] = parts[2]           # "21"

            # Headline (Artist)
            headline_h1 = details.find('h1', class_='headline')
            if headline_h1:
                # Some headlines contain <br> or multiple lines, join them cleanly
                artist_name = " ".join(headline_h1.get_text(separator=' ', strip=True).split())
                show_dict['artist'] = artist_name

            # Support (Opener)
            support_h2s = details.find_all('h2', class_='support')
            if support_h2s:
                openers = []
                for s in support_h2s:
                    # Clean up the text, removing extra whitespace and separators
                    text = s.get_text(separator=' ', strip=True)
                    text = " ".join(text.split())
                    if text and not text.startswith('(') and not text.endswith(':'):
                         openers.append(text)
                if openers:
                    show_dict['opener'] = ", ".join(openers)

            # Show Text (Doors / Venue info)
            show_text_p = details.find('p', class_='show-text')
            if show_text_p:
                text = show_text_p.get_text(strip=True)
                # e.g. "Doors at 9:00" or "Red Room / Doors at 8:00"
                match = re.search(r'Doors at (\d+:\d+)', text)
                if match:
                    show_dict['doors'] = match.group(1)
                
            # Ticket Link
            ticket_a = details.find('a', href=re.compile(r'etix\.com'))
            if ticket_a:
                show_dict['link'] = ticket_a['href']
            
            if show_dict.get('artist'):
                self.shows.append(show_dict)
