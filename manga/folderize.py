# creates a folder structure for chapters of a manga that has been downloaded from mangatown

import os
import re

# manga_path = 'D:\Weeb shit\Manga\Breasts are my Favorite Things in the World'
ch_re = re.compile(r'c(.*) - (\d{2,3})\.(jpg|png|gif)')

def rename_foldered_manga(manga:str):
    for folder in os.scandir(manga):
        if folder.is_dir():
            for img in os.scandir(f'{manga}/{folder.name}'):
                result = ch_re.search(img.name)
                if result != None:
                    os.renames(f'{folder.name}/{img.name}', f'{folder.name}/{result.group(2)}.{result.group(3)}')


def folder_and_rename_manga(manga:str):
    current_ch = -1
    for img in os.scandir(manga):
        result = ch_re.search(img.name)
        if result != None:
            try:
                new_ch = int(result.group(1))
            except:
                new_ch = float(result.group(1))
            if new_ch != current_ch:
                ch_path = f'Chapter {new_ch}'
                current_ch = new_ch
            os.renames(f'{manga}/{img.name}', f'{manga}/{ch_path}/{result.group(2)}.{result.group(3)}')
            
mangas = [
    'Ajin-chan wa Kataritai',
    'Sono Bisque Doll wa Koi wo suru',
    'The World of Moral Reversal',
    "World's End Harem",
]

for manga in mangas:
    manga_path = f'D:/Weeb shit/Manga/{manga}'
    folder_and_rename_manga(manga_path)