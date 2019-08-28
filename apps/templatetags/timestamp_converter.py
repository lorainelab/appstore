from django import template
import datetime

register = template.Library()


def human_readable_time(value):
    get_date = datetime.datetime(value)
    return get_date


register.filter('human_readable_time', human_readable_time)
