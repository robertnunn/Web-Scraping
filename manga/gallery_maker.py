import os
import re
import json
from PIL import Image
import math
from nhentai import get_thumbnail_dims

img_ext = [
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".bmp",
]

def check_tags(doujin_tags: list, tags: list):
    # tags = list to check against
    # doujin_tags = list you're checking
    doujin_tags = [i.lower() for i in doujin_tags]
    tags = [i.lower() for i in tags]
    hits = set()

    for tag in tags:
        for d_tag in doujin_tags:
            if tag in d_tag:
                hits.add(d_tag)

    return list(hits)


def load_tags(filename: str):
    try:
        # print(os.getcwd())
        with open(filename, "r") as t:
            tags = t.read().split("\n")
        tags = set(tags)
        try:
            tags.remove("")
        except:
            pass
        tags = list(tags)
        return tags
    except:
        print(f"Error loading tags file {filename}")
        return None


def make_html_table(links, width=10):
    table = ["<table>", "\t<tr>"]
    for link in links:
        table.append(f"\t\t<td>{link}</td>")
        # print((links.index(link)+1) % width)
        if not (links.index(link) + 1) % width:
            # print("new row")
            table.append("\t</tr>\n\t<tr>")
    table.append("\t</tr>\n</table>")

    return "\n".join(table)


def get_image_list(folder: str):
    # os.chdir(dir)
    pix = list()

    for pic in os.scandir(
        f"{folder}/"
    ):  # scan the folder looking for image files (not .html in this case)
        pic_ext = pic.name[pic.name.rfind(".") :]
        if pic_ext in img_ext and pic.name != 'thumb.png':
            pix.append(pic.name.split("."))  # split into tuple (filename, ext)
        # elif (
        #     not pic_ext.endswith(".html")
        #     and not pic_ext.endswith(".txt")
        #     and not pic_ext.endswith(".json")
        #     and pic.name != 'thumb.png'
        # ):
        #     print(folder, pic_ext)
        # else:
        #     print('something wacky happened')
    try:  # sort files in ascending order by int if possible, falling back to strings
        pix.sort(key=lambda pic: int(pic[0]))
    except:
        pix.sort(key=lambda pic: pic[0])

    return pix


def make_local_gallery(folder, remake_gallery=False, toc_width=10, manga_title='No Title'):
    if folder[-1] == '/':  # remove terminal '/'
        folder = folder[:-1]
    if not os.path.exists(f"{folder}/gallery.html") or remake_gallery:
        # title attribute is hover alttext for links
        bad_tags = load_tags('D:/Programming/Projects/NSFW/hentai_library/bad_tags.txt')
        stylesheet = (
            "<link rel=stylesheet href="
            + (os.path.abspath(folder).count("\\") * "../")
            + "Programming/Projects/NSFW/hentai_library/hentai.css>"
        )
        try:
            with open(f'{folder}/meta.json', 'r') as m:
                metadata = json.loads(m.read())
            meta_table = ['<ul>']
            for k,v in metadata.items():
                meta_table.append(f'<li>{k} ')
                if isinstance(v, list):
                    if len(v) > 1:
                        meta_table.append('<ul>')
                        bad_hits = check_tags(v, bad_tags)
                        for i in sorted(v):
                            if i in bad_hits:
                                bad_tag = ' bad-tag'
                            else:
                                bad_tag = ''
                            meta_table.append(f'<li class="tag{bad_tag}">{i}</li>')
                        meta_table.append('</ul>')
                    elif len(v) == 1:
                        meta_table.append(v[0])
                    else:
                        meta_table.append('None listed')
                    meta_table.append('</li>')
                else:
                    meta_table.append(v)
            id_num = re.search(r'.*\((\d{4,7}?)\)$', folder).group(1)
            if '(im)' in folder:
                url_base = f'https://imhentai.xxx/gallery/{id_num}'
            elif id_num != '0000':
                url_base = f'https://nhentai.net/g/{id_num}'
            else:
                url_base = ''
            if url_base != '':
                meta_table.append(f'<li><a href="{url_base}">Source Link</a></li>')
            meta_table.append('</ul>')
            meta_table = ''.join(meta_table)
            metadata_panel = f'<div class="metadata">{meta_table}</div>'
        except Exception as e:
            metadata_panel = f'<div class="metadata">{folder}</div>'

        script_src = (
            (os.path.abspath(folder).count("\\") * "../")
            + "Programming/Projects/NSFW/hentai_library/hentai_page.js"
        )
        toc = list()  # links to each page at the top of a gallery
        # beginning of the gallery page/metadata
        html = [
            f'<html><head><script src="{script_src}"></script><title>{os.path.basename(folder).replace("Chapter", "Ch")} - {manga_title}</title>{stylesheet}</head><body><center><div id="galleries">'
        ]
        html.append(metadata_panel)

        pix = get_image_list(folder)
        # print(pix)
        for pic in pix:
            html.append(
                f'<img src="{pic[0]}.{pic[1]}" id="{pic[0]}" title="{pic[0]}"></br></br>'
            )
            toc.append(f'<a href="#{pic[0]}">Page {pic[0]}</a>')

        # add chapter markers if present
        try:
            with open(f"{folder}/chapters.txt", "r") as ch:
                chapters = ch.read().split("\n")
            ch_list = [i.split(",") for i in chapters]
            for i in ch_list:
                index = int(i[0]) - 1  # num -> index correction
                if len(i) == 1:
                    ch_title = f"Chapter {ch_list.index(i)+1}"
                elif i[1] == "":
                    ch_title = f"Chapter {ch_list.index(i)+1}"
                else:
                    ch_title = i[1]

                toc[index] = toc[index].replace(
                    "a href", f'a class="ch" title="{ch_title}" href'
                )
        except:
            pass

        html.append("</center></body></html>")  # end of the gallery page
        html.insert(
            2, make_html_table(toc, toc_width)
        )  # insert TOC at the beginning, just after the gallery metadata, TOC is generated as img tags are generated

        with open(f"{folder}/gallery.html", "w", encoding="utf-8") as g:
            g.write("\n".join(html))


