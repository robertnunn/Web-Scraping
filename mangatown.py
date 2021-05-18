from typing import ChainMap
import bs4
import requests
import os
import json

def save_file(folder, filename, source_url):
    disallowed = ['/', '\\', '"', '*', '?', '<', '>', '|']
    replacement = [(':', '-')]
    for i in disallowed:
        filename = filename.replace(i, '')
    for i in replacement:
        filename = filename.replace(i[0], i[1])
    
    if os.path.isfile(full_path := folder+filename):  # walrus operator is pretty cool
        print(full_path, ' already exists')
    else:
        try:
            print('trying: ',full_path)
            page = requests.get(source_url)
            page.raise_for_status()
            print(f'Saving: {filename}')
            with open(full_path, 'wb') as data:
                for chunk in page.iter_content(100000):
                    data.write(chunk)
        except requests.HTTPError as e:
            print(f'error, ep_url ({source_url}) not found: ({e})')


zfill_size = 2
os.chdir(os.path.dirname(__file__))
base_url = 'https://www.mangatown.com'
# manga_url = input('Last bit of mangatown URL (no slashes): ')
manga_url = 'the_world_of_moral_reversal'
full_url = f'{base_url}/manga/{manga_url}'

req = requests.get(full_url)
req.raise_for_status()
soup = bs4.BeautifulSoup(req.text, 'lxml')

title = soup.find('h1', class_='title-top').text
os.makedirs(title, exist_ok=True)
ch_list = soup.select('ul[class="chapter_list"] > li > a')

for ch in ch_list:
    ch_page = ch.get('href')
    ch_num = os.path.split(os.path.dirname(ch_page))[1]
    ch_folder = f'{title}/Ch {str(ch_num)}/'
    os.makedirs(ch_folder, exist_ok=True)
    ch_url = f'{base_url}{ch_page}'
    ch_req = requests.get(ch_url)
    ch_req.raise_for_status()
    ch_soup = bs4.BeautifulSoup(ch_req.text, 'lxml')
    page_links = ch_soup.find('select', onchange='javascript:location.href=this.value;')
    num_pages = len(page_links.find_all('option')) - 1  # removes "featured" option

    img = ch_soup.find('img', id='image')
    img_url = f'http:{img.get("src")}'
    img_ext = os.path.splitext(img_url)[1]

    page_num = 1
    save_file(ch_folder, f'/{str(page_num).zfill(zfill_size)}{img_ext}', img_url)

    for page_num in range(2, num_pages + 1):  # because the chapter page is also the first page of the manga
        page_url = f'{ch_url}{str(page_num)}.html'
        page_req = requests.get(page_url)
        page_req.raise_for_status()
        page_soup = bs4.BeautifulSoup(page_req.text, 'lxml')

        img = page_soup.find('img', id='image')
        img_url = f'http:{img.get("src")}'
        img_ext = os.path.splitext(img_url)[1]
        save_file(ch_folder, f'/{str(page_num).zfill(zfill_size)}{img_ext}', img_url)
        