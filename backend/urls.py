from django.urls import path
from . import views
urlpatterns = [
    path(r'all_apps', views.all),
]
