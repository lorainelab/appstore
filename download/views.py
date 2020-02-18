import datetime

import pandas as pd
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from apps.models import App, Release
# put database in project directory
# see https://docs.djangoproject.com/en/2.1/ref/contrib/gis/geoip2/
from download.models import ReleaseDownloadsByDate, Download
from util.view_util import html_response, json_response, ipaddr_str_to_long


# ===================================
#   Download release
# ===================================


def _client_ipaddr(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        ipaddr_str = forwarded_for.split(',')[0]
    else:
        ipaddr_str = request.META.get('REMOTE_ADDR')
    return ipaddr_str_to_long(ipaddr_str)


def _increment_count(klass, **args):
    obj, created = klass.objects.get_or_create(**args)
    obj.count += 1
    obj.save()


def release_download(request, app_name):
    release = get_object_or_404(Release, app__name=app_name, active=True)
    ip4addr = _client_ipaddr(request)
    when = datetime.date.today()

    # Record the download as a Download object
    Download.objects.create(release=release, ip4addr=ip4addr, when=when)

    return HttpResponseRedirect(release.release_file_url)


# ===================================
#   Download statistics
# ===================================

def all_stats_timeline(request):
    dls = ReleaseDownloadsByDate.objects.filter(release=None)
    response = {'Total': [[dl.when.isoformat(), dl.count] for dl in dls]}
    return json_response(response)


def app_stats(request, app_name):
    app = get_object_or_404(App, Bundle_SymbolicName=app_name)
    releases = Release.objects.filter(app=app)
    total_download = 0
    for release in releases:
        downloads = ReleaseDownloadsByDate.objects.filter(release=release)
        for download in downloads:
            total_download += download.count
    c = {
        'app': app,
        'total_download': total_download
    }
    return html_response('app_stats.html', c, request)


def app_stats_timeline(request, app_name):
    app = get_object_or_404(App, active=True, Bundle_SymbolicName=app_name)
    releases = app.release_set.all()
    response = dict()
    for release in releases:
        dls = ReleaseDownloadsByDate.objects.filter(release=release)
        response[release.Bundle_Version] = [[dl.when.isoformat(), dl.count] for dl in dls]
    return json_response(response)


def download_timeline_csv(request, app_name):
    download_dict = dict()
    release_version = []
    date = []
    count = []

    app = get_object_or_404(App, Bundle_SymbolicName=app_name)
    releases = Release.objects.filter(app=app)
    for release in releases:
        downloads = ReleaseDownloadsByDate.objects.filter(release=release)
        if downloads.count() > 0:
            for download in downloads:
                release_version.append(download.release.Bundle_Version)
                date.append(download.when)
                count.append(int(download.count))
    download_dict['Release'] = release_version
    download_dict['Date'] = date
    download_dict['Count'] = count
    data = pd.DataFrame(download_dict)
    pivoted = data.pivot(index='Date', columns='Release', values='Count').reset_index()
    pivoted['Total'] = pivoted.sum(1)
    pivoted.fillna(0, inplace=True)
    response = HttpResponse(content_type='text/csv')
    filename = app.Bundle_Name + "_stats.csv"
    response['Content-Disposition'] = 'attachment; filename=' + filename
    pivoted.to_csv(path_or_buf=response, index=False)
    return response
