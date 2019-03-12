from django.urls import path, include
from . import views
urlpatterns = [
    path(r'^all_apps$',views.all),
]
