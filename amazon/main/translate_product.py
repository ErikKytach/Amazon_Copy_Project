from deep_translator import GoogleTranslator
import time
import os
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def translate_via_google_translate(text: str, source_lang: str = "auto", target_lang: str = "en") -> str:
    options = webdriver.ChromeOptions()

    # Путь к системному Chromium и флаги для headless-сервера
    options.binary_location = "/usr/bin/chromium"
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=en-US")
    options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/131.0.0.0 Safari/537.36"
    )

    # Привязка к системному ChromeDriver v131
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        encoded_text = urllib.parse.quote(text)
        url = f"https://translate.google.com/?sl={source_lang}&tl={target_lang}&text={encoded_text}&op=translate&hl=en"

        driver.get(url)
        wait = WebDriverWait(driver, 10)

        # 1. Согласие с куки
        try:
            cookie_btn = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button//span[contains(text(), 'Accept all')]")
                )
            )
            cookie_btn.click()
            time.sleep(1)
        except Exception:
            pass

        # 2. Ожидание и сбор текста перевода
        wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                f"//span[@class='ryNqvb'] | //span[@lang='{target_lang}']",
            ))
        )

        spans = driver.find_elements(By.XPATH, "//span[@class='ryNqvb']")
        if not spans:
            spans = driver.find_elements(
                By.XPATH, f"//span[@lang='{target_lang}']"
            )

        translation = " ".join([span.text for span in spans if span.text])
        return translation.strip()

    except Exception as e:
        driver.save_screenshot("headless_error.png")
        return f"Ошибка (подробности на скриншоте headless_error.png): {e}"
    finally:
        try:
            driver.quit()
        except Exception:
            pass
translator_en = GoogleTranslator(source="auto", target="en")
translator_de = GoogleTranslator(source="auto", target="de")
translator_uk = GoogleTranslator(source="auto", target="uk")

def translate_product(title, description):
    trans_query = f"{title} ||||| {description}"

    en_translated = translator_en.translate(trans_query)
    time.sleep(0.5)

    de_translated = translator_de.translate(trans_query)
    time.sleep(0.5)

    uk_translated = translator_uk.translate(trans_query)

    parts_en = en_translated.split("|||||")
    title_en = parts_en[0]
    description_en = parts_en[1]

    parts_de = de_translated.split("|||||")
    title_de = parts_de[0]
    description_de = parts_de[1]

    parts_uk = uk_translated.split("|||||")
    title_uk = parts_uk[0]
    description_uk = parts_uk[1]

    result = {}
    result["title_en"] = title_en
    result["title_de"] = title_de
    result["title_uk"] = title_uk

    result["description_en"] = description_en
    result["description_de"] = description_de
    result["description_uk"] = description_uk

    return result

def translate_product_title(title):
    title_en = translator_en.translate(title)
    time.sleep(0.5)

    title_de = translator_de.translate(title)
    time.sleep(0.5)

    title_uk = translator_uk.translate(title)

    result = {
        "title_en": title_en,
        "title_de": title_de,
        "title_uk": title_uk
    }
    return result

def translate_product_description(description):
    desc_en = translator_en.translate(description)
    time.sleep(0.5)

    desc_de = translator_de.translate(description)
    time.sleep(0.5)

    desc_uk = translator_uk.translate(description)

    result = {
        "description_en": desc_en,
        "description_de": desc_de,
        "description_uk": desc_uk
    }
    return result