"""
python 3.6+
scraping craigslist for given search terms and sending emails for new results

To-Do:
    allow people to "subscribe" to searches by sending an email to the bot account
"""

import smtplib
import requests
import bs4
import time
import json
import imaplib
import email
from pprint import pprint as pp
from email.mime.text import MIMEText

from my_lib import send_smtp_gmail


def process_terms(terms):
    return [i.replace(' ', '+') for i in terms]


def load_searches(filename):
    with open(filename, 'r') as f:
        searches = json.loads(f.read())
    return searches


def save_searches(filename, searches):
    with open(filename, 'w') as f:
        f.write(json.dumps(searches, indent=4))

def execute_search(search_url, search_terms, last_run):
    # do the search, extract results, filter, return list of tuples
    req = requests.get(search_url + search_terms)
    req.raise_for_status()
    soup = bs4.BeautifulSoup(req.text, 'lxml')
    raw_results = soup.find_all('p', class_='result-info')
    results = []
    final_results = []
    for res in raw_results:
        results.append((res.findChild('a').get('href'), res.findChild('time').get("datetime"), res.findChild('a').get_text()))

    if last_run == 0:
        last_run = time.localtime(time.mktime((1970,1,1,1,1,1,4,1,0)))

    for i in results:
        # print(i[1])
        date = time.strptime(i[1], '%Y-%m-%d %H:%M')
        # print(date)

        if date > last_run:
            final_results.append(i)


    return final_results


def compose_body(res, subject, extra):
    # get list of tuples, compose the email, return email as string
    body = ['<html><body>Here are the latest results for ', subject, ':</br></br><ol>']
    for i in res:
        link = i[0]
        if not link.startswith('http'):
            link = extra + link
        body.append('<li><a href="')
        body.append(link)
        body.append('">')
        body.append(i[2])
        body.append('</a></li></br>\n')

    body.append('</ol></body></html>')
    body = ''.join(body)

    mesg = MIMEText(body, 'html')

    return mesg.as_string()


if __name__ == '__main__':
    import os
    os.chdir(r'D:\Programming\Python')
    searches = load_searches('searches.json')
    url_base = 'https://baltimore.craigslist.org'
    url_search = url_base + '/search/zip?query='

    # execute the searches and send emails if any new results since last search
    for i in searches:
        print(i)
        terms = process_terms(searches[i]['terms'])
        try:
            last_run = time.localtime(time.mktime(tuple(searches[i]['last run'])))
        except:
            last_run = 0
        results = []
        for j in terms:
            results += execute_search(url_search, j, last_run)
        if len(results):
            msg = compose_body(results, i, url_base)
            # pp([searches[i]['to_list'], i, msg])
            send_smtp_gmail(searches[i]['to_list'], i, msg)
        searches[i]['last run'] = time.localtime()

    save_searches('searches.json', searches)
    # print(i, "XXX", msg)
    # send_smtp_gmail(['robnunn10@gmail.com'], i, msg)

import imaplib
import email
username = "robbot8000"
password = "airheadreluctant"
mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(username,password)
mail.select('inbox')
type, data = mail.search(None, 'ALL')
id_list = [int(i) for i in data[0].split()]

for i in range(id_list[-1], id_list[0], -1):
    typ, data = mail.fetch(i, '(RFC822)')

    for part in data:
        if isinstance(part, tuple):
            msg = email.message_from_string(part[1])
            subject = msg['subject']
            sender = msg['from']
            body = msg['body']
            print(sender, '\n', subject, '\n', body[:40])
