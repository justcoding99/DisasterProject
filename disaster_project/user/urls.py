from django.urls import path
from . import views


app_name = "user"

urlpatterns = [
    path('', views.request_help_view, name='index'),
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
    path('admin', views.admin_view, name='admin'),
    path('userslist', views.userslist_view, name='userslist'),
    path('food_form', views.food_form_view, name='food_form'),
    path('shelter_form', views.shelter_form_view, name='shelter_form'),
    path('medical_form', views.medical_form_view, name='medical_form'),
    path('hygiene_form', views.hygiene_form_view, name='hygiene_form'),
    path('clothes_form', views.clothes_form_view, name='clothes_form'),
    path('heaters_form', views.heaters_form_view, name='heaters_form'),
    path('volunteer_requests', views.volunteer_requests, name='volunteer_requests'),
    path('change-status/<int:pk>/', views.change_status, name='change_status'),
    # path('update_quantity/<int:pk>/', views.update_quantity, name='update_quantity'),
    path('update-quantity/<int:pk>/', views.update_quantity, name='update_quantity'),
    path('helped_archive', views.helped_archive, name='helped_archive'),
    path('my_requests', views.my_requests, name='my_requests'),
    path('delete_request/<int:pk>/', views.delete_request, name='delete_request'),
    path('statistics', views.statistics_view, name='statistics'),
    path('manage_help_post/', views.manage_help_post_view, name='manage_help_post'),
    path('delete_help_post/', views.delete_help_post_view, name='delete_help_post'),
    path('hide_help_post/', views.hide_help_post_view, name='hide_help_post'),
    path('show_help_post/', views.show_help_post_view, name='show_help_post'),


]