from django import template

register = template.Library()


@register.filter
def title_modified(title):
    return title.replace('_', ' ').capitalize()

def get_authors(relese_authors_queryset):
    authors = ', '.join(x.name for x in list(relese_authors_queryset))
    return authors


register.filter('title_modified', title_modified)
register.filter('get_authors', get_authors)
