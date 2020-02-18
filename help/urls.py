from django.urls import path
from . import views

urlpatterns = [
    path(r'about',                     views.about,      name='about'),
    path(r'',                   views.contact,    name='contact'),
]
