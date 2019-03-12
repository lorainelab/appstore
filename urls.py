#from django.conf.urls import patterns, include, url
#from django.conf.urls.static import static
#from django.conf import settings



# enables admin 
from django.contrib import admin
admin.autodiscover()

from django.urls import include, path


"""
# patterns module removed in Django 1.10
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'CyAppStore.views.home', name='home'),
    # url(r'^CyAppStore/', include('CyAppStore.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    #url(r'',        include('social_auth.urls')),
    url(r'^accounts/',include('users.urls')),
    url(r'^$',          'apps.views.apps_default', name='default-page'),
    url(r'^apps/',       include('apps.urls')),
    url(r'^search',      include('haystack.urls')),
    url(r'^download/',   include('download.urls')),
    url(r'^submit_app/', include('submit_app.urls')),
    url(r'^users/',      include('users.urls')),
    url(r'^help/',       include('help.urls')),
    url(r'^backend/',    include('backend.urls')),
)
"""
urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'^accounts/',include('users.urls')),
    path(r'^$',          apps.views.apps_default, name='default-page'),
    path(r'^apps/',       include('apps.urls')),
    path(r'^search',      include('haystack.urls')),
    path(r'^download/',   include('download.urls')),
    path(r'^submit_app/', include('submit_app.urls')),
    path(r'^users/',      include('users.urls')),
    path(r'^help/',       include('help.urls')),
    path(r'^backend/',    include('backend.urls')),
]
    
if settings.DJANGO_STATIC_AND_MEDIA:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
