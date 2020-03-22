"""
very simple image/file downloader, essentially a rewrite of my blank.html page because
DownThemAll! doesn't seem to work anymore

Python 3, requests

goal: just download some fuckin' files
"""

import requests
import os, sys

folder = 'D:\\Pictures\\temp dl\\'
os.makedirs(folder, exist_ok=True)
base_url = 'this needs to be replaced'

image_ext = ['.jpg', '.png', '.gif', '.jpeg', '.bmp']
video_ext = ['.avi', '.mpg', '.mkv', '.mp4', '.wmv', '.flv', '.asf', '.gifv', '.webm', '.mov', '.mpeg']
audio_ext = ['.mp3', '.wav', '.wma', '.flac', '.ogg', '.m4a', '.aiff', '.aac']

# set the relevant extension list for the file type being downloaded
ext_list = image_ext
# ext_list = video_ext
# ext_list = audio_ext

ext = ext_list[0]
prefix = ''
num_items = 21
start_num = 1

for i in range(start_num, num_items+1):
    url = base_url + str(i) + ext
    print('downloading: ', url)
    filename = folder + prefix + str(i) + ext
    if os.path.isfile(filename):
        print("Error, '" + filename + "' already exists, skipping")
    else:
        try:
            found = False
            image = requests.get(url)
            # image.raise_for_status()
            if image.status_code == requests.codes.not_found:
                for j in ext_list:
                    print("trying: " + j)
                    url = base_url + str(i) + j
                    filename = folder + prefix + str(i) + j
                    image = requests.get(url)
                    if image.status_code == requests.codes.ok:
                        ext = j
                        found = True
                        break
            elif image.status_code == requests.codes.ok:
                found = True
            
            if found:
                with open(filename, 'wb') as img:
                    for chunk in image.iter_content(100000):
                        img.write(chunk)
            else:
                raise requests.exceptions.HTTPError
        except Exception as e:
            print("Exception: ", e)