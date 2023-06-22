from django.test import TestCase, Client
from django.contrib.auth import authenticate, login
from ..models import User, SpotifyProfile
import json

# Create your tests here.
class BasicSetup():
    def setup(self):
        self.client = Client()

class UserLoggedInSetup():
    def setup(self):
        self.client = Client()
        User.objects.create_user(
            username='email',
            email='email',
            password='password'
        )
        self.client.login(username='email', password='password')

class SpotifyProfileSetup():
    def setup(self):
        self.client = Client()
        user = User.objects.create_user(
            username='email',
            email='email',
            password='password'
        )
        spotify_profile = SpotifyProfile.objects.create(user=user)
        spotify_profile.refresh_token = 'refresh_token'
        spotify_profile.save()
        self.client.login(username='email', password='password')
        
class IndexTestCase(TestCase, BasicSetup):
    def test_index_basic_response_and_template(self):
        self.setup()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'music_rec/index.html')

class HelpTestCase(TestCase, BasicSetup):
    def test_help_basic_response_and_template(self):
        self.setup()
        response = self.client.get('/help')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'music_rec/help.html')

class ErrorTestCase(TestCase, BasicSetup):
    def test_error_basic_response_and_template(self):
        self.setup()
        response = self.client.post('/error', {'error': 'test error'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/error')
        self.assertEqual(response.status_code, 300)

class SignupTestCase(TestCase, BasicSetup):
    def test_signup_basic_response_and_template(self):
        self.setup()
        response = self.client.get('/signup')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'music_rec/signup.html')

class SignupSuccessTestCase(TestCase, BasicSetup):    
    def test_signup_success_basic_response_and_template(self):
        self.setup()
        response = self.client.post('/signup_success', {'email': 'email', 'password': 'password', 'confirm_password': 'password'})
        self.assertEqual(response.status_code, 200)

class SpotifyLoginTestCase(TestCase, UserLoggedInSetup):
    def test_spotify_login_redirect(self):
        self.setup()
        response = self.client.get('/spotify_login')
        # look for 302 becuase this is django response for being redirected to external url
        self.assertEqual(response.status_code, 302)

class SpotifySuccessTestCase(TestCase, SpotifyProfileSetup):
    def test_spotify_success_basic_response_and_template(self):
        self.setup()
        response = self.client.get('/spotify_success', {'code': 'code'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'music_rec/spotify_success.html')

class GetAccessTokenTestCase(TestCase, SpotifyProfileSetup):
    def test_get_access_token_basic_response_and_template(self):
        self.setup()
        response = self.client.get('/get_access_token')
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'access': None})

class ExpiredAccessTokenTestCase(TestCase, SpotifyProfileSetup):
    def test_expired_access_token_basic_response_and_template(self):
        self.setup()
        response = self.client.get('/expired_access_token')
        self.assertEqual(response.status_code, 200)

class UserLoginTestCase(TestCase, BasicSetup): 
    def test_user_login_basic_response_and_template(self):
        self.setup()
        response = self.client.get('/user_login')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'music_rec/user_login.html')

class LoginHandlerTestCase(TestCase, UserLoggedInSetup):
    def test_login_handler_basic_response_and_template(self):
        self.setup()
        response = self.client.post('/login_handler', {'email': 'email', 'password': 'password'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'music_rec/login_success.html')

    def test_login_handler_incorrect_login(self):
        self.setup()
        response = self.client.post('/user_login', {'email': 'notemgdsgdsgdsail', 'password': 'notpasswogsgssgerd'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'music_rec/user_login.html')

class AccountTestCase(TestCase, SpotifyProfileSetup): 
    def test_account_basic_response_and_template(self):
        self.setup()
        response = self.client.get('/account')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'music_rec/account.html')

class UserLogoutTestCase(TestCase, BasicSetup):
    def test_user_logout_basic_response_and_template(self):
        self.setup()
        response = self.client.get('/user_logout')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'music_rec/index.html')

