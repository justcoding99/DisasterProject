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
        fields = ("username", "email", "password1", "password2")

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
        fields = ("name", "phone", "address")


# --------------- Rawan -------------------

class VolunteerForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = Volunteer
        fields = ("first_name","last_name", "phone", "address", "volunteer_field")

