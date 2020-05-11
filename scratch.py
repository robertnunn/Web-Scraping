import bs4
import requests
import os
import re
from pprint import pprint as pp

a = requests.get('https://fallout.fandom.com/wiki/Fallout:_New_Vegas_ammunition')
a.raise_for_status()
b = a.text.encode('utf-8')

with open('FONV test.html', mode="wb") as fnv:
    fnv.write(b)