import re
from typing import Iterable

DATA_TRASH = ('Статьи редакции',)


def normalize_title(h1: str) -> str:
    if DATA_TRASH[0] in h1:
        h1 = h1.replace(DATA_TRASH[0], '')
    return h1.strip()


def normalize_author(author: str) -> str:
    return author.strip()


def normalize_subsite(subsite: str) -> str:
    return subsite.strip()


def normalize_company(company: str) -> str:
    return company.strip()


def normalaize_date_time(date_and_time: str) -> (str, str):
    date_and_time = date_and_time.split()
    return date_and_time[0], date_and_time[1]


def normalize_json(dirty_json: str) -> str:
    occurrences = re.findall(r': \".*\"{1,3}.*\"', dirty_json)

    for occurrence in occurrences:
        dq_count = occurrence.count('"')
        before = dirty_json[:dirty_json.find(occurrence)]
        substring = dirty_json[dirty_json.find(occurrence): dirty_json.find(occurrence) + len(occurrence)]
        after = dirty_json[dirty_json.find(occurrence) + len(occurrence):]

        dq_index = 0
        for i in range(dq_count):
            dq_index = substring.find('"', dq_index + 1)
            if i == 0 or i == dq_count - 1:
                continue
            substring = substring[:dq_index] + "'" + substring[dq_index + 1:]

        dirty_json = before + substring + after

    return dirty_json


def normalize_text(text_blocks: Iterable[str]) -> str:
    texts = []
    for block in text_blocks:
        if 'embed' in str(block) or 'andropov' in str(block):
            continue
        text = block.text.strip()
        texts.append(text)

    # Deleting data with service json
    del_idx = []
    for idx, value in enumerate(texts):
        find_json = re.search(r'{.*}', value)
        find_views = re.search(r'^\d{1,5}\sпросмотров$', value)
        if find_json is not None or find_views is not None:
            del_idx.append(idx)

    texts = [value for idx, value in enumerate(texts) if idx not in del_idx]

    return '\n'.join(texts)


def normalize_hyperlinks(dirty_hyperlinks: Iterable[str]) -> list:
    hyperlinks = []
    for html_tag in dirty_hyperlinks:
        hyperlinks.append(html_tag.get('href'))
    return hyperlinks


def normalize_attachments(
        dirty_video: Iterable[str], dirty_images: Iterable[str], dirty_tweets: Iterable[str]
) -> dict:
    attachments = dict()

    if dirty_video:
        video = []
        for html_tag in dirty_video:
            video.append(html_tag.get('data-video-iframe'))
        attachments['video'] = video

    if dirty_images:
        images = []
        for html_tag in dirty_images:
            images.append(html_tag.get('data-image-src'))
        attachments['images'] = images

    if dirty_tweets:
        tweets = []
        for html_tag in dirty_tweets:
            tweets.append(html_tag.get('href'))
        attachments['tweets'] = tweets

    return attachments
