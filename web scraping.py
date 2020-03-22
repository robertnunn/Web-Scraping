"""
python 3
web scraping practice using:
    requests
    beautiful soup 4

goal: download all xkcd comics, number and title them appropriately
"""

import requests
import bs4
import os, time

os.chdir('./comics')
url_master = 'http://xkcd.com'
url = 'http://xkcd.com'
comic = 'xkcd'
folder = ' '.join([comic, time.strftime('%b-%d-%Y')])
os.makedirs(folder, exist_ok=True)
os.chdir('./' + folder)
comic_name_list = []
num = 9999
# print(dir)
# a[::-1] == reversed list

while not url.endswith('#'):
    print('downloading', url)
    comic_page = requests.get(url)
    comic_page.raise_for_status()
    soup = bs4.BeautifulSoup(comic_page.text, 'lxml')
    try:
        num = int(os.path.split(url[:-1])[1])
    except:
        print("no number detected")
    comic_data = soup.select('#comic img')
    if comic_data != []:
        comic_url = comic_data[0].get('src')
        comic_name_list.append(os.path.basename(comic_url))
        try:
            comic_res = requests.get('http:' + comic_url)
            comic_res.raise_for_status()

            with open(os.path.basename(comic_url), 'wb') as c:
                for chunk in comic_res.iter_content(100000):
                    c.write(chunk)
        except Exception as e:
            print(e)

    prev_data = soup.select('a[rel="prev"]')[0]
    prev_link = prev_data.get('href')
    url = url_master + prev_link

comic_name_list = comic_name_list[::-1]
print("renaming...")
for i in range(len(comic_name_list)):
    try:
        src = comic_name_list[i]
        dst = str(i+1).zfill(4) + ' - ' + src
        os.rename(src, dst)
    except Exception as e:
        print(e)
