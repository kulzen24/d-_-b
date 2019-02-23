#import requests
import praw
import time
import functools
import datetime
from datetime import datetime #for timestamp conversion
import smile_utils
#import os
#import csv
import io
#import glob
#import pandas as pd
#import collections
import re
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

def reddit_login():
    #reddit credentials are in file "smileconfig.py"
    from smileconfig import *

    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret,
                         password=password, user_agent=user_agent,
                         username=username)
    
    return reddit

#label dates on log files
def reddit_pull(reddit, subs, new_subs)

    now = datetime.datetime.now()

    with open(subs, 'r') as subs:
        subreddits = subs.readlines()
    subs.close()
    subreddits = [element.strip() for element in subreddits]

    #not appending file at this stage, because Spotify needs to be able to tell the difference
    with open(new_subs, 'r') as nsubs:
        nsubreddits = nsubs.readlines()
    nsubs.close()
    nsubreddits = [element.strip() for element in nsubreddits]
    [subreddits.append(sub) for sub in nsubreddits]

    majorkey = {} #holds all posts seperated by nested dictionaries for each subreddit
    files = []
    regexp = re.compile('[?:\-:]')

    #measuring how long this takes
    t1, t2 = smile_utils.time_start()

    #Set log to write
    log = smile_utils.paste([now.year], ['-'], [now.month], ['-'], [now.day], ['_reddit_log'], ['.txt'], sep='')
    log = ''.join(log)
    logger = io.open('./logs/' + log, 'w', newline = '', encoding="utf-8")
    for item in subreddits:
        logger.write(item + '\n')

    for i in range(len(subreddits)):
        j = 1 #logging counter
        #s = 1 #song counter -- test without this, can't tell if it is still being used
        majorkey['{0}'.format(subreddits[i])] = {}
        filename = smile_utils.paste([subreddits[i]], [now.year], ['-'], [now.month], ['-'], [now.day],['.csv'], sep='')
        filename = ''.join(filename)
        files.append(filename)
        csv_file = io.open('./data/' + filename, 'w', newline = '', encoding="utf-8")
        writer = csv.writer(csv_file)
        try:
            for submission in reddit.subreddit(subreddits[i]).top('month', limit=500):
                majorkey['{0}'.format(subreddits[i])]['title'] = submission.title
                majorkey['{0}'.format(subreddits[i])]['score'] = submission.score
                majorkey['{0}'.format(subreddits[i])]['updoot'] = submission.upvote_ratio
                majorkey['{0}'.format(subreddits[i])]['date'] = datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S')
                majorkey['{0}'.format(subreddits[i])]['subreddit'] = subreddits[i]
                try:
                    majorkey['{0}'.format(subreddits[i])]['author'] = submission.author.name
                except:
                    majorkey['{0}'.format(subreddits[i])]['author'] = '[deleted]'
                majorkey['{0}'.format(subreddits[i])]['tag'] = submission.link_flair_text
                #write to csv for persistent data
                writer.writerow(majorkey['{0}'.format(subreddits[i])].values())
                #write to log
                to_log = str(majorkey['{0}'.format(subreddits[i])].values()) + ' | posted ' + str(j) + ' out of 500\n\n'
                logger.write(to_log)
                j+=1
        except:
            to_log = "\n\n\n\n[!!!!EXCEPTION!!!!] on " + submission.title + "\n\n\n\n"
            logger.write(to_log)
            pass
        csv_file.close()

    duration, process_time = smile_utils.time_stop(t1, t2)
    to_log = 'Elapsed time: ' + str(duration) + ' minutes\n\nCPU Process time: ' + str(process_time) + ' minutes'

    logger.write(to_log)

    logger.close()