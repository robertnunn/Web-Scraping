import bs4
import requests
import os
import re
from pprint import pprint as pp


def get_power_data():
    url = 'https://astroneer.gamepedia.com/Power'
    power_req = requests.get(url)
    power_req.raise_for_status()
    soup = bs4.BeautifulSoup(power_req.text, 'lxml')
    flow_rate = 'Flow Rate\n'
    capacity = 'Capacity\n'
    consumption = 'Consumption Rate\n'
    prefix = ';'
    results = dict()
    tables = soup.find_all('table', limit=3)
    for table in tables:
        # print(table.attrs)
        rows = table.find_all('tr')#, limit=5)
        header = rows[0]
        print(head_strs := [j for j in header.strings])
        # for i in rows:
        #     print([j for j in i.strings])
        if flow_rate in head_strs:
            # do producers
            print('producers')
            prefix = '+'
        elif consumption in head_strs:
            # do consumers
            print('consumers')
            prefix = '-'
        elif capacity in head_strs:
            # do batteries
            print('batteries')
            prefix = ''

        for i in rows[1:]:
                strs = [j.replace('\n', '') for j in i.strings]
                results[strs[1]] = prefix + strs[4]
    return results
        

# def process_power_row(tr):
#     rate_re = re.compile('U/s')
#     item = ''
#     power = ''
#     while(len(tr)):
#         term = tr.pop(0).replace('\n', '')
#         if term == None:
#             return ('None', 'None')
#         if len(term) and not rate_re.match(term):
#             item = term
#         elif rate_re.match(term):
#             power = term

#             return (item, power)
#     return ('None', 'None')
pp(get_power_data())