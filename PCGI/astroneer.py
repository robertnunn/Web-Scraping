"""

    
"""
import os
import sys
import requests
import bs4
import re
from pprint import pprint as pp
import pandas as pd


def get_recipe_table(url):
    page_req = requests.get(url)  # get the page
    page_req.raise_for_status()  # check for errors
    soup = bs4.BeautifulSoup(page_req.text, 'lxml')  # soupify!
    # print(f'requested: {url}')
    # select tables that are direct children of a div tag, with a class attr containing "zebra" but not "recipeTable"
    table = soup.select('div > table[class~=zebra]:not(table[class~=recipeTable])')
    # print(table[0])
    return table[0]  # since we should only get one table


def process_info_box(url):
    item_page = requests.get(url)  # get the page
    item_page.raise_for_status()  # check for errors
    soup = bs4.BeautifulSoup(item_page.text, 'lxml')  # soupify!
    
    info_box = soup.find('table', class_='infoboxtable')  # there should be only one table with a "class" attr that is exactly 'infoboxtable'
    # info_box = soup.find('table', attrs={'class': 'infoboxtable'})  # alternate way of finding the same table
    rows = info_box.find_all('tr')  # grab all the rows out of the table
    row_strings = list()
    info = dict()
    # remap_dict is for internal use only
    remap_dict = {'Tier': 'size',
                  'Group': 'group',
                  'Type': 'type',
                  'Crafted at': 'crafted_at',
                  'Recipe': 'recipe',
                  'Unlock Cost': 'research_cost'}
    for i in rows:  # strip line breaks and commas out (as this will ultimately be a csv)
        row_strings.append([j.replace('\n', '').replace(',', '') for j in i.strings])
    # row_strings = row_strings[-6:]  # this is some evil magic number bs; it works but it's fragile
    try:
        parsed_table = pd.read_html(str(soup.select('table[class~="recipeTable"]')[0]))  # this is a result list, len == 1
    except IndexError as e:
        info['recipe'] = None
        info['size'] = None
        info['research_cost'] = None
        return info
    recipe_dict = process_ing_list(parsed_table[0]['Input'][0], patterns) # get the only list element, "input" column, only row
    
    for i in row_strings:  # this for loop iterates through each row of the table and extracts data under the assumption that "key" appears before "value" _somewhere_
        attr = ''
        # print(i)
        while(len(i)):  # because we're popping list items, the len(list) will be 0 when finished with that row
            term = i.pop(0)
            # print(f'term: {term}')
            if term in remap_dict.keys():  # is this data that we're looking for?
               attr = term
            elif len(term) > 3 and term != 'Bytes':  # special case for the research_cost 
                try:
                    info[remap_dict[attr]] = term
                except KeyError:
                    print(f'Infobox error: attr={attr}, term={term}')
            
            # print(info)
    info['research_cost'] = info.get('research_cost', 'Unlocked').strip()  # data validation for the cost and some formatting
    # print(info)
    info['recipe'] = recipe_dict
    return info


def process_ing_list(ing_list, patterns):
    ing_dict = dict()
    # print(ing_list)
    for pattern in patterns:
        count = pattern.findall(ing_list)
        if len(count) == 0:
            pass
                # print(f'No match found: {ing_list}')
        else:
            print(f'Found {len(count)} matches...')
            for i in count:
                if i[1] == '':
                    num = 1
                else:
                    num = int(i[1])
                ing_dict[i[0]] = num
                print(f'Matched: {i} in "{ing_list}". rebuilt: {i[0]} x{str(num)}')

    return ing_dict


def pick_label(column_labels, valid_label_list):
    for _ in column_labels:
        if _ in valid_label_list:
            return _
    
    raise KeyError(f'No valid label found.\nColumns: {column_labels}\nLabels: {valid_label_list}')


def encode_reserved_chars(url: str):
    global reserved_uri_encodings
    for k,v in reserved_uri_encodings.items():
        url = url.replace(k, v)

    return url


def process_recipe_table(table):
    results = dict()
    print(f"processing: crafting table")
    parsed_table = pd.read_html(str(table))[0]
    # print(parsed_table)
    in_label = pick_label(parsed_table.columns.values, input_labels)
    out_label = pick_label(parsed_table.columns.values, output_labels)
    print(in_label, '->', out_label)

    data = parsed_table.to_dict()
    
    # process each row
    for i in range(len(parsed_table)):
        
        # print([len(i) for i in row])
        # go to the item's page and pull the infobox data
        item_url = url_base + data[out_label][i].replace(' ', '_')
        item_url = encode_reserved_chars(item_url)
        info = process_info_box(item_url)
        print('input: ' + data[in_label][i])
        print('output: ' + data[out_label][i])
        # recipe_dict = process_ing_list(data[in_label][i], patterns)
        results[data[out_label][i]] = {'recipe': info['recipe'], 'size': info['size'], 'research_cost': info['research_cost']}

    return results


def expand_recipe(recipe):
    r = list()
    try:
        for k, v in recipe.items():  # k = ingredient, v = count
            for i in range(v):
                r.append(k)  # adds each ingredient to the list a number of times equal to its count
        while len(r) < 4:  # add empty strings to bring the ingredient count up to four, to make formatting the csv easier
            r.append('')
    except AttributeError as e:
        return ['', '', '', '']
    return r


