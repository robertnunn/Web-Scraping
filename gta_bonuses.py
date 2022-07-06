import os
from bs4 import BeautifulSoup as BS
import requests
import re
from pprint import pprint as pp
from email.mime.text import MIMEText
import logging
import datetime
from dateutil.parser import parse
import sys


logging.basicConfig(level=logging.INFO, filename='D:/scripts/gta.log', filemode='a', format='%(asctime)s %(message)s')

logging.info('Begin script')
os.chdir('D:/Programming/Projects/Web-Scraping')
url = 'http://old.reddit.com/r/gtaonline/'
url_base = 'http://old.reddit.com'
target_re = re.compile('weekly_bonuses_and_discounts', re.IGNORECASE)

with open('gta_email.txt', 'r') as g:
    recipients = [i.replace('\n', '') for i in g.readlines()]


def send_smtp_gmail(email_to, subject, msg="Default message.", login_info='email.json'):
    """
    sends an email with the relevant fields using GMail
    :param email_to: can be a single string, can be a list of strings. Must all be valid email addresses
    :param subject: subject field of the email
    :param msg: body text, can be HTML or plain text
    :param login_info: account credentials for sending email
    :return: no return value
    """
    import smtplib
    import json

    with open(login_info, 'r') as f:
        login = json.loads(f.read())

    username = login["username"]
    password = login["password"]
    smtp_server = "smtp.gmail.com:587"
    email_body = ''.join(['From: ', username, '\nSubject: ', subject, "\n", msg])

    server = smtplib.SMTP(smtp_server)
    server.starttls()
    server.login(username, password)
    server.sendmail(username, email_to, email_body)

    server.quit()

try:
    logging.info('finished setup')
    page = requests.get(url, headers={'User-agent': 'bot-tastic'})
    # pp(page.headers)
    page.raise_for_status()
    soup = BS(page.text, 'lxml')
    logging.info('retrieved and parsed r/gtaonline')
    found = False
    links = soup.find_all('a', attrs={'href': target_re, 'data-event-action': 'title'})
    for link in links:
        link_date_str = link.string[:link.string.find(' ')]
        link_date = parse(link_date_str, dayfirst=True)
        link_date_alt = parse(link_date_str, dayfirst=False)
        print(link_date_str)
        print(link_date.date(), ', ', datetime.date.today())
        if link_date.date() == datetime.date.today() or link_date_alt.date() == datetime.date.today():
            bonus_link = link
            found = True

    if not found:
        logging.info(f'date_str={link_date_str}, parsed={link_date}, alt={link_date_alt}')
        mesg = MIMEText(f'bonus script failed date check\nlink_date_str={link_date_str}\nlink_date={link_date}\nlink_date_alt={link_date_alt}\ntoday={datetime.date.today()}').as_string()
        # send_smtp_gmail(recipients[0], 'GTA Online bonus script failure', mesg)
        # logging.info('bonus post not current, retrying in 1 hour')
        sys.exit(1)
    else:
        print(bonus_url := url_base + bonus_link.get('href'))
        page = requests.get(bonus_url, headers={'User-agent': 'only scraping once per week'})
        page.raise_for_status()
        soup = BS(page.text, 'lxml')
        logging.info('retrieved and parsed bonus page')
        post = soup.select('div[class~=expando] > form > div > div[class=md]')[0]
        date = soup.find('title').string
        date = date[:date.find(' ')]
        subj = 'GTA Online Bonuses for ' + date
        msg_body = '<html><body>Here are the GTA Online bonuses for ' + date + ':</br></br>' + str(post)
        mesg = MIMEText(msg_body, 'html').as_string()
        logging.info('email body composed')
        print(mesg)
        # with open('temp.txt', 'w') as t:
        #     t.write(mesg)
        # send_smtp_gmail(recipients, subj, mesg)
        logging.info('script complete')
except Exception as e:
    logging.info(f'Something went wrong:\n{e}')
    # send_smtp_gmail('robnunn10@gmail.com', 'GTA online script failure', f'Something went wrong:\n{e}')