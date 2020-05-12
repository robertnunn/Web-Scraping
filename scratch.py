import bs4
import requests
import os
import re
from pprint import pprint as pp

tests = ['Ceramic x2 Plastic x2',
         'Aluminum Resin x2', 
         'Titanium x2 Steel Aluminum Alloy', 
         'Rubber x2 Aluminum Alloy x2', 
         'Aluminum Alloy x3', 
         'Aluminum x2', 
         'Explosive Powder Aluminum x2 Steel',
         'Aluminum Aluminum Alloy x2',
         'Aluminum Alloy Aluminum x2',
         ]

alre = re.compile('(Aluminum(?: Alloy)?)(?: x(\d))?')

for test in tests:
    count = alre.findall(test)
    if len(count) == 0:
        print(f'No match found: {test}')
    else:
        print(f'Found {len(count)} matches...')
        for i in count:
            if i[1] == '':
                num = 1
            else:
                num = int(i[1])
            print(f'Matched: {i} in "{test}". rebuilt: {i[0]} x{str(num)}')