import os
import re
from nhentai import get_image_list, get_thumbnail_dims
from PIL import Image

def get_name_modtime(dir = '.'):  # returns a list of names in the order they were created
    os.chdir(dir)
    return [
        x[0]
        for x in sorted(
            [(fn, os.stat(fn)) for fn in os.listdir(".")], key=lambda x: x[1].st_mtime   # atime, mtime, ctime; access, mod, create
        )
    ]

img_ext = [
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".bmp",
]

# settings
remake_thumb = True
starting_num = 1
zfill_num = 2

# chapters = [i for i in range(1, 64)]
chapters = [2,3]
chapters = [str(i) for i in chapters]
manga_folder = 'Magic Swordsman and Summoner'
folder_base = f"D:/Weeb shit/Manga/{manga_folder}/Chapter "

# currently setup for reindexing/rethumbing chapter folders where the first image is not indicative of the chapter
for chapter in chapters:
    folder = folder_base + chapter
    os.chdir(folder)
    print(folder)
    # files = get_name_modtime()  # sort by mod/create time
    files = [i.name for i in os.scandir() if os.path.isfile(i)]  # sort by name
    try:
        files.remove('thumb.png')
    except:
        pass
    try:
        files.remove('gallery.html')
    except:
        pass
    for filename in files:   # reindexing code
        if os.path.isfile(filename):
            ext = filename[filename.rfind(".") :]
            # if ext in img_ext and 'thumb' not in filename:
            new_name = f"{str(files.index(filename)+starting_num).zfill(zfill_num)}{ext}"
            print(filename, new_name)
            os.rename(filename, new_name)
    if not os.path.exists(f'thumb.png') or remake_thumb:   # remake thumbnail code
        first_img_path = f'{".".join(get_image_list(folder)[0])}'
        wid, hei = get_thumbnail_dims(first_img_path, 300)
        thumb = Image.open(first_img_path)
        thumb.thumbnail((wid, hei))
        thumb.save(f'thumb.png', 'PNG')
