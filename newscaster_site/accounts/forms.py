from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['display_name', 'profile_picture', 'home_country', 'city', 'age']

class CustomSignupForm(forms.Form):
    display_name = forms.CharField(max_length=255, label='Display Name')
    profile_picture = forms.ImageField(required=False, label='Profile Picture')

    def signup(self, request, user):
        """
        This is called when a user signs up.
        """
        user.userprofile.display_name = self.cleaned_data['display_name']
        if self.cleaned_data.get('profile_picture'):
            user.userprofile.profile_picture = self.cleaned_data['profile_picture']
        user.userprofile.save()
        return user
