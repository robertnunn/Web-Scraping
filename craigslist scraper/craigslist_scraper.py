#!/usr/bin/env python3
"""
python 3.6+
scraping craigslist for given search terms and sending emails for new results

To-Do:
    implement searches as dictionary items stored in a json file
    double-check save/load functions
    allow people to "subscribe" to searches by sending an email to the bot account
"""

import requests
import bs4
import time
import json
import logging
from email.mime.text import MIMEText
from my_lib import send_smtp_gmail

logging.basicConfig(level=logging.DEBUG, filename='scraper.log', filemode='a', format='%(asctime)s %(message)s')


def process_terms(terms):
    # replaces spaces with pluses so they don't break URLs
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
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0'} #, 'Cookie': '1j1pIEiJ6RGd6skKP87RWQsl1ao'}
    logging.debug(search_url + search_terms)
    req = requests.get(search_url + search_terms)#, headers=headers)
    logging.debug('issued request: ' + search_terms)
    # req.raise_for_status()
    logging.debug(req.status_code)
    print(req.status_code)
    if req.status_code == 403:
        logging.debug(req.text)
        print(search_terms, " raised a 403 error")
    # logging.debug('raised for status: ' + search_terms)
    soup = bs4.BeautifulSoup(req.text, 'lxml')
    raw_results = soup.find_all('p', class_='result-info')
    results = []
    final_results = []
    for res in raw_results:
        results.append((res.findChild('a').get('href'), 
                        res.findChild('time').get("datetime"), 
                        res.findChild('a').get_text())
                        )

    if last_run == 0:
        last_run = time.localtime(time.mktime((1970, 1, 1, 1, 1, 1, 4, 1, 0)))

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
    logging.debug('====================entered main===================')
    # import os
    # os.chdir(r'D:\Programming\Python')
    searches = load_searches("searches.json")
    logging.debug('loaded json')
    url_base = 'https://baltimore.craigslist.org'
    url_search = url_base + '/search/zip?query='

    # execute the searches and send emails if any new results since last search
    for i in searches:
        print(i)
        logging.debug('executing search: ' + i)
        terms = process_terms(searches[i]['terms'])
        logging.debug('processed search terms')
        try:
            last_run = time.localtime(time.mktime(tuple(searches[i]['last run'])))
        except:
            last_run = 0
        results = []
        for j in terms:
            logging.debug('running search for: ' + j)
            results += execute_search(url_search, j, last_run)
        if len(results):
            msg = compose_body(results, i, url_base)
            # pp([searches[i]['to_list'], i, msg])
            send_smtp_gmail(searches[i]['to_list'], i, msg, 'email.json')
            logging.debug('sent email for: ' + i)
        logging.debug('end searching for: ' + i)

        searches[i]['last run'] = time.localtime()
        print(time.localtime())
        #stuff.append(' '.join([str(searches[i]['last run']), "updated last run time"]))
    logging.debug('finished searching')

    save_searches('searches.json', searches)
    logging.debug('saved last run data')
    # print(i, "XXX", msg)
    # send_smtp_gmail(['robnunn10@gmail.com'], i, msg)
