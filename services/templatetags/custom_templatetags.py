from django.template import Library
from decimal import Decimal


register = Library()


@register.filter
def get_linked_field_value(form, linked_field):
    for field in form:
        if field.name == linked_field:
            a = form.initial.get(field.name)
            return a
    return getattr(object, linked_field)
