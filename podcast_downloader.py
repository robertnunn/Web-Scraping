"""
This script runs under the assumption that no podcast releases more than one episode per day.
It also assumes that any episodes that are displayed by pressing the "load more episodes" button
have already been downloaded and appropriately numbered.
It also assumes that the script is run daily.
It uses that assumed numbering to keep the episodes in order.


stitcher uses "< 1 day ago" to indicate today
"""

import os
import sys
import bs4
import requests
import re
import datetime
# from selenium import webdriver
# from urllib.parse import unquote
from pprint import pprint as pp


def download_podcast(podcast_url, target_folder):
    sites = {   'stitcher': stitcher_download,  
                'iheart': iheartradio_download,
            }
    os.makedirs(target_folder, exist_ok=True)
    
    for i in sites.keys():
        if i in podcast_url:
            sites[i](podcast_url, target_folder)


def save_file(folder, filename, source_url):
    disallowed = ['/', '\\', '"', '*', '?', '<', '>', '|']
    replacement = [(':', '-')]
    for i in disallowed:
        filename = filename.replace(i, '')
    for i in replacement:
        filename = filename.replace(i[0], i[1])
    
    if os.path.isfile(full_path := folder+filename) or os.path.isfile(dest_folder[:dest_folder.rfind('New')] + filename):  # walrus operator is pretty cool
        print(full_path, ' already exists')
    elif os.path.isfile(full_path.replace('/New', '')):
        print(full_path.replace('/New', ''), ' already exists')
    else:
        try:
            audio = requests.get(source_url)
            audio.raise_for_status()
            print(f'Saving: {filename}')
            with open(full_path, 'wb') as ep_audio:
                for chunk in audio.iter_content(100000):
                    ep_audio.write(chunk)
        except requests.HTTPError as e:
            print(f'error, ep_url ({source_url}) not found: ({e})')


def stitcher_download(podcast, target_folder):
    url_show_name = podcast[podcast.rfind('/')+1:]
    show_name = url_show_name.replace('-', ' ').title()
    ep_url_pattern = re.compile('episodeURL: "(.*?)",\n')
    ep_date_pattern = re.compile(r"(\<?) ?(\d) days? ago")
    full_year_pattern = re.compile(r'\d{4}')
    # ep_title_pattern = re.compile('<div id="embedPopup">.*?<h2>(.*?)</h2>', flags=re.DOTALL)
    base_url = 'https://www.stitcher.com'
    os.makedirs(f'{target_folder}/{show_name}', exist_ok=True)
    
    req = requests.get(podcast)
    req.raise_for_status()
    soup = bs4.BeautifulSoup(req.text, 'lxml')

    episode_tags = soup.find_all('div', id='episodeContainer')
    # these are the ones displayed, but not the episode at the top of the page
    episode_dict = {base_url + i.find('a').get('href'): {'date': i.find('span', class_='when').string, 'title': i.find('a').string} for i in episode_tags}
    # this is the ep at the top of the page
    cur_ep_re = f"'\/podcast\/{url_show_name}\/e\/(\d*)\\?autoplay"
    cur_ep_num = re.search(cur_ep_re, req.text)
    # add the current episode
    episode_dict[f'{podcast}/e/{cur_ep_num.group(1)}'] = {'date': soup.find('span', class_='when').string, 'title': soup.find('h2', class_='title').string}
    
    for i in episode_dict.keys():
        print(i)
        ep_page = requests.get(i)
        ep_page.raise_for_status()
        # soup = bs4.BeautifulSoup(ep_page.text, 'lxml')
        
        ep_url = ep_url_pattern.search(ep_page.text).group(1)
        print("ep_url: ", ep_url)
        
        pub_date = ep_date_pattern.search(episode_dict[i]['date'])
        if pub_date:
            if pub_date.group(1):
                date_prefix = datetime.date.today().isoformat()
            else:
                date_prefix = (datetime.date.today()-datetime.timedelta(days=int(pub_date.group(2)))).isoformat()
        else:
            if full_year_pattern.search(episode_dict[i]['date']):
                date_prefix = datetime.datetime.strptime(episode_dict[i]['date'], r'%b %d, %Y').isoformat()[:10]
            else:
                current_year = str(datetime.date.today().year)
                date_prefix = datetime.datetime.strptime(episode_dict[i]['date'], r'%b %d').isoformat().replace('1900-', f'{current_year}-')[:10]

        filename = f'{date_prefix} - {episode_dict[i]["title"]}.mp3'
        foldername = f'{target_folder}/{show_name}/'
        save_file(foldername, filename, ep_url)


def player_download(podcast, target_folder):
    url_show_name = podcast[podcast.rfind('/')+1:]
    show_name = url_show_name.replace('-', ' ').title()
    

def iheartradio_download(podcast, target_folder):
    req = requests.get(podcast)
    req.raise_for_status()
    start_soup = bs4.BeautifulSoup(req.text, 'lxml')

    rss_tag = start_soup.find('a', href=re.compile('megaphone'))
    if len(rss_tag) == 0:
        print('Error: podcast has no RSS feed')
        return

    rss_url = rss_tag.get('href').strip()
    print(rss_url)
    rss_req = requests.get(rss_url)
    soup = bs4.BeautifulSoup(rss_req.text, 'lxml')

    show_name = soup.find('title').string
    episodes = soup.find_all('item')
    os.makedirs(f'{target_folder}/{show_name}', exist_ok=True)

    for episode in episodes:
        ep_title = episode.find('title').string.strip()
        # next three lines slice and dice an extended date/time stamp into a YYYY-MM-DD format
        pub_date = episode.find('pubdate').string
        pub_date = pub_date[pub_date.find(' ')+1:pub_date.find(':')-3]
        pub_date = datetime.datetime.strptime(pub_date, '%d %b %Y').isoformat()[:10]
        ep_url = episode.find('enclosure').get('url')
        ep_filename = f'{pub_date} - {ep_title}.mp3'
        save_file(f'{target_folder}/{show_name}/', ep_filename, ep_url)


os.chdir('D:/Programming/Projects/Web-Scraping')

with open('podcast list.txt') as slist:
    podcasts = slist.read().split('\n')
try:
    podcasts.remove('') # gets rid of the empty string that occurs if there are blank lines in the text file
except:
    pass
dest_folder = 'D:/Podcasts/New'

for i in podcasts:
    download_podcast(i, dest_folder)

# delete folders for podcasts that have no updates
new_folder_list = os.scandir(dest_folder)
for _ in new_folder_list:
    try:
        os.rmdir(_)
    except:
        pass
try:
    os.rmdir(dest_folder)
except:
    pass