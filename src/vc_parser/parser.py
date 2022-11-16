import requests
import lxml
from bs4 import BeautifulSoup

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}


# Function returns HTML-code of page received from URL
def get_response(url):
    response = requests.get(url, headers=header)
    return response
# TODO: добавить получение header (и его возвращение?)


def get_html(response):
    return response.text


def get_json(response):
    return response.json()


# Getting ID's of publications for collection of their content
def get_ids(soup):
    pass


def get_soup(html):
    soup = BeautifulSoup(html, 'lxml')
    return soup


def generate_next_url(soup, page):
    path_segment = soup.find('div', {'class': 'feed'}).get('data-feed-more-url')
    last_id = soup.find('div', {'class': 'feed'}).get('data-feed-last-id')
    last_sorting_value = soup.find('div', {'class': 'feed'}).get('data-feed-last-sorting-value')
    exclude_ids = soup.find('div', {'class': 'feed'}).get('data-feed-exclude-ids')
    template = f'{path_segment}?last_id={last_id}&last_sorting_value={last_sorting_value}&page={page}&exclude_ids={exclude_ids}&mode=raw'

    return template


def main():
    url = 'https://vc.ru/'
    response = get_response(url)
    html = get_html(response)
    soup = get_soup(html)
    # json = get_json(response)
    pages_count = 2        # TODO: вывести в параметры
    
    url = generate_next_url(soup, pages_count)
    response = get_response(url)
    json = get_json(response)
    print(json)
# TODO: Написать условие получения html или json (если в header - Content Type находится 'html' или 'json')
# TODO: Написать функцию получения данных из JSON
# TODO: Оттуда забрать ID и попробовать позакидывать запросы с этими ID в Postman. Посмотреть на ответ и публикации,
#  которые там отдаются. Внимательнее отнестись к выборке и тому, насколько результат по GET запросу, соответствует
#  реальности. Учесть, что параметр last_sorting_value больше не участвует в запросе (точнее пробую без него)


if __name__ == '__main__':
    main()
