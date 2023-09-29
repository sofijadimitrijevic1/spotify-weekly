import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect, render_template
import time

app = Flask(__name__)
app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'
app.secret_key = 'ewhruyrenjrh324()#*%&*('
TOKEN_INFO = 'token_info'

@app.route('/login')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/index')
def index():
    return "Welcome to the index page"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/redirect')
def redirect_page():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('save_discover_weekly', external=True))

@app.route('/saveDiscoverWeekly')
def save_discover_weekly():
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect('/login')
    

    sp = spotipy.Spotify(auth = token_info['access_token'])
    user_id = sp.current_user()['id']

    saved_weekly_playlist_id = None
    discover_weekly_playlist_id = None
    

    current_playlists = sp.current_user_playlists()['items']
    for playlist in current_playlists:
        if(playlist['name'] == 'Discover Weekly' ):
            discover_weekly_playlist_id = playlist['id']
        if(playlist['name'] == 'Saved Weekly' ):
            saved_weekly_playlist_id = playlist['id']
    
    if not discover_weekly_playlist_id:
        new_playlist = sp.user_playlist_create(user_id, 'Discover Weekly', True)
        discover_weekly_playlist_id = new_playlist['id']
    
    if not saved_weekly_playlist_id:
        new_playlist = sp.user_playlist_create(user_id, 'Saved Weekly', True)
        saved_weekly_playlist_id = new_playlist['id']
    
    discover_weekly_playlist = sp.playlist_items(discover_weekly_playlist_id)
    song_uris = []
    for song in discover_weekly_playlist['items']:
        song_uri = song['track']['uri']
        song_uris.append(song_uri)
       
    sp.user_playlist_add_tracks(user_id, saved_weekly_playlist_id, song_uris, None )
    return "Discover Weekly saved successfully"


def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        return redirect(url_for('login', external = False))

    now = int(time.time())

    is_expired = token_info['expires_at'] - now < 60
    if (is_expired):
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])

    return token_info



def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = "515fea9d19a6494da6199a4ddd570116",
        client_secret = "2ede4e5ebfd44488bf3f4ed2a17b9932",
        redirect_uri = url_for(('redirect_page'), _external = True),
        scope = 'user-library-read playlist-read-private playlist-modify-public playlist-modify-private'
        )

app.run(debug=True)