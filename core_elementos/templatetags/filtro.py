from django import template

register = template.Library()

@register.filter
def get_attr(objeto, nombre_atributo):
    if isinstance(objeto, dict):
        # Si objeto es un dict, usar la sintaxis de acceso a las claves
        return objeto.get(nombre_atributo)
    else:
        # Si objeto es un objeto, usar la sintaxis de acceso a los atributos
        return getattr(objeto, nombre_atributo, None)
