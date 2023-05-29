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


from .models import HelpNeed, Volunteer, HelpNeedHelper
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from .forms import NewUserForm, HelpNeedForm, VolunteerForm, ProfileForm, ReadyForm, \
    VolunteerRequestForm, ClothesRequestForm, VolunteerClothesRequestForm, QuantityForm
from django.http import JsonResponse
from pymongo import MongoClient
from django.core.paginator import Paginator
import logging
import uuid



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
    return render(request=request, template_name="user/help_map.html", context={"needs": needs})


def help_need_list(request):
    needs = HelpNeed.objects.all()
    return render(request=request, template_name="user/help_need_list.html", context={"needs": needs})


def volunteer_view(request):
    needs = HelpNeed.objects.filter(quantity__gt=0).order_by('-created_at')
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




def admin_view(request):
     return render(request=request, template_name="user/admin.html")



def userslist_view(request):
    users = User.objects.all()
    return render(request=request, template_name="user/userslist.html", context={"users":users})

def food_form_view(request):
    if request.user.is_authenticated:
        form = VolunteerRequestForm(request.POST or None, initial={'help_class': "food", 'user_type': "volunteer"})
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.info(request, f"Volunteer, Your help request has been received.")
                form = VolunteerRequestForm(request.POST or None, initial={'help_class': "food", 'user_type': "volunteer"})
        else:
            form = VolunteerRequestForm(request.POST or None, initial={'help_class': "food", 'user_type': "volunteer"})
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
        form = VolunteerRequestForm(request.POST or None, initial={'help_class': "shelter", 'user_type': "volunteer"})
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.info(request, f"Volunteer, Your help request has been received.")
                form = VolunteerRequestForm(request.POST or None, initial={'help_class': "shelter", 'user_type': "volunteer"})

        else:
            form = VolunteerRequestForm(request.POST or None, initial={'help_class': "shelter", 'user_type': "volunteer"})
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
        form = VolunteerRequestForm(request.POST or None, initial={'help_class': "medical_supplies", 'user_type': "volunteer"})
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.info(request, f"Volunteer, Your help request has been received.")
                form = VolunteerRequestForm(request.POST or None, initial={'help_class': "medical_supplies", 'user_type': "volunteer"})
        else:
            form = VolunteerRequestForm(request.POST or None, initial={'help_class': "medical_supplies", 'user_type': "volunteer"})
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
        form = VolunteerRequestForm(request.POST or None, initial={'help_class': "hygiene", 'user_type': "volunteer"})
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.info(request, f"Volunteer, Your help request has been received.")
                form = VolunteerRequestForm(request.POST or None, initial={'help_class': "hygiene", 'user_type': "volunteer"})
        else:
            form = VolunteerRequestForm(request.POST or None, initial={'help_class': "hygiene", 'user_type': "volunteer"})
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
        form = VolunteerClothesRequestForm(request.POST or None, initial={'help_class': "clothes", 'user_type': "volunteer"})
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.info(request, f"Volunteer, Your help request has been received.")
                form = VolunteerClothesRequestForm(request.POST or None, initial={'help_class': "clothes", 'user_type': "volunteer"})
        else:
            form = VolunteerClothesRequestForm(request.POST or None, initial={'help_class': "clothes", 'user_type': "volunteer"})
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
        form = VolunteerRequestForm(request.POST or None, initial={'help_class': "heating", 'user_type': "volunteer"})
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.info(request, f"Volunteer, Your help request has been received.")
                form = VolunteerRequestForm(request.POST or None, initial={'help_class': "heating", 'user_type': "volunteer"})
        else:
            form = VolunteerRequestForm(request.POST or None, initial={'help_class': "heating", 'user_type': "volunteer"})
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
    form = VolunteerRequestForm(request.POST or None, initial={'user_type':"volunteer"})
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.info(request, f"Volunteer, Your help request has been received.")
            return redirect("user:volunteer_requests")
    else:
        form = VolunteerRequestForm(request.POST or None, initial={'user_type':"volunteer"})
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

