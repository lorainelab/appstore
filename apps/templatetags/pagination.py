from django import template

register = template.Library()


@register.inclusion_tag('pagination.html')
def pagination(downloaded_apps_pg):
    return {'downloaded_apps_pg': downloaded_apps_pg}
