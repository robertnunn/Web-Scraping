# scrape mission region, name, and start data from the wiki

import requests
from bs4 import BeautifulSoup as BS
import os
from pprint import pprint as pp
import json

def get_mission_data(s):
    # if name := s.select(name_selector)[0].string:
    #     name = 'ERROR'
    # if region := s.select(region_selector)[0].string:
    #     region = 'ERROR'
    # if start := s.select(start_selector)[0].string:
    #     start = "ERROR"
    name = s.select(name_selector)[0].text.strip()
    region = s.select(region_selector)[0].text.strip()
    start = s.select(start_selector)[0].text.strip()
    return region, name, start
    # return region.strip(), name.strip(), start.strip()

start_selector = 'div[data-source="start"]'
name_selector = 'h1[class="page-header__title"]'
region_selector = 'div[data-source="region"]'

url_base = 'https://generation-zero.fandom.com'
url = 'https://generation-zero.fandom.com/wiki/Missions'

req = requests.get(url)
req.raise_for_status()
soup = BS(req.text, 'lxml')

mission_links = soup.select('a[href^="/wiki"]')[9:-7]
mission_links = [i for i in mission_links]
results = dict()
for i in mission_links:
    url = f'{url_base}{i.get("href")}'
    req = requests.get(url)
    req.raise_for_status()
    print(url)
    s = BS(req.text, 'lxml')
    try:
        region, name, start = get_mission_data(s)
        try:
            results[region][name] = start
        except:
            results[region] = {name: start}
    except:
        print(f'Manually check {url}')
        
with open('gzmissions.json', 'w') as g:
    g.write(json.dumps(results, indent=2))