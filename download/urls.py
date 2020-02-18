from django.urls import path, re_path
from . import views

urlpatterns = [
	re_path(r'^(?P<app_name>[-\w\d\.]+)/timeline',                  views.download_timeline_csv,            name='download-timeline-csv'),
	re_path(r'^(?P<app_name>[-\w\d\.]+)/',                      views.app_stats,                    name='app_stats'),
	re_path(r'^(?P<app_name>[-\w\d\.]+)/',                    views.release_download,             name='release_download')
]
