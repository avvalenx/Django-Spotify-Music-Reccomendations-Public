from django import forms
from music_rec import api

class Recommendations(forms.Form):
    name = forms.CharField(label='Enter a playlist name')
    
    def get_recommendations():
        name = name
        try:
            # FIXME api.get_recommendations(name, ACCESS_TOKEN)
            pass
        except Exception:
            print('unable to get recommendations')
            return [('fail', 'fail')]

class SignUp(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password')
    confirm_password = forms.CharField