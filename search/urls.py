from django.urls import path

urlpatterns = [
    path(r'', 'search.views.search', name='search'),
]
