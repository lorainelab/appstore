from django.urls import path, include
from . import views

urlpatterns = [
    path(r'',                                views.apps_default),
    path(r'all',                             views.all_apps,             name='all_apps'),
    path(r'wall',                            views.wall_of_apps,         name='wall_of_apps'),
    path(r'with_tag/(\w{1,100})',            views.apps_with_tag,        name='tag_page'),
    path(r'with_author/(.{1,300})',          views.apps_with_author,     name='author_page'),
    path(r'(\w{1,100})',                     views.app_page,             name='app_page'),
    path(r'(\w{1,100})/edit',                views.app_page_edit,        name='app_page_edit'),
    path(r'(\w{1,100})/author_names',        views.author_names),
    path(r'(\w{1,100})/institution_names',   views.institution_names),
]
