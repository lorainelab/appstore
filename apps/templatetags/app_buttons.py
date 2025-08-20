from django import template
from django.db.models.functions import Cast, Replace
from django.db.models import F, Value, IntegerField
from apps.models import App, Release
from curated_categories.models import CuratedCategoriesMapping, CuratedCategory
from download.models import ReleaseDownloadsByDate
register = template.Library()


@register.inclusion_tag('apps/app_button.html')
def app_button(app, order_index, release):
    try:
        releases = Release.objects.filter(app=app)
        cat_mapping = CuratedCategoriesMapping.objects.filter(app=app)
    except:
        releases = Release.objects.filter(app=app.object)
        cat_mapping = CuratedCategoriesMapping.objects.filter(app=app.object)

    total_download = 0
    for release_obj in releases:
        downloads = ReleaseDownloadsByDate.objects.filter(release=release_obj)
        for download in downloads:
            total_download += download.count
    # Getting Curated Categories from App Object
    curated_categories = []
    for qs in cat_mapping:
        for cat in qs.curated_categories.all():
            curated_categories.append(cat.curated_category)
    try:
        app.star_percentage = 100 * app.object.stars / 5
        c = {}
        c['app'] = app.object
        c['order_index'] = order_index
        c['release'] = release[app]
        c['total_download'] = total_download
        c['curated_categories'] = ','.join(curated_categories)
        return c
    except:
        app.star_percentage = 100 * app.stars / 5
        c = {}
        c['app'] = app
        c['order_index'] = order_index
        c['release'] = release[app]
        c['total_download'] = total_download
        c['curated_categories'] = ','.join(curated_categories)
        return c

@register.inclusion_tag('apps/app_button.html')
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


@register.inclusion_tag('apps/app_buttons.html')
def app_buttons(apps, releases):
    return {'apps': apps,
            'releases': releases}


@register.inclusion_tag('apps/list_of_apps_search.html')
def list_of_apps_search(apps, releases):
    if releases == "Temp":
        releases = {}
        for app in apps:
            released_app = Release.objects.filter(active=True, app=app).annotate(natural_version=Cast(Replace(F("Bundle_Version"), Value("."), Value("")),output_field=IntegerField())).order_by('-natural_version').first()
            releases[app] = released_app

    return {'apps_with_releases': apps,
            'releases': releases,
            }
