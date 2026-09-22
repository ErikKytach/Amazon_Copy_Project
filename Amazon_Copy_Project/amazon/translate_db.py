import os
import time
import django
from deep_translator import GoogleTranslator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amazon.settings')
django.setup()

from main.models import Product

def translate_products():
    translator_de = GoogleTranslator(source='auto', target='de')
    translator_uk = GoogleTranslator(source='auto', target='uk')

    products = Product.objects.all()
    print(f"Найдено товаров для проверки: {products.count()}")

    for product in products:
        updated = False

        # Если немецкий перевод совпадает с английским оригиналом или пуст — переводим
        if product.title and (not product.title_de or product.title_de == product.title):
            try:
                product.title_de = translator_de.translate(product.title)
                updated = True
            except Exception as e:
                print(f"Ошибка перевода title_de для {product.id}: {e}")

        # Украинский перевод
        if product.title and (not product.title_uk or product.title_uk == product.title):
            try:
                product.title_uk = translator_uk.translate(product.title)
                updated = True
            except Exception as e:
                print(f"Ошибка перевода title_uk для {product.id}: {e}")

        # Описание (немецкий)
        if product.description and (not product.description_de or product.description_de == product.description):
            try:
                product.description_de = translator_de.translate(product.description)
                updated = True
            except Exception as e:
                print(f"Ошибка перевода description_de для {product.id}: {e}")

        # Описание (украинский)
        if product.description and (not product.description_uk or product.description_uk == product.description):
            try:
                product.description_uk = translator_uk.translate(product.description)
                updated = True
            except Exception as e:
                print(f"Ошибка перевода description_uk для {product.id}: {e}")

        if updated:
            product.save()
            print(f"[OK] Успешно переведен товар ID {product.id}: {product.title}")
            time.sleep(0.5)  # Пауза, чтобы не поймать 500/rate-limit от Google

if __name__ == "__main__":
    translate_products()