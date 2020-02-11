from django.urls import path
from . import views

urlpatterns = [
    path(r'about',                     views.about,      name='about'),
    path(r'',                   views.contact,    name='contact'),
    path(r'getstarted',                views.getstarted, name='getstarted'),
    path(r'getstarted_app_install',    views.getstarted_app_install, name='getstarted_app_install'),
]
