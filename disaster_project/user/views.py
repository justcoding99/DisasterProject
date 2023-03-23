from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
# Create your views here.
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template import loader
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from .models import HelpNeed, Volunteer
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from .forms import NewUserForm, HelpNeedForm, VolunteerForm


def index(request):
    template = loader.get_template('user/base.html')
    context = {}
    if not request.user.is_authenticated:
        context['variable'] = "you are not allowed"
        context['logged'] = False
    else:
        context['variable'] = "you are allowed"
        context['logged'] = True

    return HttpResponse(template.render(context, request))


def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("user:index")


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("user:index")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="user/login.html", context={"login_form": form})


def register_view(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            # save form in the memory not in database
            user = form.save(commit=False)
            if settings.DEVELOPMENT != 'True':
                user.is_active = False
            user.save()
            # to get the domain of the current site
            current_site = get_current_site(request)
            mail_subject = 'Activation link has been sent to your email id'
            message = render_to_string('user/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            if settings.DEVELOPMENT != 'True':
                email.send()
            return render(request, 'user/Email.html',
                          {'msg': 'Please confirm your email address to complete the registration'})
    else:
        from django.urls import reverse
        form = NewUserForm()
    return render(request=request, template_name="user/register.html", context={"register_form": form})


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'user/Email.html',
                      {'msg': 'Thank you for your email confirmation. Now you can login your account.'})
    else:
        return render(request, 'user/Email.html', {'msg': 'Activation link is invalid!'})


def help_need_view(request):
    if request.method == "POST":
        form = HelpNeedForm(request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, f"Your help request has been received.")
            return redirect("user:index")
        else:
            messages.error(request, "Name and phone are mandatory.")
    form = HelpNeedForm()
    return render(request=request, template_name="user/help_need.html", context={"help_need_form": form})


def help_map(request):
    needs = HelpNeed.objects.all()
    return render(request=request, template_name="user/help_map.html", context={"needs": needs})


def help_need_list(request):
    needs = HelpNeed.objects.all()
    return render(request=request, template_name="user/help_need_list.html", context={"needs": needs})


# --------------- Rawan -------------------
def volunteer_view(request):
    form = VolunteerForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            phone = request.POST['phone']
            address = request.POST['address']
            volunteer_field = request.POST['volunteer_field']
            vol = Volunteer.objects.create(first_name=first_name, last_name=last_name, phone=phone, address=address,
                                           volunteer_field=volunteer_field)
            messages.success(request, 'Data has been submitted')
            form.save()
        else:
            print(form.errors)
    return render(request=request, template_name="user/volunteer.html", context={"volunteer_form": form})

def firstaid_view(request):
    return render(request=request, template_name="user/firstaid.html")