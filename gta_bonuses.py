import os
from bs4 import BeautifulSoup as BS
import requests
import re
from pprint import pprint as pp
from email.mime.text import MIMEText
import logging


logging.basicConfig(level=logging.INFO, filename='D:/scripts/gta.log', filemode='a', format='%(asctime)s %(message)s')

logging.info('Begin script')
os.chdir('D:/Programming/Projects/Web-Scraping')
url = 'http://old.reddit.com/r/gtaonline/'
url_base = 'http://old.reddit.com'
target_re = re.compile('weekly_gta_online_bonuses', re.IGNORECASE)

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
    link = soup.find('a', href=target_re)
    print(bonus_url := url_base + link.get('href'))

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
    send_smtp_gmail(recipients, subj, mesg)
    logging.info('script complete')
except Exception as e:
    logging.info(f'Something went wrong:\n{e}')
    send_smtp_gmail('robnunn10@gmail.com', 'GTA online script failure', f'Something went wrong:\n{e}')