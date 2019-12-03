#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Набор вспомогательных функций.

Version: 0.1
Created: 02/12/2019
Last modified: 02/12/2019
"""

import requests
import time
from bs4 import BeautifulSoup as bs
from typing import Optional


def get_soup(url_or_file: str, headers: dict = None, session: requests.Session = None) -> Optional[bs]:
    """
    Возвращяет объект супа, из переданного URL или файла

    :param url_or_file: URL или путь к файлу
    :param headers: заголовки запроса
    :param session: сессия, в которой выполняется запрос
    :return: объект супа или None
    """

    # Если передан путь к файлу (для локальных тестов), читаем файл и возвращаем объект супа
    if not (url_or_file.startswith('http://') or url_or_file.startswith('https://')):
        with open(url_or_file, encoding='utf-8') as fp:
            soup = bs(fp, 'lxml')

        return soup

    # Если передан URL

    # Возможно, сессия в данном случае не нужна, но пусть будет
    if not session:
        session = requests.session()

    request = session.get(url_or_file, headers=headers)

    # Если запрос вернул код, отличный от 200, считаем, что соединение не удалось, и пишем ошибку в консоль
    if request.status_code != 200:
        print("Can't get URL {}".format(url_or_file))
        print("Status code {}\n".format(request.status_code))
        return

    return bs(request.content, 'lxml')


def main():
    pass


if __name__ == '__main__':
    __time_start = time.perf_counter()
    main()
    __time_delta = time.perf_counter() - __time_start
    __TIMES = (('d', 24 * 60 * 60), ('h', 60 * 60), ('m', 60), ('s', 1))
    __times = ''
    for __i in range(len(__TIMES) - 1):
        __t, __time_delta = divmod(__time_delta, __TIMES[__i][1])
        if __t > 0:
            __times += "{} {} ".format(int(__t), __TIMES[__i][0])
    __times += "{:.3} {}".format(__time_delta, __TIMES[~0][0])
    print("\n[Finished in {}]".format(__times))
