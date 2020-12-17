from django import template

register = template.Library()


@register.filter
def title_modified(title, isTitle):
    if '_' in title:
        return title.replace('_', ' ').capitalize()
    if isTitle:
        return title.capitalize()
    else:
        return title

def get_authors(relese_authors_queryset):
    authors = ', '.join(x.name for x in list(relese_authors_queryset))
    return authors


register.filter('title_modified', title_modified)
register.filter('get_authors', get_authors)
