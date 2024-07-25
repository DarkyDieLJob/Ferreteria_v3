from django.template import Library
register = Library()

@register.filter
def custom_price(price):
    if price > 1000:
        price = round(price / 500) * 500
    else:
        price = round(price / 50) * 50

    if price != 0 and price % 1000 == 0:
        price -= 100

    return price


@register.filter
def zip_lists(a, b):
    return zip(a, b)

@register.filter
def to_float(value):
    value = float(value)
    value = value * 1.15
    if value > 10:
        value = round(value / 10) * 10
    else:
        value = int(value)
    return value

@register.filter
def en_lista(value):
    partes = value.split("/")
    if len(partes) > 1:
        letras = partes[1]
        valor = "/" + str(letras)
        mi_lista = ["/Nc","/Dx","/B", "/Cb", "/3D", "/F",]
        bool = True
        if valor in mi_lista:
            bool = False
    else:
        bool = True
    return bool



