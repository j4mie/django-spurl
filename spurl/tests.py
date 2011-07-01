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

@nose.tools.raises(TemplateSyntaxError)
def test_malformed_args_raises_exception():
    render("""{% spurl something %}""")

@nose.tools.raises(TemplateSyntaxError)
def test_missing_quotes_raises_exception():
    render("""{% spurl base="http://www.google.com" secure=True %}""")

def test_passthrough():
    template = """{% spurl base="http://www.google.com" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com'

def test_url_in_variable():
    template = """{% spurl base=myurl %}"""
    data = {'myurl': 'http://www.google.com'}
    rendered = render(template, data)
    assert rendered == 'http://www.google.com'

def test_make_secure():
    template = """{% spurl base="http://www.google.com" secure="True" %}"""
    rendered = render(template)
    assert rendered == 'https://www.google.com'

def test_make_secure_with_variable():
    template = """{% spurl base=myurl secure=is_secure %}"""
    data = {'myurl': 'http://www.google.com', 'is_secure': True}
    rendered = render(template, data)
    assert rendered == 'https://www.google.com'

def test_make_insecure():
    template = """{% spurl base="https://www.google.com" secure="False" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com'

def test_make_insecure_with_variable():
    template = """{% spurl base=myurl secure=is_secure %}"""
    data = {'myurl': 'https://www.google.com', 'is_secure': False}
    rendered = render(template, data)
    assert rendered == 'http://www.google.com'

def test_set_query_from_string():
    template = """{% spurl base="http://www.google.com" query="foo=bar&bar=foo" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com?foo=bar&bar=foo'

def test_set_query_from_string_with_variable():
    template = """{% spurl base=myurl query=myquery %}"""
    data = {'myurl': 'http://www.google.com', 'myquery': 'foo=bar&bar=foo'}
    rendered = render(template, data)
    assert rendered == 'http://www.google.com?foo=bar&bar=foo'

def test_set_query_from_dict_with_variable():
    template = """{% spurl base=myurl query=myquery %}"""
    data = {'myurl': 'http://www.google.com', 'myquery': {'foo': 'bar', 'bar': 'foo'}}
    rendered = render(template, data)
    assert rendered == 'http://www.google.com?foo=bar&bar=foo'

def test_set_query_removes_existing_query():
    template = """{% spurl base="http://www.google.com?something=somethingelse" query="foo=bar&bar=foo" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com?foo=bar&bar=foo'

def test_add_to_query_from_string():
    template = """{% spurl base="http://www.google.com?something=somethingelse" add_query="foo=bar&bar=foo" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com?something=somethingelse&foo=bar&bar=foo'

def test_add_to_query_from_dict_with_variable():
    template = """{% spurl base=myurl add_query=myquery %}"""
    data = {'myurl': 'http://www.google.com?something=somethingelse', 'myquery': {'foo': 'bar', 'bar': 'foo'}}
    rendered = render(template, data)
    assert rendered == 'http://www.google.com?something=somethingelse&foo=bar&bar=foo'

def test_override_scheme():
    template = """{% spurl base="http://google.com" scheme="ftp" %}"""
    rendered = render(template)
    assert rendered == 'ftp://google.com'

def test_override_host():
    template = """{% spurl base="http://www.google.com/some/path/" host="www.example.com" %}"""
    rendered = render(template)
    assert rendered == 'http://www.example.com/some/path/'

def test_override_path():
    template = """{% spurl base="http://www.google.com/some/path/" path="/another/different/one/" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com/another/different/one/'

def test_override_fragment():
    template = """{% spurl base="http://www.google.com/#somefragment" fragment="someotherfragment" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com/#someotherfragment'
