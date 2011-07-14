from django.conf import settings
from django.template import Template, Context, loader, TemplateSyntaxError
from .templatetags.spurl import convert_to_boolean
import nose

# bootstrap django
settings.configure()

# add spurl to builtin tags
loader.add_to_builtins('spurl.templatetags.spurl')

def render(template_string, dictionary=None, autoescape=False):
    """
    Render a template from the supplied string, with optional context data.

    This differs from Django's normal template system in that autoescaping
    is disabled by default. This is simply to make the tests below easier
    to read and write. You can re-enable the default behavior by passing True
    as the value of the autoescape parameter
    """
    context = Context(dictionary, autoescape=autoescape)
    return Template(template_string).render(context)

def test_convert_argument_value_to_boolean():
    assert convert_to_boolean(True) is True
    assert convert_to_boolean(False) is False
    assert convert_to_boolean("True") is True
    assert convert_to_boolean("true") is True
    assert convert_to_boolean("On") is True
    assert convert_to_boolean("on") is True
    assert convert_to_boolean("False") is False
    assert convert_to_boolean("false") is False
    assert convert_to_boolean("Off") is False
    assert convert_to_boolean("off") is False
    assert convert_to_boolean("randomstring") is False

@nose.tools.raises(TemplateSyntaxError)
def test_noargs_raises_exception():
    render("""{% spurl %}""")

@nose.tools.raises(TemplateSyntaxError)
def test_malformed_args_raises_exception():
    render("""{% spurl something %}""")

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

def test_set_query_from_template_variables():
    template = """{% spurl base=myurl query="foo={{ first_var }}&bar={{ second_var }}" %}"""
    data = {'myurl': 'http://www.google.com', 'first_var': 'bar', 'second_var': 'baz'}
    rendered = render(template, data)
    assert rendered == 'http://www.google.com?foo=bar&bar=baz'

def test_set_query_from_template_variables_not_double_escaped():
    template = """{% spurl base="http://www.google.com" query="{{ query }}" %}"""
    data = {'query': 'foo=bar&bar=foo'}
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

def test_multiple_add_query():
    template = """{% spurl base="http://www.google.com/" add_query="foo=bar" add_query="bar=baz" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com/?foo=bar&bar=baz'

def test_add_to_query_from_template_variables():
    template = """{% spurl base="http://www.google.com/?foo=bar" add_query="bar={{ var }}" %}"""
    data = {'var': 'baz'}
    rendered = render(template, data)
    assert rendered == 'http://www.google.com/?foo=bar&bar=baz'

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

def test_add_path():
    template = """{% spurl base="http://www.google.com/some/path/" add_path="another/" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com/some/path/another/'

def test_multiple_add_path():
    template = """{% spurl base="http://www.google.com/" add_path="some" add_path="another/" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com/some/another/'

def test_multiple_add_path_from_template_variables():
    """Usage example for building media urls"""
    template = """{% spurl base=STATIC_URL add_path="javascript" add_path="lib" add_path="jquery.js" %}"""
    data = {'STATIC_URL': 'http://cdn.example.com'}
    rendered = render(template, data)
    assert rendered == 'http://cdn.example.com/javascript/lib/jquery.js'

def test_override_fragment():
    template = """{% spurl base="http://www.google.com/#somefragment" fragment="someotherfragment" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com/#someotherfragment'

def test_override_port():
    template = """{% spurl base="http://www.google.com:80" port="8080" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com:8080'

def test_build_complete_url():
    template = """{% spurl scheme="http" host="www.google.com" path="/some/path/" port="8080" fragment="somefragment" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com:8080/some/path/#somefragment'

def test_sensible_defaults():
    template = """{% spurl path="/some/path/" %}"""
    rendered = render(template)
    assert rendered == '/some/path/'

    template = """{% spurl path="/some/path/" host="www.google.com" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com/some/path/'

def test_autoescaping():
    template = """{% spurl base="http://www.google.com" query="a=b" add_query="c=d" add_query="e=f" fragment="frag" %}"""
    rendered = render(template, autoescape=True) # Ordinarily, templates will be autoescaped by default
    assert rendered == 'http://www.google.com?a=b&amp;c=d&amp;e=f#frag'

def test_disable_autoescaping_with_parameter():
    template = """{% spurl base="http://www.google.com" query="a=b" add_query="c=d" autoescape="False" %}"""
    rendered = render(template, autoescape=True)
    assert rendered == 'http://www.google.com?a=b&c=d'
