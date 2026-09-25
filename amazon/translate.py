import os
import time
import polib
from deep_translator import GoogleTranslator

def translate_po_file(file_path, target_lang):
    po = polib.pofile(file_path)
    translator = GoogleTranslator(source='en', target=target_lang)

    for entry in po:
        if entry.msgid and not entry.msgstr:
            try:
                translated = translator.translate(entry.msgid)
                if translated:
                    entry.msgstr = translated
                    print(f"[{target_lang}] {entry.msgid} -> {translated}")
                time.sleep(0.5)  # Небольшая пауза, чтобы Google не блокировал запросы
            except Exception as e:
                print(f"Skipping '{entry.msgid}' due to error: {e}")

    po.save(file_path)
    print(f"Successfully updated and saved: {file_path}\n")

languages = ['de', 'uk']

for lang in languages:
    po_path = os.path.join('locale', lang, 'LC_MESSAGES', 'django.po')
    if os.path.exists(po_path):
        print(f"Starting translation for: {lang}")
        translate_po_file(po_path, lang)
    else:
        print(f"File not found: {po_path}")
