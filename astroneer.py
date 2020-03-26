import os
import sys
import requests
import bs4

# these are the pages we're going to be scraping
urls = ['https://astroneer.gamepedia.com/Large_Printer',
        'https://astroneer.gamepedia.com/Small_Printer',
        'https://astroneer.gamepedia.com/Medium_Printer',
        'https://astroneer.gamepedia.com/Chemistry_Lab',
        'https://astroneer.gamepedia.com/Smelting_Furnace',
        ]

url = urls[2]
