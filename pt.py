from matplotlib import pyplot as plt
from moviepy.editor import *
import requests
import json
import os
import time
import pandas
import sys

import datetime
import dateutil.parser as parser
from unidecode import unidecode

from bs4 import BeautifulSoup
import cv2

MAIL = "intergalaktyczne.shoty@gmail.com"

authURL = 'https://id.twitch.tv/oauth2/token'
Client_ID = '***'
Secret  = '***'

AutParams = {'client_id': Client_ID,
'Accept': 'application/vnd.twitchtv.v5+json',
'client_secret': Secret,
'grant_type': 'client_credentials'
}

AutCall = requests.post(url=authURL, params=AutParams)
access_token = AutCall.json()['access_token']

head = {
'Client-ID' : Client_ID,
'Authorization' :  "Bearer " + access_token,
'Accept': 'application/vnd.twitchtv.v5+json'
}

script_dir = os.path.dirname(__file__)
def downloadfile(name,url):
    name=name+".mp4"
    r=requests.get(url)

    script_dir_x = os.path.dirname(__file__)
    file_path_x = os.path.join(script_dir_x, name)

    f=open(file_path_x,'wb')
    for chunk in r.iter_content(chunk_size=255):
        if chunk: # filter out keep-alive new chunks
            f.write(chunk)
    f.close()

tmp_array_of_clips = []

script_dir10 = os.path.dirname(__file__)
file_path10 = os.path.join(script_dir10, 'blacklist_id.txt')
blacklisted = open(file_path10, 'r')
BLACKLISTED_IDS = blacklisted.read().split(";")
BLACKLISTED_IDS = BLACKLISTED_IDS[:-1]


URL = "https://api.twitch.tv/kraken/clips/top?language=pl&limit=100&period=week"
r = requests.get(URL, headers = head).json()

try:
    for i in range(len(r["clips"])):
        try:
            if r["clips"][i] is not None:
                clipURL = ""
                if r["clips"][i]['vod'] is None:
                    clipURL = "VOD został usunięty :("
                else:
                    clipURL = r["clips"][i]['vod']['url']

                if r["clips"][i]['tracking_id'] not in BLACKLISTED_IDS:
                    new_clip = {
                    'ID': r["clips"][i]['tracking_id'],
                    'URL': r["clips"][i]['url'],
                    'TITLE': r["clips"][i]['title'],
                    'GAME': r["clips"][i]['game'],
                    'VIEWS': r["clips"][i]['views'],
                    'BROADCASTER_NAME': r["clips"][i]['broadcaster']['display_name'],
                    'BROADCASTER_URL': r["clips"][i]['broadcaster']['channel_url'],
                    'CLIP_CREATOR': r["clips"][i]['curator']['display_name'],
                    'VOD_URL': clipURL,
                    'DOWNLOAD_URL': r["clips"][i]['thumbnails']['medium'].split("-preview-480x272.jpg")[0] + ".mp4",
                    }
                    tmp_array_of_clips.append(new_clip)
        except IndexError:
            print("Index error.")
except IndexError:
    print("No Clips!")

################################## SELECT TOP 20 CLIPS
tmp_array_of_clips.sort(key = lambda json: (json['VIEWS']))
tmp_array_of_clips = tmp_array_of_clips[::-1]
tmp_array_of_clips = tmp_array_of_clips[:20]

### GET GAMES
games_arr = []
for item in tmp_array_of_clips:
    if item["GAME"] not in games_arr:
        games_arr.append(item["GAME"])

### SORT BY GAMES
array_of_clips = []
for item in games_arr:
    for clip in tmp_array_of_clips:
        if item == clip["GAME"]:
            array_of_clips.append(clip)

################################## DOWNLOAD SELECTED CLIPS PART
script_dir11 = os.path.dirname(__file__)
file_path11 = os.path.join(script_dir11, 'blacklist_id.txt')
blacklisted = open(file_path11, 'a', encoding='utf-8')

streamer_urls = []
vod_links = []
downloaded_clip_filenames = []
for item in array_of_clips:
    print("Downloading ID:" + item["ID"] + "...")
    downloadfile(item["ID"] + "_" + str(item["VIEWS"]), item["DOWNLOAD_URL"])
    streamer_urls.append(item["BROADCASTER_URL"])
    vod_links.append(item["VOD_URL"])
    downloaded_clip_filenames.append(item["ID"] + "_" + str(item["VIEWS"]) + ".mp4")
    blacklisted.write(item["ID"] + ";")
    time.sleep(2)
    print("Done!")

for item in array_of_clips:
    item["VIDEO"] = {
        'TITLE': item['TITLE'] + " | " + item['BROADCASTER_NAME'],
        'DESCRIPTION': "Streamer: " + item["BROADCASTER_URL"] + " NEWLINE " + "Twórca shota: " + item['CLIP_CREATOR'] + " NEWLINE " + "VOD: " + item["VOD_URL"] + " NEWLINE " + "Jeżeli masz do mnie jakąś sprawę pisz na email: klubharambe@gmail.com" + " NEWLINE " + "#twitch #clip #" + item['BROADCASTER_NAME'],
        'TAGS': "twitch, clip, lol, " + item['BROADCASTER_NAME'],
        'DESTINATION': "clips\\" + item["BROADCASTER_NAME"] + "_" + item["ID"] + ".mp4"
    }

script_dir4 = os.path.dirname(__file__)
file_path4 = os.path.join(script_dir4, 'temp_download_list.json')
with open(file_path4, 'w', encoding='utf-8') as f:
    json.dump(array_of_clips, f, ensure_ascii=False, indent=4)



