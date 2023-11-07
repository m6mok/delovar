import os
import sys
import platform


if 1:
    sys.path.insert(0, '/home/c/cn57892/delovar/public_html/delovar')
    sys.path.insert(0, '/home/c/cn57892/delovar/public_html/delovar/delovar')
    sys.path.insert(0, '/home/c/cn57892/delovar/venv/lib/python{0}/site-packages'.format(platform.python_version()[0:3]))
    os.environ["DJANGO_SETTINGS_MODULE"] = "delovar.settings"
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delovar.settings')


from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
