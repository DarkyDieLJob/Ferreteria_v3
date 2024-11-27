# templatetags/my_tags.py
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag(takes_context=True)
def render_buttons(context, button_list:dict):
    output = ''
    for button_data in button_list:
        output += f'<button class="{button_data["class"]}">{button_data["text"]}</button>'
    return mark_safe(output)

@register.simple_tag(takes_context=True)
def render_button(context, button_data:dict):
    return mark_safe(f'<button class="{button_data["class"]}">{button_data["text"]}</button>')