def make_library_page(folder: str, remake_thumbs=False):
    stylesheet = (
            "<link rel=stylesheet href="
            + (os.path.abspath(folder).count("\\") * "../")
            + "Programming/Projects/NSFW/hentai_library/hentai.css>"
        )
    title = os.path.basename(folder)
    
    folders = list()
    for i in os.scandir(folder):
        if i.is_dir():
            folders.append(i.name)
            # do thumbnail stuff
            if not os.path.exists(f'{i.name}/thumb.png') or remake_thumbs:
                first_img_path = f'{i.name}/{".".join(get_image_list(i.name)[0])}'
                wid, hei = get_thumbnail_dims(first_img_path, 300)
                thumb = Image.open(first_img_path)
                thumb.thumbnail((wid, hei))
                thumb.save(f'{i.name}/thumb.png', 'PNG')
    folders.sort(key=lambda f: float(f.split(' ')[1]))  # sort by ch num without needing leading zeros
    
    table = ['<table>']
    cols = 5
    rows = math.ceil(len(folders) / cols) 
    chapter = 0
    for i in range(rows):
        table.append('<tr>')
        for j in range(cols):
            table.append(f'<td><a href="{folders[chapter]}/gallery.html"><img src="{folders[chapter]}/thumb.png"><br>{folders[chapter]}</a></td>')
            chapter += 1
            if chapter >= len(folders):
                break
        table.append('</tr>')
    table.append('</table>')
    table = '\n'.join(table)
    
    
    html = f'<html><head>{stylesheet}<title>{title}</title></head><body><center>{table}</center></body></html>'
    
    with open('galleries.html', 'w') as g:
        g.write(html)


mangas = [
    # 'Spy X Family',
    # 'Monster Musume no Iru Nichijou',
    # 'My Dress-up Darling',
    # 'The World of Moral Reversal',
    # "World's End Harem",
    # 'Oppai Yuri Anthology',
    # 'Monster Musume no Iru Nichijou',
    # 'Hen Suki',
    'Breasts are my Favorite Things in the World',
    # 'Interviews with Monster Girls',
    # 'While Killing Slimes for 300 Years, I Became the MAX Level Unknowingly',
    # 'Overlord',
]

for manga in mangas:
    manga_path = f'D:/Weeb shit/Manga/{manga}'
    os.chdir(manga_path)
    for folder in os.scandir():
        if folder.is_dir():
            # print(folder.name)
            make_local_gallery(folder.name, True, manga_title=manga)
    make_library_page(manga_path, False)