'''
------------------------------------------------------------------------------------------
This file contains playlist building functions
------------------------------------------------------------------------------------------
'''
import playlistbuilder as plb
import pprint
import sys
import subprocess
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

def spotify_token(spusername, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope):
    if scope == 'public':
        try:
            token = util.prompt_for_user_token(spusername, scope='playlist-modify-public', client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI)
        except:
            os.remove(f".cache-{username}")
            token = util.prompt_for_user_token(spusername, scope='playlist-modify-public', client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI)

        spotifyObject = spotipy.Spotify(auth=token)

        user = spotifyObject.current_user()

        props = json.dumps(user, sort_keys=True, indent=4) #TODO: Write to log
    elif scope == 'private':
        try:
            token = util.prompt_for_user_token(spusername, scope='playlist-modify-private', client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI)
        except:
            os.remove(f".cache-{username}")
            token = util.prompt_for_user_token(spusername, scope='playlist-modify-private', client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI)

        spotifyObject = spotipy.Spotify(auth=token)

        user = spotifyObject.current_user()

        props = json.dumps(user, sort_keys=True, indent=4) #TODO: Write to log
    else:
        print('scope must be either "private" or "public"') #TODO: Write to log
        spotifyObject = None
    
    return spotifyObject



def spotify_login():
    from smileconfig import *

    spusername = spusername
    SPOTIPY_CLIENT_ID=SPOTIPY_CLIENT_ID
    SPOTIPY_CLIENT_SECRET=SPOTIPY_CLIENT_SECRET
    SPOTIPY_REDIRECT_URI=SPOTIPY_REDIRECT_URI

    spotifyObject = spotify_token(spusername, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, 'public')
    privateObject = spotify_token(spusername, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, 'private')
    
    return (spotifyObject, privateObject)



def album(jawn, track_counter, playlist_counter, logger, sp_tracks, spotifyObject):
    lp = re.sub("\[?\!album!\]?", "", jawn)
    album = spotifyObject.search(q=lp, limit=1, type='album') #obtain album object
    try:
        album_id = album['albums']['items'][0]['id'] #used to search album tracks
        tracklist = spotifyObject.album_tracks(album_id) #obtain track list object
        for track in range(len(tracklist['items'])):
            album_track_id = tracklist['items'][jj]['id']
            track_id.append(album_track_id)
            track_counter += 1
        track_counter = 0 #reset so that this can be re-used for track popularity
        track_id = track_id[:49] #if track_id has over 50 ID's, Spotify Exception: "too many ids requested" occurs...should put in T:E
        my_tracks = spotifyObject.tracks(track_id) #obtain track objects for popularity key
        popularity = {i:0 for i in track_id} #dictionary key is track id and value is popularity
        for titles in range(len(my_tracks['tracks'])):
            track_pop = my_tracks['tracks'][track_counter]['popularity']
            popularity[track_id[track_counter]] = track_pop
            track_counter += 1
        track_counter = 0

        #TODO: sort dictionary by value and if most popular is on there, going down the dict
        popular_track = max(popularity, key=popularity.get) #most popular song on album
        a = spotifyObject.track(popular_track)
        track_id = [] #reset for next album import
        if a['id'] in sp_tracks: #does not return exception, so using conditional if nothing found
            playlist_counter = playlist_counter
        else:
            sp_tracks.append(a['id'])
            playlist_counter += 1
        print("list has {0} songs".format(len(sp_tracks)))
        logger.write("list has {0} songs\n".format(len(sp_tracks)))
        print(sp_tracks)
        for item in sp_tracks:
            logger.write(item + '\n')
    except:
        pass
    
    return (sp_tracks, playlist_counter)



def track(jawn, playlist_counter, sp_tracks, logger, not_found_log, spotifyObject):
    a = spotifyObject.search(q=jawn, limit=1, type='track')

    #if the track is not found, the list will be empty
    if a['tracks']['items']!=[]:
        if a['tracks']['items'][0]['id'] in sp_tracks: #does not return exception, so using conditional if nothing found
            playlist_counter = playlist_counter
        else:
            sp_tracks.append(a['tracks']['items'][0]['id'])
            playlist_counter += 1
            logger.write("list has {0} songs\n".format(len(sp_tracks)))
            for item in sp_tracks:
                logger.write(item + '\n')
    else:
        no_worky.write(jawn + '\n')
        playlist_counter = playlist_counter
        
    return (sp_tracks, playlist_counter)


#retry type of create, modify, or modify_new
def retry(retry_type, spotifyObject):
    import ast
    
    if retry_type == 'create':
        #open retry new file
        with open('retries_new.txt', 'r') as retry_file:
            resub = retry_file.readlines()
        retry_file.close()
        resub = [element.strip() for element in resub] #replace this with ast logic in modify playlist function
        
        plb.create(plb.currentmonth, plb.currentyear, plb.months, nsubreddit = 'retries_new.txt', subreddit = 'subreddits.txt', spotifyObject)
        
        #run create with nsubreddit parameter set to retry file (must manually remove playlist ID and failed subreddit from those files for now...programatically can adjust to remove the line with designated "retry" key from one file and line with "retry" value from the other
    elif retry_type == 'modify':
        #open retry file
        with open('retries.txt', 'r') as retry_file:
            resub = retry_file.readlines()
        retry_file.close()
        resub = [element.strip() for element in resub]
        #run modify
    elif retry_type == 'modify_new':
        #open retry file
        with open('retries.txt', 'r') as retry_file:
            resub = retry_file.readlines()
        retry_file.close()
        resub = [element.strip() for element in resub]
        #run modify_new
    else:
        print('retry_type must be one of : "create" "modify" or "modify_new"')