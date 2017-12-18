from django.template import Library
from decimal import Decimal


register = Library()


@register.filter
def get_linked_field_value(form, linked_field):
    """
    Defining if current form instance has a value in a link field to the parent model if it is Update model
    """
    for field in form:
        if field.name == linked_field:
            linked_field_value = form.initial.get(field.name)
            return linked_field_value
    return hasattr(object, linked_field)
