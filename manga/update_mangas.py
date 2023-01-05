import json
import os
# import requests
# import bs4
# import re
# from PIL import Image
# import copy
# from tqdm import tqdm
# import math
from utils import make_manga_listing
from utils import make_library_page
from mangatown import get_gallery as get_mangatown_gallery
from manganato import get_gallery as get_manganato_gallery


def send_smtp_gmail(email_to: list, subject: str, msg: str, login_info='email.json', smtp_server="smtp.gmail.com:587"):
    """
    sends an email with the relevant fields using GMail
    :param email_to: list of valid email addresses
    :param subject: subject field of the email
    :param msg: body text, can be HTML or plain text
    :param login_info: account credentials for sending email
    :return: no return value
    """
    import smtplib
    import json
    from email.mime.text import MIMEText

    with open(login_info, 'r') as f:
        login = json.loads(f.read())

    email_to = ','.join(email_to)
    username = login["username"]
    password = login["password"]
    
    email = MIMEText(msg)
    email['Subject'] = subject
    email['From'] = username
    email['To'] = email_to
    
    server = smtplib.SMTP(smtp_server)
    server.starttls()
    server.login(username, password)
    server.sendmail(username, email_to, email.as_string())
    server.quit()


sites = {
    'mangatown': get_mangatown_gallery,
    'manganato': get_manganato_gallery,
}

os.chdir(os.path.dirname(__file__))
# with open('scrape_testing.json') as ms:
with open('manga sources.json') as ms:
    manga_data = json.loads(ms.read())

updates = dict()
download_folder = manga_data['target_folder']
mangas = manga_data['mangas']
for site in mangas.keys():
    base_url = mangas[site]['base_url']
    headers = mangas[site]['header_info']
    dl_gallery = sites[site]
    for manga, data in mangas[site]['manga'].items():
        if data['status'] == 'ongoing':
            data['status'], title, new_chapters = dl_gallery(base_url, manga, download_folder, headers, data['display_name'])
            if data['display_name']:
                title = data["display_name"]
            else:
                data['display_name'] = title
            
            manga_path = f"{download_folder}/{title}"
            if len(new_chapters) > 0:
                updates[title] = new_chapters
            make_library_page(manga_path, False)

if len(updates) > 0:
    msg = ['The following updates are available:\n']
    for k,v in updates.items():
        msg.append(f'{k} chapter(s): {", ".join(sorted(v))}')
    msg = '\n'.join(msg)
    send_smtp_gmail(['robnunn10@gmail.com'], 'Manga Updates Available', msg, '../email.json')

with open('manga sources.json', 'w') as ms:
    ms.write(json.dumps(manga_data, indent=2))
make_manga_listing(download_folder)