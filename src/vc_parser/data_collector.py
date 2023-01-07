import requests
from bs4 import BeautifulSoup
from time import sleep
import json
from datetime import datetime
import normalizer
import writers
import database
from typing import Union, NoReturn

HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}


# Returns a "response" object contains the server's response to the HTTP request.
def get_response(url: str) -> requests.Response:
    response = requests.get(url, headers=HEADER)
    return response


# Returns html-code of the page
def get_html(response: requests.Response) -> str:
    return response.text


# Returns "BeautifulSoup" object (represents the parsed document as a whole)
def get_soup(html: str) -> BeautifulSoup:
    soup = BeautifulSoup(html, 'lxml')
    return soup


# Returns the article IDs for finding the most recent article.
# Numbering of articles on source sites is in the order of their creation, from smallest to largest.
def get_articles_ids(soup: BeautifulSoup) -> str:
    ids = soup.find('div', {'class': 'feed'}).get('data-feed-exclude-ids')
    return ids


# Returns most recent article
def get_max_article_id(url: str) -> int:
    response = get_response(url)
    html = get_html(response)
    soup = get_soup(html)
    articles_ids = get_articles_ids(soup)
    # '[12,34,56]' -> 56
    max_article_id = max((int(i) for i in articles_ids[1:-1].split(',')))

    return max_article_id


# Returns a json array with data about the article (subsite label, author name, rating, comments, favorites ...)
def get_article_info(soup: BeautifulSoup) -> dict:
    article_info = soup.find('div', {'class': 'l-hidden entry_data'}).get('data-article-info')

    if article_info is None:
        article_info = soup.find('div', {'class': 'l-hidden entry_data'}).text

    try:
        article_info = json.loads(article_info)
    except Exception:
        article_info = json.loads(normalizer.normalize_json(article_info))

    return article_info


# Returns title of the article from h1-tag
def get_title(soup: BeautifulSoup) -> Union[str, None]:
    try:
        h1 = soup.find('h1').text
        h1 = normalizer.normalize_title(h1)
    except AttributeError:

        try:
            h1 = soup.find_all('div', {'class': 'content-title content-title--short l-island-a'})[1].text
            h1 = normalizer.normalize_title(h1)
        except IndexError:
            h1 = None

    return h1


# Returns cleaned text of the article
def get_text(soup: BeautifulSoup) -> str:
    text_blocks = soup.find('div', {'class': 'content content--full'}).find_all('div', {'class': 'l-island-a'})
    return normalizer.normalize_text(text_blocks)


# Returns a list of hyperlinks from text
def get_hyperlinks(soup: BeautifulSoup) -> str:
    hyperlinks = soup.find_all('a', {'rel': 'nofollow noreferrer noopener'})
    hyperlinks = json.dumps(normalizer.normalize_hyperlinks(hyperlinks))
    return hyperlinks


# Returns a list of attachment links
def get_attachments(soup: BeautifulSoup) -> str:
    videos = soup.find_all('div', {'data-andropov-type': 'video'})
    images = soup.find_all('div', {'data-andropov-type': 'image'})
    tweets = soup.find_all('a', {'class': 'andropov_tweet__date'})
    return json.dumps(normalizer.normalize_attachments(videos, images, tweets))


# Returns author name and profile link.
def get_author(soup: BeautifulSoup) -> (str, str):
    try:
        author = soup.find('a', {'class': 'content-header-author__name'}).text
        author_link = soup.find('a', {'class': 'content-header-author__name'}).get('href')
    except AttributeError:
        author = soup.find('div', {'class': 'content-header-author__name'}).text
        author_link = soup.find('div', {'class': 'content-header__info'}).find('a').get('href')

    return normalizer.normalize_author(author), author_link


# Returns validated name of subsite and link
def get_subsite(soup: BeautifulSoup, is_subsite: bool) -> (Union[str, None], Union[str, None]):
    subsite = soup.find('div', {'class': 'content-header-author__name'}).text
    subsite_link = soup.find('div', {'class': 'content-header__info'}).find('a').get('href')

    if not is_subsite:
        subsite, subsite_link = None, None

    return normalizer.normalize_subsite(subsite) if subsite is not None else subsite, subsite_link


# Returns validated name of company and link
def get_company(soup: BeautifulSoup, is_subsite: bool) -> (Union[str, None], Union[str, None]):
    company = soup.find('div', {'class': 'content-header-author__name'}).text
    company_link = soup.find('div', {'class': 'content-header__info'}).find('a').get('href')

    if is_subsite or '/u/' in company_link:
        company, company_link = None, None

    return normalizer.normalize_company(company) if company is not None else company, company_link


# Returns date and time article was published
def get_date_time(soup: BeautifulSoup) -> (str, str):
    date_and_time = soup.find('time').get('title')
    date, time = normalizer.normalize_date_time(date_and_time)
    return date, time


