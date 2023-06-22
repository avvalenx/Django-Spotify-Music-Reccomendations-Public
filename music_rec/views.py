from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import SpotifyProfile
from music_rec import api
import json
import logging
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
import requests

logger = logging.getLogger(__name__)

with open('secrets.json', 'r') as s:
    secret = json.load(s)
    CLIENT_ID = secret['client_id']
    CLIENT_SECRET = secret['client_secret']

# home page
def index(request):
    if str(request.user) != 'AnonymousUser':
        context = {'user': 'logged in as ' + str(request.user)}
    else:
        context = {'user': 'No User Logged in'} 
    return render(request, 'music_rec/index.html', context)

# help page with instructions
def help(request):
    return render(request, 'music_rec/help.html')

def error(request):
    if request.POST:
        logger.warning(request.POST['error'])
        response = HttpResponse()
        return response
    else:
        logger.warning('did not send a post request to error')
        response = HttpResponse()
        response.status_code = 300
        return response

#signup for an account and link your spotify account
def signup(request):
    return render(request, 'music_rec/signup.html')

# handler for linking spotify account and storing credentials in db
def signup_success(request):
    if request.POST:
        # Create an instance of EmailValidator
        email_validator = EmailValidator()

        try:
            # Call the __call__ method of EmailValidator to validate the email
            email_validator(request.POST['email'])
        except ValidationError:
            return render(request, 'music_rec/signup.html', {'error':'Enter a valid email address.'})
        # ensure password is at least 8 characters
        if len(request.POST['password']) < 8:
            return render(request, 'music_rec/signup.html', {'error': 'Enter a password with at least 8 characters.'})
        # ensure passwords match
        elif request.POST['password'] != request.POST['confirm_password']:
            return render(request, 'music_rec/signup.html', {'error': 'Enter matching passwords.'})
        # if all conditions are met create a new user with the credentials
        else:
            user = User.objects.create_user(username=request.POST['email'],
                                            email=request.POST['email'],
                                            password=request.POST['password'])
            user.save()
            # associate the newly created profile with the spotify profile object in a 1 to 1 relationship
            SpotifyProfile.objects.create(user=user)
            login(request, user)
            auth_url = api.get_refresh_token()
            return HttpResponseRedirect(auth_url.auth_url)

@login_required(login_url='/user_login')
def spotify_login(request):
    auth_url = api.get_refresh_token()
    return HttpResponseRedirect(auth_url.auth_url)

# page that is displayed after successfully logging in
@login_required(login_url='/user_login')
def spotify_success(request):
    # get the spotify profile of current logged in user
    spotify_profile = SpotifyProfile.objects.get(user=request.user)

    # sets refresh and access token to spotify profile model
    tokens = api.get_access_token(request.GET['code'])
    spotify_profile.access_token = tokens.access_token
    spotify_profile.refresh_token = tokens.refresh_token

    # get the userid of the user and associate it to the spotify profile model
    spotify_profile.userid = api.get_userid(spotify_profile.access_token).userid
    spotify_profile.save()

    return render(request, 'music_rec/spotify_success.html')

# get the access token from the database for a logged in user
@login_required(login_url='/user_login')
def get_access_token(request):
    return JsonResponse({'access': SpotifyProfile.objects.get(user=request.user).access_token})

# get a new access token if it is expired
@login_required(login_url='/user_login')
def expired_access_token(request):
    spotify_profile = SpotifyProfile.objects.get(user=request.user)
    spotify_profile.access_token = api.expired_access_token(spotify_profile.refresh_token).access_token
    spotify_profile.save()
    return JsonResponse({'success': 'success'})

# page to log into an existing user's account
def user_login(request):
    return render(request, 'music_rec/user_login.html')

# handle log in of an existing user
# TODO do not yet have a password reset
def login_handler(request):
    if request.POST:
        user = authenticate(username=request.POST['email'], password=request.POST['password'])
    if user is not None:
        login(request, user)
        return render(request, 'music_rec/login_success.html')
    else:
        return render(request, 'music_rec/user_login.html', {'error': 'Enter a valid login'})

# manage account and connect spotify account
@login_required(login_url='/user_login')
def account(request):
    try:
        if SpotifyProfile.objects.get(user=request.user).userid != None:
            spotify_account = SpotifyProfile.objects.get(user=request.user).userid
            need_to_connect_spotify = False
        else:
            spotify_account = 'No Spotify Account Connected'
            need_to_connect_spotify = True
    except Exception:
        SpotifyProfile.objects.create(user=request.user)
        spotify_account = 'No Spotify Account Connected'
        need_to_connect_spotify = True
    context = {'username': request.user, 'spotify': spotify_account, 'need_to_connect_spotify': need_to_connect_spotify}
    return render(request, 'music_rec/account.html', context)

# log out a logged in user
def user_logout(request):
    logout(request)
    return render(request, 'music_rec/index.html')

