"""
Let's create a generalized webcomic downloader, that can be fed the relevant selectors (and python expressions)
and will automatically traverse a comic and download everything.

requires:
    beautiful soup 4
    requests
    python 3

TO DO:
"""

import os
import sys
import bs4
import requests
import re
from pprint import pprint as pp
import json

webcomics_folder = 'D:/Pictures/Webcomics/'
new_folder = webcomics_folder + 'New/'

def get_comics(comic_dict):
    url = comic_dict['url']
    os.makedirs(new_folder + comic_dict['folder'], exist_ok=True)
    while(url != comic_dict['stop_url']):
        print(url)
        # get the page and parse it
        req = requests.get(url)
        req.raise_for_status()
        soup = bs4.BeautifulSoup(req.text, 'lxml')

        img_url = comic_dict['img_base'] + soup.select(comic_dict['img'])[0].get('src')
        if comic_dict['img_url_mod'] != "":
            img_url = eval(comic_dict['img_url_mod'])
        # title the comic is one is available/defined
        if comic_dict['title'] != "":
            title = eval(comic_dict['title']) + os.path.splitext(img_url)[1]
        else:
            title = os.path.basename(img_url)
        
        if comic_dict['numbering'] != False:
            img_filename = f'{str(eval(comic_dict["numbering"])).zfill(4)} - {title}'
        else:
            img_filename = title  # shouldn't ever have a title but no numbering (maybe?)
        img_filename = f'{comic_dict["folder"]}/{img_filename}'  # append comic-specific folder to path

        # if this particular comic exists in either of the two proper places, we have presumably reached the most recent already-downloaded comic, so break the loop and move on to the next comic
        if not os.path.exists(new_folder + img_filename) and not os.path.exists(webcomics_folder + img_filename):
            img_req = requests.get(img_url)
            img_req.raise_for_status()
            with open(new_folder + img_filename, 'wb') as c:
                for chunk in img_req.iter_content(100000):
                    c.write(chunk)
        else:
            break
        
        # if we're not done yet, get the link to the previous page and continue the cycle
        url = comic_dict['prev_base'] + soup.select(comic_dict['prev'])[0].get('href')


with open('D:/Programming/Projects/Web-Scraping/webcomics.json', 'r') as w:
    asdf = w.read()
    comics_data = json.loads(asdf)

del comics_data['template']
# pp(comics_data)

# DO THE NEEDFUL!
for i in comics_data.keys():
    get_comics(comics_data[i])

# delete folders for comics that have no updates
new_folder_list = os.scandir(new_folder)
for _ in new_folder_list:
    try:
        os.rmdir(_)
    except:
        pass