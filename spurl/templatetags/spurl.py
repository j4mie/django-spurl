import re
from django.conf import settings
from django.utils.html import escape
from django.utils.encoding import smart_str
from urlobject import URLObject
from urlobject.query_string import QueryString
from django.template import StringOrigin, Lexer, Parser
from django.template.defaulttags import kwarg_re
from django.template import Template, Library, Node, TemplateSyntaxError


register = Library()

TRUE_RE = re.compile(r'^(true|on)$', flags=re.IGNORECASE)


def convert_to_boolean(string_or_boolean):
    if isinstance(string_or_boolean, bool):
        return string_or_boolean
    if isinstance(string_or_boolean, basestring):
        return bool(TRUE_RE.match(string_or_boolean))


class SpurlURLBuilder(object):

    def __init__(self, args, context, tags, filters):
        self.args = args
        self.context = context
        self.tags = tags
        self.filters = filters
        self.autoescape = self.context.autoescape
        self.url = URLObject()

    def build(self):
        for argument, value in self.args:
            self.handle_argument(argument, value)

        self.set_sensible_defaults()

        url = unicode(self.url)

        if self.autoescape:
            url = escape(url)

        return url

    def handle_argument(self, argument, value):
        argument = smart_str(argument, 'ascii')
        handler_name = 'handle_%s' % argument
        handler = getattr(self, handler_name, None)

        if handler is not None:
            value = value.resolve(self.context)
            handler(value)

    def handle_base(self, value):
        base = self.prepare_value(value)
        self.url = URLObject(base)

    def handle_secure(self, value):
        is_secure = convert_to_boolean(value)
        scheme = 'https' if is_secure else 'http'
        self.url = self.url.with_scheme(scheme)

    def handle_query(self, value):
        query = self.prepare_value(value)
        if isinstance(query, dict):
            query = QueryString().set_params(**query)
        self.url = self.url.with_query(QueryString(query))

    def handle_query_from(self, value):
        url = URLObject(value)
        self.url = self.url.with_query(url.query)

    def handle_add_query(self, value):
        query_to_add = self.prepare_value(value)
        if isinstance(query_to_add, basestring):
            query_to_add = QueryString(query_to_add).dict
        self.url = self.url.add_query_params(**query_to_add)

    def handle_add_query_from(self, value):
        url = URLObject(value)
        self.url = self.url.add_query_params(**url.query.dict)

    def handle_set_query(self, value):
        query_to_set = self.prepare_value(value)
        if isinstance(query_to_set, basestring):
            query_to_set = QueryString(query_to_set).dict
        self.url = self.url.set_query_params(**query_to_set)

    def handle_set_query_from(self, value):
        url = URLObject(value)
        self.url = self.url.set_query_params(**url.query.dict)

    def handle_remove_query_param(self, value):
        self.url = self.url.del_query_param(value)

    def handle_toggle_query(self, value):
        query_to_toggle = self.prepare_value(value)
        if isinstance(query_to_toggle, basestring):
            query_to_toggle = QueryString(query_to_toggle).dict
        current_query = self.url.query.dict
        for key, value in query_to_toggle.items():
            if isinstance(value, basestring):
                value = value.split(',')
            first, second = value
            if key in current_query and first in current_query[key]:
                self.url = self.url.set_query_param(key, second)
            else:
                self.url = self.url.set_query_param(key, first)

    def handle_scheme(self, value):
        self.url = self.url.with_scheme(value)

    def handle_scheme_from(self, value):
        url = URLObject(value)
        self.url = self.url.with_scheme(url.scheme)

    def handle_host(self, value):
        host = self.prepare_value(value)
        self.url = self.url.with_hostname(host)

    def handle_host_from(self, value):
        url = URLObject(value)
        self.url = self.url.with_hostname(url.hostname)

    def handle_path(self, value):
        path = self.prepare_value(value)
        self.url = self.url.with_path(path)

    def handle_path_from(self, value):
        url = URLObject(value)
        self.url = self.url.with_path(url.path)

    def handle_add_path(self, value):
        path_to_add = self.prepare_value(value)
        self.url = self.url.add_path(path_to_add)

    def handle_add_path_from(self, value):
        url = URLObject(value)
        path_to_add = url.path
        if path_to_add.startswith('/'):
            path_to_add = path_to_add[1:]
        self.url = self.url.add_path(path_to_add)

    def handle_fragment(self, value):
        fragment = self.prepare_value(value)
        self.url = self.url.with_fragment(fragment)

    def handle_fragment_from(self, value):
        url = URLObject(value)
        self.url = self.url.with_fragment(url.fragment)

    def handle_port(self, value):
        self.url = self.url.with_port(int(value))

    def handle_port_from(self, value):
        url = URLObject(value)
        self.url = self.url.with_port(url.port)

    def handle_autoescape(self, value):
        self.autoescape = convert_to_boolean(value)

    def set_sensible_defaults(self):
        if self.url.hostname and not self.url.scheme:
            self.url = self.url.with_scheme('http')

    def prepare_value(self, value):
        """Prepare a value by unescaping embedded template tags
        and rendering through Django's template system"""
        if isinstance(value, basestring):
            value = self.unescape_tags(value)
            value = self.render_template(value)
        return value

    def unescape_tags(self, template_string):
        """Spurl allows the use of templatetags inside templatetags, if
        the inner templatetags are escaped - {\% and %\}"""
        return template_string.replace('{\%', '{%').replace('%\}', '%}')

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

    def render_template(self, template_string):
        """Used to render an "inner" template, ie one which
        is passed as an argument to spurl"""
        original_autoescape = self.context.autoescape
        self.context.autoescape = False

        template = Template('')
        if settings.TEMPLATE_DEBUG:
            origin = StringOrigin(template_string)
        else:
            origin = None

        template.nodelist = self.compile_string(template_string, origin)

        rendered = template.render(self.context)
        self.context.autoescape = original_autoescape
        return rendered


class SpurlNode(Node):

    def __init__(self, args, tags, filters, asvar=None):
        self.args = args
        self.asvar = asvar
        self.tags = tags
        self.filters = filters

    def render(self, context):
        builder = SpurlURLBuilder(self.args, context, self.tags, self.filters)
        url = builder.build()

        if self.asvar:
            context[self.asvar] = url
            return ''

        return url


@register.tag
def spurl(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'spurl' takes at least one argument")

    args = []
    asvar = None
    bits = bits[1:]

    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]

    for bit in bits:
        name, value = kwarg_re.match(bit).groups()
        if not (name and value):
            raise TemplateSyntaxError("Malformed arguments to spurl tag")
        args.append((name, parser.compile_filter(value)))
    return SpurlNode(args, parser.tags, parser.filters, asvar)
