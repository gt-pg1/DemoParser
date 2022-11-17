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