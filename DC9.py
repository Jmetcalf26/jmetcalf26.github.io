from Venue import Venue

URL="https://dc9.club/api/plot/v1/listings?currentpage=1&notLoaded=false&listingsPerPage=100&_locale=user"
NAME="DC9"
COOLDOWN=10

class DC9(Venue):
    def __init__(self):
        super().__init__(url=URL, name=NAME, cooldown=COOLDOWN, isAPI=True)

    def parse(self, soup):
        for show in soup:
            self.shows.append(self.parse_show(show))

    def parse_show(self, show):
        show_dict = {}
        dates = show['dateTime']
        if dates is not None:
            date = dates.strip().split()
            show_dict['dayOfWeek'] = date[0]
            show_dict['day'] = date[2]
            show_dict['month'] = date[1]
        
        doors = show['doors']
        if doors is not None:
            doors = doors.strip()
            if doors != "":
                ds = doors.split()
                show_dict['doors'] = ds[1]

        artist_info = ""
        supports = []
        if 'lineup' in show:
            lineup = show['lineup']
            if 'headliners' in lineup:
                headliners = lineup['headliners']
                if 'title' in headliners[0]:
                    artist_info = headliners[0]['title']
                else:
                    artist_info = headliners[0]['post_title']
            if 'standard' in lineup:
                standard = lineup['standard']
                if artist_info == "":
                    if 'title' in standard[0]:
                        artist_info = standard[0]['title']
                    else:
                        artist_info = standard[0]['post_title']
                if len(standard) > 1:
                    for act in standard[1:]:
                        if 'title' in act:
                            supports.append(act['title'])
                        else:
                            supports.append(act['post_title'])
        else:
            artist_info = show['title']



        print(artist_info)
        print(supports)

        if artist_info is not None:
            show_dict['artist'] = artist_info
        if supports is not None:
            opener = supports
            show_dict['opener'] = opener

        if 'permalink' in show:
            show_dict['link'] = show['permalink']
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
