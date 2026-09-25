import os
import django

#settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amazon.settings')
django.setup()

from main.models import Category

with open('dummy_categories.py', 'w', encoding='utf-8') as f:
    f.write("from django.utils.translation import gettext as _\n\n")
    for cat in Category.objects.all():
        # writing every category like  _("categoryName")
        f.write(f'_("{cat.name}")\n')

print("categories are now in dummy_categories.py")