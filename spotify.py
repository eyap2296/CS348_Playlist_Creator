import sqlite3
from bs4 import BeautifulSoup
import requests
import json
from datetime import date
from tokens import spotify_user_id, refresh_token, access_token


# Variables
song_counter = 0
header = ""
song_array = []
artist_array = []
wanted_artists = ["Lil Uzi Vert", "Travis Scott", "Jack Harlow", "Kendrick Lamar", "Logic", "Lil Tjay", "Drake", "Lil Tecca", "Pop Smoke",
                    "Juice Wrld", "Lil Baby", "LIL NAS X", "Post Malone", "CHRIS BROWN", "ED SHEERAN"]
wanted_artist_array = []
wanted_song_array = []
song_info = {}


# Constructor
def __init__(self):
    self.spotify_user_id = spotify_user_id
    self.access_token = access_token
    self.refresh_token = refresh_token
    self.spotify_token = ""


# Returns the Header Used in the Spotify API
def get_header():
    header = {"Content-Type": "application/json", "Authorization": "Bearer {}".format(spotify_token)}
    return header


# Creates a Playlist on Spotify
# Returns the Playlist ID
def create_playlist():

    date_today = date.today().strftime("%m/%d/%Y")

    if (date_today[0] == '0'):
        date_today = date_today[1:]

    request_body = json.dumps({ "name": "Tops Songs From " + date_today, "description": "Tops Songs from Rolling Loud", "public": False })
    
    queryString = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id)
    
    response = requests.post(queryString, data = request_body, headers = get_header())
    
    response_json = response.json()

    return response_json["id"]

   
# Gets the Spotify ID For Each Song Given the Song Name & Artist
def get_song_id(song_name, artist):
    
    queryString = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=20".format(song_name, artist)

    response = requests.get(queryString, headers = get_header())

    response_json = response.json()

    songs = response_json["tracks"]["items"]

    song_uri = songs[0]["uri"]

    return song_uri


# Adds Songs to the Created Playlist
def add_songs_to_playlist():

    all_song_uri = [information["Spotify URI"] for song, information in song_info.items()]

    playlist_id = create_playlist()

    request_data = json.dumps(all_song_uri)
   
    queryString = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlist_id)

    response = requests.post(queryString, data = request_data, headers = get_header())

    response_json = response.json()

    return response_json


# Returns a new Spotify Access Token
def refresh():

    query = "https://accounts.spotify.com/api/token"

    response = requests.post(query, data = {"grant_type": "refresh_token", "refresh_token": refresh_token}, headers = {"Authorization": "Basic " + access_token})

    response_json = response.json()

    return response_json["access_token"]



# Database Logic
conn = sqlite3.connect('songs.db')
c = conn.cursor()

#c.execute("""CREATE TABLE spotify_user (
#            user_id INTEGER,
#            account_name VARCHAR(30),
#            refresh_token INTEGER,
#            likes VARCHAR(30)
#            )""")

#c.execute("""CREATE TABLE weekly_top_songs (
#            song_name VARCHAR(30),
#            artist_name VARCHAR(30),
#            genre VARCHAR(30),
#            length VARCHAR(30),
#            ranking INTEGER
#            )""")

#c.execute("""CREATE TABLE song (
#            name VARCHAR(30),
#            main_artist VARCHAR(30),
#            length VARCHAR(10),
#            genre VARCHAR(10)
#            )""")

#c.execute("""CREATE TABLE artist (
#            name VARCHAR(30)
#            )""")

#c.execute("""CREATE TABLE ranking (
#            song_ranking INTEGER,
#            song_name VARCHAR(30),
#            artist_name VARCHAR(30)
#            )""")


# Main Logic
# Scrapes Rolling Stones to get the top songs of the week
url = 'https://www.officialcharts.com/charts/singles-chart//'

spotify_token = refresh()
        
try:
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'lxml')

    top_song = soup.find_all('div', class_= 'title-artist')
    main_artist = soup.find_all('div', class_ = 'artist')

except:
    print("Unable to Parse HTML")
    raise


for song in top_song:
    song_array.append(song.a.text.strip())

for artist in main_artist:

    first_artist = "" 

    if artist.a.text.strip().find(',') != -1:
        index = artist.a.text.strip().index(",")
        first_artist = artist.a.text.strip()[:index]
        artist_array.append(first_artist)

    elif artist.a.text.strip().find("feat") != -1:
        index = artist.a.text.strip().index("feat")
        first_artist = artist.a.text.strip()[:index - 1]
        artist_array.append(first_artist)
    else:
        artist_array.append(artist.a.text.strip())


for each_artist in artist_array:

    if each_artist in wanted_artists:

        song_counter += 1
        
        index = artist_array.index(each_artist)
        wanted_artist_array.append(artist_array[index])
        wanted_song_array.append(song_array[index])


for song in wanted_song_array:
    for artist in wanted_artist_array:

        song_info[song] = {
        "Song Name": song,
        "Artist": artist,
        "Spotify URI": get_song_id(song, artist)
        }

        c.executemany("INSERT INTO artist(name) VALUES(?)", artist)
        conn.commit()

        wanted_artist_array.remove(artist)
        break


add_songs_to_playlist()


if song_counter == 0:
    print("None of your requested artists had songs in the top songs of the week!")
else:
    print("Successfully Added Songs to Playlist")

c.execute("SELECT * FROM artist")

result = c.fetchall()

for row in result:
    print(row[0])


conn.commit()
conn.close()