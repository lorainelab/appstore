from django.urls import include, path
from . import views

urlpatterns = [
    path(r'^$',                      views.submit_app,         name='submit-app'),
    path(r'^pending$',               views.pending_apps,       name='pending-apps'),
    path(r'^cy2xplugins$',           views.cy2x_plugins,       name='cy2x-plugins'),
    path(r'^confirm/(\d{1,5})$',     views.confirm_submission, name='confirm-submission'),
    path(r'^submit_api/(\d{1,5})$',  views.submit_api,         name='submit-api'),
    path(r'^artifact_exists$',       views.artifact_exists),
]
