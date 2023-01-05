from utils import save_file, make_local_gallery
import re
import bs4
import requests
import os


def get_gallery(base_url, manga_url, download_folder, header_info, display_name=None):
    status_re = re.compile('Status\(s\)\:\<\/b\>Ongoing')  
    zfill_size = 2
    # os.chdir(os.path.dirname(__file__))
    # base_url = 'https://www.mangatown.com'
    # manga_url = 'overlord'
    # download_folder = "D:/Weeb shit/Manga"
    full_url = f'{base_url}/manga/{manga_url}'

    req = requests.get(full_url)
    req.raise_for_status()
    soup = bs4.BeautifulSoup(req.text, 'lxml')

    if display_name:
        title = display_name
    else:
        title = soup.find('h1', class_='title-top').text
    ch_list = soup.select('ul[class="chapter_list"] > li > a')
    
    thumb_src = soup.select('div[class~=detail_info] > img')[0].get('src')
    ch_folder = f'{download_folder}/{title}/'
    thumb_name = 'thumb.jpg'
    # if not os.path.exists(f'{ch_folder}{thumb_name}'):
    save_file(ch_folder, thumb_name, thumb_src, {'Referer': 'https://www.mangatown.com', 'Host': 'fmcdn.mangahere.com'})
    
    status = status_re.search(req.text)
    if status:
        status = 'ongoing'
    else:
        status = 'completed'
        print(f'{title} has completed')
    new_ch = set()
    for ch in ch_list:
        ch_page = ch.get('href')  #includes the /manga part of the url
        ch_num = os.path.split(os.path.dirname(ch_page))[1]
        try:
            ch_num = int(ch_num[1:])
        except:
            ch_num = float(ch_num[1:])
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
        if os.path.exists(f'{ch_folder}Chapter {ch_num}/{str(page_num).zfill(zfill_size)}{img_ext}'):
            print(f'broke loop for {display_name}')
            break
        
        save_file(f'{ch_folder}Chapter {ch_num}/', f'{str(page_num).zfill(zfill_size)}{img_ext}', img_url, header_info)
        new_ch.add(str(ch_num))

        for page_num in range(2, num_pages + 1):  # because the chapter page is also the first page of the manga
            page_url = f'{ch_url}{str(page_num)}.html'
            page_req = requests.get(page_url)
            page_req.raise_for_status()
            page_soup = bs4.BeautifulSoup(page_req.text, 'lxml')

            img = page_soup.find('img', id='image')
            img_url = f'http:{img.get("src")}'
            img_ext = os.path.splitext(img_url)[1]
            save_file(f'{ch_folder}Chapter {ch_num}/', f'{str(page_num).zfill(zfill_size)}{img_ext}', img_url, header_info)
        make_local_gallery(f'{ch_folder}Chapter {ch_num}/', True, manga_title=title)
            
    return status, title, new_ch