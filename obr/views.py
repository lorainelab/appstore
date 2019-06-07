from django.http import HttpResponse
from django.conf import settings
import os
from . import repogen


def serve_file(request):
    os.remove(settings.MEDIA_ROOT + '/pending_releases/repository.xml')
    get_status = repogen.main()
    if get_status:
        filepath = '/pending_releases/repository.xml'
        with open(settings.MEDIA_ROOT + filepath, 'r') as fp:
            data = fp.read()
        response = HttpResponse(content_type="text/xml")
        # response['Content-Disposition'] = 'attachment; filename=%s' % filename # force browser to download file
        response.write(data)
    else:
        response = HttpResponse(content_type="text/raw")
        response.write("Repository XML Failed to generate")
    return response
