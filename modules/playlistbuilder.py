import datetime
from datetime import datetime
import os
import io
import pandas as pd
import re
import smile_utils
import plist_utils
import sys
import subprocess
import json
from json.decoder import JSONDecodeError
import webbrowser
import operator
from itertools import cycle
from time import sleep

try:
    my_csv = paste([now.year], ['-'], [now.month], ['-'], [now.day], ['_songs'], ['.csv'], sep='')
    my_csv = ''.join(my_csv)
    songs = pd.read_csv('./logs/' + my_csv)
except:
    #in case it runs the following day
    my_csv = paste([now.year], ['-'], [now.month], ['-'], [(now.day) + 1], ['_songs'], ['.csv'], sep='')
    my_csv = ''.join(my_csv)
    songs = pd.read_csv('./logs/' + my_csv)

currentmonth = datetime.now()
currentmonth = currentmonth.month
currentyear = datetime.now().year
months = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6:'June', 7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'}
# script must run spotify login from utils
user = spotifyObject.current_user()

def modify(subreddit = 'subreddits.txt', playlists = 'playlist_ids.txt', spotifyObject, songs):
    import ast

    track_id = []
    jj = 0 #album track indexer
    retry_ids = {}

    with open(subreddit, 'r') as subs:
        subreddits = subs.readlines()
    subs.close()
    subreddits = [element.strip() for element in subreddits]

    with open(playlists, 'r') as ids:
        playlist_ids = ids.readlines()
    ids.close()
    playlist_ids = [element.strip() for element in playlist_ids]

    pl_ids = list(zip(subreddits, playlist_ids))

    #logging
    log = paste([now.year], ['-'], [now.month], ['-'], [now.day], ['_spotify_log'], ['.txt'], sep='')
    log = ''.join(log)
    logger = io.open('./logs/' + log, 'w', newline = '', encoding="utf-8")

    #archiveids file
    archive_file = io.open('./archiveids.txt', 'r', newline = '', encoding="utf-8")
    with open('./archiveids.txt', 'r') as dict_file:
        mydict = dict_file.read()
        archive_ids = ast.literal_eval(mydict)

    #subs to retry
    retry_file = io.open('./' + 'retries.txt', 'w', newline = '', encoding="utf-8")

    #strings which didn't return songs
    no_worky = io.open('./no_worky.txt', 'w', newline = '', encoding="utf-8")

    for pl in pl_ids:
        try:
            print('\n\n\n\n\n' + pl[0] + '\n\n\n\n\n')
            logger.write('\n\n\n\n\n' + pl[0] + '\n\n\n\n\n')

            #add tracks from current playlist to archive
            p = 0
            track_refresh = []
            tracklist = spotifyObject.user_playlist_tracks(user['id'], playlist_id=pl[1], fields=None, limit=50, offset=0, market=None)
            for track in range(len(tracklist['items'])):
                pl_track = tracklist['items'][p]['track']['id']
                track_refresh.append(pl_track)
                p += 1
            privateObject.user_playlist_add_tracks(user=user['id'], playlist_id=archive_ids[pl[0]],tracks=track_refresh)

            #filter dataframe to target subreddit
            plist = songs.loc[songs['subreddit']==pl[0]]
            plist = plist['track'].tolist()

            #initialize a list used to collect track IDs and to add tracks
            sp_tracks = []
            j = 1 #playlist track counter
            counter = 0 #determines when to write tracks to playlist...inelegant, unpythonic, and should be fixed

            #for every track in the list pulled from the subreddit posts
            for i in plist:
                counter += 1 #once this is the length of the list, add songs to playlist

                #max out playlist length at 50 tracks
                if j > 50:
                    #Add tracks to playlist
                    spotifyObject.user_playlist_replace_tracks(user=user['id'], playlist_id=pl[1], tracks=sp_tracks)
                    break

                #if album flag is detected, find the most popular song on the album to add to playlist
                if '!album!' in i:
                    sp_tracks, j = plist_utils.album(i, jj, j, logger, sp_tracks, spotifyObject)
                else:
                    sp_tracks, j = plist_utils.track(i, j, logger, sp_tracks, no_worky, spotifyObject)

                #this is how the script knows to add the track when the list has been completely read
                if counter >= len(plist):
                    spotifyObject.user_playlist_replace_tracks(user=user['id'], playlist_id=pl[1], tracks=sp_tracks) #so old tracks are removed
        except:
            print('a system or network error was encountered')
            logger.write('a system or network error was encountered\n')
            retry_ids[str(pl[0])] = str(pl[1])
            #overcome max requests issue
            time.sleep(120)
            continue

    no_worky.close()
    dict_file.close()
    retry_file.write(json.dumps(retry_ids))
    retry_file.close()
    logger.close()
    
    
