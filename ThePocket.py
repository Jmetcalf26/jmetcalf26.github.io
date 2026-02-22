from bs4 import BeautifulSoup
from Venue import Venue

URL="https://thepocket.7drumcity.com/shows"
NAME="ThePocket"
COOLDOWN=10

class ThePocket(Venue):
    def __init__(self):
        super().__init__(url=URL, name=NAME, cooldown=COOLDOWN, isAPI=False)

    def parse(self, soup):
        # Shows are in divs with class 'uui-layout88_item-2'
        items = soup.find_all('div', class_='uui-layout88_item-2')
        for item in items:
            show_dict = {}
            
            # Artist - find h3 tags that are NOT invisible
            # Webflow often uses 'w-condition-invisible' to hide fields
            titles = item.find_all('h3', class_='uui-heading-xxsmall-4')
            artist = ""
            for t in titles:
                if 'w-condition-invisible' not in t.get('class', []):
                    artist = t.get_text(strip=True)
                    break
            
            if not artist:
                continue
            
            show_dict['artist'] = artist

            # Date
            month = item.find('div', class_='event-month-2')
            day = item.find('div', class_='event-day-2')
            if month: show_dict['month'] = month.get_text(strip=True)
            if day: show_dict['day'] = day.get_text(strip=True)

            # Time (Show time usually, but we use it for doors if that's all we have)
            time_div = item.find('div', class_='event-time-new-2')
            if time_div:
                show_dict['doors'] = time_div.get_text(strip=True)

            # Opener
            supports = item.find('h4', class_='supports-line')
            if supports and 'w-condition-invisible' not in supports.get('class', []):
                opener = supports.get_text(strip=True)
                if opener:
                    show_dict['opener'] = opener

            # Link
            link_a = item.find('a', class_='link-block-2')
            if link_a and 'href' in link_a.attrs:
                href = link_a['href']
                if href.startswith('/'):
                    show_dict['link'] = "https://thepocket.7drumcity.com" + href
                else:
                    show_dict['link'] = href

            self.shows.append(show_dict)
