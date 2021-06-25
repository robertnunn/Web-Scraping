# import bs4
import requests
import os
import time
# import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pprint import pprint as pp

def save_file(folder, filename, source_url):
    disallowed = ['/', '\\', '"', '*', '?', '<', '>', '|']
    replacement = [(':', '-')]
    for i in disallowed:
        filename = filename.replace(i, '')
    for i in replacement:
        filename = filename.replace(i[0], i[1])
    if not folder.endswith('/') and not folder.endswith('\\'):
        folder = folder + '/'
    os.makedirs(folder, exist_ok=True)
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


def pause_point():
    while True:
        a = input('stop? (y/n): ')
        if a == 'y':
            break
    return


driver = webdriver.Chrome()
zfill_size = 2
os.chdir(os.path.dirname(__file__))
base_url = 'https://mangadex.org'
# manga_url = input('Last bit of mangatown URL (no slashes): ')
folder = r'D:/Documents/Manga/Hen Suki'
manga_url = 'c0d82f31-be5f-45c9-a8fe-eb5d5eae7400'  #hensuki
full_url = f'{base_url}/title/{manga_url}'   #https://mangadex.org/title/c0d82f31-be5f-45c9-a8fe-eb5d5eae7400

driver.get(full_url)
time.sleep(1)
try:
    elem = driver.find_elements_by_xpath('//button')
    # print([el.text for el in elem])
    for el in elem:
        if el.text.lower() == "chapters":
            # print(el.tag_name)
            # print(el.get_attribute('class'))
            # print(el.text)
            ch_button = el
            break
    ch_button.click()
    time.sleep(3)

    buttons = driver.find_elements_by_xpath('//button')
    for b in buttons:
        if b.text.lower() == 'load more':
            # print(b.text)
            b.click()
            break
    time.sleep(1)

    lang_filter = driver.find_elements_by_xpath('//input')
    # print(len(lang_filter))
    for option in lang_filter:
        if option.get_attribute('id') == 'input-151':
            # print('found', option.get_attribute('id'))
            option.send_keys('English' + Keys.ENTER)
            break
    time.sleep(1)

    link_container = driver.find_element_by_css_selector('div[class~="v-window-item--active"')
    link_elems = link_container.find_elements_by_tag_name('a')
    links = dict()
    for link in link_elems:
        if 'chapter' in link.get_attribute('href'):
            links[link.text] = link.get_attribute('href')
            # print(link.text)
    # print(len(links))
    pp(links)
    # links = links[::-1]  # reverse the list to put it in chronological order

    for ch, link in links.items():
        driver.get(link)
        time.sleep(1)
        imgs = driver.find_elements_by_tag_name('img')
        # print(len(imgs))
        img_links = [img.get_attribute('src') for img in imgs if 'uploads' in img.get_attribute('src')]
        for link in img_links:
            save_file(f'{folder}/{ch}', os.path.basename(link), link)
    

except Exception as e:
    print(e)

# pause_point()
driver.close()