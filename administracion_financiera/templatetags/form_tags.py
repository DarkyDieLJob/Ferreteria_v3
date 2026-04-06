from django import template

register = template.Library()

@register.filter(name="add_class")
def add_class(field, css):
    try:
        return field.as_widget(attrs={"class": css})
    except Exception:
        return field

@register.filter(name="add_attrs")
def add_attrs(field, attrs_str):
    attrs = {}
    for chunk in attrs_str.split(","):
        if not chunk.strip():
            continue
        if ":" in chunk:
            k, v = chunk.split(":", 1)
            attrs[k.strip()] = v.strip()
        else:
            attrs[chunk.strip()] = ""
    try:
        return field.as_widget(attrs=attrs)
    except Exception:
        return field
