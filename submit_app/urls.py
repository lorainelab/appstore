from django.urls import include, path, re_path
from . import views

urlpatterns = [
    path(r'',                      views.submit_app,         name='submit-app'),
    path(r'pending',               views.pending_apps,       name='pending-apps'),
    re_path(r'confirm/(\d{1,5})',     views.confirm_submission, name='confirm-submission'),
# IGBF-1994
#    re_path(r'submit_api/(\d{1,5})',  views.submit_api,         name='submit-api'),
    path(r'artifact_exists',       views.artifact_exists),
]
