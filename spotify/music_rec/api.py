import base64
import requests
import json
import urllib.parse
import random
import string

# TODO this is not how we are going to do things in production
with open('secrets.json', 'r') as s:
    secret = json.load(s)
    CLIENT_ID = secret['client_id']
    CLIENT_SECRET = secret['client_secret']
    
SEARCH_LIMIT = 10

class get_refresh_token():
    auth_url = None
    url = 'https://accounts.spotify.com/authorize'

    def __init__(self):
        #state_token = self.generate_state_token()
        self.auth_url = urllib.parse.urlencode({
            'client_id': CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': 'http://localhost:8000/spotify_success',
            'scope': 'user-read-private, playlist-modify-public',
            #'state': state_token
            })
        self.create_auth_url()
    
    def generate_state_token(length=16):
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for i in range(length))
    
    def create_auth_url(self):
        self.auth_url = f"{self.url}?{self.auth_url}"

class get_access_token():
    client_id = CLIENT_ID
    client_secret = CLIENT_SECRET
    url = 'https://accounts.spotify.com/api/token'
    access_token = ''

    def __init__(self, refresh_token):
        self.refresh_token = refresh_token
        self.get_access_token()
            
    def b64_encode(self):
        return base64.b64encode(f'{self.client_id}:{self.client_secret}'.encode()).decode()
    
    def body_parameter(self):
        return {'grant_type': 'authorization_code', 'code': self.refresh_token, 'redirect_uri': 'http://localhost:8000/spotify_success'}

    def header(self):
        return {'Authorization': f'Basic {self.b64_encode()}', 'Content-Type': 'application/x-www-form-urlencoded'}

    def get_access_token(self):
        try:
            r = requests.post(self.url, headers=self.header(), data=self.body_parameter())
            self.access_token = r.json()['access_token']
            self.refresh_token = r.json()['refresh_token']
        #FIXME fix all exceptions
        except Exception:   
            print(f'unable to get access token {r.json()}')

class expired_access_token():
    client_id = CLIENT_ID
    client_secret = CLIENT_SECRET
    url = 'https://accounts.spotify.com/api/token'
    access_token = ''

    def __init__(self, refresh_token):
        self.refresh_token = refresh_token
        self.get_access_token()
            
    def b64_encode(self):
        return base64.b64encode(f'{self.client_id}:{self.client_secret}'.encode()).decode()
    
    def body_parameter(self):
        return {'grant_type': 'refresh_token', 'refresh_token': self.refresh_token}

    def header(self):
        return {'Authorization': f'Basic {self.b64_encode()}', 'Content-Type': 'application/x-www-form-urlencoded'}

    def get_access_token(self):
        try:
            r = requests.post(self.url, headers=self.header(), data=self.body_parameter())
            self.access_token = r.json()['access_token']
        #FIXME fix all exceptions
        except Exception:   
            print(f'unable to get access token {r.json()}')

class get_userid():
    url = "https://api.spotify.com/v1/me"
    userid = ''

    def __init__(self, access_token):
        self.access_token = access_token
        try:
            r = requests.get(self.url, headers=self.header())
            self.userid = r.json()['id']
        except Exception as e:
            print(e)
            print('unable to get userid')

    def header(self):
        return {'Authorization': f'Bearer {self.access_token}'}


class get_recommendations():
    url="https://api.spotify.com/v1/recommendations"
    data=[]

    def __init__(self, access_token,songs,artists,genres,parameters):
        #BUG: Cannot allow to run with just Genre
        self.access_token = access_token
        self.limit = 20
        self.artists=artists
        self.genres=genres
        self.songs=songs
        self.parameters=parameters

        try:
            raw_search = requests.get(self.url, headers=self.header(), params=self.query_params()).json()
            self.data = raw_search
        except Exception:
            print('error in api.py get_recommendations get request')
            
    def header(self):
        return {'Authorization': f'Bearer {self.access_token}'}

    def query_params(self):
        dict = {'limit': self.limit, 'seed_artists': self.artists, 'seed_genres': self.genres, 'seed_tracks': self.songs}
        dict.update(self.parameters)
        return dict

#create playlist with songs
class create_playlist():
    url=""
    data=[]

    def __init__(self,access_token,account,playlist_name,uris):
        self.access_token = access_token
        self.uris=uris
        self.url_playlist="https://api.spotify.com/v1/users/"+account+"/playlists"
        self.playlist_name = {"name": playlist_name, "description":"Generated using Spotify's Reccomendation Algorithm"}

        try:
          data = requests.post(self.url_playlist, headers=self.header(), json=self.playlist_name)
          self.data = json.loads(data.text)
          self.playlist=self.data["id"]
          self.url_songs="https://api.spotify.com/v1/playlists/"+self.playlist+"/tracks"
          self.uris = {"uris":self.uris,"position":0}
          data = requests.post(self.url_songs, headers=self.header(), json=self.uris)
          self.data = data.text
        except Exception as e:
          print(e)
          print('error in api.py create_playlist')

    def header(self):
        return {'Authorization': f'Bearer {self.access_token}'}