def statistics_view(request):

    client = MongoClient('mongodb://root:example@localhost:27017,localhost/?authMechanism=DEFAULT')
    db = client['djongo']
    collection = db['user_helpneed']

    data = collection.find({}, {'_id': 0, 'quantity': 1, 'help_class': 1})
    food_no = HelpNeed.objects.filter(help_class='food').count()
    food_no = int(food_no)
    shelter_no = HelpNeed.objects.filter(help_class='shelter').count()
    shelter_no = int(shelter_no)
    heating_no = HelpNeed.objects.filter(help_class='heating').count()
    heating_no = int(heating_no)
    clother_no = HelpNeed.objects.filter(help_class='clothes').count()
    clother_no = int(clother_no)
    medical_supplies_no = HelpNeed.objects.filter(help_class='medical_supplies').count()
    medical_supplies_no = int(medical_supplies_no)
    hygiene_no = HelpNeed.objects.filter(help_class='hygiene').count()
    hygiene_no = int(hygiene_no)

    help_class_list = ['food','shelter','heating','clother','medical_supplies','hygiene']
    count_list = [food_no,shelter_no,heating_no,clother_no,medical_supplies_no,hygiene_no]
    context={

        'help_class_list':help_class_list,
        'count_list':count_list

            }

    return render(request,"user/statistics.html",context)


def manage_help_post_view(request):
    needs = HelpNeed.objects.all() #filter here.
    context={
        "needs": needs
        }
    return render(request, "user/manage_help_post.html", context)

logger = logging.getLogger(__name__)


    








def delete_help_post_view(request):
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_ids[]')
        print(f'Selected IDs: {selected_ids}')
        try:
            client = MongoClient('mongodb://root:example@localhost:27017/?authMechanism=DEFAULT')
            db = client['djongo']
            collection = db['user_helpneed']
            # Delete the selected objects using their helpneedid values
            filter = {'helpneedid': {'$in': [uuid.UUID(id_) for id_ in selected_ids]}}
            print(f'Delete filter: {filter}')
            result = collection.delete_many(filter)
            print(f'Deleted count: {result.deleted_count}')
            if result.deleted_count > 0:
                # Return a JSON response indicating success
                return JsonResponse({'status': 'success'})
            else:
                # Handle case when the documents were not found or not deleted
                # Return a JSON response indicating failure
                return JsonResponse({'status': 'failure'})
        except Exception as e:
            # Handle any exceptions that occur during the deletion process
            # Return a JSON response indicating failure
            return JsonResponse({'status': 'failure'})
    else:
        # Handle GET requests or requests that are not made via AJAX
        return redirect('user:manage_help_post')





    """"
    return HttpResponse('Error deleting the document') 
    """

def hide_help_post_view(request):
    if request.method == 'POST':
        # Get the ID of the record to hide from the POST data
        helpneedid = request.POST.get('helpneedid')
        try:
            client = MongoClient('mongodb://root:example@localhost:27017/?authMechanism=DEFAULT')
            db = client['djongo']
            collection = db['user_helpneed']
            # Get the HelpNeed object with the specified ID
            help_need = HelpNeed.objects.get(helpneedid=helpneedid)
            # Set the hidden field to True
            help_need.hidden = True
            # Save the changes to the database
            help_need.save()
            # Return a JSON response indicating success
            return JsonResponse({'status': 'success'})
        except HelpNeed.DoesNotExist:
            # Handle case when the HelpNeed object with the specified ID does not exist
            # Return a JSON response indicating failure
            return JsonResponse({'status': 'failure'})
    else:
        # Handle GET requests or requests that are not made via AJAX
        return redirect('user:manage_help_post')
    


def show_help_post_view(request):
    if request.method == 'POST':
        helpneedids = request.POST.getlist('helpneedids[]')
        print(f'HelpNeed IDs: {helpneedids}')
        try:
            client = MongoClient('mongodb://root:example@localhost:27017/?authMechanism=DEFAULT')
            db = client['djongo']
            collection = db['user_helpneed']
            # Get the HelpNeed objects with the specified IDs
            help_needs = HelpNeed.objects.filter(helpneedid__in=helpneedids)
            # Set the hidden field to False for all objects
            result = help_needs.update(hidden=False)
            print(f'Update result: {result}')
            # Return a JSON response indicating success
            return JsonResponse({'status': 'success'})
        except Exception as e:
            # Handle any exceptions that occur during the showing process
            # Return a JSON response indicating failure
            return JsonResponse({'status': 'failure'})
    else:
        # Handle GET requests or requests that are not made via AJAX
        return redirect('user:manage_help_post')

