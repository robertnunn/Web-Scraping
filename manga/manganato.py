from utils import save_file, make_local_gallery
import re
import bs4
import requests
import os


def get_gallery(base_url, manga_url, download_folder, header_info, display_name=None):
    status_re = re.compile(r'\<td class=\"table-value\"\>Ongoing')
    ch_re = re.compile(r'chapter-(\d{1,}(\.\d{1,})?)')
    img_re = re.compile(r'^https.*chapter_.*?\/(\d{1,})-\w\.(\w{3,})$')
    zfill_size = 2
    full_url = f'{base_url}/manga-{manga_url}'
    
    req = requests.get(full_url)
    req.raise_for_status()
    soup = bs4.BeautifulSoup(req.text, 'lxml')
    
    if display_name:
        title = display_name
    else:
        title = soup.select('div[class="story-info-right"] > h1')[0].string
    
    thumb_src = soup.select('span[class="info-image"] > img')[0].get('src')
    ch_folder = f'{download_folder}/{title}/'
    thumb_name = 'thumb.jpg'
    # if not os.path.exists(f'{ch_folder}{thumb_name}'):
    save_file(ch_folder, thumb_name, thumb_src, header_info)
    
    status = status_re.search(req.text)
    if status:
        status = 'ongoing'
    else:
        status = 'completed'
        print(f'{title} has completed')
        
    new_ch = set()
    ch_list = soup.select('div[class="panel-story-chapter-list"]')[0].find_all('a')
    for chapter_tag in ch_list:
        ch_url = chapter_tag.get('href')
        ch_req = requests.get(ch_url)
        ch_req.raise_for_status()
        ch_soup = bs4.BeautifulSoup(ch_req.text, 'lxml')
        if match := ch_re.search(ch_url):
            try:
                ch_num = int(match.group(1))
            except:
                ch_num = float(match.group(1))
        else:
            print(f'chapter link "{ch_url}" did not match regex')
            continue
        if os.path.exists(f'{ch_folder}Chapter {ch_num}'):
            print(f'broke loop for {display_name}')
            break
            
        new_ch.add(str(ch_num))
        img_tags = ch_soup.select('div[class="container-chapter-reader"] > img')
        for tag in img_tags:
            href = tag.get('src')
            match = img_re.search(href)
            page_num = match.group(1)
            img_ext = match.group(2)
            save_file(f'{ch_folder}Chapter {ch_num}/', f'{str(page_num).zfill(zfill_size)}.{img_ext}', href, header_info)
        make_local_gallery(f'{ch_folder}Chapter {ch_num}/', True, manga_title=title)
        
        
        
    
    return status, title, new_ch