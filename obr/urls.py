from django.urls import path
from . import views

urlpatterns = [
    path('pending_releases/repository.xml', views.serve_file_pending),
    path('releases/', views.redirect_page),
    path('releases/repository.xml', views.serve_file_released),
]