def modify_new(subreddit = 'subreddits.txt', playlists = 'playlist_ids.txt', spotifyObject, songs):

    track_id = []
    jj = 0 #album track indexer
    archive_ids = {}
    retry_ids = {}

    with open(subreddit, 'r') as subs:
        subreddits = subs.readlines()
    subs.close()
    subreddits = [element.strip() for element in subreddits]

    with open(playlists, 'r') as ids:
        playlist_ids = ids.readlines()
    ids.close()
    playlist_ids = [element.strip() for element in playlist_ids]

    pl_ids = list(zip(subreddits, playlist_ids))

    #logging
    log = paste([now.year], ['-'], [now.month], ['-'], [now.day], ['_spotify_log'], ['.txt'], sep='')
    log = ''.join(log)
    logger = io.open('./logs/' + log, 'w', newline = '', encoding="utf-8")

    #archiveids file
    archive_file = io.open('./archiveids.txt', 'w', newline = '', encoding="utf-8")

    #subs to retry
    retry_file = io.open('./' + 'retries.txt', 'w', newline = '', encoding="utf-8")
    
    #strings which didn't return songs
    no_worky = io.open('./no_worky.txt', 'w', newline = '', encoding="utf-8")

    for pl in pl_ids:
        try:
            print('\n\n\n\n\n' + pl[0] + '\n\n\n\n\n')
            logger.write('\n\n\n\n\n' + pl[0] + '\n\n\n\n\n')

            #creating an archive so the same followers can remain on one playlist and we can document the history of the playlist
            title = '-_- r/' + str(pl[0]) + ' ' + str(months[currentmonth]) + ' ' + str(currentyear)
            archive = spotifyObject.user_playlist_create(user['id'], title, public=True)
            #to_private.append(archive['id'])
            archive_ids[str(pl[0])] = archive['id']

            #add tracks from current playlist to archive
            p = 0
            track_refresh = []
            tracklist = spotifyObject.user_playlist_tracks(user['id'], playlist_id=pl[1], fields=None, limit=50, offset=0, market=None)
            for track in range(len(tracklist['items'])):
                pl_track = tracklist['items'][p]['track']['id']
                track_refresh.append(pl_track)
                p += 1
            spotifyObject.user_playlist_add_tracks(user=user['id'], playlist_id=archive['id'],tracks=track_refresh)

            #filter dataframe to target subreddit
            plist = songs.loc[songs['subreddit']==pl[0]]
            plist = plist['track'].tolist()

            #initialize a list used to collect track IDs and to add tracks
            sp_tracks = []
            j = 1 #playlist track counter
            counter = 0

            #for every track in the list pulled from the subreddit posts
            for i in plist:
                counter += 1 #once this is the length of the list, add songs to playlist

                #max out playlist length at 50 tracks
                if j > 50:
                    #Add tracks to playlist
                    spotifyObject.user_playlist_replace_tracks(user=user['id'], playlist_id=pl[1], tracks=sp_tracks)
                    break
                print(i)

                #if album flag is detected, find the most popular song on the album to add to playlist
                if '!album!' in i:
                    sp_tracks, j = plist_utils.album(i, jj, j, logger, sp_tracks, spotifyObject)
                else:
                    sp_tracks, j = plist_utils.track(i, j, logger, sp_tracks, no_worky, spotifyObject)

                #this is how the script knows to add the track when the list has been completely read
                if counter >= len(plist):
                    spotifyObject.user_playlist_replace_tracks(user=user['id'], playlist_id=pl[1], tracks=sp_tracks)
        except:
            print('a system or network error was encountered')
            logger.write('a system or network error was encountered\n')
            retry_ids[str(pl[0])] = str(pl[1])
            #overcome max requests issue
            time.sleep(120)
            continue


    archive_file.write(json.dumps(archive_ids))
    archive_file.close()
    retry_file.write(json.dumps(retry_ids))
    retry_file.close()
    no_worky.close()
    logger.close()
    
    

