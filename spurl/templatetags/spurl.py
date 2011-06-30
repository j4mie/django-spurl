from django import template
from templatetag_sugar.register import tag
from templatetag_sugar.parser import Name, Variable, Constant, Optional, Model

register = template.Library()

@tag(register, [Variable()])
def spurl(context, base_url):
    return base_url
