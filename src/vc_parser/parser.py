import sys
import argparse
from typing import NoReturn
import data_collector


def create_command_line_parser():
    parser_cl = argparse.ArgumentParser(prog='VC and DTF parser')
    subparsers_cl = parser_cl.add_subparsers(
        dest='source', title='Possible commands', description='Commands must be entered as the first parameter'
    )

    vc_parser = subparsers_cl.add_parser('vc')
    vc_parser.add_argument(
        '-a', '--articles', type=int, default=1000, help='(int) Set number of articles to collect'
    )
    vc_parser.add_argument(
        '-aid', '--article_id', type=int, help='(int) Set ID from which the collection will start or a specific article'
    )
    vc_parser.add_argument(
        '-d', '--delay', type=float, default=0.5, help='(float) Set the delay between requests to the server'
    )
    vc_parser.add_argument(
        '-csv', '--output_csv', type=bool, default=False, help='(bool) Generate .csv file with result'
    )
    vc_parser.add_argument(
        '-json', '--output_json', type=bool, default=False, help='(bool) Generate .json file with result'
    )

    dtf_parser = subparsers_cl.add_parser('dtf')
    dtf_parser.add_argument(
        '-a', '--articles', type=int, default=1000, help='(int) Set number of articles to collect'
    )
    dtf_parser.add_argument(
        '-aid', '--article_id', type=int, help='(int) Set ID from which the collection will start or a specific article'
    )
    dtf_parser.add_argument(
        '-d', '--delay', type=float, default=0.5, help='(float) Set the delay between requests to the server'
    )
    dtf_parser.add_argument(
        '-csv', '--output_csv', type=bool, default=False, help='(bool) Generate .csv file with result'
    )
    dtf_parser.add_argument(
        '-json', '--output_json', type=bool, default=False, help='(bool) Generate .json file with result'
    )

    return parser_cl


def run_vc(namespace):
    url = 'https://vc.ru/'

    if namespace.article_id is None:
        namespace.article_id = data_collector.get_max_article_id(url)

    data_collector.parsing(
        url, namespace.article_id, namespace.articles,
        namespace.delay, namespace.output_csv, namespace.output_json, 'vc'
    )


def run_dtf(namespace):
    url = 'https://dtf.ru/'

    if namespace.article_id is None:
        namespace.article_id = data_collector.get_max_article_id(url)

    data_collector.parsing(
        url, namespace.article_id, namespace.articles,
        namespace.delay, namespace.output_csv, namespace.output_json, 'dtf'
    )
# TODO: добавить подсказки по командам


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
