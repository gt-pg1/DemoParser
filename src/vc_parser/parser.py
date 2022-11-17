import requests
from bs4 import BeautifulSoup
from time import sleep
import json
from datetime import datetime
import normalizer
import storages


HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}
# PAGE_TYPE_FEATURES = ('/s/', '/u/')


# TODO: class ResponseComponents
# Function returns HTML-code of page received from URL
def get_response(url):
    response = requests.get(url, headers=HEADER)
    return response


def get_html(response):
    return response.text


def get_soup(html):
    soup = BeautifulSoup(html, 'lxml')
    return soup


# TODO: class Data
# Getting ID's of articles for collection of their content
def get_articles_ids(soup):
    ids = soup.find('div', {'class': 'feed'}).get('data-feed-exclude-ids')
    return ids


def get_title(soup):

    try:
        h1 = soup.find('h1').text
    except AttributeError:

        try:
            h1 = soup.find_all('div', {'class': 'content-title content-title--short l-island-a'})[1].text
        except IndexError:
            h1 = None

    return normalizer.normalize_h1(h1) if h1 is not None else h1


# Getting author name and profile link.
# There is an important rule in site content logic: if there is no subsite, then in the subsite block - the author
def get_author(soup):

    try:
        author = soup.find('a', {'class': 'content-header-author__name'}).text
        profile_link = soup.find('a', {'class': 'content-header-author__name'}).get('href')
    except AttributeError:
        author = soup.find('div', {'class': 'content-header-author__name'}).text
        profile_link = soup.find('div', {'class': 'content-header__info'}).find('a').get('href')

    return normalizer.normalize_author(author), profile_link


# Getting subsite (articles subcategory) name and link
# There are 2 signs that a profile is not a subsite:
# 1. Presence of subfolders /s/ and /u/ in the URL
# 2. Presence of account verification
def get_subsite(soup, is_subsite):

    subsite = soup.find('div', {'class': 'content-header-author__name'}).text
    subsite_link = soup.find('div', {'class': 'content-header__info'}).find('a').get('href')

    if not is_subsite:
        subsite, subsite_link = None, None

    return normalizer.normalize_subsite(subsite) if subsite is not None else subsite, subsite_link


# Getting company name and link
# If
def get_company(soup, is_verified, is_subsite):

    company = soup.find('div', {'class': 'content-header-author__name'}).text
    company_link = soup.find('div', {'class': 'content-header__info'}).find('a').get('href')

    if is_subsite or '/u/' in company_link:
        company, company_link = None, None

    return normalizer.normalize_company(company) if company is not None else company, company_link
# TODO: Бывают случаи, когда компания верифицирована, имеет модный URL, но выпустила публикацию в подсайте.
#  В таких случаях в этой функции, если добавить соответствующее условие, находится ссылка на подсайт и он же туда
#  пишется соответственно (есть пример в файле 'data_17-11-2022_17-33-18' с тинковым и ещё одним под ним).
#  Нужно дописать функцию


def check_author(soup):
    authors_fields = list()

    try:
        author = soup.find('a', {'class': 'content-header-author__name'}).text
        authors_fields.append(author)
        author = soup.find('div', {'class': 'content-header-author__name'}).text
        authors_fields.append(author)
    except AttributeError:
        author = soup.find('div', {'class': 'content-header-author__name'}).text
        authors_fields.append(author)

    is_authors = True if len(authors_fields) == 2 else False

    return is_authors


def check_verified(soup):

    try:
        is_verified = bool(soup.find('div', {'class': 'content-header-author__approved'}))
    except AttributeError:
        is_verified = False

    return is_verified


def check_subsite(soup, is_authors):
    article_info = soup.find('div', {'class': 'l-hidden entry_data'}).get('data-article-info')
    article_info = json.loads(article_info)

    is_subsite = (article_info['subsite_label'] != 'unknown' and
                  article_info['subsite_label'].lower() != article_info['author_name'].lower() and
                  is_authors)

    return is_subsite


# TODO: удалить если не пригодится
def generate_next_url(soup, page):
    path_segment = soup.find('div', {'class': 'feed'}).get('data-feed-more-url')
    last_id = soup.find('div', {'class': 'feed'}).get('data-feed-last-id')
    last_sorting_value = soup.find('div', {'class': 'feed'}).get('data-feed-last-sorting-value')
    exclude_ids = soup.find('div', {'class': 'feed'}).get('data-feed-exclude-ids')
    template = f'{path_segment}?last_id={last_id}&last_sorting_value={last_sorting_value}&page={page}&exclude_ids={exclude_ids}&mode=raw'

    return template


def main():
    url = 'https://vc.ru/'

    # Getting the maximum articles ID at the time the parser is launched
    response = get_response(url)
    html = get_html(response)
    soup = get_soup(html)
    articles_ids = get_articles_ids(soup)
    max_article_id = max((int(i) for i in articles_ids[1:-1].split(',')))
    parsing_dt = datetime.now()
    max_article_id = 541503

    articles_count = 30
    for i in range(max_article_id, max_article_id - articles_count, -1):
        article_url = f'{url}{i}'
        response = get_response(article_url)
        html = get_html(response)
        soup = get_soup(html)

        if response.status_code == 200:
            h1 = get_title(soup)
            is_authors = check_author(soup)
            is_verified = check_verified(soup)
            is_subsite = check_subsite(soup, is_authors)
            author, profile_link = get_author(soup)
            subsite, subsite_link = get_subsite(soup, is_subsite)
            company, company_link = get_company(soup, is_verified, is_subsite)

            data = {
                'ID': i,
                '_URL': article_url,
                'URL': response.url,
                'Title': h1,
                'Author': author,
                'Profile Link': profile_link,
                'Subsite': subsite,
                'Subsite Link': subsite_link,
                'Company': company,
                'Company Link': company_link,
                '_is_verified': is_verified,
                '_is_subsite': is_subsite,
                '_is_author': is_authors,
                'Status Code': response.status_code
            }
        else:
            data = {
                'ID': i,
                '_URL': None,
                'URL': article_url,
                'Title': None,
                'Author': None,
                'Profile Link': None,
                'Subsite': None,
                'Subsite Link': None,
                'Company': None,
                'Company Link': None,
                '_is_verified': None,
                '_is_subsite': None,
                '_is_author': None,
                'Status Code': response.status_code
            }
        # TODO: достать из ифа и заменить тернарным выражением
        sleep(1)
        storages.write_csv(data, parsing_dt)
        print(data)
        # with open(f'{i}.html', 'x', encoding='utf-8') as file:
        #     file.write(html)


if __name__ == '__main__':
    main()
