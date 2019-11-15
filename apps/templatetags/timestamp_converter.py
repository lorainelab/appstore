from django import template
import datetime

register = template.Library()


def human_readable_time(value):
    get_date = datetime.datetime(value)
    return get_date


@register.filter
def strip_double_quotes(quoted_string):
    return quoted_string.replace('"', '')


register.filter('human_readable_time', human_readable_time)
register.filter('strip_double_quotes', strip_double_quotes)