from django import template
from apps.models import App, Release
from download.models import ReleaseDownloadsByDate
register = template.Library()


@register.inclusion_tag('app_button.html')
def app_button(app, order_index, release):
    try:
        releases = Release.objects.filter(app=app)
    except:
        releases = Release.objects.filter(app=app.object)
    total_download = 0
    for release_obj in releases:
        downloads = ReleaseDownloadsByDate.objects.filter(release=release_obj)
        for download in downloads:
            total_download += download.count
    try:
        app.star_percentage = 100 * app.object.stars / 5
        c = {}
        c['app'] = app.object
        c['order_index'] = order_index
        c['release'] = release[app]
        c['total_download'] = total_download
        return c
    except:
        app.star_percentage = 100 * app.stars / 5
        c = {}
        c['app'] = app
        c['order_index'] = order_index
        c['release'] = release[app]
        c['total_download'] = total_download
        return c

@register.inclusion_tag('app_button.html')
def app_button_by_name(app_name):
    try:
        app = App.objects.get(name = app_name)
        c = {}
        c['app'] = app
        return c
    except:
        app = App.objects.get(name = app_name)
        c = {}
        c['app'] = app
        return c


@register.inclusion_tag('app_buttons.html')
def app_buttons(apps, releases):
    return {'apps': apps,
            'releases': releases}


@register.inclusion_tag('list_of_apps_search.html')
def list_of_apps_search(apps, releases, include_relevancy = False):
    # a list of sort buttons to display
    if releases == "Temp":
        releases = {}
        for app in apps:
            released_app = Release.objects.filter(active=True, app=app).extra(select={'natural_version': "CAST(REPLACE(Bundle_Version, '.', '') as UNSIGNED)"}).order_by('-natural_version')[:1][0]
            releases[app] = released_app

                    # button name       div attr name          attr type
    sort_criteria = (('name',           'object.Bundle_Name',            'str'),
                    ('downloads',      'object.downloads',           'int'))

    if include_relevancy:
        sort_criteria = (('relevancy',  'order_index',  'int'), ) + sort_criteria

    return {'apps_with_releases': apps,
            'releases': releases,
            'sort_criteria': sort_criteria}


@register.inclusion_tag('list_of_apps.html')
def list_of_apps(apps, releases, include_relevancy = False):

    # a list of sort buttons to display
                    # button name       div attr name          attr type
    sort_criteria = (('name',           'Bundle_Name',            'str'),
                     ('downloads',      'downloads',           'int'),
                     ('newest release', 'created', 'date'))

    if include_relevancy:
        sort_criteria = (('relevancy',  'order_index',  'int'), ) + sort_criteria

    return {'apps_with_releases': apps,
            'releases': releases,
            'sort_criteria': sort_criteria}
