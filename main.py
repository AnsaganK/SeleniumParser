from pip._vendor import requests
from selenium import webdriver
import csv
import time
from bs4 import BeautifulSoup as BS
from constants import CHROME_PATH, IS_LINUX
from datetime import datetime
import re
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

INDEX = 0
FILE_NAME = 'hotels.csv'  # Назавние файла для сохранения
# QUERY = 'lawn care New york'  # Запрос в поиске
QUERY = 'Отели в москве'  # Запрос в поиске
URL = f'https://www.google.com/search?q={QUERY}&newwindow=1&tbm=lcl&sxsrf=AOaemvJF91rSXoO-Kt8Dcs2gkt9_JXLlCQ%3A1632305149583&ei=_f9KYayPI-KExc8PlcaGqA4&oq={QUERY}&gs_l=psy-ab.3...5515.12119.0.12483.14.14.0.0.0.0.0.0..0.0....0...1c.1.64.psy-ab..14.0.0....0.zLZdDbmH5so#rlfi=hd:;'
PAGE = 100  # Количество страниц для парсинга

KEY = 'AIzaSyAbOkxUWUw9z54up8AiMSCMX7rO7-8hqv8'
CID_API_URL = 'https://maps.googleapis.com/maps/api/place/details/json?cid={0}&key='+KEY
CID_URL = 'https://maps.google.com/?cid={0}'

display = None

if IS_LINUX:
    from pyvirtualdisplay import Display
    display = Display(visible=False, size=(800, 600))
    display.start()


def startFireFox(url=URL):
    driver = webdriver.Firefox()
    driver.get(url)
    return driver


def startChrome(url=URL, path=None):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    if path:
        driver = webdriver.Chrome(executable_path=path, options=chrome_options)
    else:
        driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    return driver

def is_find_object(parent_object, class_name):
    try:
        object = parent_object.find_element_by_class_name(class_name)
    except:
        print(class_name)
        object = ''
    return object


def get_site(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.text
    return None


def get_soup(html):
    if html:
        return BS(html)
    return html


def get_attractions(driver):
    attractions_list = []
    try:
        attractions = is_find_object(driver, 'xtu1r-K9a4Re-ibnC6b-haAclf')
        attractions = attractions.find_elements_by_class_name('NovK6')
        for attraction in attractions:
            pattern = r'(?<=image:url\(//)(.+?)(?=\))'
            attraction_img = attraction.get_attribute('innerHTML')
            attraction_img_url = re.search(pattern, attraction_img)
            attraction_text = attraction.get_attribute('innerText')
            attractions_list.append({'url': attraction_img_url.group(), 'text': attraction_text})
    except:
        pass
    print(attractions_list)
    return attractions_list


def get_photos(driver):
    try:
        photo_buttons = driver.find_elements_by_class_name('a4izxd-tUdTXb-xJzy8c-haAclf-UDotu')
        photo_buttons[0].click()
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'mWq4Rd-HiaYvf-CNusmb-gevUs')))
        photos = driver.find_elements_by_class_name('mWq4Rd-HiaYvf-CNusmb-gevUs')[:3]
        print(len(photos))
        time.sleep(3)
        for i in photos:
            print(i)
            print(i.get_attribute('innerHTML'))
            photo = i.find_element_by_class_name('mWq4Rd-HiaYvf-CNusmb-gevUs').get_attribute('innerHTML')
            pattern = r'(?<=image:url\(")(.+?)(?="\))'
            photo_url = re.search(pattern, photo)
            print(photo_url.group())
    except Exception as e:
        print(e.__class__.__name__)
        pass


def get_place_information(driver):
    try:
        place_information = is_find_object(driver, 'uxOu9-sTGRBb-UmHwN')
        print(place_information.get_attribute('innerText'))
        return place_information.get_attribute('innerText')
    except:
        return None

def get_location_information(driver):
    try:
        location_name = is_find_object(driver, 'exOO9c-V1ur5d')
        location_rating = is_find_object(driver, 'v10Rgb-v88uof-haAclf')
        location_text = is_find_object(driver, 'XgnsRd-HSrbLb-h3fvze-text')
        print(location_name.get_attribute('innerText'))
        print(location_rating.get_attribute('innerText'))
        print(location_text.get_attribute('innerText'))
    except:
        print('Район не взял')

def get_base_photo(driver):
    try:
        photo = is_find_object(driver, 'F8J9Nb-LfntMc-header-HiaYvf-LfntMc')
        button = photo.find_element_by_tag_name('img')
        src = button.get_attribute('src')
        if len(src.split('=')) == 2:
            print('Ссылка на главное фото: ', src.split('=')[0])
        else:
            print('Ссылка на главное фото: ', src)
    except Exception as e:
        print(e.__class__.__name__)
        return None


