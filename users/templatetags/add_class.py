from django import template
register = template.Library()

@register.filter
def add_class(field, class_name):

    widget_class = ''
    if 'class' in field.field.widget.attrs:
        widget_class = field.field.widget.attrs['class']

    return field.as_widget(attrs={
        "class": " ".join((widget_class, class_name))
    })