from urllib.request import urlopen
import json
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

# wait times

wait_not_playing = 30
wait_playing = 60
wait_song_change = 30

# dev wait times

#wait_not_playing = 10
#wait_playing = 20
#wait_song_change = 10

# external env

ip_player = os.environ.get('IP_PLAYER')
ip_and_port_maloja = os.environ.get('IP_AND_PORT_MALOJA')
api_key = os.environ.get('API_KEY')
verbose = os.environ.get('VERBOSE')

# Build player and maloja url

url_player = "http://" + ip_player + ":81/api/player/status"

url_maloja = "http://" + ip_and_port_maloja + "/apis/mlj_1/newscrobble"


# Save Respone
def load_json():
    # Load json from player
    global player_json
    response = urlopen(url_player)
    player_json = json.loads(response.read())
    type(player_json)

def current_song():
    # get the current song
    load_json()
    x = player_json["players"][1]["title"]
    return x

def playing_status():
    # get the playing status from the player
    load_json()
    state = player_json["players"][1]["state"]
    return state

def current_artists():
    # get the playing status from the player
    load_json()
    artist_string = player_json["players"][1]["artist"]
    return artist_string

def maloja_json():
    # Build the json object for transmitting to maloja
    load_json()

    # Save relevant data in Var
    title = player_json["players"][1]["title"]
    artist_string = player_json["players"][1]["artist"]

    # Artists to List object, maloja want the artist as seperate strings
    artist_list = artist_string.split(",")

    # Build json object
    data = {}
    data["artists"] = artist_list
    data["title"] = title
    data["key"] = api_key
    maloja_json = json.dumps(data)
    return maloja_json

print("Start programm...")

while True:

    # If Status of the Player is "playing" looping this loop.
    if playing_status() == "playing":
        # Important because, when the Player starts, the playing status changed, but the song information not.
        intermediate_titel = current_song()
        while intermediate_titel == current_song():
            print("No song change yet, wait....")
            while intermediate_titel == current_song():
                time.sleep(wait_song_change)
                # Exit while loop, when the song stops playing
                if verbose == "yes":
                    print("Is in loop: No song change yet, wait....")
            if playing_status() !=  "playing":
                print("Song paused")
                break
        else:
            print("Song is playing, wait if the song is running long enough, for",wait_playing,"seconds")
            # Save current song name, to check later, if the songs changed. If not skip
            intermediate_titel = current_song()
            time.sleep(wait_playing)

            # Load json from Player again to check if title has changed
            if intermediate_titel == current_song():
                r = requests.post(url_maloja, data=maloja_json(), headers={'Content-type': 'application/json', 'Accept': 'text/plain'})
                if verbose == "yes":
                    print(r.text)
                print("Was scrobbled!:", intermediate_titel, "-", current_artists())
            else:
                print("Title was skipped:", intermediate_titel, "=/=", current_song())

#    elif playing_status() == "paused":
#        print("Paused")
#        time.sleep(wait_not_playing)

    else:
        print("Paused or not yet started")
        while playing_status() != "playing":
            if verbose == "yes":
                print("Is in loop: Paused or not yet started")
            time.sleep(wait_not_playing)