def get_reviews(driver):
    try:
        review_button = driver.find_element_by_class_name('Yr7JMd-pane-hSRGPd')
        review_button.click()
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'ODSEW-ShBeI')))
        reviews = driver.find_elements_by_class_name('ODSEW-ShBeI')
        print(len(reviews))
        for review in reviews:
            author_name = review.find_element_by_class_name('ODSEW-ShBeI-title').get_attribute('innerText')
            stars = review.find_element_by_class_name('ODSEW-ShBeI-RGxYjb-wcwwM').get_attribute('innerText')
            text = ''
            print(author_name, stars)
    except Exception as e:
        print(e.__class__.__name__)
        return None


def place_detail(cid):
    global startTime
    url = CID_URL.format(cid)
    # driver = startFireFox(url=url)
    driver = startChrome(url=url)
    try:
        endTime = datetime.now()
        time = endTime - startTime
        title = is_find_object(driver, 'x3AX1-LfntMc-header-title-title').text
        # address = is_find_object(driver, 'rogA2c').text
        print(' --------- Главное фото: ')
        base_photo = get_base_photo(driver)
        print(' --------- Информация о месте: ')
        place_information = get_place_information(driver)
        print(' --------- Достопримечательности: ')
        attractions = get_attractions(driver)                     # class Attraction - manyToMany
        print(' --------- Информация о месте: ')
        location_information = get_location_information(driver)     # class LocationInfo, class Location - ForeignKey
        # photos = get_photos(driver)                                 # class PlacePhoto
        print(' --------- Отзывы: ')
        reviews = get_reviews(driver)
        print(title, )
        print(time)
        print('Закрыто')
        print('----------------')
        driver.close()
    except Exception as e:
        print(e.__class__.__name__)
        print('Ошибка')
        driver.close()


def place_api_detail(cid):
    url = CID_API_URL.format(cid)
    r = requests.get(url)
    if r.status_code == 200:
        print(r.json())
        if r.json()['status'] == 'OK':
            result = r.json()['result']
            print(result['place_id'], result['formatted_address'])
        else:
            print(r.json()['status'])
    return None


# Функция которая парсит отели на странице
def parse_places(driver):
    global INDEX
    time.sleep(3)
    places = driver.find_elements_by_class_name('uMdZh')
    print(len(places))
    for place in places:
        title = place.find_element_by_class_name('dbg0pd').text if place.find_element_by_class_name('dbg0pd') else None
        cid = place.find_element_by_class_name('C8TUKc').get_attribute('data-cid') if place.find_element_by_class_name('C8TUKc') else None
        INDEX += 1
        print(INDEX, 'https://www.google.com/maps?cid='+cid)
        place_detail(cid) if cid else None


# Функция для смены страниц

def get_pagination(driver, page):
    pagination = driver.find_element_by_class_name('AaVjTc')
    available_pages = pagination.find_elements_by_tag_name('td')
    for i in available_pages:
        if str(page) == i.text and page != 1:
            i.click()
            # После клика нужно ждать
            # чтобы не ставить на долгое время, использовал цикл, который при
            # изменении текущей страницы на следующую запустить парсинг страницы
            for j in range(20):
                try:
                    pagination = driver.find_element_by_class_name('AaVjTc')
                    current_page = pagination.find_element_by_class_name('YyVfkd')
                    if current_page.text == str(page):
                        return True
                except:
                    pass
                time.sleep(1)
            time.sleep(1)
            break
    return False

# Запуск скрипта
def main():
    #driver = startChrome()
    driver = startChrome(path=CHROME_PATH)
    # driver = startFireFox()
    try:
        for page in range(1, PAGE+1):
            # Проверяю сколько доступных страниц для клика, и если следующая страница есть в пагинации то происходит клик
            if page == 1:
                print(f'СТРАНИЦА {page} начата')
                parse_places(driver)
                print(f'{page} страница готова')
                print('-----------------------------------')
            elif get_pagination(driver, page):
                print(f'СТРАНИЦА {page} начата')
                parse_places(driver)
                print(f'{page} страница готова')
                print('-----------------------------------')
        print('Парсинг завершен')
        driver.close()
    except Exception as e:
        print(e.__class__.__name__)
        if display:
            display.stop()
        print('Критическая ошибка')
        driver.close()


if __name__ == '__main__':
    startTime = datetime.now()
    main()

