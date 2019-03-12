from django.urls import path, include
from . import views

urlpatterns = [
    path(r'^about$',                     views.about,      name='about'),
    path(r'^contact$',                   views.contact,    name='contact'),
    path(r'^competitions$',              views.competitions,name='competitions'),
    path(r'^md$',                        views.md,         name='md'),
    path(r'^getstarted$',                views.getstarted, name='getstarted'),
    path(r'^getstarted_app_install$',    views.getstarted_app_install, name='getstarted_app_install'),
]
