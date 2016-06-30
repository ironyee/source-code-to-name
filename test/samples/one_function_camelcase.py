"""
from: https://github.com/django/django/blob/master/django/core/wsgi.py
"""
import django
from django.core.handlers.wsgi import WSGIHandler


def getWsgiApplication():
    django.setup(set_prefix=False)
    return WSGIHandler()