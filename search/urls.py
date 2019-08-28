from django.urls import include, path

urlpatterns = [
    path(r'', 'search.views.search', name='search'),
]
