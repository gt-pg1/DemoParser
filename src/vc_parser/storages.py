import csv
from datetime import datetime

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
           'Favorites',
           '_is_verified',
           '_is_subsite',
           '_is_author',
           'Status Code')


def form_data(keys=HEADERS, values=(None for _ in HEADERS)):
    return dict(zip(keys, values))


def create_csv(parsing_datetime, header=HEADERS):
    with open(fr'files\data_{parsing_datetime.strftime("%d-%m-%Y_%H-%M-%S")}.csv',
              'x', encoding='utf-8',  newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)


def write_csv(data, parsing_datetime):
    with open(fr'files\data_{parsing_datetime.strftime("%d-%m-%Y_%H-%M-%S")}.csv',
              'a', encoding='utf-8',  newline='') as file:
        writer = csv.writer(file)
        writer.writerow((data['ID'],
                         data['_generated_url'],
                         data['URL'],
                         data['Date'],
                         data['Time'],
                         data['Title'],
                         data['Author'],
                         data['Profile Link'],
                         data['Subsite'],
                         data['Subsite Link'],
                         data['Company'],
                         data['Company Link'],
                         data['Text'],
                         data['Hyperlinks from text'],
                         data['Attachments'],
                         data['Comments count'],
                         data['Rating'],
                         data['Favorites'],
                         data['_is_verified'],
                         data['_is_subsite'],
                         data['_is_author'],
                         data['Status Code']))
