"""
WSGI config for blogsite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

application = get_wsgi_application()


# WSGIScriptAlias / /home/star/Documents/blogsite/blogsite/wsgi.py
# WSGIPythonPath /home/star/Documents/blogsite
#
# <Directory /home/star/Documents/blogsite/blogsite>
# <Files wsgi.py>
# Require all granted
# </Files>
# </Directory>