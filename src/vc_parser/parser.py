"""Parse command line arguments

Run parameters:
    vc                      - Parsing vc.ru
    dtf                     - Parsing dtf.ru

Command parameters (optional):
    articles        : int   - Set number of articles to collect.                                   Default value: 100
    article_id      : int   - Set ID from which the collection will start or a specific article
    delay           : float - Set the delay in seconds between requests to the server.             Default value: 0.5
    output_csv      : bool  - Save parsed result to .csv.                                          Default value: True
    output_json     : bool  - Save parsed result as json to .json file.                            Default value: False
    output_texts    : bool  - Save texts result to .csv.                                           Default value: False

Example:
    src/vc_parser/parser.py dtf --article 150 --output_json True
"""

import sys
import argparse
from typing import NoReturn
import data_collector


def create_command_line_parser():
    parser_cl = argparse.ArgumentParser(prog='VC and DTF parser')
    subparsers_cl = parser_cl.add_subparsers(
        dest='source', title='Possible commands', description='Command must be entered as the first parameter'
    )

    vc_parser = subparsers_cl.add_parser('vc')
    vc_parser.add_argument(
        '-a', '--articles', type=int, default=100, help='(int) Set number of articles to collect. \
        Default value: 100'
    )
    vc_parser.add_argument(
        '-aid', '--article_id', type=int, help='(int) Set ID from which the collection will start or a specific article'
    )
    vc_parser.add_argument(
        '-d', '--delay', type=float, default=0.5, help='(float) Set the delay in seconds between requests to the \
        server. Default value: 0.5'
    )
    vc_parser.add_argument(
        '-csv', '--output_csv', type=bool, default=True, help='(bool) Generate .csv file with result. \
        Default value: True'
    )
    vc_parser.add_argument(
        '-json', '--output_json', type=bool, default=False, help='(bool) Generate .json file with result. \
        Default value: False'
    )
    vc_parser.add_argument(
        '-texts', '--output_texts', type=bool, default=False, help='(bool) Generate .csv file with TEXTS. \
        Default value: False'
    )

    dtf_parser = subparsers_cl.add_parser('dtf')
    dtf_parser.add_argument(
        '-a', '--articles', type=int, default=100, help='(int) Set number of articles to collect. \
        Default value: 100'
    )
    dtf_parser.add_argument(
        '-aid', '--article_id', type=int, help='(int) Set ID from which the collection will start or a specific article'
    )
    dtf_parser.add_argument(
        '-d', '--delay', type=float, default=0.5, help='(float) Set the delay in seconds between requests to the \
        server. Default value: 0.5'
    )
    dtf_parser.add_argument(
        '-csv', '--output_csv', type=bool, default=True, help='(bool) Generate .csv file with result. \
        Default value: True'
    )
    dtf_parser.add_argument(
        '-json', '--output_json', type=bool, default=False, help='(bool) Generate .json file with result. \
        Default value: False'
    )
    dtf_parser.add_argument(
        '-texts', '--output_texts', type=bool, default=False, help='(bool) Generate .json file with TEXTS. \
        Default value: False'
    )

    return parser_cl


def run_vc(namespace):
    url = 'https://vc.ru/'

    if namespace.article_id is None:
        namespace.article_id = data_collector.get_max_article_id(url)

    data_collector.parsing(
        url, namespace.article_id, namespace.articles, namespace.delay,
        namespace.output_csv, namespace.output_json, namespace.output_texts, 'vc'
    )


def run_dtf(namespace):
    url = 'https://dtf.ru/'

    if namespace.article_id is None:
        namespace.article_id = data_collector.get_max_article_id(url)

    data_collector.parsing(
        url, namespace.article_id, namespace.articles, namespace.delay,
        namespace.output_csv, namespace.output_json, namespace.output_texts, 'dtf'
    )


def main() -> NoReturn:
    parser_cl = create_command_line_parser()
    namespace = parser_cl.parse_args(sys.argv[1:])

    if namespace.source == 'vc':
        run_vc(namespace)
    elif namespace.source == 'dtf':
        run_dtf(namespace)
    else:
        print('Specify source ("vc" or "dtf")')


if __name__ == '__main__':
    main()
