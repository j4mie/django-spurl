import re
from django.conf import settings
from django.utils.html import escape
from django.utils.encoding import smart_str
from urlobject import URLObject, decode_query
from django.template.base import StringOrigin, Lexer, Parser
from django.template.defaulttags import kwarg_re
from django.utils.datastructures import MultiValueDict
from django.template import Template, Library, Node, TemplateSyntaxError


register = Library()

TRUE_RE = re.compile(r'^(true|on)$', flags=re.IGNORECASE)


def convert_to_boolean(string_or_boolean):
    if isinstance(string_or_boolean, bool):
        return string_or_boolean
    if isinstance(string_or_boolean, basestring):
        return bool(TRUE_RE.match(string_or_boolean))


def unescape_tags(template_string):
    """Spurl allows the use of templatetags inside templatetags, if
    the inner templatetags are escaped - {\% and %\}"""
    return template_string.replace('{\%', '{%').replace('%\}', '%}')


class SpurlNode(Node):
    def __init__(self, kwargs, tags, filters, asvar=None):
        self.kwargs = kwargs
        self.asvar = asvar
        self.tags = tags
        self.filters = filters

    def compile_string(self, template_string, origin):
        """Re-implementation of django.template.base.compile_string
        that takes into account the tags and filter of the parser
        that rendered the parent template"""
        if settings.TEMPLATE_DEBUG:
            from django.template.debug import DebugLexer, DebugParser
            lexer_class, parser_class = DebugLexer, DebugParser
        else:
            lexer_class, parser_class = Lexer, Parser
        lexer = lexer_class(template_string, origin)
        parser = parser_class(lexer.tokenize())

        # Attach the tags and filters from the parent parser
        parser.tags = self.tags
        parser.filters = self.filters

        return parser.parse()

    def render_template(self, template_string, context):
        """Used to render an "inner" template, ie one which
        is passed as an argument to spurl"""
        original_autoescape = context.autoescape
        context.autoescape = False

        template = Template('')
        if settings.TEMPLATE_DEBUG:
            origin = StringOrigin(template_string)
        else:
            origin = None

        template.nodelist = self.compile_string(template_string, origin)

        rendered = template.render(context)
        context.autoescape = original_autoescape
        return rendered

    def render(self, context):

        kwargs = MultiValueDict()
        for key in self.kwargs:
            key = smart_str(key, 'ascii')
            values = [value.resolve(context) for value in self.kwargs.getlist(key)]
            kwargs.setlist(key, values)

        if 'base' in kwargs:
            base = kwargs['base']
            if isinstance(base, basestring):
                base = unescape_tags(base)
                base = self.render_template(base, context)
            url = URLObject.parse(base)
        else:
            url = URLObject(scheme='http')

        if 'secure' in kwargs:
            if convert_to_boolean(kwargs['secure']):
                url = url.with_scheme('https')
            else:
                url = url.with_scheme('http')

        if 'query' in kwargs:
            query = kwargs['query']
            if isinstance(query, basestring):
                query = unescape_tags(query)
                query = self.render_template(query, context)
            url = url.with_query(query)

        if 'add_query' in kwargs:
            for query_to_add in kwargs.getlist('add_query'):
                if isinstance(query_to_add, basestring):
                    query_to_add = unescape_tags(query_to_add)
                    query_to_add = self.render_template(query_to_add, context)
                    query_to_add = dict(decode_query(query_to_add))
                for key, value in query_to_add.items():
                    url = url.add_query_param(key, value)

        if 'set_query' in kwargs:
            for query_to_set in kwargs.getlist('set_query'):
                if isinstance(query_to_set, basestring):
                    query_to_set = unescape_tags(query_to_set)
                    query_to_set = self.render_template(query_to_set, context)
                    query_to_set = dict(decode_query(query_to_set))
                for key, value in query_to_set.items():
                    url = url.set_query_param(key, value)

        if 'remove_query' in kwargs:
            for query_to_remove in kwargs.getlist('remove_query'):
                url = url.without_query_param(query_to_remove)

        if 'scheme' in kwargs:
            url = url.with_scheme(kwargs['scheme'])

        if 'host' in kwargs:
            host = kwargs['host']
            host = unescape_tags(host)
            host = self.render_template(host, context)
            url = url.with_host(host)

        if 'path' in kwargs:
            path = kwargs['path']
            if isinstance(path, basestring):
                path = unescape_tags(path)
                path = self.render_template(path, context)
            url = url.with_path(path)

        if 'add_path' in kwargs:
            for path_to_add in kwargs.getlist('add_path'):
                if isinstance(path_to_add, basestring):
                    path_to_add = unescape_tags(path_to_add)
                    path_to_add = self.render_template(path_to_add, context)
                url = url.add_path_component(path_to_add)

        if 'fragment' in kwargs:
            fragment = kwargs['fragment']
            if isinstance(fragment, basestring):
                fragment = unescape_tags(fragment)
                fragment = self.render_template(fragment, context)
            url = url.with_fragment(fragment)

        if 'port' in kwargs:
            url = url.with_port(kwargs['port'])

        # sensible default
        if not url.host:
            url = url.with_scheme('')

        # Convert the URLObject to its unicode representation
        url = unicode(url)

        # Handle escaping. By default, use the value of
        # context.autoescape. This can be overridden by
        # passing an "autoescape" keyword to the tag.
        if 'autoescape' in kwargs:
            autoescape = convert_to_boolean(kwargs['autoescape'])
        else:
            autoescape = context.autoescape

        if autoescape:
            url = escape(url)

        if self.asvar:
            context[self.asvar] = url
            return ''

        return url


@register.tag
def spurl(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'spurl' takes at least one argument")

    kwargs = MultiValueDict()
    asvar = None
    bits = bits[1:]

    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]

    for bit in bits:
        name, value = kwarg_re.match(bit).groups()
        if not (name and value):
            raise TemplateSyntaxError("Malformed arguments to spurl tag")
        kwargs.appendlist(name, parser.compile_filter(value))
    return SpurlNode(kwargs, parser.tags, parser.filters, asvar)
