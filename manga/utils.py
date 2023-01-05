import os
import requests
import json
import re
import math
from PIL import Image

from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
    loader=FileSystemLoader("D:/Programming/Projects/Web-Scraping/manga/templates"),
    autoescape=select_autoescape()
)


img_ext = [
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".bmp",
]

def save_file(folder, filename, source_url, header_info):
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
            os.makedirs(folder, exist_ok=True)
            print('trying: ',full_path)
            # headers={
            #     'Host': header_info['Host'],
            #     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0',
            #     'Accept': 'image/avif,image/webp,*/*',
            #     'Accept-Language': 'en-US,en;q=0.5',
            #     'Accept-Encoding': 'gzip, deflate, br',
            #     'Referer': header_info['Referer'],
            #     # 'Sec-Fetch-Dest': 'image',
            #     # 'Sec-Fetch-Site': 'cross-site',
            #     # 'Sec-Fetch-Mode': 'no-cors'
            # }
            # print(headers)
            page = requests.get(source_url, headers=header_info)
            page.raise_for_status()
            print(f'Saving: {filename}')
            with open(full_path, 'wb') as data:
                for chunk in page.iter_content(100000):
                    data.write(chunk)
        except requests.HTTPError as e:
            print(f'error, ep_url ({source_url}) not found: ({e})')


def get_thumbnail_dims(img_path, target_dim=400):
    pic = Image.open(img_path)
    size = pic.size  # (width, height)
    factor = target_dim / size[0]
    return (round(size[0] * factor, 0), round(size[1] * factor, 0))


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
        # bad_tags = load_tags('D:/Programming/Projects/NSFW/hentai_library/bad_tags.txt')
        stylesheet = (
            "<link rel=stylesheet href="
            + (os.path.abspath(folder).count("\\") * "../")
            + "Programming/Projects/NSFW/hentai_library/hentai.css>"
        )
        # try:
        #     with open(f'{folder}/meta.json', 'r') as m:
        #         metadata = json.loads(m.read())
        #     meta_table = ['<ul>']
        #     for k,v in metadata.items():
        #         meta_table.append(f'<li>{k} ')
        #         if isinstance(v, list):
        #             if len(v) > 1:
        #                 meta_table.append('<ul>')
        #                 bad_hits = check_tags(v, bad_tags)
        #                 for i in sorted(v):
        #                     if i in bad_hits:
        #                         bad_tag = ' bad-tag'
        #                     else:
        #                         bad_tag = ''
        #                     meta_table.append(f'<li class="tag{bad_tag}">{i}</li>')
        #                 meta_table.append('</ul>')
        #             elif len(v) == 1:
        #                 meta_table.append(v[0])
        #             else:
        #                 meta_table.append('None listed')
        #             meta_table.append('</li>')
        #         else:
        #             meta_table.append(v)
        #     id_num = re.search(r'.*\((\d{4,7}?)\)$', folder).group(1)
        #     if '(im)' in folder:
        #         url_base = f'https://imhentai.xxx/gallery/{id_num}'
        #     elif id_num != '0000':
        #         url_base = f'https://nhentai.net/g/{id_num}'
        #     else:
        #         url_base = ''
        #     if url_base != '':
        #         meta_table.append(f'<li><a href="{url_base}">Source Link</a></li>')
        #     meta_table.append('</ul>')
        #     meta_table = ''.join(meta_table)
        #     metadata_panel = f'<div class="metadata">{meta_table}</div>'
        # except Exception as e:
        #     metadata_panel = f'<div class="metadata">{os.path.basename(folder)}</div>'

        # script_src = (
        #     (os.path.abspath(folder).count("\\") * "../")
        #     + "Programming/Projects/NSFW/hentai_library/hentai_page.js"
        # )
        # toc = list()  # links to each page at the top of a gallery
        # beginning of the gallery page/metadata
        page_title = f'{os.path.basename(folder).replace("Chapter", "Ch")} - {manga_title}'
        # html = [
        #     f'<html><head><script src="{script_src}"></script><title></title>{stylesheet}</head><body><center><div id="galleries">'
        # ]
        # html.append(metadata_panel)

        pix = get_image_list(folder)
        # print(pix)
        # for pic in pix:
            # html.append(
            #     f'<img src="{pic[0]}.{pic[1]}" id="{pic[0]}" title="{pic[0]}"></br></br>'
            # )
            # toc.append(f'<a href="#{pic[0]}">Page {pic[0]}</a>')

        # add chapter markers if present
        try:
            with open(f"{folder}/chapters.txt", "r") as ch:
                chapters = ch.read().split("\n")
            ch_list = [i.split(",") for i in chapters]
            for i in ch_list:
                i[0] = int(i[0]) - 1  # num -> index correction
                if len(i) == 1:
                    i.append(f"Chapter {ch_list.index(i)+1}")
                elif i[1] == '':
                    i[1] = f"Chapter {ch_list.index(i)+1}"

                # toc[index] = toc[index].replace(
                #     "a href", f'a class="ch" title="{ch_title}" href'
                # )
        except:
            ch_list = [['', '']]

        # html.append("</center></body></html>")  # end of the gallery page
        # html.insert(
        #     2, make_html_table(toc, toc_width)
        # )  # insert TOC at the beginning, just after the gallery metadata, TOC is generated as img tags are generated

        with open(f"{folder}/gallery.html", "w", encoding="utf-8") as g:
            g.write(render_template('manga_gallery_template.html', stylesheet=stylesheet, page_title=page_title, page_list=[f'{i[0]}.{i[1]}' for i in pix], chapter_indices=[i[0] for i in ch_list], chapter_titles=[i[1] for i in ch_list], title=os.path.basename(folder)))
            # g.write("\n".join(html))