# main page to see what items have been added to each list
@login_required(login_url='/user_login')
def setup(request):
    # session variables store song artsit and genres selection information
    if 'songs' not in request.session:
        request.session['songs'] = []
    if 'artists' not in request.session:
        request.session['artists'] = []
    if 'genres' not in request.session:
        request.session['genres'] = []
    if 'songs_ids' not in request.session:
        request.session['songs_ids'] = []
    if 'artists_ids' not in request.session:
        request.session['artists_ids'] = []
    if 'genres_ids' not in request.session:
        request.session['genres_ids'] = []

    if request.POST:
        data = request.POST.copy()

        # collect data from form and add it to appropriate session variables for items
        for item in data:
            if request.META.get('HTTP_REFERER').endswith(reverse('music_rec:songs')) and item != 'csrfmiddlewaretoken' and len(request.session['songs']) < 5:
                request.session['songs'] = request.session['songs'] + [item]
                request.session['songs_ids'] = request.session['songs_ids'] + [data[item]]
            
            elif request.META.get('HTTP_REFERER').endswith(reverse('music_rec:artists')) and item != 'csrfmiddlewaretoken' and len(request.session['artists']) < 5:
                request.session['artists'] = request.session['artists'] + [item]
                request.session['artists_ids'] = request.session['artists_ids'] + [data[item]]
            
            elif request.META.get('HTTP_REFERER').endswith(reverse('music_rec:genres')) and item != 'csrfmiddlewaretoken' and len(request.session['genres']) < 5:
                request.session['genres'] = request.session['genres'] + [item]
                request.session['genres_ids'] = request.session['genres_ids'] + [data[item]]
    
    context = {'songs': request.session['songs'],
               'genres': request.session['genres'],
               'artists': request.session['artists']}
    return render(request, 'music_rec/setup.html', context)

# clear all songs artists and genres from session variables
def clear(request):
    try:
        request.session['songs'] = []
        request.session['artists'] = []
        request.session['genres'] = []
        request.session['songs_ids'] = []
        request.session['artists_ids'] = []
        request.session['genres_ids'] = []
    except Exception as e:
        logger.warning(e)
    
    return render(request, 'music_rec/setup.html')

# method that checks a user has a refresh token
def spotify_account_check(user):
    return SpotifyProfile.objects.get(user=user).refresh_token != None

# search for songs
@user_passes_test(spotify_account_check, login_url='/spotify_login')
def songs(request):
    return render(request, 'music_rec/songs.html')

# search for artists
@user_passes_test(spotify_account_check, login_url='/spotify_login')
def artists(request):
    return render(request, 'music_rec/artists.html')

# search for genres
@user_passes_test(spotify_account_check, login_url='/spotify_login')
def genres(request):
    return render(request, 'music_rec/genres.html')

# enter extra parameters if wanted for recommendations algorithm
def parameters(request):
    context = {}
    return render(request, 'music_rec/parameters.html', context)

# view songs returned and name playlist
@login_required(login_url='/user_login')
def submit(request):
    parameters={}

    # collect form data
    if request.POST:
        data = request.POST.copy()
        del data['csrfmiddlewaretoken']
        for key,value in data.items():
            parameters[key]=float(value)
            if key=="target_popularity":
                parameters[key]=int(value)
    try:
        payload=[]
        uris=[]
        # make api call to get songs from recommendation algorithm
        recommendations = api.get_recommendations(SpotifyProfile.objects.get(user=request.user).access_token,
                                                request.session['songs_ids'],
                                                request.session['artists_ids'],
                                                request.session['genres_ids'],
                                                parameters).data

        # append them to the payload variable to display on page
        for item in recommendations['tracks']:
            payload.append([item['artists'][0]['name'], item['name']])
            uris.append(item['uri'])
        request.session['uris'] = uris
        context = {'recommendations': payload, 'uris': uris}
        return render(request, 'music_rec/submit.html', context)
    except Exception as e:
        logger.warning(e)
        return render(request, 'music_rec/error.html', {'error': 'An Error occured'})
        
# create the playlist
@login_required(login_url='/user_login')
def playlist(request):
    try:
        # use the playlist name entered or if there is not a name auto name the playlist
        if request.POST:
            data = request.POST.copy()
            playlist_name = data['playlist']
        else:
            playlist_name = 'Spotify Music Recommendations Playlist'

        # get Spotify userid and make playlist creation api call
        spotify_profile = SpotifyProfile.objects.get(user=request.user)
        response = api.create_playlist(spotify_profile.access_token,
                                       spotify_profile.userid,playlist_name,
                                       request.session['uris'])
        if 'error' in response.data:
            if response.data['error']['status'] == 401:
                expired_access_token(request)
                response = api.create_playlist(spotify_profile.access_token,
                                               spotify_profile.userid,
                                               playlist_name,
                                               request.session['uris'])
        if 'snapshot_id' in response.data:
            context = {'response': 'Playlist created successfully!'}
        else:
            context = {'response': 'Error creating playlist'}
        return render(request, 'music_rec/playlist.html', context)
    except Exception as e:
        logger.warning(e)
        return render(request, 'music_rec/playlist.html', {'response': 'Error creating playlist'})