# Returns comments count at the time of parsing
def get_comments_count(soup: BeautifulSoup) -> int:
    article_info = get_article_info(soup)
    return article_info['comments']


# Returns rating at the time of parsing
def get_rating(soup: BeautifulSoup) -> int:
    article_info = get_article_info(soup)
    return article_info['likes']


# Returns additions to favorites count at the time of parsing
def get_favorites(soup: BeautifulSoup) -> int:
    article_info = get_article_info(soup)
    return article_info['favorites']


# Checking if the data is the author
def check_author(soup: BeautifulSoup) -> bool:
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


# Checking if the data is the subsite
def check_subsite(soup: BeautifulSoup, is_authors: bool) -> bool:
    article_info = get_article_info(soup)

    is_subsite = (article_info['subsite_label'] != 'unknown' and
                  article_info['subsite_label'].lower() != article_info['author_name'].lower() and
                  is_authors)

    return is_subsite


# Checking for 18+ content on a page
def check_adult(soup: BeautifulSoup) -> bool:
    return bool(soup.find('div', {'class': 'adult'}))


# Checking if needing to collect data from the page
def check_parsable(response: requests.Response, is_adult_content: bool) -> bool:
    return response.status_code == 200 and not is_adult_content


# Collecting data in a python dictionary
def get_data(
        idx: int, soup: BeautifulSoup, response: requests.Response, is_parsable: bool, gen_url: str
) -> dict:
    data = dict()

    if is_parsable:
        h1 = get_title(soup)
        is_authors = check_author(soup)
        is_subsite = check_subsite(soup, is_authors)
        author, author_link = get_author(soup)
        subsite, subsite_link = get_subsite(soup, is_subsite)
        company, company_link = get_company(soup, is_subsite)
        if company is None and '/u/' not in author_link and is_subsite:
            company, company_link = author, author_link
        text = get_text(soup)
        date, time = get_date_time(soup)
        comments = get_comments_count(soup)
        rating = get_rating(soup)
        favorites = get_favorites(soup)
        hyperlinks = get_hyperlinks(soup)
        attachments = get_attachments(soup)

        data = {
            'ID': idx,
            '_generated_url': gen_url,
            'URL': response.url,
            'Date': date,
            'Time': time,
            'Title': h1,
            'Author': author,
            'Profile Link': author_link,
            'Subsite': subsite,
            'Subsite Link': subsite_link,
            'Company': company,
            'Company Link': company_link,
            'Text': text,
            'Hyperlinks from text': hyperlinks,
            'Attachments': attachments,
            'Comments count': comments,
            'Rating': rating,
            'Favorites': favorites,
            '_is_subsite': is_subsite,
            '_is_author': is_authors,
            'Status Code': response.status_code
        }
    else:
        data = {
            'ID': idx,
            '_generated_url': gen_url,
            'URL': None,
            'Date': None,
            'Time': None,
            'Title': None,
            'Author': None,
            'Profile Link': None,
            'Subsite': None,
            'Subsite Link': None,
            'Company': None,
            'Company Link': None,
            'Text': None,
            'Hyperlinks from text': None,
            'Attachments': None,
            'Comments count': None,
            'Rating': None,
            'Favorites': None,
            '_is_subsite': None,
            '_is_author': None,
            'Status Code': response.status_code
        }

    return data


# Decision-making function and data recording in different formats
def parsing(
        url: str, parsed_ids: list, start_idx: int, articles_count: int, delay: float,
        write_csv: bool, write_json: bool, write_texts: bool, source: str
) -> NoReturn:
    parsing_dt = datetime.now()

    folder_exist = False
    if not folder_exist:
        folder_exist = writers.check_folder()

    if write_csv:
        writers.create_csv(parsing_dt, source)

    if write_json:
        writers.create_json(parsing_dt, source)

    while True:
        idx = start_idx
        gen_url = f'{url}{idx}'
        response = get_response(gen_url)
        html = get_html(response)
        soup = get_soup(html)
        is_adult_content = check_adult(soup)
        is_parsable = check_parsable(response, is_adult_content)

        data = get_data(idx, soup, response, is_parsable, gen_url)

        if data['ID'] not in parsed_ids:
            database.insert_data(data, source)

        start_idx -= 1
        if is_parsable:
            print(f'Осталось собрать статей: {articles_count}')
            articles_count -= 1

            if write_csv:
                writers.write_csv(data, parsing_dt, source, write_texts)
            if write_json:
                writers.write_json(data, parsing_dt, source, articles_count)

        if articles_count == 0:
            break

        sleep(delay)

    if write_json:
        writers.finalize_json(parsing_dt, source)

    print('Готово!')
