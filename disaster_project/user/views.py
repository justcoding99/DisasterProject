from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
# Create your views here.
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template import loader
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from .models import HelpNeed, Volunteer, HelpNeedHelper, Hospitals
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from .forms import NewUserForm, HelpNeedForm, VolunteerForm, ProfileForm, ReadyForm, \
    VolunteerRequestForm, ClothesRequestForm, VolunteerClothesRequestForm, QuantityForm
from django.http import JsonResponse
from pymongo import MongoClient
from django.core.paginator import Paginator
import folium
from folium.plugins import FastMarkerCluster
from math import radians, sin, cos, sqrt, atan2



def index(request):
    template = loader.get_template('user/index.html')
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
                return redirect("user:volunteer")
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
    return render(request=request, template_name="user/index.html", context={"help_need_form": form})


def help_map(request):
    needs = HelpNeed.objects.all()
    map = folium.Map()
    marker_cluster = FastMarkerCluster(
        data=list(
            zip([need.lat for need in needs], [need.lon for need in needs])))

    locations = [(need.lat, need.lon) for need in needs]
    popups = [(need.first_name, need.last_name, need.phone, need.help_class) for need in needs]

    for location, popup in zip(locations, popups):
        folium.Marker(location, popup=popup).add_to(marker_cluster)

    marker_cluster.add_to(map)

    needs = map._repr_html_()

    return render(request=request, template_name="user/help_map.html", context={"needs": needs})


def help_need_list(request):
    needs = HelpNeed.objects.all()
    return render(request=request, template_name="user/help_need_list.html", context={"needs": needs})


def volunteer_view(request):
    needs = HelpNeed.objects.filter(quantity__gt=0).order_by('-created_at').exclude(volunteer=request.user)
    paginator = Paginator(needs, 10) # Change 10 to the number of items you want per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    form = VolunteerForm(request.POST or None)
    quantityForm = QuantityForm(request.POST or None)
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
    return render(request=request, template_name="user/volunteer.html", context={"volunteer_form": form, "needs": page_obj, "quantityForm": quantityForm})
def firstaid_view(request):
    return render(request=request, template_name="user/firstaid.html")

