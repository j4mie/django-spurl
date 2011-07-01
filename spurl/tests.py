from django.conf import settings
from django.template import Template, Context, loader, TemplateSyntaxError
import nose

# bootstrap django
settings.configure()

# add spurl to builtin tags
loader.add_to_builtins('spurl.templatetags.spurl')

def render(template_string, dictionary=None):
    return Template(template_string).render(Context(dictionary))

@nose.tools.raises(TemplateSyntaxError)
def test_noargs_raises_exception():
    render("""{% spurl %}""")

def test_passthrough():
    template = """{% spurl base="http://www.google.com" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com'

def test_url_in_variable():
    template = """{% spurl base=myurl %}"""
    data = {'myurl': 'http://www.google.com'}
    rendered = render(template, data)
    assert rendered == 'http://www.google.com'
