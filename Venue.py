import requests
import time
import os
import json
from math import floor
from bs4 import BeautifulSoup


class Venue:
    def __init__(self, url, name="", cooldown=10, isUSP=False, isAPI=False):
        self.url = url
        self.name = name
        self.cooldown = cooldown
        self.isAPI=isAPI
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
        }
        self.shows = []

        self.cd_path = ""
        if isUSP:
            self.cd_path = "./cooldowns/USP_cooldown"
        else:
            self.cd_path = "./cooldowns/" + self.name + "_cooldown"




    def backupData(self, r):
        with open('pages/'+self.name+'.html', 'wb') as of:
            of.write(r.content)
        
    def updateCooldown(self):
        with open(self.cd_path, "w") as cd:
            cd.write(str(floor(time.time())))

    def waitCooldown(self):
        if not os.path.exists(self.cd_path):
            with open(self.cd_path, 'w') as cd:
                cd.write(str(floor(time.time())))
        
        with open(self.cd_path, "r") as cd:
            prev_scrape = int(cd.read())
            diff = time.time() - prev_scrape
            print("Time since last scrape:", diff)
            if diff < self.cooldown:
                print("ABOUT TO SLEEP:", diff)
                time.sleep(diff)

    def getData(self):
        self.waitCooldown()
        r = requests.get(self.url, headers=self.headers)
        self.updateCooldown()
        self.backupData(r)

        if self.isAPI:
            return json.loads(r.content)
        else:
            return BeautifulSoup(r.content, 'html.parser')

    def parse(self, soup):
        pass
    
    def print(self):
        pass
