from util.view_util import html_response
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import redirect


def compile_app_with_pipeline(request):
    return redirect("https://docs.google.com/document/d/1JdS9vnaXHkSJb0XdR7JgExCI2Y1MhpXhN8X8okO00-0")
