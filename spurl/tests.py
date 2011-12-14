from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.http import HttpResponse
from django.template import Template, Context, loader, TemplateSyntaxError
from .templatetags.spurl import convert_to_boolean
import nose

# This file acts as a urlconf
urlpatterns = patterns('',
    url('^test/$', lambda r: HttpResponse('ok'), name='test')
)

# bootstrap django
settings.configure(
    ROOT_URLCONF='spurl.tests',
    INSTALLED_APPS=['spurl.tests'],
)

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

def test_query_from():
    template = """{% spurl base="http://www.google.com/" query_from=url %}"""
    data = {'url': 'http://example.com/some/path/?foo=bar&bar=foo'}
    rendered = render(template, data)
    assert rendered == 'http://www.google.com/?foo=bar&bar=foo'

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

def test_add_query_from():
    template = """{% spurl base="http://www.google.com/?bla=bla&flub=flub" add_query_from=url %}"""
    data = {'url': 'http://example.com/some/path/?foo=bar&bar=foo'}
    rendered = render(template, data)
    assert rendered == 'http://www.google.com/?bla=bla&flub=flub&foo=bar&bar=foo'

def test_set_query_param_from_string():
    template = """{% spurl base="http://www.google.com?something=somethingelse" set_query="something=foo&somethingelse=bar" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com?somethingelse=bar&something=foo'

def test_set_query_param_from_dict_with_variable():
    template = """{% spurl base=myurl set_query=myquery %}"""
    data = {'myurl': 'http://www.google.com?something=somethingelse', 'myquery': {'something': 'foo', 'somethingelse': 'bar'}}
    rendered = render(template, data)
    assert rendered == 'http://www.google.com?somethingelse=bar&something=foo'

def test_toggle_query():
    template = """{% spurl base="http://www.google.com/?foo=bar" toggle_query="bar=first,second" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com/?foo=bar&bar=first'

    template = """{% spurl base="http://www.google.com/?foo=bar&bar=first" toggle_query="bar=first,second" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com/?foo=bar&bar=second'

    template = """{% spurl base="http://www.google.com/?foo=bar&bar=second" toggle_query="bar=first,second" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com/?foo=bar&bar=first'

    template = """{% spurl base="http://www.google.com/?foo=bar&bar=first" toggle_query=to_toggle %}"""
    data = {'to_toggle': {'bar': ('first', 'second')}}
    rendered = render(template, data)
    assert rendered == 'http://www.google.com/?foo=bar&bar=second'

    template = """{% spurl base="http://www.google.com/?foo=bar&bar=second" toggle_query=to_toggle %}"""
    data = {'to_toggle': {'bar': ('first', 'second')}}
    rendered = render(template, data)
    assert rendered == 'http://www.google.com/?foo=bar&bar=first'

def test_multiple_set_query():
    template = """{% spurl base="http://www.google.com/?foo=test" set_query="foo=bar" set_query="bar=baz" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com/?foo=bar&bar=baz'

def test_set_query_param_from_template_variables():
    template = """{% spurl base="http://www.google.com/?foo=bar" set_query="foo={{ var }}" %}"""
    data = {'var': 'baz'}
    rendered = render(template, data)
    assert rendered == 'http://www.google.com/?foo=baz'

def test_empty_parameters_preserved():
    template = """{% spurl base="http://www.google.com/?foo=bar" set_query="bar={{ emptyvar }}" %}"""
    data = {} # does not contain and "emptyvar" key
    rendered = render(template, data)
    assert rendered == 'http://www.google.com/?foo=bar&bar='

def test_none_values_are_removed_when_setting_query():
    template = """{% spurl base="http://www.google.com/?foo=bar" set_query="bar={{ nonevar|default_if_none:'' }}" %}"""
    data = {'nonevar': None}
    rendered = render(template, data)
    assert rendered == 'http://www.google.com/?foo=bar&bar='

def test_set_query_from():
    template = """{% spurl base="http://www.google.com/?bla=bla&foo=something" set_query_from=url %}"""
    data = {'url': 'http://example.com/some/path/?foo=bar&bar=foo'}
    rendered = render(template, data)
    assert rendered == 'http://www.google.com/?bla=bla&foo=bar&bar=foo'

def test_none_values_are_removed_when_adding_query():
    template = """{% spurl base="http://www.google.com/?foo=bar" add_query="bar={{ nonevar|default_if_none:'' }}" %}"""
    data = {'nonevar': None}
    rendered = render(template, data)
    assert rendered == 'http://www.google.com/?foo=bar&bar='

def test_remove_from_query():
    template = """{% spurl base="http://www.google.com/?foo=bar&bar=baz" remove_query_param="foo" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com/?bar=baz'

def test_remove_multiple_params():
    template = """{% spurl base="http://www.google.com/?foo=bar&bar=baz" remove_query_param="foo" remove_query_param="bar" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com/'

def test_remove_param_from_template_variable():
    template = """{% spurl base="http://www.google.com/?foo=bar&bar=baz" remove_query_param=foo remove_query_param=bar %}"""
    data = {'foo': 'foo', 'bar': 'bar'}
    rendered = render(template, data)
    assert rendered == 'http://www.google.com/'

def test_override_scheme():
    template = """{% spurl base="http://google.com" scheme="ftp" %}"""
    rendered = render(template)
    assert rendered == 'ftp://google.com'

def test_scheme_from():
    template = """{% spurl base="http://www.google.com/?bla=bla&foo=bar" scheme_from=url %}"""
    data = {'url': 'https://example.com/some/path/?foo=bar&bar=foo'}
    rendered = render(template, data)
    assert rendered == 'https://www.google.com/?bla=bla&foo=bar'

def test_override_host():
    template = """{% spurl base="http://www.google.com/some/path/" host="www.example.com" %}"""
    rendered = render(template)
    assert rendered == 'http://www.example.com/some/path/'

def test_host_from():
    template = """{% spurl base="http://www.google.com/?bla=bla&foo=bar" host_from=url %}"""
    data = {'url': 'https://example.com/some/path/?foo=bar&bar=foo'}
    rendered = render(template, data)
    assert rendered == 'http://example.com/?bla=bla&foo=bar'

def test_override_path():
    template = """{% spurl base="http://www.google.com/some/path/" path="/another/different/one/" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com/another/different/one/'

def test_path_from():
    template = """{% spurl base="http://www.google.com/original/?bla=bla&foo=bar" path_from=url %}"""
    data = {'url': 'https://example.com/some/path/?foo=bar&bar=foo'}
    rendered = render(template, data)
    assert rendered == 'http://www.google.com/some/path/?bla=bla&foo=bar'

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

def test_add_path_from():
    template = """{% spurl base="http://www.google.com/original/?bla=bla&foo=bar" add_path_from=url %}"""
    data = {'url': 'https://example.com/some/path/?foo=bar&bar=foo'}
    rendered = render(template, data)
    assert rendered == 'http://www.google.com/original/some/path/?bla=bla&foo=bar'

def test_override_fragment():
    template = """{% spurl base="http://www.google.com/#somefragment" fragment="someotherfragment" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com/#someotherfragment'

def test_fragment_from():
    template = """{% spurl base="http://www.google.com/?bla=bla&foo=bar#fragment" fragment_from=url %}"""
    data = {'url': 'https://example.com/some/path/?foo=bar&bar=foo#newfragment'}
    rendered = render(template, data)
    assert rendered == 'http://www.google.com/?bla=bla&foo=bar#newfragment'

def test_override_port():
    template = """{% spurl base="http://www.google.com:80" port="8080" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com:8080'

def test_port_from():
    template = """{% spurl base="http://www.google.com:8000/?bla=bla&foo=bar" port_from=url %}"""
    data = {'url': 'https://example.com:8888/some/path/?foo=bar&bar=foo'}
    rendered = render(template, data)
    assert rendered == 'http://www.google.com:8888/?bla=bla&foo=bar'

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

def test_url_as_template_variable():
    template = """{% spurl base="http://www.google.com" as foo %}The url is {{ foo }}"""
    rendered = render(template)
    assert rendered == 'The url is http://www.google.com'

def test_reversing_inside_spurl_tag():
    template = """{% load url from future %}{% spurl base="http://www.google.com/" path="{\% url 'test' %\}" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com/test/'

    template = """{% load url from future %}{% spurl base="http://www.google.com/" query="next={\% url 'test' %\}" %}"""
    rendered = render(template)
    assert rendered == 'http://www.google.com/?next=/test/'

def test_xzibit():
    template = """Yo dawg, the URL is: {% spurl base="http://www.google.com/" query="foo={\% spurl base='http://another.com' secure='true' %\}" %}"""
    rendered = render(template)
    assert rendered == 'Yo dawg, the URL is: http://www.google.com/?foo=https://another.com'
