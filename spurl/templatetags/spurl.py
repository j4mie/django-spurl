from django.template import Library, Node, TemplateSyntaxError
from django.template.defaulttags import kwarg_re
from django.utils.encoding import smart_str
from urlobject import URLObject, decode_query

register = Library()

class SpurlNode(Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):

        kwargs = {}
        for key, value in self.kwargs.items():
            key = smart_str(key, 'ascii')
            value = value.resolve(context)

            # If value is empty here, the user probably did something wrong.
            # Django convention is to stay silent, but I think it's probably
            # going to be more helpful to shout loudly here. Maybe this should
            # only happen if we're in DEBUG mode?
            if value == '':
                raise TemplateSyntaxError("'spurl' failed to find a value for the "
                                          "key '%s'. If you are passing a literal "
                                          "string to 'spurl', remember to surround "
                                          "it with quotes." % key)

            kwargs[key] = value

        if 'base' in kwargs:
            url = URLObject.parse(kwargs['base'])
        else:
            url = URLObject()

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
            url = url.with_query(kwargs['query'])

        if 'add_query' in kwargs:
            query_to_add = kwargs['add_query']
            if isinstance(query_to_add, basestring):
                query_to_add = dict(decode_query(query_to_add))
            for key, value in query_to_add.items():
                url = url.add_query_param(key, value)

        return unicode(url)

@register.tag
def spurl(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'spurl' takes at least one argument")

    kwargs = {}
    bits = bits[1:]

    for bit in bits:
        name, value = kwarg_re.match(bit).groups()
        if not (name and value):
            raise TemplateSyntaxError("Malformed arguments to spurl tag")
        kwargs[name] = parser.compile_filter(value)
    return SpurlNode(kwargs)
