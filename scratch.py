import bs4
import requests
import os
import re
from pprint import pprint as pp
import pandas as pd

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
    
    parsed_table = pd.read_html(str(soup.select('table[class~="recipeTable"]')[0]))
    recipe_dict = process_ing_list(parsed_table[0]['Input'][0], patterns)
    
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
    print(info)
    info['recipe'] = recipe_dict

    return info


# Tuple of search patterns
base_patterns = ('(Ammonium)',
                '(Argon)',
                '(Carbon)',
                '(Ceramic)',
                '(Clay)',
                '(Compound)',
                '(Copper)',
                '(Diamond)',
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
digit_group = '(?: x(\d))?'
# original order: i+digit_group
patterns = [re.compile(i+digit_group) for i in base_patterns]  # append the digit group and compile the regexes

urls =  [
        'https://astroneer.gamepedia.com/Large_Rover_Seat',
        'https://astroneer.gamepedia.com/Large_Shredder',

        ]

for _ in urls:
    pp(process_info_box(_))