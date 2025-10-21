import requests
from bs4 import BeautifulSoup

url = 'https://www.930.com/#upcoming-shows-title'

class NineThirty(Venue):
    

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
}
r = requests.get(url, headers=headers)
with open('pages/930.html', 'wb') as of:
    of.write(r.content)

soup = BeautifulSoup(r.content, 'html.parser')

upcoming_shows = soup.select(".list-view-item")

for a in upcoming_shows:
    dates = a.find('span', class_="dates")
    if dates is not None:
        print("Date:", dates.text.strip().split())
    doors = a.find('span', class_="doors")
    if doors is not None:
        print("Doors:", doors.text.strip())
    artist_info = a.find(class_="headliners")
    supports = a.find(class_="supports")
    if artist_info is not None:
        print("Artist:", artist_info.text.strip())
    else:
        print("Artist: N/A")
    if supports is not None:
        print("Opener:", supports.text.strip())
    else:
        print("Opener: N/A")
    ticket_price = a.find("section", class_="ticket-price")
    sold_out = a.find(class_="sold-out")
    if sold_out is not None:
        print("SOLD OUT:", sold_out)
    elif ticket_price is not None:
        print("Ticket link:", ticket_price.a['href'])
