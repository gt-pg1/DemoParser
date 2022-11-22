import csv
import json
from datetime import datetime
from typing import NoReturn

# class Writer
#   def write_json
#   def write_csv
# class DataBaseConnector
#   def write_db
#   def write_text

HEADERS = ('ID',
           '_generated_url',
           'URL',
           'Date',
           'Time',
           'Title',
           'Author',
           'Profile Link',
           'Subsite',
           'Subsite Link',
           'Company',
           'Company Link',
           'Text',
           'Hyperlinks from text',
           'Attachments',
           'Comments count',
           'Rating',
           'Favorites'
           )


def form_data(keys=HEADERS, values=(None for _ in HEADERS)) -> dict:
    return dict(zip(keys, values))


def create_csv(parsing_datetime: datetime, source: str, header=HEADERS) -> NoReturn:
    with open(
            fr'files\{source}_{parsing_datetime.strftime("%d-%m-%Y_%H-%M-%S")}.csv', 'x', encoding='utf-8',  newline=''
    ) as file:
        writer = csv.writer(file)
        writer.writerow(header)


def write_csv(data: dict, parsing_datetime: datetime, source: str) -> NoReturn:
    with open(
            fr'files\{source}_{parsing_datetime.strftime("%d-%m-%Y_%H-%M-%S")}.csv', 'a', encoding='utf-8',  newline=''
              ) as file:
        writer = csv.writer(file)
        writer.writerow((data[value] for value in HEADERS))


def create_json(parsing_datetime: datetime, source: str) -> NoReturn:
    with open(
            fr'files\{source}_{parsing_datetime.strftime("%d-%m-%Y_%H-%M-%S")}.json', 'x', encoding='utf-8', newline=''
    ) as file:
        file.write('[\n')


def write_json(data: dict, parsing_datetime: datetime, source: str, articles_count: int) -> NoReturn:
    with open(
            fr'files\{source}_{parsing_datetime.strftime("%d-%m-%Y_%H-%M-%S")}.json', 'a', encoding='utf-8',  newline=''
    ) as file:
        json_object = json.dumps(data, indent=4)

        if articles_count != 0:
            file.write(json_object + ',\n')
        else:
            file.write(json_object)


def finalize_json(parsing_datetime: datetime, source: str):
    with open(
            fr'files\{source}_{parsing_datetime.strftime("%d-%m-%Y_%H-%M-%S")}.json', 'a', encoding='utf-8', newline=''
    ) as file:
        file.write('\n]')
