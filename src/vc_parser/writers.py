import csv
import json
from datetime import datetime
from typing import NoReturn

HEADERS = ('ID',
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
           'Hyperlinks from text',
           'Attachments',
           'Comments count',
           'Rating',
           'Favorites')


# Create csv with header
def create_csv(parsing_datetime: datetime, source: str, header=HEADERS) -> NoReturn:
    with open(
            fr'files\{source}_{parsing_datetime.strftime("%d-%m-%Y_%H-%M-%S")}.csv',
            'x', encoding='utf-8',  newline=''
    ) as file:
        writer = csv.writer(file)
        writer.writerow(header)


# Writing data in created csv file
def write_csv(data: dict, parsing_datetime: datetime, source: str, write_texts: bool) -> NoReturn:

    with open(
            fr'files\{source}_{parsing_datetime.strftime("%d-%m-%Y_%H-%M-%S")}.csv',
            'a', encoding='utf-8',  newline=''
    ) as file:
        writer = csv.writer(file)
        writer.writerow((data[value] for value in HEADERS))

    if write_texts:
        with open(
                fr'files\{source}_{parsing_datetime.strftime("%d-%m-%Y_%H-%M-%S")}_texts.csv',
                'a', encoding='utf-8', newline=''
        ) as file:
            writer = csv.writer(file)
            writer.writerow((data['ID'], data['Text']))


# Creating a json file and ensuring a valid output file structure
def create_json(parsing_datetime: datetime, source: str) -> NoReturn:
    with open(
            fr'files\{source}_{parsing_datetime.strftime("%d-%m-%Y_%H-%M-%S")}.json',
            'x', encoding='utf-8', newline=''
    ) as file:
        file.write('[\n')


# Writing data in json format in created json file
def write_json(data: dict, parsing_datetime: datetime, source: str, articles_count: int) -> NoReturn:
    with open(
            fr'files\{source}_{parsing_datetime.strftime("%d-%m-%Y_%H-%M-%S")}.json',
            'a', encoding='utf-8',  newline=''
    ) as file:
        json_object = json.dumps({key: data[key] for key in HEADERS}, indent=4)

        if articles_count != 0:
            file.write(json_object + ',\n')
        else:
            file.write(json_object)


# Closing square bracket is added after all the data has been collected to ensure the validity of json structure.
def finalize_json(parsing_datetime: datetime, source: str):
    with open(
            fr'files\{source}_{parsing_datetime.strftime("%d-%m-%Y_%H-%M-%S")}.json',
            'a', encoding='utf-8', newline=''
    ) as file:
        file.write('\n]')