class SetupTestCase(TestCase, UserLoggedInSetup):
    def test_setup_basic_response_and_template(self):
        self.setup()
        response = self.client.get('/setup')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'music_rec/setup.html')

    def test_add_too_many_songs(self):
        self.setup()
        session = self.client.session 
        session['songs'] = ['item1', 'item2', 'item3', 'item4']
        session['songs_ids'] = ['item1', 'item2', 'item3', 'item4']
        session.save()

        response = self.client.post('/setup', {
            'csrfmiddlewaretoken': ['7KVhi12vhghr4Nw0ZHaC0gpAUGa6fzv4NuA3vQQTkdmJgxp2NglEyqmwyV4iGANj'],
            'Test & Recognise - Flume Re-work': ['24BYTj1tb5ovZcnIbtdTYD'],
            'TEST DRIVE': ['1DMEzmAoQIikcL52psptQL'],}, HTTP_REFERER='/songs')

        self.assertEqual(len(self.client.session['songs']), 5)
        self.assertEqual(len(self.client.session['songs_ids']), 5)
    
    def test_add_too_many_artists(self):
        self.setup()
        session = self.client.session 
        session['artists'] = ['item1', 'item2', 'item3', 'item4']
        session['artists_ids'] = ['item1', 'item2', 'item3', 'item4']
        session.save()

        response = self.client.post('/setup', {
            'csrfmiddlewaretoken': ['7KVhi12vhghr4Nw0ZHaC0gpAUGa6fzv4NuA3vQQTkdmJgxp2NglEyqmwyV4iGANj'],
            'Test & Recognise - Flume Re-work': ['24BYTj1tb5ovZcnIbtdTYD'],
            'TEST DRIVE': ['1DMEzmAoQIikcL52psptQL'],}, HTTP_REFERER='/artists')

        self.assertEqual(len(self.client.session['artists']), 5)
        self.assertEqual(len(self.client.session['artists_ids']), 5)
    
    def test_add_too_many_genres(self):
        self.setup()
        session = self.client.session 
        session['genres'] = ['item1', 'item2', 'item3', 'item4']
        session['genres_ids'] = ['item1', 'item2', 'item3', 'item4']
        session.save()

        response = self.client.post('/setup', {
            'csrfmiddlewaretoken': ['o4vJLdt10PVFrDTj0WzboHF1oIuTATMT4OavY2hp3M0XDnMlOvKdWRCX2Xo51U48'],
            'acoustic': ['acoustic'],
            'afrobeat': ['afrobeat'],}, HTTP_REFERER='/genres')

        self.assertEqual(len(self.client.session['genres']), 5)
        self.assertEqual(len(self.client.session['genres_ids']), 5)

class Clear(TestCase, BasicSetup):   
    def test_clear_basic_response_and_template(self):
        self.setup()
        response = self.client.get('/clear')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'music_rec/setup.html')

class SongsTestCase(TestCase, SpotifyProfileSetup):
    def test_songs_basic_response_and_template(self):
        self.setup()

        response = self.client.get('/songs')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'music_rec/songs.html')

class ArtistsTestCase(TestCase, SpotifyProfileSetup):
    def test_artists_basic_response_and_template(self):
        self.setup()

        response = self.client.get('/artists')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'music_rec/artists.html')
    
class GenresTestCase(TestCase, SpotifyProfileSetup):
    def test_genres_basic_response_and_template(self):
        self.setup()

        response = self.client.get('/genres')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'music_rec/genres.html')

class ParametersTestCase(TestCase, BasicSetup):    
    def test_parameters_basic_response_and_template(self):
        self.setup()
        response = self.client.get('/parameters')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'music_rec/parameters.html')

class SubmitTestCase(TestCase, UserLoggedInSetup):
    def test_submit_basic_response_and_template(self):
        self.setup()
        
        response = self.client.get('/submit')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'music_rec/error.html')

class Playlist(TestCase, SpotifyProfileSetup):
    def test_playlist_basic_response_and_template(self):
        self.setup()
        
        response = self.client.get('/playlist')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'music_rec/playlist.html')