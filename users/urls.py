from django.urls import path, include, re_path
from . import views

urlpatterns = [
    path(r'', include('social_django.urls', namespace='social')),
    path(r'login/',                         views.login,           name='login'),
    path(r'login',                          views.login,           name='login'),
    re_path(r'login/done/([\w-]{1,100})/',  views.login,            name='login_done'),
    path(r'logout',                         views.logout,             name='logout'),
]