def profile_view(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == 'POST':
        if form.is_valid():
         form.save()
    else:
        form = ProfileForm(request.POST or None, instance=request.user)
    return render(request=request, template_name="user/profile.html", context={"profile_form": form})

def food_form_view(request):
    if request.user.is_authenticated:
        form = VolunteerRequestForm(request.POST or None, initial={'help_class': "food", 'user_type': "volunteer", 'volunteer': request.user})
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.info(request, f"Volunteer, Your help request has been received.")
                form = VolunteerRequestForm(request.POST or None, initial={'help_class': "food", 'user_type': "volunteer", 'volunteer': request.user})
        else:
            form = VolunteerRequestForm(request.POST or None, initial={'help_class': "food", 'user_type': "volunteer", 'volunteer': request.user})
        return render(request=request, template_name="user/volunteer_requests.html", context={"help_need_form": form})
    else:
        form = ReadyForm(request.POST or None,initial={'help_class': "food", 'user_type': "victim"})
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.info(request, f"Your help request has been received.")
                return redirect("user:food_form")
        else:
            form = ReadyForm(request.POST or None,initial={'help_class': "food", 'user_type':"victim"})
        return render(request=request, template_name="user/food_form.html", context={"ready_form":form})
def shelter_form_view(request):
    if request.user.is_authenticated:
        form = VolunteerRequestForm(request.POST or None, initial={'help_class': "shelter", 'user_type': "volunteer", 'volunteer_requests': request.user})
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.info(request, f"Volunteer, Your help request has been received.")
                form = VolunteerRequestForm(request.POST or None, initial={'help_class': "shelter", 'user_type': "volunteer", 'volunteer': request.user})

        else:
            form = VolunteerRequestForm(request.POST or None, initial={'help_class': "shelter", 'user_type': "volunteer", 'volunteer': request.user})
        return render(request=request, template_name="user/volunteer_requests.html", context={"help_need_form": form})
    else:
        form = ReadyForm(request.POST or None, initial={'help_class': "shelter", 'user_type': "victim"})
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.info(request, f"Your help request has been received.")
                return redirect("user:shelter_form")
        else:
            form = ReadyForm(request.POST or None, initial={'help_class': "shelter", 'user_type': "victim"})
        return render(request=request, template_name="user/shelter_form.html", context={"ready_form": form})
def medical_form_view(request):
    if request.user.is_authenticated:
        form = VolunteerRequestForm(request.POST or None, initial={'help_class': "medical_supplies", 'user_type': "volunteer", 'volunteer': request.user})
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.info(request, f"Volunteer, Your help request has been received.")
                form = VolunteerRequestForm(request.POST or None, initial={'help_class': "medical_supplies", 'user_type': "volunteer", 'volunteer': request.user})
        else:
            form = VolunteerRequestForm(request.POST or None, initial={'help_class': "medical_supplies", 'user_type': "volunteer", 'volunteer': request.user})
        return render(request=request, template_name="user/volunteer_requests.html", context={"help_need_form": form})
    else:
        form = ReadyForm(request.POST or None,initial={'help_class': "medical_supplies", 'user_type': "victim"})
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.info(request, f"Your help request has been received.")
                return redirect("user:medical_form")
        else:
            form = ReadyForm(request.POST or None,initial={'help_class': "medical_supplies", 'user_type':"victim"})
        return render(request=request, template_name="user/medical_form.html", context={"ready_form":form})

def hygiene_form_view(request):
    if request.user.is_authenticated:
        form = VolunteerRequestForm(request.POST or None, initial={'help_class': "hygiene", 'user_type': "volunteer", 'volunteer': request.user})
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.info(request, f"Volunteer, Your help request has been received.")
                form = VolunteerRequestForm(request.POST or None, initial={'help_class': "hygiene", 'user_type': "volunteer", 'volunteer': request.user})
        else:
            form = VolunteerRequestForm(request.POST or None, initial={'help_class': "hygiene", 'user_type': "volunteer", 'volunteer': request.user})
        return render(request=request, template_name="user/volunteer_requests.html", context={"help_need_form": form})
    else:
        form = ReadyForm(request.POST or None, initial={'help_class': "hygiene", 'user_type': "victim"})
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.info(request, f"Your help request has been received.")
                return redirect("user:hygiene_form")
        else:
            form = ReadyForm(request.POST or None, initial={'help_class': "hygiene", 'user_type': "victim"})
        return render(request=request, template_name="user/hygiene_form.html", context={"ready_form": form})

def clothes_form_view(request):
    if request.user.is_authenticated:
        form = VolunteerClothesRequestForm(request.POST or None, initial={'help_class': "clothes", 'user_type': "volunteer", 'volunteer': request.user})
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.info(request, f"Volunteer, Your help request has been received.")
                form = VolunteerClothesRequestForm(request.POST or None, initial={'help_class': "clothes", 'user_type': "volunteer", 'volunteer': request.user})
        else:
            form = VolunteerClothesRequestForm(request.POST or None, initial={'help_class': "clothes", 'user_type': "volunteer", 'volunteer': request.user})
        return render(request=request, template_name="user/volunteer_requests.html", context={"help_need_form": form})
    else:
        form = ClothesRequestForm(request.POST or None, initial={'help_class': "clothes", 'user_type': "victim"})
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.info(request, f"Your help request has been received.")
                return redirect("user:clothes_form")
        else:
            form = ClothesRequestForm(request.POST or None, initial={'help_class': "clothes", 'user_type': "victim"})
        return render(request=request, template_name="user/clothes_form.html", context={"ready_form": form})

def heaters_form_view(request):
    if request.user.is_authenticated:
        form = VolunteerRequestForm(request.POST or None, initial={'help_class': "heating", 'user_type': "volunteer", 'volunteer': request.user})
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.info(request, f"Volunteer, Your help request has been received.")
                form = VolunteerRequestForm(request.POST or None, initial={'help_class': "heating", 'user_type': "volunteer", 'volunteer': request.user})
        else:
            form = VolunteerRequestForm(request.POST or None, initial={'help_class': "heating", 'user_type': "volunteer", 'volunteer': request.user})
        return render(request=request, template_name="user/volunteer_requests.html", context={"help_need_form": form})
    else:
        form = ReadyForm(request.POST or None, initial={'help_class': "heating", 'user_type': "victim"})
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.info(request, f"Your help request has been received.")
                return redirect("user:heaters_form")
        else:
            form = ReadyForm(request.POST or None, initial={'help_class': "heating", 'user_type': "victim"})
        return render(request=request, template_name="user/heaters_form.html", context={"ready_form": form})

def request_help_view(request):
    return render(request=request, template_name="user/index.html")
def volunteer_requests(request):
    form = VolunteerRequestForm(request.POST or None, initial={'user_type':"volunteer", 'volunteer': request.user})
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.info(request, f"Volunteer, Your help request has been received.")
            return redirect("user:volunteer_requests")
    else:
        form = VolunteerRequestForm(request.POST or None, initial={'user_type': "volunteer"})
    return render(request=request, template_name="user/volunteer_requests.html")

@login_required
def change_status(request, pk):
    instance = get_object_or_404(HelpNeed, pk=pk)
    instance.quantity = 0
    instance.is_helped = True
    instance.helper_id = request.user
    instance.save()
    messages.info(request, f"Volunteer, Thank You For Your Help")
    return redirect('user:volunteer')

@login_required
def update_quantity(request, pk):
    post = get_object_or_404(HelpNeed, pk=pk)

    if request.method == 'POST':
        newquantity = int(request.POST.get('quantity'))
        quantity_change = post.quantity - newquantity
        post.quantity = quantity_change
        post.helpers.add(request.user)
        post.save()

        # Update the quantity for the current user in the through model
        helper = HelpNeedHelper.objects.get(help_need=post, user=request.user)
        helper.quantity += newquantity
        helper.save()

        if post.quantity == 0:
            post.is_helped = True
            post.save()
            messages.info(request, "Volunteer, Thank You For Your Help")
            return redirect('user:volunteer')

        messages.info(request, "Volunteer, Thank You For Your Help")
        return redirect('user:volunteer')

# def helped_archive(request):
#     client = MongoClient('mongodb://localhost:27017')
#     db = client['djongo']
#     collection = db['user_helpneed']
#     query = {"is_helped": True}
#     posts = collection.find(query)
#     client.close()
#     context = {
#         'posts': posts
#     }
#     return render(request, 'user/helped_archive.html', context)

@login_required
def helped_archive(request):
    posts = HelpNeedHelper.objects.filter(
        user=request.user
    ).order_by('-help_need__updated_at')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'posts': page_obj
    }
    return render(request, 'user/helped_archive.html', context)

