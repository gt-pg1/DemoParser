import requests
from bs4 import BeautifulSoup
from time import sleep
import json
from datetime import datetime
import normalizer
import storages

HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}


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


def get_max_article_id(url):
    response = get_response(url)
    html = get_html(response)
    soup = get_soup(html)
    articles_ids = get_articles_ids(soup)
    max_article_id = max((int(i) for i in articles_ids[1:-1].split(',')))

    return max_article_id

# TODO: class Data
# Getting ID's of articles for collection of their content
def get_articles_ids(soup):
    ids = soup.find('div', {'class': 'feed'}).get('data-feed-exclude-ids')
    return ids


def get_article_info(soup):
    article_info = soup.find('div', {'class': 'l-hidden entry_data'}).get('data-article-info')

    if article_info is None:
        article_info = soup.find('div', {'class': 'l-hidden entry_data'}).text

    try:
        article_info = json.loads(article_info)
    except Exception:
        article_info = json.loads(normalizer.normalize_json(article_info))

    return article_info


def get_title(soup):
    try:
        h1 = soup.find('h1').text
    except AttributeError:

        try:
            h1 = soup.find_all('div', {'class': 'content-title content-title--short l-island-a'})[1].text
        except IndexError:
            h1 = None

    return normalizer.normalize_h1(h1) if h1 is not None else h1


def get_text(soup):
    text_blocks = soup.find('div', {'class': 'content content--full'}).find_all('div', {'class': 'l-island-a'})
    return normalizer.normalize_text(text_blocks)


def get_hyperlinks(soup):
    hyperlinks = soup.find_all('a', {'rel': 'nofollow noreferrer noopener'})
    hyperlinks = json.dumps(normalizer.normalize_hyperlinks(hyperlinks))
    return hyperlinks


def get_attachments(soup):
    videos = soup.find_all('div', {'data-andropov-type': 'video'})
    images = soup.find_all('div', {'data-andropov-type': 'image'})
    tweets = soup.find_all('a', {'class': 'andropov_tweet__date'})
    return json.dumps(normalizer.normalize_attachments(videos, images, tweets))


# Getting author name and profile link.
# There is an important rule in site content logic: if there is no subsite, then in the subsite block - the author
def get_author(soup):
    try:
        author = soup.find('a', {'class': 'content-header-author__name'}).text
        author_link = soup.find('a', {'class': 'content-header-author__name'}).get('href')
    except AttributeError:
        author = soup.find('div', {'class': 'content-header-author__name'}).text
        author_link = soup.find('div', {'class': 'content-header__info'}).find('a').get('href')

    return normalizer.normalize_author(author), author_link


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


def get_date_time(soup):
    date_and_time = soup.find('time').get('title')
    return date_and_time.split()


def get_comments_count(soup):
    article_info = get_article_info(soup)
    return article_info['comments']


def get_rating(soup):
    article_info = get_article_info(soup)
    return article_info['likes']


def get_favorites(soup):
    article_info = get_article_info(soup)
    return article_info['favorites']


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
    article_info = get_article_info(soup)

    is_subsite = (article_info['subsite_label'] != 'unknown' and
                  article_info['subsite_label'].lower() != article_info['author_name'].lower() and
                  is_authors)

    return is_subsite


def check_adult(soup):
    return bool(soup.find('div', {'class': 'adult'}))


# TODO: удалить если не пригодится
def _generate_next_url(soup, page):
    path_segment = soup.find('div', {'class': 'feed'}).get('data-feed-more-url')
    last_id = soup.find('div', {'class': 'feed'}).get('data-feed-last-id')
    last_sorting_value = soup.find('div', {'class': 'feed'}).get('data-feed-last-sorting-value')
    exclude_ids = soup.find('div', {'class': 'feed'}).get('data-feed-exclude-ids')
    template = f'{path_segment}?last_id={last_id}&last_sorting_value={last_sorting_value}&page={page}&exclude_ids={exclude_ids}&mode=raw'

    return template


def get_data(idx, soup, response, is_adult_content, gen_url):
    if response.status_code == 200 and not is_adult_content:
        h1 = get_title(soup)
        is_authors = check_author(soup)
        is_verified = check_verified(soup)
        is_subsite = check_subsite(soup, is_authors)
        author, author_link = get_author(soup)
        subsite, subsite_link = get_subsite(soup, is_subsite)
        company, company_link = get_company(soup, is_verified, is_subsite)
        if company is None and '/u/' not in author_link and is_subsite:
            company, company_link = author, author_link
        text = get_text(soup)
        date_and_time = get_date_time(soup)
        comments = get_comments_count(soup)
        rating = get_rating(soup)
        favorites = get_favorites(soup)
        hyperlinks = get_hyperlinks(soup)
        attachments = get_attachments(soup)

        data = {
            'ID': idx,
            '_generated_url': gen_url,
            'URL': response.url,
            'Date': date_and_time[0],
            'Time': date_and_time[1],
            'Title': h1,
            'Author': author,
            'Profile Link': author_link,
            'Subsite': subsite,
            'Subsite Link': subsite_link,
            'Company': company,
            'Company Link': company_link,
            'Text': None,  # Can set variable to 'text' if texts needed
            'Hyperlinks from text': hyperlinks,
            'Attachments': attachments,
            'Comments count': comments,
            'Rating': rating,
            'Favorites': favorites,
            '_is_verified': is_verified,
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
            '_is_verified': None,
            '_is_subsite': None,
            '_is_author': None,
            'Status Code': response.status_code
        }

    return data


def parsing(url, start_idx, articles_count=100):
    parsing_dt = datetime.now()
    storages.create_csv(parsing_dt)
    for i in range(start_idx, start_idx - articles_count, -1):
        # if i in db: continue
        gen_url = f'{url}{i}'
        response = get_response(gen_url)
        html = get_html(response)
        soup = get_soup(html)
        is_adult_content = check_adult(soup)
        # with open(f'{i}.html', 'x', encoding='utf-8') as file:
        #     file.write(html)

        data = get_data(i, soup, response, is_adult_content, gen_url)
        sleep(0.5)
        storages.write_csv(data, parsing_dt)

        print(data)


def main():
    url = 'https://vc.ru/'
    max_article_id = get_max_article_id(url)
    parsing(url, max_article_id)


if __name__ == '__main__':
    main()
