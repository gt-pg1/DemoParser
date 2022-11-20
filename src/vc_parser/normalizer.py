import re

data_trash = ('Статьи редакции', )


def normalize_h1(h1):
    if data_trash[0] in h1:
        h1 = h1.replace(data_trash[0], '')
    return h1.strip()


def normalize_author(author):
    return author.strip()


def normalize_subsite(subsite):
    return subsite.strip()


def normalize_company(company):
    return company.strip()


def normalize_json(dirty_json: str):
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


def normalize_text(text_blocks: list):
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
        find_views = re.search(r'\d{1,5}\sпросмотров', value)
        # TODO: Это плохо. Нужно чтобы только эта маска была в блоке и ничего больше
        if find_json is not None or find_views is not None:
            del_idx.append(idx)

    for idx in del_idx:
        del texts[idx]
    # TODO: Это тоже плохо. Если в списке 2 и более, то вывалится в IndexError

    return '\n'.join(texts)


def normalize_hyperlinks(dirty_hyperlinks: list):
    hyperlinks = []
    for html_tag in dirty_hyperlinks:
        hyperlinks.append(html_tag.get('href'))
    return hyperlinks


def normalize_attachments(dirty_video, dirty_images, dirty_tweets):
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
