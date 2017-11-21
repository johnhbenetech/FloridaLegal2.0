from django.template import Library

import re
register = Library()

@register.simple_tag
def str_replace(search, replace, subject):
    return re.sub(search,replace,subject)