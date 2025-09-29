from django import template

register = template.Library()


@register.filter(name="add_class")
def add_class(field, css_class):
    """
    Adiciona uma classe CSS a um campo de formulário
    Usage: {{ form.field|add_class:"my-class" }}
    """
    if hasattr(field, "as_widget"):
        return field.as_widget(attrs={"class": css_class})
    return field


@register.filter(name="add_attrs")
def add_attrs(field, attrs_string):
    """
    Adiciona múltiplos atributos a um campo de formulário
    Usage: {{ form.field|add_attrs:"class:my-class,placeholder:Enter text" }}
    """
    if not hasattr(field, "as_widget"):
        return field

    attrs = {}
    for attr_pair in attrs_string.split(","):
        if ":" in attr_pair:
            key, value = attr_pair.split(":", 1)
            attrs[key.strip()] = value.strip()

    return field.as_widget(attrs=attrs)


@register.filter(name="placeholder")
def placeholder(field, text):
    """
    Adiciona placeholder a um campo de formulário
    Usage: {{ form.field|placeholder:"Enter your name" }}
    """
    if hasattr(field, "as_widget"):
        return field.as_widget(attrs={"placeholder": text})
    return field
