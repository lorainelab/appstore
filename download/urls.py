from django.urls import path, include, re_path
from . import views

urlpatterns = [
	path(r'stats/',                                      views.all_stats,                   name='all_stats'),
	path(r'stats/timeline',                              views.all_stats_timeline),
	path(r'stats/geography/all',                         views.all_stats_geography_all),
	path(r'stats/geography/world',                       views.all_stats_geography_world),
	re_path(r'stats/geography/country/(\w{2})',             views.all_stats_geography_country),
    re_path(r'^(?P<app_name>[-\w\d]+)/',                          views.app_stats,                   name='app_stats'),
    re_path(r'stats/(\w{1,100})/timeline',                  views.app_stats_timeline),
    re_path(r'stats/(\w{1,100})/geography/all',             views.app_stats_geography_all),
    re_path(r'stats/(\w{1,100})/geography/world',           views.app_stats_geography_world),
    re_path(r'stats/(\w{1,100})/geography/country/(\w{2})', views.app_stats_country),
	re_path(r'^(?P<app_name>[-\w\d]+)/',                       views.release_download,            name='release_download'),
]
