import csv
from datetime import datetime

# class Writer
#   def write_json
#   def write_csv
# class DataBaseConnector
#   def write_db
#   def write_text


def write_csv(data, parsing_datetime):
    with open(f'data_{parsing_datetime.strftime("%d-%m-%Y_%H-%M-%S")}.csv', 'a', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow((data['ID'],
                         data['_URL'],
                         data['URL'],
                         data['Title'],
                         data['Author'],
                         data['Profile Link'],
                         data['Subsite'],
                         data['Subsite Link'],
                         data['Company'],
                         data['Company Link'],
                         data['_is_verified'],
                         data['_is_subsite'],
                         data['_is_author'],
                         data['Status Code']))
