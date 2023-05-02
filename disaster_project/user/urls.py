from django.urls import path
from . import views


app_name = "user"

urlpatterns = [
    path('', views.help_need_view, name='index'),
    path('login', views.login_view, name='login'),
    path('help_need', views.help_need_view, name='help_need'),
    path('help_need_list', views.help_need_list, name='help_need_list'),
    path('help_map', views.help_map, name='help_map'),
    path('volunteer', views.volunteer_view, name='volunteer'),
    path('register', views.register_view, name='register'),
    path("logout", views.logout_view, name="logout"),
    path("activate/<str:uidb64>/<str:token>", views.activate, name='activate'),
    path('first_aid', views.firstaid_view, name='first_aid'),
    path('profile', views.profile_view, name='profile'),
    path('ready_form', views.ready_form_view, name='ready_form'),
    path('admin', views.admin_view, name='admin'),
    path('userslist', views.userslist_view, name='userslist'),
]