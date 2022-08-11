import requests
from bs4 import BeautifulSoup
import json
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import img2pdf
from fake_useragent import UserAgent
import os
import colorama
colorama.init();
from colorama import Fore, Back, Style #Цвета текста

headers = {
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36',
    'accept': '*/*'
}


def get_a_normal_price(price):
    return int( ''.join( [i for i in price if i.isdigit()] ) )

def get_a_photo_link(code):
    left = code.find('/upload/resize_cache/')
    right = code.find('.jpg')
    return code[left:right+4];


def parse(headers):

    page = 1
    all_the_orders = [];
    while True:
        URL = f'https://dofshoes.ru/catalog/zima/?PAGEN_1={page}'
        request = requests.get(URL, headers=headers)
        soup = BeautifulSoup(request.text, 'html.parser')

        orders = soup.findAll('div', class_='item-wrap col');
        for i in range(len(orders)):
            try:
                order_status = orders[i].find('div', class_='in-stock').text.strip()
                order_price = get_a_normal_price(orders[i].find('div', class_='price-block').find('div', class_='price font-body bold').text)
                order_title = orders[i].find('a', class_='name font-title').text.strip()
                order_href = 'https://dofshoes.ru'+orders[i].find('a', class_='name font-title').get('href').strip()
                order_photo_link = 'https://dofshoes.ru'+get_a_photo_link(str(orders[i].find('div', class_='product-image')))

                order_photo = requests.get(order_photo_link, headers=headers).content

                current_order = {

                'Статус': order_status,
                'Цена': order_price,
                'Название': order_title,
                'Ссылка на товар': order_href

                }

                order_title = order_title.replace('/','-')
                if not(os.path.isdir(f'Собранная информация/{order_title}')):
                    os.mkdir(f'Собранная информация/{order_title}')

                with open(f'Собранная информация/{order_title}/info.txt', 'w', encoding='UTF-8') as file:
                    txt = ''
                    for key, value in current_order.items():
                        txt += f'{key}: {value}\n'
                    file.write(txt);

                with open(f'Собранная информация/{order_title}/{order_price} ({order_status}).jpg', 'wb') as img:
                    img.write(order_photo);
                

                all_the_orders.append(current_order);
                print(f'\r[INFO] Process {i+1}/{len(orders)}',end='')

            except Exception as error:
                continue

        print(f'\n{Back.BLACK}Товары из страницы #{page} загружены!\n')
        page += 1;

        if not soup.find('i', class_='icon-arrow-right'):
            print(f'Сбор информации о товарах завершён!')
            break
        time.sleep(2);

    with open('Собранная информация/order.json', 'w', encoding='UTF-8') as file:
        all_the_orders.sort(key=lambda order: order['Цена'])
        json.dump(all_the_orders, file, indent=4, ensure_ascii=False);
        print(f'Вся информация о товарах занесена в файл .../order.json')


def main():
    parse(headers=headers)

if __name__ == '__main__':
    main()