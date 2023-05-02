from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import HelpNeed, Volunteer, ClothesRequest

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
    lat = forms.CharField(widget=forms.HiddenInput(), initial='0')
    lon = forms.CharField(widget=forms.HiddenInput(), initial='0')
    address = forms.CharField(required=True)

    class Meta:
        model = HelpNeed
        fields = ("first_name","last_name", "phone", "address", "lat", "lon", "description")



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

class ReadyForm(forms.ModelForm):
    lat = forms.CharField(widget=forms.HiddenInput(), initial='0')
    lon = forms.CharField(widget=forms.HiddenInput(), initial='0')
    address = forms.CharField(required=True)
    help_class = forms.CharField(max_length=20, widget=forms.HiddenInput())
    user_type = forms.CharField(max_length=20, widget=forms.HiddenInput())
    class Meta:
        model = HelpNeed
        fields = ("first_name","last_name", "phone", "address","lat", "lon", "quantity", "help_class", "user_type")

class ClothesRequestForm(forms.ModelForm):
    lat = forms.CharField(widget=forms.HiddenInput(), initial='0')
    lon = forms.CharField(widget=forms.HiddenInput(), initial='0')
    address = forms.CharField(required=True)
    help_class = forms.CharField(max_length=20, widget=forms.HiddenInput())
    user_type = forms.CharField(max_length=20, widget=forms.HiddenInput())

    class Meta:
        model = ClothesRequest
        fields = ("first_name","last_name", "phone", "address","lat", "lon", "quantity", "help_class", "user_type", "category", "size")

class ProfileForm(forms.ModelForm):
    username = forms.CharField(required=False, disabled=True)
    email = forms.CharField(required=False, disabled=True)
    class Meta:
        model = User
        fields = ('first_name','last_name', 'username', 'email', 'phone', 'address')
        help_texts = {
            'username': None,
        }
        # def __init__(self, *args, **kwargs):
        #     super(ProfileForm, self).__init__(*args, **kwargs)
        #     self.fields['username'].disabled = True
        #     self.fields['email'].disabled = True

class VolunteerRequestForm(forms.ModelForm):
    lat = forms.CharField(widget=forms.HiddenInput(), initial='0')
    lon = forms.CharField(widget=forms.HiddenInput(), initial='0')
    address = forms.CharField(required=True)
    user_type = forms.CharField(max_length=20, widget=forms.HiddenInput())

    class Meta:
        model = HelpNeed
        fields = ("first_name","last_name", "address", "lat", "lon", "quantity", "help_class", "user_type")


