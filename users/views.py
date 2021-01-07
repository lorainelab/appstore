import logging

from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from social_core.actions import do_complete
from social_core.utils import setting_name
from social_django.utils import psa

from util.view_util import html_response


def login(request):
    next_url = request.GET.get('next', reverse('default-page'))
    if request.user.is_authenticated:
        return HttpResponseRedirect(next_url)
    return html_response('users/login.html', {'navbar_selected': 'signin', 'next_url': next_url}, request)


logger = logging.getLogger(__name__)
NAMESPACE = getattr(settings, setting_name('URL_NAMESPACE'), None) or 'social'

# If a user logs in through Google and clicks "Deny", it'll throw an exception.
# However, social_auth.views.complete() does not handle exceptions at all. This
# method replaces complete() to handle exceptions.
@csrf_exempt
@psa('{0}:complete'.format(NAMESPACE))
def login_done(request, backend, *args, **kwargs):
    if request.user.is_authenticated:
        return complete(request, backend, *args, **kwargs)
    else:
        try:
            return do_complete(request, backend, *args, **kwargs)
        except Exception as e:
            logger.exception(e)
            return html_response('users/login.html', {'at_login': True, 'error': str(e)}, request)


def logout(request):
    auth_logout(request)
    next_url = request.GET.get('next', reverse('default-page'))
    return HttpResponseRedirect(next_url)


@csrf_exempt
@psa('{0}:complete'.format(NAMESPACE))
def complete(request, backend, *args, **kwargs):
    """Authentication complete view"""
    return do_complete(request.backend, _do_login, request.user,
                       redirect_name=REDIRECT_FIELD_NAME, request=request,
                       *args, **kwargs)
