from django.template import Template, Library, Node, TemplateSyntaxError
from django.template.defaulttags import kwarg_re
from django.utils.encoding import smart_str
from django.utils.datastructures import MultiValueDict
from django.utils.html import escape
from urlobject import URLObject, decode_query

register = Library()

def render_template_from_string_without_autoescape(template_string, context):
    context_copy = context.__copy__()
    context_copy.autoescape = False
    return Template(template_string).render(context_copy)


class SpurlNode(Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):

        kwargs = MultiValueDict()
        for key in self.kwargs:
            key = smart_str(key, 'ascii')
            values = [value.resolve(context) for value in self.kwargs.getlist(key)]

            # If value is empty here, the user probably did something wrong.
            # Django convention is to stay silent, but I think it's probably
            # going to be more helpful to shout loudly here. Maybe this should
            # only happen if we're in DEBUG mode?
            for value in values:
                if value == '':
                    raise TemplateSyntaxError("'spurl' failed to find a value for the "
                                              "key '%s'. If you are passing a literal "
                                              "string to 'spurl', remember to surround "
                                              "it with quotes." % key)

            kwargs.setlist(key, values)

        if 'base' in kwargs:
            url = URLObject.parse(kwargs['base'])
        else:
            url = URLObject(scheme='http')

        if 'secure' in kwargs:
            secure = kwargs['secure']
            if isinstance(secure, basestring):
                if secure.lower() == 'true':
                    secure = True
                else:
                    secure = False
            if secure:
                url = url.with_scheme('https')
            else:
                url = url.with_scheme('http')

        if 'query' in kwargs:
            query = kwargs['query']
            if isinstance(query, basestring):
                query = render_template_from_string_without_autoescape(query, context)
            url = url.with_query(query)

        if 'add_query' in kwargs:
            for query_to_add in kwargs.getlist('add_query'):
                if isinstance(query_to_add, basestring):
                    query_to_add = render_template_from_string_without_autoescape(query_to_add, context)
                    query_to_add = dict(decode_query(query_to_add))
                for key, value in query_to_add.items():
                    url = url.add_query_param(key, value)

        if 'scheme' in kwargs:
            url = url.with_scheme(kwargs['scheme'])

        if 'host' in kwargs:
            url = url.with_host(kwargs['host'])

        if 'path' in kwargs:
            url = url.with_path(kwargs['path'])

        if 'add_path' in kwargs:
            for path_to_add in kwargs.getlist('add_path'):
                url = url.add_path_component(path_to_add)

        if 'fragment' in kwargs:
            url = url.with_fragment(kwargs['fragment'])

        if 'port' in kwargs:
            url = url.with_port(kwargs['port'])

        # sensible default
        if not url.host:
            url = url.with_scheme('')

        # Convert the URLObject to its unicode representation
        url = unicode(url)

        # Handle escaping. By default, use the value of
        # context.autoescape. This can be overridden by
        # passing and "autoescape" keyword to the tag.
        if 'autoescape' in kwargs:
            autoescape = kwargs['autoescape']
            if isinstance(autoescape, basestring):
                autoescape = autoescape.lower() == 'true'
        else:
            autoescape = context.autoescape

        if autoescape:
            url = escape(url)

        return url

@register.tag
def spurl(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'spurl' takes at least one argument")

    kwargs = MultiValueDict()
    bits = bits[1:]

    for bit in bits:
        name, value = kwarg_re.match(bit).groups()
        if not (name and value):
            raise TemplateSyntaxError("Malformed arguments to spurl tag")
        kwargs.appendlist(name, parser.compile_filter(value))
    return SpurlNode(kwargs)
