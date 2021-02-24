from util.view_util import html_response
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import redirect

def about(request):
    c = dict()
    c['footer_selected'] = 'about'
    c['google_api_key'] = settings.GOOGLE_API_KEY
    return html_response('help/about.html', c, request)

def compile_app_with_pipeline(request):
    return redirect("https://docs.google.com/document/d/1JdS9vnaXHkSJb0XdR7JgExCI2Y1MhpXhN8X8okO00-0")

def contact(request):
    c = { 'footer_selected': 'contact' }
    if request.method == 'POST':
        user_email = request.POST.get('user_email')
        message = request.POST.get('message')
        no_robot = request.POST.get('no_robot')
        if not user_email:
            c['error_from'] = True
        elif not message:
            c['error_message'] = True
        elif not no_robot == u'6':
            c['error_no_robot'] = True
        else:
            send_mail('IGB App Store - User Submitted Contact', 'From: %s\n\n%s' % (user_email, message), user_email, settings.CONTACT_EMAILS, fail_silently=False)
            return html_response('help/contact_thanks.html', c, request)
        c['user_email'] = user_email
        c['message'] = message
    return html_response('help/contact.html', c, request)
