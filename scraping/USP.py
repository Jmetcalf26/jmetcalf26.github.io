from bs4 import BeautifulSoup
from Venue import Venue

URL="https://www.unionstagepresents.com/"
NAME="USP"
COOLDOWN=10

class USP(Venue):
    def __init__(self, usp_ext="", usp_name=NAME):
        super().__init__(url=URL+usp_ext, name=usp_name, cooldown=COOLDOWN, isUSP=True)

    def parse(self, soup):
        # The USP site redesigned in early 2026. Shows are now <a class="show-card-link"> elements.
        # Each show appears twice in the DOM (desktop + mobile card variants);
        # only cards with a real /shows/... href are the primary entries.
        upcoming_shows = soup.select(".show-card-link")
        for show in upcoming_shows:
            href = show.get('href', '')
            if not href.startswith('/shows/'):
                continue
            s = self.parse_show(show)
            if "Private Event" not in s.get('artist', ''):
                self.shows.append(s)

    def parse_show(self, show):
        show_dict = {}

        # --- Date ---
        day_of_week = show.select_one('.event-day-day')
        month       = show.select_one('.event-month')
        day         = show.select_one('.event-day')
        if day_of_week:
            show_dict['dayOfWeek'] = day_of_week.text.strip()
        if month:
            show_dict['month'] = month.text.strip()
        if day:
            show_dict['day'] = day.text.strip()

        # --- Artist ---
        artist_el = show.select_one('.show-card-header')
        if artist_el:
            show_dict['artist'] = artist_el.text.strip()

        # --- Doors time ---
        # The info footer has two .show-info blocks: venue/age-rating and the doors/show times.
        # Find the block containing "DOORS" and extract the first time value.
        for info_block in show.select('.show-info'):
            if 'DOORS' in info_block.get_text():
                for el in info_block.select('.base-text-size-caps'):
                    # Time values have exactly one class; labels/separators have extra classes.
                    if el.get('class') == ['base-text-size-caps']:
                        t = el.text.strip()
                        if t:
                            show_dict['doors'] = t
                            break
                break

        # --- Ticket link ---
        # Tickets button has class w-condition-invisible when not available (sold out / private).
        tickets_available = True
        for btn in show.select('.text-block-60'):
            if btn.text.strip() == 'Tickets' and 'w-condition-invisible' in btn.get('class', []):
                tickets_available = False
                break

        if tickets_available:
            show_dict['link'] = 'https://www.unionstagepresents.com' + show.get('href', '')

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
