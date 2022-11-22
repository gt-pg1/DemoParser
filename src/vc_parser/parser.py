import sys
import argparse
from typing import NoReturn
import data_collector


def create_cl_parser():
    parser_cl = argparse.ArgumentParser()
    subparsers_cl = parser_cl.add_subparsers(dest='command')

    vc_parser = subparsers_cl.add_parser('vc')
    vc_parser.add_argument('-a', '--articles', type=int, default=1000)
    vc_parser.add_argument('-aid', '--article_id', type=int)
    vc_parser.add_argument('-d', '--delay', type=float, default=0.5)
    vc_parser.add_argument('--output_csv', type=bool, default=False)
    vc_parser.add_argument('--output_json', type=bool, default=False)

    dtf_parser = subparsers_cl.add_parser('dtf')
    dtf_parser.add_argument('-a', '--articles', type=int, default=1000)
    dtf_parser.add_argument('-aid', '--article_id', type=int)
    dtf_parser.add_argument('-d', '--delay', type=float, default=0.5)
    dtf_parser.add_argument('--output_csv', type=bool, default=False)
    dtf_parser.add_argument('--output_json', type=bool, default=False)

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
    parser_cl = create_cl_parser()
    namespace = parser_cl.parse_args(sys.argv[1:])

    if namespace.command == 'vc':
        run_vc(namespace)
    elif namespace.command == 'dtf':
        run_dtf(namespace)
    else:
        print('Specify source ("vc" or "dtf")')


if __name__ == '__main__':
    main()
