#!/usr/bin/python3

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, url_for, session, request, redirect, render_template
import json
import time
import pandas as pd
import time

from spotify import *
import tokens
from tokens import spotify_user_id, refresh_token, access_token

scope = "&scope=playlist-modify-private%20playlist-modify-public"

header = ""

# App config
app = Flask(__name__)

app.secret_key = 'jldkfhueo437289'
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'


@app.route('/')
def home():
    return (render_template('homepage.html'))




@app.route('/main')
def main():
    return (render_template('main.html'))


@app.route("/success", methods=['post'])
def sucessful():
    username = request.form['Username']
    artistList = request.form['ArtistList']
    user_id = request.form['User_id']
    print(username)
    print(artistList)
    print(user_id)

    var_username = "spotify_user_id = " + "'" + username + "'\n"
    replace_line('tokens.py', 0, var_username)

    file = open("temp.txt", "w")
    file1 = open("username.txt", "w")
    #after done handling in spotify.py  remove all in file
    file1.write(user_id)

    file.write(artistList)


    file1.close()
    file.close()

    return redirect("/thanks")


@app.route('/thanks')
def thanks():


    return (render_template('thanks.html'))



@app.route('/login')
def login():
    sp_oauth = create_spotify_oauth()

    auth_url = sp_oauth.get_authorize_url()
    print(auth_url)

    new_auth_url = auth_url[0:-24]
    new_auth_url = new_auth_url + scope

    print(new_auth_url)

    return redirect(new_auth_url)


@app.route('/authorize')
def authorize():
    sp_oauth = create_spotify_oauth()

    session.clear()
    code = request.args.get('code')

    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info

    access_token = token_info['access_token']
    refresh_token = token_info['refresh_token']

    var_refresh_token = "refresh_token = " + "'" + refresh_token + "'\n"

    var_access_token = "access_token = " + "'" + access_token + "'\n"

    replace_line('tokens.py', 1, var_refresh_token)
    # replace_line('tokens.py', 2, var_access_token)

    return redirect("/main")


@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)

    return redirect('/')


# Checks to see if token is valid and gets a new token if not
def get_token():
    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    # Refreshing token if it has expired
    if (is_token_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid


def replace_line(file_name, line_num, text):
    lines = open(file_name, 'r').readlines()
    lines[line_num] = text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id="231549513d0f4adaaeca7aa9f4d313b8",
        client_secret="2aff9d0a365c49058bf2206c7ef3cabb",
        redirect_uri=url_for('authorize', _external=True),
        scope="user-library-read")
