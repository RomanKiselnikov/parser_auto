import requests
from bs4 import BeautifulSoup
import csv
import subprocess, sys

# URL = 'https://auto.ru/krasnodar/cars/mazda/all/'
HEADERS = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 OPR/80.0.4170.16',
           'accept': '*/*'}
HOST = 'https://auto.ru'
FILE = 'cars.csv'


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find_all(le='link', class_='ListingPagination__page')
    if pagination:
        return len(pagination)
    else:
        return 1


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='ListingItem')

    cars = []
    for item in items:
        price = item.find('div', class_='ListingItemPrice ListingItem__price')
        if price:
            price = price.get_text().replace(' • ', '')
        else:
            price = 'Цену уточняйте'
        cars.append({
            'title': item.find('h3', class_='ListingItemTitle ListingItem__title').get_text(strip=True),
            'link': HOST + item.find('a', class_='Link ListingItemTitle__link').get('href'),
            'price': price,
            'engine': item.find('div', class_='ListingItemTechSummaryDesktop__cell').get_text(strip=True),
        })
    return cars


def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Марка', 'Ссылка', 'Цена в $', 'Мощность двигателя'])
        for item in items:
            writer.writerow([item['title'], item['link'], item['price'], item['engine']])


def parse():
    URL = input('Введите URL: ')
    URL = URL.strip()
    html = get_html(URL)
    if html.status_code == 200:
        cars = []
        pages_count = get_pages_count(html.text)
        for page in range(1, pages_count + 1):
            print(f'Парсинг страницы {page} из {pages_count}...')
            html = get_html(URL, params={'page': page})
            cars.extend(get_content(html.text))
        save_file(cars, FILE)
        print(f'Получено {len(cars)} автомобилей')
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, FILE])
    else:
        print('Error')


parse()
