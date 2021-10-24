from pip._vendor import requests
from selenium import webdriver
import csv
import time
from bs4 import BeautifulSoup as BS
from constants import CHROME_PATH, IS_LINUX
from datetime import datetime

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

INDEX = 0
FILE_NAME = 'hotels.csv'  # Назавние файла для сохранения
QUERY = 'lawn care New york'  # Запрос в поиске
URL = f'https://www.google.com/search?q={QUERY}&newwindow=1&tbm=lcl&sxsrf=AOaemvJF91rSXoO-Kt8Dcs2gkt9_JXLlCQ%3A1632305149583&ei=_f9KYayPI-KExc8PlcaGqA4&oq={QUERY}&gs_l=psy-ab.3...5515.12119.0.12483.14.14.0.0.0.0.0.0..0.0....0...1c.1.64.psy-ab..14.0.0....0.zLZdDbmH5so#rlfi=hd:;'
PAGE = 100  # Количество страниц для парсинга

KEY = 'AIzaSyAbOkxUWUw9z54up8AiMSCMX7rO7-8hqv8'
CID_API_URL = 'https://maps.googleapis.com/maps/api/place/details/json?cid={0}&key='+KEY
CID_URL = 'https://maps.google.com/?cid={0}'

display = None

if IS_LINUX:
    from pyvirtualdisplay import Display
    display = Display(visible=0, size=(800, 600))
    display.start()



def startFireFox(url=URL):
    driver = webdriver.Firefox()
    driver.get(url)
    return driver

def startChrome(url=URL, path=None):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    if path:
        driver = webdriver.Chrome(executable_path=path, options=chrome_options)
    else:
        driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    return driver


def time_sleep(action, returned=False):
    for i in range(20):
        try:
            data = action
            if returned:
                return data
            break
        except:
            pass
        time.sleep(1)
    return ''


# Функция для возврата данных из файла, если такого файла нет то создает
def read_file():
    try:
        file = open(FILE_NAME, 'r', encoding='utf-8')
        reader = csv.reader(file, delimiter=',', lineterminator="\r")
        file.close()
        return reader
    except:
        write_file()
        return read_file()

# Функция для записи данных в файл, при создании файла
# по умолчанию добавляются заголовки
def write_file(data=[['№', 'Название', 'Адрес', 'Рейтинг', 'Сайт']]):
    with open(FILE_NAME, mode='w', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=',', lineterminator="\r")
        for i in data:
            writer.writerow(i)


# Функция добавления данных в файл
# не удаляя прежние данные
def add_file(data):
    with open(FILE_NAME, mode='a', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=',', lineterminator="\r")
        for i in data:
            writer.writerow(i)


# Перед тем как сохранять данные в файл мы должны
# проверить создан ли файл и после добавить данные
def save_file(data):
    read_file()
    add_file(data)

# Функция для получения адреса отеля.Создано по причине того что адрес хранится в модальном
# окне которое подгружается при клике на отель
def get_address(driver, hotel, last_address, index, hotels):
    hotel_list = hotels
    for i in range(20):
        try:
            #hotel.find_element_by_class_name('dbg0pd').click()
            try:
                hotel.click()
            except:
                hotel = get_hotel(driver, hotel_list, index).click()
            break
        except:
            pass
        time.sleep(1)
    address = last_address
    for i in range(20):
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "LrzXr"))
            )
            address = driver.find_element_by_class_name('LrzXr').text
        except:
            pass
        if address != last_address:
            return address
        time.sleep(1)
    return address


def get_hotel(driver, hotels, index):
    time.sleep(1)
    hotel_list = hotels
    for i in range(20):
        try:
            data = hotel_list[index]
            return data
        except:
            print('Список отелей скрылся\n')
            for j in range(20):
                try:

                    element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "uMdZh"))
                        )
                    hotel_list = element

                    hotel_list = driver.find_elements_by_class_name('uMdZh')
                    break
                except:
                    pass
                time.sleep(1)
        time.sleep(1)


def place_detail(cid):
    global startTime

    url = CID_URL.format(cid)
    driver = startChrome(url=url)
    try:
        endTime = datetime.now()
        time = endTime - startTime
        title = driver.find_element_by_class_name('x3AX1-LfntMc-header-title-title').text
        print(driver.find_element_by_class_name('x3AX1-LfntMc-header-title-title').text)
        print(time)
        print('Закрыто')
        driver.close()
    except:
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
def parse_hotels(driver):
    global INDEX
    time.sleep(3)
    hotels = time_sleep(driver.find_elements_by_class_name('uMdZh'), True)
    print(len(hotels))
    for hotel in hotels:
        # print(hotel.get_attribute('innerHTML'))
        title = hotel.find_element_by_class_name('dbg0pd').text if hotel.find_element_by_class_name('dbg0pd') else None
        cid = hotel.find_element_by_class_name('C8TUKc').get_attribute('data-cid') if hotel.find_element_by_class_name('C8TUKc') else None
        time.sleep(1)
        INDEX += 1
        print(INDEX, title, cid)

        place_detail(cid) if cid else None
        print('-------------')
        # title = ''
        # hotel = get_hotel(driver, hotels, hotel_index)
        # for i in range(20):
        #     try:
        #         hotel = get_hotel(driver, hotels, hotel_index)
        #         title_block = hotel.find_element_by_class_name('dbg0pd')
        #         title = title_block.text
        #         if not title:
        #             hotel = get_hotel(driver, hotels, hotel_index)
        #             title_block = hotel.find_element_by_class_name('dbg0pd')
        #             title = title_block.text
        #         break
        #     except:
        #         pass
        #     time.sleep(1)
        #
        # try:
        #     rating = hotel.find_element_by_class_name('rllt__details').find_element_by_xpath('div[1]/span[1]').text
        # except:
        #     rating = 'Нет отзывов'
        # try:
        #     site = hotel.find_element_by_class_name('yYlJEf').get_attribute('href')
        # except:
        #     site = 'Сайта нет'
        # address = get_address(driver, hotel, last_address, hotel_index, hotels)
        # last_address = address
        # index += 1
        #print(f' ---- {index}', title, ' | ')

        #hotel_object = [index, title, address, rating, site]
        #hotel_objects.append(hotel_object)
    #save_file(hotel_objects)
    # return INDEX


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
    try:
        for page in range(1, PAGE+1):
            # Проверяю сколько доступных страниц для клика, и если следующая страница есть в пагинации то происходит клик
            if page == 1:
                print(f'СТРАНИЦА {page} начата')
                parse_hotels(driver)
                print(f'{page} страница готова')
                print('-----------------------------------')
            elif get_pagination(driver, page):
                print(f'СТРАНИЦА {page} начата')
                parse_hotels(driver)
                print(f'{page} страница готова')
                print('-----------------------------------')
        print('Парсинг завершен')
        driver.close()
    except:
        if display:
            display.stop()
        print('Критическая ошибка')
        driver.close()


if __name__ == '__main__':
    startTime = datetime.now()
    main()

