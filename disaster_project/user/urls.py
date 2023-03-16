from django.urls import path
from . import views


app_name = "user"

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login_view, name='login'),
    path('register', views.register_view, name='register'),
    path("logout", views.logout_view, name="logout"),
    path("activate/<str:uidb64>/<str:token>", views.activate, name='activate'),


]