import requests
import lxml
from bs4 import BeautifulSoup

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}

# Function returns HTML-code of page received from URL
def get_html(url):
    r = requests.get(url, headers=header)
    return r.text


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
    html = get_html(url)
    soup = get_soup(html)
    pages_count = 5        # TODO: вывести в параметры

    url = generate_next_url(soup, pages_count)
    print(url)
    for i in range(2, pages_count):
        html = get_html(url)
        soup = get_soup(html)
        url = generate_next_url(soup, pages_count)
        print(url)

if __name__ == '__main__':
    main()
