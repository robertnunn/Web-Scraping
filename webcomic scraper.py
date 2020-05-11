"""
Let's create a generalized webcomic downloader, that can be fed the relevant selectors
and will automatically traverse a comic and download everything.

requires:
    beautiful soup 4
    requests
    python 3

info needed:
    front page url
    img tag selector
    (prev) link selector
    stop criteria
    folder/comic name

TO DO:
    finish requirements
    add code to stop once already downloaded comics are reached
"""

import os
import sys
import bs4
import requests
import re
from pprint import pprint as pp