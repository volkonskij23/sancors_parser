from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import json
import time

"""
    Функция чтения json-файла

    :param     filename: Название файла
    :type      filename: str.
    
    :returns: dict или list
"""
def json_load(filename):
    with open(filename, "r", encoding="utf8") as read_file:
        result = json.load(read_file)
    return result

"""
    Функция записи в json-файл

    :param     filename: Название файла
    :type      filename: str.
    :param     data: Записываемые данные
    :type      data: list or dict.
  
"""
def json_dump(filename, data):
    with open(filename, "w", encoding="utf8") as write_file:
        json.dump(data, write_file, ensure_ascii=False)


"""
    Функция получения списка ссылок на товар
    
    :returns: list
"""
def get_urls():
    url = "https://sancors.ru/info/brands/bas/?PAGEN_2={}"
    products_urls = []
    for page in range(1, 13):
        driver.get(url.format(page))
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "thumb"))
        )

        cards = driver.find_elements(
            By.CLASS_NAME,
            "col-lg-3.col-md-4.col-sm-6.col-xs-6.col-xxs-12.item.item-parent.catalog-block-view__item.js-notice-block.item_block",
        )

        for card in cards:
            card_url = card.find_element(By.CLASS_NAME, "thumb").get_attribute("href")
            products_urls.append(card_url)

    return products_urls



try:
    result = json_load("result.json")
except:
    result = {}
    
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

products_urls = get_urls()

for url in products_urls:
    if url not in result.keys():
        try:
            result[url] = {}
            driver.get(url + "#desc")
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "content"))
            )
            result[url]["imgs"] = []
            img_block = driver.find_element(
                By.CLASS_NAME,
                "product-detail-gallery__slider.owl-carousel.owl-theme.big.owl-bg-nav.short-nav.square.owl-loaded.owl-drag",
            )

            for link in img_block.find_elements(By.TAG_NAME, "a"):
                result[url]["imgs"].append(link.get_attribute("href"))

            result[url]["name"] = driver.find_element(By.ID, "pagetitle").text
            result[url]["artikul"] = driver.find_element(
                By.CLASS_NAME, "article__value"
            ).text
            result[url]["path"] = driver.find_element(
                By.CLASS_NAME, "breadcrumbs.swipeignore"
            ).text
            result[url]["price"] = driver.find_element(
                By.CLASS_NAME, "values_wrapper"
            ).text
            result[url]["desc"] = driver.find_element(By.CLASS_NAME, "content").text

            try:
                driver.get(url + "#props")
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "props_list.nbg"))
                )

                props = driver.find_elements(By.TAG_NAME, "tr")
                for tr in props:
                    tds = tr.find_elements(By.TAG_NAME, "td")
                    char_name = tds[0].text
                    if len(char_name) > 2:
                        result[url][char_name] = tds[1].text
            except:
                props_block = driver.find_elements(
                    By.CLASS_NAME, "properties__item.properties__item--compact.font_xs"
                )
                for prop in props_block:
                    char_name = prop.find_element(
                        By.CLASS_NAME,
                        "properties__title.muted.properties__item--inline",
                    ).text
                    if len(char_name) > 2:
                        result[url][char_name] = prop.find_element(
                            By.CLASS_NAME,
                            "properties__value.darken.properties__item--inline",
                        ).text
        except:
            json_dump("result.json", result)
            continue
        time.sleep(5)


json_dump("result.json", result)
