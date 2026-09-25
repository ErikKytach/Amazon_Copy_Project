from django import template
from django.utils.translation import get_language
from deep_translator import GoogleTranslator

register = template.Library()

@register.filter(name='translate_text')
def translate_text(text):
    if not text:
        return ""

    current_lang = get_language()
    if not current_lang:
        return text

    try:
        translated = GoogleTranslator(source='auto', target=current_lang).translate(text)
        return translated
    except Exception as e:
        return text