from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import SpotifyProfile
from music_rec import api
from .forms import Recommendations
import json

with open('secrets.json', 'r') as s:
    secret = json.load(s)
    CLIENT_ID = secret['client_id']
    CLIENT_SECRET = secret['client_secret']

def index(request):
    return render(request, 'music_rec/index.html')

#signup for an account and link your spotify account
def signup(request):
    return render(request, 'music_rec/signup.html')

def signup_success(request):
    if request.POST:
        if request.POST['password'] == request.POST['confirm_password']:
            user = User.objects.create_user(username=request.POST['email'], email=request.POST['email'], password=request.POST['password'])
            user.save()
            # associate the newly created profile with the spotify profile object in a 1 to 1 relationship
            SpotifyProfile.objects.create(user=user)
            login(request, user)
            auth_url = api.get_refresh_token()
            return HttpResponseRedirect(auth_url.auth_url)
        else:
            return render(request, 'music_rec/signup.html', {'error': 'please ensure passwords match'})

# log into your spotify account to get refresh token
@login_required(login_url='/user_login')
def spotify_login(request):
    # generate the url for signing into spotify account
    auth_url = api.get_refresh_token()
    
    return HttpResponseRedirect(auth_url.auth_url)

# page that is displayed after successfully logging in
# we do not yet have a login failed page in case of errors
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

@login_required(login_url='/user_login')
def get_access_token(request):
    return JsonResponse({'access': SpotifyProfile.objects.get(user=request.user).access_token})

@login_required(login_url='/user_login')
def expired_access_token(request):
    spotify_profile = SpotifyProfile.objects.get(user=request.user)
    spotify_profile.access_token = api.expired_access_token(spotify_profile.refresh_token).access_token
    spotify_profile.save()
    return JsonResponse({'success': 'success'})

def user_login(request):
    return render(request, 'music_rec/user_login.html')

def login_handler(request):
    if request.POST:
        user = authenticate(username=request.POST['email'], password=request.POST['password'])
    if user is not None:
        login(request, user)
        return render(request, 'music_rec/login_success.html')
    else:
        return render(request, 'music_rec/user_login.html', {'error': 'login incorrect'})

def user_logout(request):
    logout(request)
    return render(request, 'music_rec/index.html', {'message': 'Successfully logged out'})

# main page to see what items have been added to each list
@login_required(login_url='/user_login')
def setup(request):
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
    
    context = {'songs': request.session['songs'], 'genres': request.session['genres'], 'artists': request.session['artists']}
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
    except Exception:
        print('session variables for rec input does not exist')
    
    return render(request, 'music_rec/setup.html')


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

# enter extra parameters if wanted for reccomendations algorithm
def parameters(request):
    context = {}
    return render(request, 'music_rec/parameters.html', context)

# view songs returned and name playlist
@login_required(login_url='/user_login')
def submit(request):
    #Get parameter data and format correctly
    parameters={}
    if request.POST:
        data = request.POST.copy()
        del data['csrfmiddlewaretoken']
        for key,value in data.items():
            parameters[key]=float(value)
            if key=="target_popularity":
                parameters[key]=int(value)
    else:
        pass # display an error showing no items added to search for
    try:
        recommendations = api.get_recommendations(SpotifyProfile.objects.get(user=request.user).access_token,request.session['songs_ids'],request.session['artists_ids'],request.session['genres_ids'],parameters).data
        payload=[]
        uris=[]
        for item in recommendations['tracks']:
            payload.append([item['name'],item['artists'][0]['name']])
            uris.append(item['uri'])
        request.session['uris'] = uris
        context = {'recommendations': payload,'uris':uris}
        return render(request, 'music_rec/submit.html', context)
    except Exception as e:
        # TODO once you get this working look for a 401 error which says that access token is expired
        # call expired_access_token and retry the api call
        # here is an expired access token BQCiRAWvfoVmHE6BFEdSljSKlju-ZIQxV7NcvekmSmgYBDDzexpbFbTyo3n_spw2TQBNs-wCbN_aAmTEg5FtF_0I7QrzXH6q2nxgmaWbpWfFiAwap_ZjtxV_nyK0wN4O9cnnS8bS4UbxzHm2bkZC7EcJsGE5ksrRvOZlBpgsb-HJi7iywhFoETYkPe3ZiW6xP6giwNulaT3bZCfDpSj1HyF-RCQ
        print('unable to parse recommendations data', e)
        return render(request, 'music_rec/submit.html')

# enter extra parameters if wanted for reccomendations algorithm
@login_required(login_url='/user_login')
def playlist(request):
    try:
        if request.POST:
            data = request.POST.copy()
            playlist_name = data['playlist']
        else:
            playlist_name = 'Spotify Music Reccomendations Playlist'

        spotify_profile = SpotifyProfile.objects.get(user=request.user)
        response = api.create_playlist(spotify_profile.access_token,spotify_profile.userid,playlist_name,request.session['uris'])
        if 'error' in response.data:
            if response.data['error']['status'] == 401:
                expired_access_token(request)
                response = api.create_playlist(spotify_profile.access_token,spotify_profile.userid,playlist_name,request.session['uris'])
        # TODO once you get this working put api call in a try exceipt and look for a 401 error which says that access token is expired
        # call expired_access_token and retry the api call
        if 'snapshot_id' in response.data:
            context = {'response': 'Playlist created successfully!'}
        else:
            context = {'response': 'Error creating playlist'}
        return render(request, 'music_rec/playlist.html', context)
    except Exception as e:
        return render(request, 'music_rec/playlist.html', {'response': 'Error creating playlist'})

# confirmation of songs added to playlist

# failure of songs added to playlist