def get_power_data():
    url = 'https://astroneer.gamepedia.com/Power'
    power_req = requests.get(url)
    power_req.raise_for_status()
    soup = bs4.BeautifulSoup(power_req.text, 'lxml')
    flow_rate = 'Flow Rate (U/s)\n'
    capacity = 'Capacity\n'
    consumption = 'Consumption Rate\n'
    prefix = ';'
    suffix = 'error'
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
            suffix = ' U/s'
        elif consumption in head_strs:
            # do consumers
            print('consumers')
            prefix = '-'
            suffix = ''
        elif capacity in head_strs:
            # do batteries
            print('batteries')
            prefix = ''
            suffix = ''

        for i in rows[1:]:
                strs = [j.replace('\n', '') for j in i.strings]
                results[strs[1]] = prefix + strs[4] + suffix
    return results


def get_scrap_data():
    url = 'https://astroneer.gamepedia.com/Scrap'
    req = requests.get(url)
    req.raise_for_status()
    soup = bs4.BeautifulSoup(req.text, 'lxml')
    scrap_table_marker = 'Name'
    results = dict()

    fields = ['Name', 'Scrap Amount']
    tables = soup.find_all('table')
    # print(tables)
    # print(len(tables))
    for _ in tables:
        headers = _.find('th')
        if headers != None and headers.string != None:
            if scrap_table_marker == headers.string.replace('\n', ''):
                table = _
                break
    
    # print(str(table)[:100])
    parsed_table = pd.read_html(str(table))[0]
    data = parsed_table[fields].to_dict()
    # pp(data)
    for _ in range(len(parsed_table)):
        item = data[fields[0]][_]
        item = item.replace(' (Full) *', '').replace(' **', '').replace(' (Full)', '')
        results[item] = data[fields[1]][_]

    return results

# these are the pages we're going to be scraping
urls = [
        'https://astroneer.gamepedia.com/Large_Printer',
        'https://astroneer.gamepedia.com/Small_Printer',
        'https://astroneer.gamepedia.com/Medium_Printer',
        'https://astroneer.gamepedia.com/Chemistry_Lab',
        'https://astroneer.gamepedia.com/Smelting_Furnace',
        'https://astroneer.gamepedia.com/Backpack',
        ]
tables = dict()
crafting = dict()
reserved_uri_encodings = {
    '!': '%21',
    '#': '%23',
    '$': '%24',
    '%': '%25',
    '&': '%26',
    "'": '%27',
    '(': '%28',
    ')': '%29',
    '*': '%2A',
    '+': '%2B',
    ',': '%2C',
    # '/': '%2F',
    # ':': '%3A',
    ';': '%3B',
    '=': '%3D',
    # '?': '%3F',
    '@': '%40',
    '[': '%5B',
    ']': '%5D',
}
url_base = 'https://astroneer.gamepedia.com/'
# input/output column aliases
input_labels = ['Input', 'Recipe']
output_labels = ['Output', 'Name']

# Tuple of search patterns
base_patterns = ('(Ammonium)',
                '(Argon)',
                '(Carbon)',
                '(Ceramic)',
                '(Clay)',
                '(Compound)',
                '(Copper)',
                '(Diamond)',
                '(EXO Chip)',
                '(Explosive Powder)',
                '(Glass)',
                '(Graphene)',
                '(Graphite)',
                '(Helium)',
                '(Hematite)',
                '(Hydrazine)',
                '(Hydrogen)',
                '(Iron)',
                '(Laterite)',
                '(Lithium)',
                '(Malachite)',
                '(Methane)',
                '(Nanocarbon Alloy)',
                '(Nitrogen)',
                '(Organic)',
                '(Plastic)',
                '(Quartz)',
                '(Resin)',
                '(Rubber)',
                '(Silicone)',
                '(Sphalerite)',
                '(Steel)',
                '(Sulfur)',
                '(Titanite)',
                '(Wolframite)',
                '(Zinc)',
                '(Aluminum(?: Alloy)?)',
                '(Titanium(?: Alloy)?)',
                '(Tungsten(?: Carbide)?)',
            )
digit_group = r'(?: x(\d))?'
# original order: i+digit_group
patterns = [re.compile(i+digit_group) for i in base_patterns]  # append the digit group and compile the regexes

for i in urls:
    tables[os.path.basename(i)] = get_recipe_table(i)  # basename(i) returns everything after the last '/'

for k, v in tables.items():  # k = name of crafting station, v = recipe table for that station
    crafting[k] = process_recipe_table(v)

pp(crafting)
power_data = get_power_data()
scrap_data = get_scrap_data()
# write the csv
csv = list()
ing_label = 'Input'
out_label = 'Output'
station_label = 'Crafted By'
cost_label = 'Research Cost'
power_label = 'Power'
size_label = 'Size/Class'
scrap_label = 'Scrap Value'
csv.append(f'{ing_label} 1,{ing_label} 2,{ing_label} 3,{ing_label} 4,{out_label},{station_label},{cost_label},{scrap_label},{power_label},{size_label}')
for k in crafting.keys():  # k = crafting station
    for v in crafting[k].keys():  # v = item name
        r = expand_recipe(crafting[k][v]['recipe'])  # recipe for item v
        csv.append(f'{r[0]},{r[1]},{r[2]},{r[3]},{v},{k},{crafting[k][v]["research_cost"]},{scrap_data.get(v, "")},{power_data.get(v, "")},{crafting[k][v]["size"]}')  # look at that beautiful f-string

# pp(scrap_data)
# output to disk
if os.path.exists('recipes.csv'):
    os.rename('recipes.csv', 'old recipes.csv')

with open('recipes.csv', mode='w') as r:
    r.write('\n'.join(csv))