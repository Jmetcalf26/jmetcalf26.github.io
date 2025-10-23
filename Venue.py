import requests
import time
import os
from math import floor
from bs4 import BeautifulSoup


class Venue:
    def __init__(self, url, name="", cooldown=10):
        self.url = url
        self.name = name
        self.cooldown = cooldown
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
        }
        self.shows = []

    def getHTML(self):
        
        cd_path = "./cooldowns/" + self.name + "_cooldown"
        
        if not os.path.exists(cd_path):
            with open(cd_path, 'w') as cd:
                cd.write(str(floor(time.time())))
        
        with open(cd_path, "r") as cd:
            prev_scrape = int(cd.read())
            diff = time.time() - prev_scrape
            print("Time since last scrape:", diff)
            if diff < self.cooldown:
                time.sleep(diff)
        
        r = requests.get(self.url, headers=self.headers)
        with open(cd_path, "w") as cd:
            cd.write(str(floor(time.time())))

        with open('pages/'+self.name+'.html', 'wb') as of:
            of.write(r.content)

        return BeautifulSoup(r.content, 'html.parser')
        
    def parse(self, soup):
        pass
    
    def print(self):
        pass
