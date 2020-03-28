import os
import sys
import requests
import bs4
import re
from pprint import pprint as pp


def get_recipe_table(url):
    page_req = requests.get(url)  # get the page
    page_req.raise_for_status()  # check for errors
    soup = bs4.BeautifulSoup(page_req.text, 'lxml')  # soupify!

    table = soup.select('div > table[class~=zebra]:not(table[class~=recipeTable])')
    return table[0]


def process_recipe_row(tr):
    url_master = 'https://astroneer.gamepedia.com'
    try:
        outp, inp = tr.find_all('td')  # get the two cells and assign them to the input and output variables
        olink = outp.find('a', title=True)
        print(olink.get('title'))
        out_str = olink.get('title')

        item_url = url_master + olink.get('href')
        info = process_info_box(item_url)
        
        strs = list()
        for i in inp.strings:
            strs.append(i)
        print(strs)
        return out_str, {'recipe': process_ing_list(strs), 'size': info['size'], 'research_cost': info['research_cost']}
    except ValueError as e:
        print(f'{e}, skipping header row...')
        return None, None


def process_info_box(url):
    item_page = requests.get(url)
    item_page.raise_for_status()
    soup = bs4.BeautifulSoup(item_page.text, 'lxml')
    
    info_box = soup.find('table', class_='infoboxtable')
    rows = info_box.find_all('tr')
    row_strings = list()
    info = dict()
    remap_dict = {'Tier': 'size',
                  'Group': 'group',
                  'Type': 'type',
                  'Crafted at': 'crafted_at',
                  'Recipe': 'recipe',
                  'Unlock Cost': 'research_cost'}
    for i in rows:
        row_strings.append([j.replace('\n', '').replace(',', '') for j in i.strings])
    row_strings = row_strings[-6:]
    
    for i in row_strings:
        attr = ''
        while(len(i)):
            term = i.pop(0)
            # print(f'term: {term}')
            if term in remap_dict.keys():
               attr = term
            elif len(term) > 3 and term != 'Bytes':
                try:
                    info[remap_dict[attr]] = term
                except KeyError:
                    print(f'Infobox error: attr={attr}, term={term}')
            
            # print(info)
    info['research_cost'] = info.get('research_cost', 'Unlocked').strip()
    return info


def process_ing_list(ing_list):
    ing_dict = dict()
    count_re = re.compile(' ?x(\d)\n?')  # regex with a group for the count
    ing_list.pop(0)  # remove the leading whitespace
    last_ing = ''  # so we can remember the last ingredient name while checking for a quantity string
    while(len(ing_list)):
        term = ing_list.pop(0)  # reading the list left to right
        count = count_re.search(term)  # test if the current term is a quantity string
        if len(term) > 3 and count is None:
            ing_dict[term] = 1
            last_ing = term
        elif count is not None:
            ing_dict[last_ing] = int(count.group(1))
    
    return ing_dict


def process_recipe_table(table):
    results = dict()
    rows = table.find_all('tr')
    for i in rows:
        name, data = process_recipe_row(i)
        if name != None:
            results[name] = data
    return results


def expand_recipe(recipe):
    r = list()
    for k, v in recipe.items():
        for i in range(v):
            r.append(k)
    while len(r) < 4:
        r.append('')
    return r


# these are the pages we're going to be scraping
urls = ['https://astroneer.gamepedia.com/Large_Printer',
        'https://astroneer.gamepedia.com/Small_Printer',
        'https://astroneer.gamepedia.com/Medium_Printer',
        'https://astroneer.gamepedia.com/Chemistry_Lab',
        'https://astroneer.gamepedia.com/Smelting_Furnace',
        'https://astroneer.gamepedia.com/Backpack',
        ]
tables = dict()
cd = dict()

for i in urls:
    tables[os.path.basename(i)] = get_recipe_table(i)

for k, v in tables.items():
    cd[k] = process_recipe_table(v)

# write the csv
csv = list()
for k in cd.keys():
    for v in cd[k].keys():
        r = expand_recipe(cd[k][v]['recipe'])
        csv.append(f'{r[0]},{r[1]},{r[2]},{r[3]},{v},{k},{cd[k][v]["research_cost"]},,{cd[k][v]["size"]}')

# ouput to disk
with open('recipes.csv', mode='w') as r:
    r.write('\n'.join(csv))