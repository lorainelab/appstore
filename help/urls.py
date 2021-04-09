from django.urls import path
from . import views

urlpatterns = [
    path(r'compile_app_with_pipeline', views.compile_app_with_pipeline, name='compile-app-with-pipeline'),
]
