from xml.etree import ElementTree as ET

from django.http import HttpResponse

from util.view_util import html_response
from . import repogen


def serve_file_pending(request):
    data = repogen.main('pending')
    response = HttpResponse(content_type="text/xml")
    # Use the below line for serving the file as attachment (Begin Direct Download)
    # response['Content-Disposition'] = 'attachment; filename=%s' % filename # force browser to download file
    response.write(ET.tostring(data, encoding='unicode', method='xml'))
    return response

def redirect_page(request):
    return html_response('redirect.html', {}, request)

def serve_file_released(request):
    data = repogen.main('released')
    response = HttpResponse(content_type="text/xml")
    # Use the below line for serving the file as attachment (Begin Direct Download)
    # response['Content-Disposition'] = 'attachment; filename=%s' % filename # force browser to download file
    response.write(ET.tostring(data, encoding='unicode', method='xml'))
    return response
