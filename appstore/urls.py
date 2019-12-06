"""appstore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from apps import views
from django.conf.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'accounts/',include('users.urls')),
    path(r'',          views.apps_default, name='default-page'),
    path(r'apps/',       include('apps.urls')),
    #re_path(r'apps/<slug:>/,       include('apps.urls')),
    path(r'search',      include('haystack.urls')),
    path(r'download/',   include('download.urls')),
    path(r'submit_app/', include('submit_app.urls')),
    path(r'users/',      include('users.urls')),
    path(r'help/',       include('help.urls')),
    path(r'backend/',    include('backend.urls')),
    path(r'obr/', include('obr.urls')),
    path(r'community_fav/<int:page>/', views.apps_default),
    re_path(r'installapp/(.+)', views.install_app, name='install-app')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# see https://docs.djangoproject.com/en/2.1/howto/static-files/
