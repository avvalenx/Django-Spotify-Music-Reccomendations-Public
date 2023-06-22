from django.urls import path

from . import views

app_name = 'music_rec'
urlpatterns = [
    path('', views.index, name='index'),
    path('help', views.help, name='help'),
    path('error', views.error, name='error'),
    path('signup', views.signup, name='signup'),
    path('signup_success', views.signup_success, name='signup_success'),
    path('spotify_login', views.spotify_login, name='spotify_login'),
    path('spotify_success', views.spotify_success, name='spotify_success'),
    path('get_access_token', views.get_access_token, name='get_access_token'),
    path('expired_access_token', views.expired_access_token, name='expired_access_token'),
    path('user_login', views.user_login, name='user_login'),
    path('login_handler', views.login_handler, name='login_handler'),
    path('account', views.account, name='account'),
    path('user_logout', views.user_logout, name='user_logout'),
    path('setup', views.setup, name='setup'),
    path('clear', views.clear, name='clear'),
    path('songs', views.songs, name='songs'),
    path('artists', views.artists, name='artists'),
    path('genres', views.genres, name='genres'),
    path('parameters', views.parameters, name='parameters'),
    path('submit', views.submit, name='submit'),
    path('playlist', views.playlist, name='playlist'),
]