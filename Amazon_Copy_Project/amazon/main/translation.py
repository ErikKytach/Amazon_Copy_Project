from modeltranslation.translator import register, TranslationOptions
from main.models import Product

@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('title', 'description')