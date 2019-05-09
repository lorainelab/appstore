from django.urls import path, include, re_path
from . import views

urlpatterns = [
    path(r'',                                views.apps_default),
    re_path(r'all',                             views.all_apps,             name='all_apps'),
    path(r'wall',                            views.wall_of_apps,         name='wall_of_apps'),
    re_path(r'with_tag/(\w+ ?-?\w+)',            views.apps_with_tag,        name='tag_page'),
    re_path(r'with_author/(.{1,300})',          views.apps_with_author,     name='author_page'),
    re_path(r'^(?P<app_name>[-\w\d]+)',                     views.app_page,             name='app_page'),
    re_path(r'^(?P<app_name>[-\w\d]+)/edit',                views.app_page_edit,        name='app_page_edit'),
    re_path(r'^(?P<app_name>[-\w\d]+)/author_names',        views.author_names),
    re_path(r'^(?P<app_name>[-\w\d]+)/institution_names',   views.institution_names),
]
