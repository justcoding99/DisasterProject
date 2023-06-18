from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template import loader
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .models import HelpNeed,  HelpNeedHelper, Hospitals
from .models import HelpNeed, HelpNeedHelper, User
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from .forms import NewUserForm, HelpNeedForm, ProfileForm, ReadyForm, \
    VolunteerRequestForm, ClothesRequestForm, VolunteerClothesRequestForm
from django.http import JsonResponse
from pymongo import MongoClient
from django.core.paginator import Paginator
import folium
from folium.plugins import FastMarkerCluster
from math import radians, sin, cos, sqrt, atan2
import logging
import uuid
from django.db.models import Max, Min



logger = logging.getLogger(__name__)
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
            admin = "admin"
            user = authenticate(username=username, password=password)

            if username == admin:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("user:admin")
            elif user != None:
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
            user = form.save(commit=False)
            if settings.DEVELOPMENT != 'True':
                user.is_active = False
            user.save()

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
    map = folium.Map(location=[38.9637, 35.2433], zoom_start=6)
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
    return render(request=request, template_name="user/volunteer.html", context={"needs": page_obj})

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



@login_required
def admin_view(request):
     return render(request=request, template_name="user/admin.html")


@login_required
def userslist_view(request):
    users = User.objects.all()
    paginator = Paginator(users, 10) # Show 10 users per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request=request, template_name="user/userslist.html", context={"page_obj": page_obj})


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

def ornek_form_view(request):
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


@login_required
def update_quantity(request, pk):
    post = get_object_or_404(HelpNeed, pk=pk)

    if request.method == 'POST':
        newquantity = int(request.POST.get('quantity'))
        quantity_change = post.quantity - newquantity
        post.quantity = quantity_change
        post.helpers.add(request.user)
        post.save()
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

"""my support page """
@login_required
def helped_archive(request):
    posts = HelpNeedHelper.objects.filter(
        user=request.user
    ).order_by('-help_need__updated_at')
    """last time helped """

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'user/helped_archive.html', context={"posts": page_obj})

def my_requests(request):
    posts = HelpNeed.objects.filter(volunteer= request.user).order_by('-created_at')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'user/my_requests.html', context={"posts": page_obj})

def delete_request(request, pk):
    instance = get_object_or_404(HelpNeed, pk=pk)
    instance.delete()
    messages.info(request, f"Your request has been deleted successfully ")
    return redirect('user:my_requests')



def aboutus_view(request):
    return render(request=request, template_name="user/about_us.html")

def hospital_locations_view(request):

    hospitals = Hospitals.objects.all()
    map = folium.Map(location=[38.9637, 35.2433], zoom_start=6)
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
    R = 6371
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

    threshold_distance = 15  # kilometers


    hospitals = Hospitals.objects.all()
    nearby_hospitals = []
    for hospital in hospitals:
        distance = calculate_distance(user_lat, user_lon, hospital.lat, hospital.lon)
        print(distance)
        if distance <= threshold_distance:
            nearby_hospitals.append(hospital)

    map = folium.Map(location=[user_lat, user_lon], zoom_start=12)
  
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






@login_required
def manage_help_post_view(request):
    needs = HelpNeed.objects.all()
    paginator = Paginator(needs, 10) # Show 10 help needs per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, "user/manage_help_post.html", context)


@login_required
def delete_help_post_view(request):
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_ids[]')
        print(f'Selected IDs: {selected_ids}')
        try:
            client = MongoClient('mongodb://root:example@localhost:27017/?authMechanism=DEFAULT')
            db = client['djongo']
            collection = db['user_helpneed']
            filter = {'helpneedid': {'$in': [uuid.UUID(id_) for id_ in selected_ids]}}
            print(f'Delete filter: {filter}')
            result = collection.delete_many(filter)
            print(f'Deleted count: {result.deleted_count}')
            if result.deleted_count > 0:
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'failure'})
        except Exception as e:
            
            return JsonResponse({'status': 'failure'})
    else:
        return redirect('user:manage_help_post')

@login_required
def hide_help_post_view(request):
    if request.method == 'POST':
        helpneedid = request.POST.get('helpneedid')
        try:
            client = MongoClient('mongodb://root:example@localhost:27017/?authMechanism=DEFAULT')
            db = client['djongo']
            collection = db['user_helpneed']
            help_need = HelpNeed.objects.get(helpneedid=helpneedid)
            help_need.hidden = True
            help_need.save()
            return JsonResponse({'status': 'success'})
        except HelpNeed.DoesNotExist:
            return JsonResponse({'status': 'failure'})
    else:
        return redirect('user:manage_help_post')
    

@login_required
def show_help_post_view(request):
    print('show_help_post_view called')
    if request.method == 'POST':
        helpneedids = request.POST.getlist('helpneedids[]')
        print(f'HelpNeed IDs: {helpneedids}')
        try:
            client = MongoClient('mongodb://root:example@localhost:27017/?authMechanism=DEFAULT')
            db = client['djongo']
            collection = db['user_helpneed']
            help_needs = HelpNeed.objects.filter(helpneedid__in=helpneedids)
            print(f'HelpNeeds: {help_needs}')
            result = help_needs.update(hidden=False)
            print(f'Update result: {result}')
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'failure'})
    else:
        return redirect('user:manage_help_post')



   


@login_required
def statistics_view(request):
    top_users = HelpNeedHelper.objects.values('user__username').annotate(max_quantity=Max('quantity')).order_by('-max_quantity')[:20]
    least_users = HelpNeedHelper.objects.values('user__username').annotate(min_quantity=Min('quantity')).order_by('min_quantity')[:20]
    food_requests = HelpNeed.objects.filter(help_class='food').count()
    shelter_requests = HelpNeed.objects.filter(help_class='shelter').count()
    heating_requests = HelpNeed.objects.filter(help_class='heating').count()
    clothes_requests = HelpNeed.objects.filter(help_class='clothes').count()
    medical_supplies_requests = HelpNeed.objects.filter(help_class='medical_supplies').count()
    hygiene_requests = HelpNeed.objects.filter(help_class='hygiene').count()
    

    context = {
        'top_users': top_users,
        'least_users': least_users,
        'food_requests': food_requests,
        'shelter_requests': shelter_requests,
        'heating_requests': heating_requests,
        'clothes_requests': clothes_requests,
        'medical_supplies_requests': medical_supplies_requests,
    }
    return render(request, 'user/statistics.html', context)







