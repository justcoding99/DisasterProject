from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import HelpNeed, Volunteer

User = get_user_model()


# Create your forms here.
class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class HelpNeedForm(forms.ModelForm):
    name = forms.CharField(required=True)
    lat = forms.CharField(widget=forms.HiddenInput(), initial='0')
    lon = forms.CharField(widget=forms.HiddenInput(), initial='0')
    address = forms.CharField(required=False)

    class Meta:
        model = HelpNeed
        fields = ("name", "phone", "address", "lat", "lon", "description")


# --------------- Rawan -------------------

class VolunteerForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = Volunteer
        fields = ("first_name","last_name", "phone", "address")

# class ProfileForm(VolunteerForm):
#     class Meta:
#         model = Volunteer
#         fields = ('username','email') + VolunteerForm.Meta.fields
#     def __init__(self, *args, **kwargs):
#         super(ProfileForm, self).__init__(*args, **kwargs)
#         self.fields.pop('volunteer_field')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name','last_name', 'username', 'email', 'phone', 'address')
        help_texts = {
            'username': None,
        }
        def __init__(self, *args, **kwargs):
            super(ProfileForm, self).__init__(*args, **kwargs)
            self.fields['username'].disabled = True
            self.fields['email'].disabled = True