################################## description
script_dir5 = os.path.dirname(__file__)
file_path5 = os.path.join(script_dir5, 'description.txt')
description_file = open(file_path5, 'a', encoding='utf-8')
description_file.write("20 Najpopularniejszych Polskich Shotów\n\n")
description_file.write("Streamerzy, którzy wzięli udział:\n")
streamer_urls = set(streamer_urls)
for item in streamer_urls:
    streamer_name_tmp = item.split('/')
    streamer_name = streamer_name_tmp[len(streamer_name_tmp)-1]
    description_file.write(streamer_name + ": " + item + "\n")
description_file.write("Link do momentu shota na VODzie:\n")
i_counter = 1
for item in vod_links:
    streamer_name_tmp = item.split('/')
    streamer_name = streamer_name_tmp[len(streamer_name_tmp)-1]
    description_file.write(str(i_counter) + " - " + item + "\n")
    i_counter = i_counter + 1

description_file.write("\nJeżeli masz do mnie jakąś sprawę pisz na maila: " + MAIL + "\n\n")
for item in streamer_urls:
    streamer_name_tmp = item.split('/')
    streamer_name = streamer_name_tmp[len(streamer_name_tmp)-1]
    description_file.write("#" + streamer_name + " ")
description_file.write("#twitch #clips")

################################## TITLE
FINAL_MOVIE_TITLE = array_of_clips[0]['TITLE'] + " | SD ("
for item in streamer_urls:
    streamer_name_tmp = item.split('/')
    streamer_name = streamer_name_tmp[len(streamer_name_tmp)-1]
    FINAL_MOVIE_TITLE += streamer_name
    FINAL_MOVIE_TITLE += ", "
FINAL_MOVIE_TITLE = FINAL_MOVIE_TITLE[:-2] + ")"
description_file.write("\n\n\n" + FINAL_MOVIE_TITLE)
##################################

clips_array = []
for filename in downloaded_clip_filenames:
    tmp_clip = VideoFileClip(filename)
    tmp_clip = tmp_clip.resize([1920, 1080])
    clips_array.append(tmp_clip)


final_array = []
for clip in clips_array:
    for x in array_of_clips:
        if x["ID"] == clip.filename.split("_")[0]:
            STREAMER_NAME = x["BROADCASTER_NAME"]
            STREAMER_NAME = unidecode(STREAMER_NAME)
            SHOT_TITLE = x["TITLE"]
            SHOT_TITLE = unidecode(SHOT_TITLE)
            if(len(SHOT_TITLE) > 72):
                SHOT_TITLE = SHOT_TITLE[:-3] + "..."

    img = clip.get_frame(0)

    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl,a,b))
    final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    #STREAMER NAME BORDER
    font                   = cv2.FONT_HERSHEY_SIMPLEX
    # get coords based on boundary
    textsize = cv2.getTextSize(STREAMER_NAME, font, 4, 2)[0]
    textX = (img.shape[1] - textsize[0]) / 2
    textY = (img.shape[0] + textsize[1]) / 2 - 60
    fontScale              = 4
    fontColor              = (0,0,0)
    thickness              = 15
    lineType               = 1
    pos = (int(textX), int(textY))
    cv2.putText(final, STREAMER_NAME,
        pos,
        font,
        fontScale,
        fontColor,
        thickness,
        lineType)
    #STREAMER NAME
    font                   = cv2.FONT_HERSHEY_SIMPLEX
    # get coords based on boundary
    textsize = cv2.getTextSize(STREAMER_NAME, font, 4, 2)[0]
    textX = (img.shape[1] - textsize[0]) / 2
    textY = (img.shape[0] + textsize[1]) / 2 - 60
    fontScale              = 4
    fontColor              = (255,255,255)
    thickness              = 8
    lineType               = 1
    pos = (int(textX), int(textY))
    cv2.putText(final, STREAMER_NAME,
        pos,
        font,
        fontScale,
        fontColor,
        thickness,
        lineType)



    #CLIP TITLE BORDER
    font                   = cv2.FONT_HERSHEY_PLAIN
    # get coords based on boundary
    textsize = cv2.getTextSize(SHOT_TITLE, font, 3, 2)[0]
    textX = (img.shape[1] - textsize[0]) / 2
    textY = (img.shape[0] + textsize[1]) / 2 + 60
    fontScale              = 3
    fontColor              = (0,0,0)
    thickness              = 7
    lineType               = 1
    pos = (int(textX), int(textY))
    cv2.putText(final, SHOT_TITLE,
        pos,
        font,
        fontScale,
        fontColor,
        thickness,
        lineType)
    #CLIP TITLE
    font                   = cv2.FONT_HERSHEY_PLAIN
    # get coords based on boundary
    textsize = cv2.getTextSize(SHOT_TITLE, font, 3, 2)[0]
    textX = (img.shape[1] - textsize[0]) / 2
    textY = (img.shape[0] + textsize[1]) / 2 + 60
    fontScale              = 3
    fontColor              = (255,255,255)
    thickness              = 3
    lineType               = 1
    pos = (int(textX), int(textY))
    cv2.putText(final, SHOT_TITLE,
        pos,
        font,
        fontScale,
        fontColor,
        thickness,
        lineType)

    audiosweep = AudioFileClip("sweep.wav")
    painting_for_clip = ImageClip(final).set_duration(audiosweep.duration)
    painting_for_clip = painting_for_clip.set_audio(audiosweep)

    final_array.append(painting_for_clip)
    final_array.append(clip)


final_clip = concatenate_videoclips(final_array)
final_clip.write_videofile("o.mp4")