def make_library_page(folder: str, remake_thumbs=False):
    stylesheet = (
            "<link rel=stylesheet href="
            + (os.path.abspath(folder).count("\\") * "../")
            + "Programming/Projects/NSFW/hentai_library/hentai.css>"
        )
    title = os.path.basename(folder)
    original_cwd = os.getcwd()
    folders = list()
    for i in os.scandir(folder):
        if i.is_dir():
            os.chdir(folder)
            folders.append(i.name)
            # do thumbnail stuff
            if not os.path.exists(f'{i.name}/thumb.png') or remake_thumbs:
                first_img_path = f'{i.name}/{".".join(get_image_list(i.name)[0])}'
                wid, hei = get_thumbnail_dims(first_img_path, 300)
                thumb = Image.open(first_img_path)
                thumb.thumbnail((wid, hei))
                thumb.save(f'{i.name}/thumb.png', 'PNG')
    folders.sort(key=lambda f: float(f.split(' ')[1]))  # sort by ch num without needing leading zeros
    
    # table = ['<table>']
    # cols = 5
    # rows = math.ceil(len(folders) / cols) 
    # chapter = 0
    # for i in range(rows):
    #     table.append('<tr>')
    #     for j in range(cols):
    #         table.append(f'<td><a href="{folders[chapter]}/gallery.html"><img src="{folders[chapter]}/thumb.png"><br>{folders[chapter]}</a></td>')
    #         chapter += 1
    #         if chapter >= len(folders):
    #             break
    #     table.append('</tr>')
    # table.append('</table>')
    # table = '\n'.join(table)
    
    
    # html = f'<html><head>{stylesheet}<title>{title}</title></head><body><center>{table}</center></body></html>'
    
    # with open('galleries.html', 'w') as g:
    #     g.write(html)
        
    with open('galleries.html', 'w') as n:
        n.write(render_template('manga_chapters_template.html', stylesheet=stylesheet, chapter_data=folders, title=title))
        
    os.chdir(original_cwd)
        
    
def get_name_table(manga_data: dict):
    # pass the data for key: "mangas"
    status_for = dict()
    
    for k,v in manga_data.items():
        for manga in v['manga'].values():
            status_for[manga['display_name']] = manga['status']
            
    return status_for


def make_manga_listing(folder: str):
    galleries = list()
    manga_data = list()
    
    with open('D:/Programming/Projects/Web-Scraping/manga/manga sources.json', 'r') as ms:
        manga_info = json.loads(ms.read())
    
    status_for = get_name_table(manga_info['mangas'])
    
    for _ in os.scandir(folder):
        gal_path = f'{folder}/{_.name}/galleries.html'
        if os.path.exists(gal_path):
            galleries.append(_.name)
            manga_data.append({'name': _.name, 'status': status_for[_.name]})
            
    stylesheet = (
        "<link rel=stylesheet href="
        + (os.path.abspath(folder).count("\\") * "../")
        + "Programming/Projects/NSFW/hentai_library/hentai.css>"
    )
    # gallery_links = list()
    # for name in galleries:
    #     gallery_links.append(f'<a href="{name}/galleries.html">{name}</a>')
        
    # table = ['<table>']
    # cols = 5
    # rows = math.ceil(len(galleries) / cols) 
    # chapter = 0
    # for i in range(rows):
    #     table.append('<tr>')
    #     for j in range(cols):
    #         table.append(f'<td><a href="{galleries[chapter]}/galleries.html"><img src="{galleries[chapter]}/thumb.jpg"><br>{galleries[chapter]}</a></td>')
    #         chapter += 1
    #         if chapter >= len(galleries):
    #             break
    #     table.append('</tr>')
    # table.append('</table>')
    # table = '\n'.join(table)
        
    # html = f'<html><head>{stylesheet}<title>Manga Listing</title></head><body><center>{table}</center></body></html>'
    
    # with open(f'{folder}/manga.html', 'w') as m:
    #     m.write(html)
        
    with open(f'{folder}/manga.html','w') as n:
        n.write(render_template('manga_listing_template.html', stylesheet=stylesheet, manga_data=json.dumps(manga_data)))
        

def render_template(template_name: str, **kwargs):
    global env
    template = env.get_template(template_name)
    return template.render(**kwargs)