import requests
from datetime import datetime, timedelta
import os
import logging

# config options
max_delta = timedelta(1,0,0,0,0,13,0) # maximum age of latest data for analysis to be valid, default 24hrs
pos_threshold = 2.0 # maximum % threshold for positive testing rate, above this no email is sent
os.chdir(os.path.dirname(__file__))
logging.basicConfig(level=logging.INFO, filename='covid.log', filemode='a', format='%(asctime)s %(message)s')


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


def get_covid_data():
    # returns csv formatted master covid data for MD
    # MD Dept of Health updates data between 10am-11am every day
    covid_csv_url = 'https://state-of-maryland.github.io/TestingGraph/DailyTestingData.csv'
    req = requests.get(covid_csv_url)
    req.raise_for_status()
    covid_data = req.text.split('\r\n')
    with open('DailyTestingData.csv', 'w') as td:
        td.write('\n'.join(covid_data))
    covid_data = [row.split(',') for row in covid_data]
    return covid_data


# update covid data
covid = get_covid_data()
logging.info('retrieved and wrote DailyTestingData.csv')

# with open('covid.json', 'r') as c:
#     covid = json.loads(c.read())

with open('covid_email.txt', 'r') as g:
    recipients = [i.replace('\n', '') for i in g.readlines()]

data_index = -1
rolling_avg_index = -2
date_index = 0
pos_percent = float(covid[data_index][rolling_avg_index])
pos_delta = float(covid[data_index][rolling_avg_index]) - float(covid[data_index-1][rolling_avg_index])
pos_delta = f'{pos_delta}' if pos_delta < 0 else f'+{pos_delta}'
time_pattern = r'%m/%d/%Y'
data_date = datetime.strptime(covid[data_index][date_index], time_pattern)
today = datetime.today()
delta = today - data_date
logging.info(f'7-day avg: {pos_percent}')

if delta > max_delta:
    logging.info('Error: data is more than one day old!')
else:
    logging.info(f'% Testing Positive: {pos_percent}')
    if pos_percent < pos_threshold:
        logging.info(f'mailed to: {recipients}')
        send_smtp_gmail(recipients, f'COVID-19 Positive Test Rate Below {pos_threshold}%', f'On {data_date.date()}, the 7-day rolling average of positive tests is: {pos_percent}%, a difference of {pos_delta} percentage points from the day before.', '../email.json')
    else:
        logging.info('Pos rate over threshold')
