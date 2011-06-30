# bootstrap django
from django.conf import settings
settings.configure()#INSTALLED_APPS=('spurl',))

from django.template import Template, Context, loader

loader.add_to_builtins('spurl.templatetags.spurl')

def render(template_string, dictionary=None):
    return Template(template_string).render(Context(dictionary))

def test_passthrough():
    template = """{% spurl "http://www.google.com" %}"""
    assert render(template) == 'http://www.google.com'

def test_url_in_variable():
    template = """{% spurl myurl %}"""
    data = {'myurl': 'http://www.google.com'}
    assert render(template, data) == 'http://www.google.com'
