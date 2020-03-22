# a = 'abcdefghijklmnopqrstuvwxyz'
a = 'https://imgur.com/a/2p4e7XS'
import requests
from urllib.parse import unquote

# req = requests.get(a)
# print(req.text)

a = r'https%3A%2F%2Fd3ctxlq1ktw2nl.cloudfront.net%2Fproduction%2F2019-11-22%2F40136715-44100-2-e884a0cf5647b.mp3'
print(a)
b = unquote(a)
print(b)