import os
import json
from utils import make_manga_listing, make_library_page, make_local_gallery

os.chdir(os.path.dirname(__file__))

with open('manga sources.json', 'r') as ms:
    manga_data = json.loads(ms.read())

library_folder = manga_data['target_folder']
os.chdir(library_folder)

for manga in os.scandir():
    if manga.is_dir():
        print(manga.name)
        for chapter in os.scandir(manga.name):
            if chapter.is_dir():
                print(chapter.name)
                make_local_gallery(f'{manga.name}/{chapter.name}', True, manga_title=manga.name)
        make_library_page(f'{library_folder}/{manga.name}', True)
make_manga_listing(library_folder)