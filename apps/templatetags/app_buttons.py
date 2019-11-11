from django import template
from apps.models import App, Release

register = template.Library()


@register.inclusion_tag('app_button.html')
def app_button(app, order_index, release):
    try:
        app.star_percentage = 100 * app.object.stars / 5
        c = {}
        c['app'] = app.object
        c['order_index'] = order_index
        c['release'] = release[app]
        return c
    except:
        app.star_percentage = 100 * app.stars / 5
        c = {}
        c['app'] = app
        c['order_index'] = order_index
        c['release'] = release[app]
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
                    # button name       div attr name          attr type
    sort_criteria = (('name',           'object.fullname',            'str'),
                    ('downloads',      'object.downloads',           'int'),
                    ('newest release', 'object.latest_release_date', 'date'))

    if include_relevancy:
        sort_criteria = (('relevancy',  'order_index',  'int'), ) + sort_criteria

    return {'apps_with_releases': apps,
            'releases': releases,
            'sort_criteria': sort_criteria}


@register.inclusion_tag('list_of_apps.html')
def list_of_apps(apps, releases, include_relevancy = False):

    # a list of sort buttons to display
                    # button name       div attr name          attr type
    sort_criteria = (('name',           'fullname',            'str'),
                     ('downloads',      'downloads',           'int'),
                     ('newest release', 'latest_release_date', 'date'))

    if include_relevancy:
        sort_criteria = (('relevancy',  'order_index',  'int'), ) + sort_criteria

    return {'apps_with_releases': apps,
            'releases': releases,
            'sort_criteria': sort_criteria}
