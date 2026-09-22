from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Product

@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    list_display = ('title', 'price', 'status', 'short_description')
    
    def short_description(self, obj):
        if obj.description:
            return obj.description[:50] + '...'
        return ''
    
    short_description.short_description = 'description'
    
    # Опционально, чтобы языковые поля группировались по вкладкам
    group_fieldsets = True