def my_requests(request):
    posts = HelpNeed.objects.filter(volunteer= request.user).order_by('-created_at')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'posts': page_obj
    }
    return render(request, 'user/my_requests.html', context)

def delete_request(request, pk):
    instance = get_object_or_404(HelpNeed, pk=pk)
    instance.delete()
    messages.info(request, f"Your request has been deleted successfully ")
    return redirect('user:my_requests')

def aboutus_view(request):
    return render(request=request, template_name="user/about_us.html")

def hospital_locations_view(request):

    hospitals = Hospitals.objects.all()

    # Create a map object centered on Turkey
    map = folium.Map(location=[38.9637, 35.2433], zoom_start=6)

    # FastMarkerCluster(list(
    #     zip([hospital.lat for hospital in hospitals], [hospital.lon for hospital in hospitals]))).add_to(
    #     map)
    # Add markers to the map
    # for hospital in hospitals:
    #     latitude = float(hospital.lat)
    #     longitude = float(hospital.lon)
    #
    #     # Check if both latitude and longitude are valid
    #     if latitude is not None and longitude is not None and isinstance(latitude, float) and isinstance(longitude,
    #                                                                                                      float):
    #         folium.Marker(
    #             location=[latitude, longitude],
    #             popup=hospital.name
    #         ).add_to(map)

    marker_cluster = FastMarkerCluster(
        data=list(zip([hospital.lat for hospital in hospitals], [hospital.lon for hospital in hospitals])))

    locations = [(hospital.lat, hospital.lon) for hospital in hospitals]
    popups = [hospital.name for hospital in hospitals]

    for location, popup in zip(locations, popups):
        folium.Marker(location, popup=popup).add_to(marker_cluster)

    marker_cluster.add_to(map)
    map_hospitals = map._repr_html_()

    return render(request=request, template_name="user/hospitals.html", context= {'map_html': map_hospitals})

def calculate_distance(lat1, lon1, lat2, lon2):
    # Haversine formula
    R = 6371  # earth radius
    lat1_rad, lon1_rad = radians(lat1), radians(lon1)
    lat2_rad, lon2_rad = radians(lat2), radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    return distance

def nearby_hospitals(request):
    if request.method == 'POST':
        user_lat = float(request.POST.get('user_lat'))
        print(user_lat)
        user_lon = float(request.POST.get('user_lon'))
        print(user_lon)
    if request.method != "POST":
        return HttpResponse("No user location data available.")

    threshold_distance = 1800  # kilometers


    hospitals = Hospitals.objects.all()
    nearby_hospitals = []
    for hospital in hospitals:
        distance = calculate_distance(user_lat, user_lon, hospital.lat, hospital.lon)
        print(distance)
        if distance <= threshold_distance:
            nearby_hospitals.append(hospital)

    map = folium.Map(location=[user_lat, user_lon], zoom_start=12)
    # FastMarkerCluster(list(
    #     zip([hospital.lat for hospital in nearby_hospitals], [hospital.lon for hospital in nearby_hospitals]))).add_to(
    #     map)

    # for hospital in nearby_hospitals:
    #     folium.Marker(
    #         location=[hospital.lat, hospital.lon],
    #         popup=hospital.name
    #     ).add_to(map)
    marker_cluster = FastMarkerCluster(
        data=list(zip([hospital.lat for hospital in nearby_hospitals], [hospital.lon for hospital in nearby_hospitals])))

    locations = [(hospital.lat, hospital.lon) for hospital in nearby_hospitals]
    popups = [hospital.name for hospital in nearby_hospitals]

    for location, popup in zip(locations, popups):
        folium.Marker(location, popup=popup).add_to(marker_cluster)

    marker_cluster.add_to(map)

    map_hospitals = map._repr_html_()
    context = {'map_html': map_hospitals}
    return render(request, 'user/hospitals.html', context)