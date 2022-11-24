import re
from typing import Iterable

DATA_TRASH = ('Статьи редакции',)


# "{title}\n\s{DATA_TRASH}\n\s" -> "{title}"
def normalize_title(h1: str) -> str:
    if DATA_TRASH[0] in h1:
        h1 = h1.replace(DATA_TRASH[0], '')
    return h1.strip()


# "\s\n{author}\s\n" -> "{author}"
def normalize_author(author: str) -> str:
    return author.strip()


# "\s\n{subsite}\s\n" -> "{subsite}"
def normalize_subsite(subsite: str) -> str:
    return subsite.strip()


# # "\s\n{company}\s\n" -> "{company}"
def normalize_company(company: str) -> str:
    return company.strip()


# "20.11.2022 08:45:30 (Europe/Moscow)" -> ("20.11.2022", "08:45:30")
def normalize_date_time(date_and_time: str) -> (str, str):
    date_and_time = date_and_time.split()
    return date_and_time[0], date_and_time[1]


# Eliminates json validity issue in case of repetition of quotes
# ...company: "ООО "РОМАШКА"",... -> ...company: "ООО РОМАШКА"
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


# Removes service blocks with content, json data or view count
def normalize_text(text_blocks: Iterable) -> str:
    texts = []
    for block in text_blocks:
        if 'embed' in str(block) or 'andropov' in str(block):
            continue

        text = block.text.strip()
        texts.append(text)

    # Deleting data with json-blocks and views
    del_idx = []
    for idx, value in enumerate(texts):
        find_json = re.search(r'{.*}', value)
        find_views = re.search(r'^\d{1,5}\sпросмотров$', value)

        if find_json is not None or find_views is not None:
            del_idx.append(idx)

    texts = [value for idx, value in enumerate(texts) if idx not in del_idx]

    return '\n'.join(texts)


# Cleans and collects hyperlinks to list
def normalize_hyperlinks(dirty_hyperlinks: Iterable) -> list:
    hyperlinks = []

    for html_tag in dirty_hyperlinks:
        hyperlinks.append(html_tag.get('href'))

    return hyperlinks


# Cleans and collects attachments to dictionary
def normalize_attachments(
        dirty_video: Iterable, dirty_images: Iterable, dirty_tweets: Iterable
) -> dict:
    attachments = dict()

    # Videos can be in two types of video-blocks
    if dirty_video:
        video = []

        for html_tag in dirty_video:
            iframe = html_tag.get('data-video-iframe')
            mp4 = html_tag.get('data-video-mp4')

            if iframe:
                video.append(iframe)

            if mp4:
                video.append(mp4)

        attachments['video'] = video

    if dirty_images:
        images = []

        for html_tag in dirty_images:
            image_src = html_tag.get('data-image-src')

            if image_src:
                images.append(image_src)

        attachments['images'] = images

    if dirty_tweets:
        tweets = []

        for html_tag in dirty_tweets:
            href = html_tag.find('href')

            if href:
                tweets.append(href)

        attachments['tweets'] = tweets

    return attachments
