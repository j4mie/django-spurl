from django.template import Library, Node, TemplateSyntaxError
from django.template.defaulttags import kwarg_re
from django.utils.encoding import smart_str

register = Library()

class SpurlNode(Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):

        kwargs = dict([(smart_str(k, 'ascii'), v.resolve(context))
                       for k, v in self.kwargs.items()])

        return kwargs['base']

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
