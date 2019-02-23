#import requests
#import praw
#import time
#import functools
#import datetime
#import os
#import csv
#import io
import glob
import pandas as pd
import collections
import re
import smile_utils
#import pprint
#import sys
#import subprocess
#import spotipy
#from spotipy.oauth2 import SpotifyClientCredentials
#import spotipy.util as util
#import json
#from json.decoder import JSONDecodeError
#import webbrowser
#import operator
#from itertools import cycle
#from time import sleep
#import string

#Create dataframe with post information
songs = pd.concat([pd.read_csv(file, header=None) for file in glob.glob('./data/*.csv')], ignore_index=True)
cols = ['track', 'upvotes', 'ratio', 'date', 'subreddit', 'author', 'tag']
songs.columns = cols

#Standardize casing and remove tagged discussion posts
songs['track'] = [i.lower() for i in songs['track']]
songs['tag'] = songs['tag'].astype('str')
songs['tag'] = [i.lower() for i in songs['tag']]
songs = songs[~songs['track'].str.contains("discussion")]
    
#filter to posts that are formatted like song posts
regexp = re.compile('[?:\-:]')
songs = songs[songs['track'].str.contains(regexp)]
songs.reset_index(drop = True, inplace = True)

#Different types of album flags
album_tags = ['[fresh album]', '[fresh ep]', '(new album)', '[new album]', '(full album)', '[full album]',
              '(fresh album)', '(fresh ep)', '(album)', '[album]','(ep album)', '[ep album]', 'full album', 'album',
             '[fresh compilation]', '(fresh compilation)']

for i in album_tags:
    songs['track'] = [x.replace(i, '!album!') for x in songs['track']]

#when album flag is identified in link text flair ("tag" column)
for row, x in songs.iterrows():
    if x[6] in ['ep', 'album', 'fresh ep', 'fresh album', 'set', 'fresh set', 'mix', 'fresh mix']:
        songs.at[row, 'track'] = '!album! ' + x[0]

#Remove trailing characters
for row, s in songs.iterrows():
    f = s[0].find('-')
    g = s[0].find('[')
    h = s[0].find('(')
    i = s[0].find('{')
    
    no_neg = [f,g,h,i]
    
    neg100 = smile_utils.infinite_neg(no_neg)
    
    if (neg100[0] < neg100[1] and neg100[0] < neg100[2] and neg100[0] < neg100[3]):
        print(songs['track'][row])
        songs.at[row,'track'] = re.split(r'[(){}[\]]', s[0])[0]
    
#Remove characters in parentheses and any punctuation which may not be key part of artist or song name
#Look up remix logic from before
substitutions = {" ft. ": " ", " ft ": " ", " feat. ": " ", " feat ":" ", " prod ":" ", " prod. ":" ",
                 " prod by ":" ", " prod. by ":" ", " produced by ":" ", " featuring ":" ", " by ": " "}
songs['track'] = [x.replace('\u200e', ' ') for x in songs['track']] #encoding error that intermittently occurs

#for edge cases where a song title is followed by another hyphen then some commentary in the title
for x in songs['track']:
    counts = collections.Counter(x)['-']
    if counts > 1:
        try:
            x = x.split(' - ', 2)[0] + ' ' + x.split(' - ', 2)[1]
        except:
            print(x)
            pass

#Remix, mix, edit logic
for row, x in songs.iterrows():
    #parentheses
    if '(' in x[0]:
        y = x[0][x[0].find("(")+1:x[0].find(")")] #index 0 refers to track column
        if 'remix' in y or 'mix' in y or 'edit' in y:
            songs.at[row,'track'] = y + ' ' + x[0]
    #bracket logic: must reverse since some titles start with bracket tags which I need
    if '[' in x[0]:
        yy = x[0][::-1]
        yy = yy[yy.find("]")+1:yy.find("[")]
        yy = yy[::-1]
        if 'remix' in yy or 'mix' in yy or 'edit' in yy:
            songs.at[row,'track'] = yy + ' ' + x[0]

songs['track'] = [re.sub("[\(\[\{].*?[\)\]\}]", "", x) for x in songs['track']]
songs['track'] = [x.replace('--', ' ') for x in songs['track']]
songs['track'] = [x.replace('-', ' ') for x in songs['track']]
songs['track'] = [x.replace(' & ', ' ') for x in songs['track']]
songs['track'] = [x.replace(' x ', ' ') for x in songs['track']]
songs['track'] = [x.replace(' | ', ' ') for x in songs['track']]
songs['track'] = [x.replace('/', ' ') for x in songs['track']]
songs['track'] = list(map(lambda x: smile_utils.replace2(x, substitutions), songs['track']))

#write Spotify dataframe to csv
my_csv = paste([now.year], ['-'], [now.month], ['-'], [now.day], ['_songs'], ['.csv'], sep='')
my_csv = ''.join(my_csv)
songs.to_csv('./logs/' + my_csv, sep=',', encoding = 'utf-8')