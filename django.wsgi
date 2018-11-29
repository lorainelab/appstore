import os
from os.path import join as filejoin
import sys

SITE_PARENT_DIR = '/home/pranav'
SITE_DIR = filejoin(SITE_PARENT_DIR, 'CyAppStore')

sys.path.append(SITE_PARENT_DIR)
sys.path.append(SITE_DIR)


os.environ['PYTHON_EGG_CACHE'] = filejoin(SITE_DIR, '.python-egg')
os.environ['DJANGO_SETTINGS_MODULE'] = 'CyAppStore.settings'

import django
django.setup()

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