def create(currentmonth, currentyear, months, nsubreddit = 'new_subreddits.txt', subreddit = 'subreddits.txt', spotifyObject, songs):

    track_id = []
    jj = 0
    retry_ids = {}

    #Need to erase contents of this file (not delete it) at the end of this function
    with open(nsubreddit, 'r') as nsubs:
        nsubreddits = nsubs.readlines()
    nsubs.close()
    nsubreddits = [element.strip() for element in nsubreddits]

    #append new subreddit titles to existing file...because of this create must run AFTER modify
    with open(subreddit, 'a') as subs:
        for el in nsubreddits:
            subs.write("{}\n".format(el))
    subs.close()

    #logging
    log = paste([now.year], ['-'], [now.month], ['-'], [now.day], ['_spotify_log'], ['.txt'], sep='')
    log = ''.join(log)
    logger = io.open('./logs/' + log, 'a', newline = '', encoding="utf-8") #append to existing one
    to_log = '\n\n\n\n\n\n' + '-'*45 + 'Creating new playlists' + '-'*45 + '\n\n\n\n\n'
    logger.write(to_log)

    archive_file = io.open('./archiveids.txt', 'w', newline = '', encoding="utf-8")

    #subs to retry
    retry_file = io.open('./' + 'retries_new.txt', 'w', newline = '', encoding="utf-8")
    
    #strings which didn't return songs
    no_worky = io.open('./no_worky.txt', 'a', newline = '', encoding="utf-8")


    for sub in nsubreddits:
        try:
            print('\n\n\n\n\n' + sub + '\n\n\n\n\n')
            logger.write('\n\n\n\n\n' + sub + '\n\n\n\n\n')

            #creating an archive so the same followers can remain on one playlist and we can document the history of the playlist
            title = '-_- r/' + str(pl[0]) + ' ' + str(months[currentmonth]) + ' ' + str(currentyear)
            archive = spotifyObject.user_playlist_create(user['id'], title, public=True)
            archive_ids[str(sub)] = archive['id']

            #create a fresh playlist
            playlist = spotifyObject.user_playlist_create(user['id'], '-_- ' + 'r/' + sub, public=True)
            new_id = playlist['id']

            #write playlist ID to playlist IDs file
            with open("playlist_ids.txt", "a") as ids:
                ids.write("{}\n".format(new_id))
            ids.close()

            #filter dataframe to target subreddit
            plist = songs.loc[songs['subreddit']==sub]
            plist = plist['track'].tolist()

            #initialize a list used to collect track IDs and to add tracks
            sp_tracks = []
            j = 1 #playlist track counter
            counter = 0 #TODO: deprecate counter by using T:E or other strategy

            #for every track in the list pulled from the subreddit posts
            for i in plist:
                counter += 1 #this helps write to playlist when the length of reddit titles has been reached to prevent index error

                #max out playlist length at 50 tracks
                if j > 50:
                    #Add tracks to playlist
                    spotifyObject.user_playlist_add_tracks(user=user['id'], playlist_id=playlist['id'],tracks=sp_tracks)
                    break

                #if album flag is detected, find the most popular song on the album to add to playlist
                if '!album!' in i:
                    sp_tracks, j = plist_utils.album(i, jj, j, logger, sp_tracks, spotifyObject)
                else:
                    sp_tracks, j = plist_utils.track(i, j, logger, sp_tracks, no_worky, spotifyObject)

                #this is how the script knows to add the track when the list has been completely read
                if counter >= len(plist):
                    spotifyObject.user_playlist_add_tracks(user=user['id'], playlist_id=playlist['id'],tracks=sp_tracks)
        except:
            logger.write('a system or network error was encountered\n')
            retry_ids[str(sub)] = str(new_id)
            #overcome max requests issue
            time.sleep(120)
            continue

    archive_file.write(json.dumps(archive_ids))
    archive_file.close()
    retry_file.write(json.dumps(retry_ids))
    no_worky.close()
    retry_file.close()
    logger.close()