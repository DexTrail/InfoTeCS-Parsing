#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Парсинг страниц организаций с сайта list-org.com

Version: 0.2
Created: 02/12/2019
Last modified: 03/12/2019
"""

import re
import requests
import sys
import time
import utility
from bs4 import BeautifulSoup as bs
from bs4.element import Tag
from typing import Optional


def parse(url_or_file: str, headers: dict = None, session: requests.Session = None) -> Optional[dict]:
    """
    Извлекает информацию из объекта супа

    :param url_or_file: URL или путь к файлу
    :param headers: заголовки запроса
    :param session: сессия, в которой выполняется запрос
    :return: словарь с данными о компании или None
    """
    # Получаем объект супа для URL или файла
    soup = utility.get_soup(url_or_file, headers, session)
    if not soup:
        print(f"Unable to get BeautifulSoup object from {url_or_file}\n", file=sys.stderr)
        return

    # Получаем первый инфоблок с наименованием и таблицей
    current_info_block = soup.find('div', attrs={'class': 'c2m'})
    if not current_info_block:
        print(f"Unable to find <div class=\"c2m\"> in {url_or_file}. "
              f"Check document structure.\nParsing was interrupted.\n",
              file=sys.stderr)
        return

    """ Можно взять данные из краткой справки, но тогда появляется
    зависимость от формата справки и входящих в нее данных. """

    # Данные об организации
    company_info = {}

    # Получаем полное наименование организации
    text = current_info_block.find('a').string
    company_info['full_name'] = text.strip() if text else ''

    # Таблица с данными о руководителе, дате регистрации и статусе
    table = current_info_block.find('table')

    # Получаем имя руководителя
    # Если нужно только ФИО, можно запросить страницу физ. лица и взять оттуда.
    # Парсить строку не стоит - должность может быть не только ген. дир., может не быть отчества и т.д.
    # Таким образом мы не можем точно знать, где должность, а где ФИО.
    company_info['chief'] = _get_value_from_info_block("Руководитель", table, url_or_file,
                                                       block_type=1, is_link=True)

    # Получаем дату регистрации
    company_info['registration_date'] = _get_value_from_info_block("Дата регистрации", table, url_or_file,
                                                                   block_type=1)

    # Получаем статус
    company_info['status'] = _get_value_from_info_block("Статус", table, url_or_file, block_type=1)

    # Получаем инфоблок с реквизитами
    header_div = soup.find(string=re.compile("Реквизиты компании")).find_parent('div')
    if not header_div:
        print(f"Unable to find wrap div for 'Реквизиты компании' in {url_or_file}. "
              f"Check document structure\nParsing was interrupted.\n",
              file=sys.stderr)
        return

    current_info_block = header_div.find_next_sibling('div', attrs={'class': 'c2m'})
    if not current_info_block:
        print(f"Unable to find <div class=\"c2m\"> for 'Реквизиты компании' in {url_or_file}. "
              f"Check document structure\nParsing was interrupted.\n",
              file=sys.stderr)
        return

    # Получаем ИНН, КПП, ОГРН
    company_info['INN'] = _get_value_from_info_block("ИНН", current_info_block, url_or_file)
    company_info['KPP'] = _get_value_from_info_block("КПП", current_info_block, url_or_file)
    company_info['OGRN'] = _get_value_from_info_block("ОГРН", current_info_block, url_or_file)

    # FIXME
    print("\ncompany_info {")
    for key, value in company_info.items():
        print(f"{key}: {value}")
    print("}")

    return company_info


def _get_value_from_info_block(entity_name: str, block: Tag, url_or_file: str,
                               *, block_type: int = 0, is_link: bool = False) -> str:
    """
    Возвращает значение свойства из инфоблока по названию

    :param entity_name: название свойства
    :param block: информационный блок с данными
    :param url_or_file: URL или путь к файлу (для сообщений об ошибках)
    :param block_type: тип информационного блока (0 - список, 1 - таблица)
    :param is_link: является ли значение ссылкой (только для таблиц)
    :return: значение свойства
    """
    # Если такого свойства нет, возвращаем пустую строку (исключение не нужно)
    entity_header = block.find(string=re.compile(entity_name))
    if not entity_header:
        return ''

    # Если структура не соотвествует заданной, дальнейший парсинг невозможен,
    # т.к. могут быть записаны неправильные данные
    # Выбрасываем исключение, чтобы обратить на это внимание
    try:
        if block_type == 0:
            entity_value = entity_header.find_parent('i').next_sibling
        elif block_type == 1:
            target_td = entity_header.find_parent('td').find_next_sibling()
            entity_value = target_td.find('a').string if is_link else target_td.string
        else:
            raise Exception(f"Unsupported block_type value {block_type}")
    except Exception:
        print(f"Exception while parsing {entity_name} in {url_or_file}. "
              f"Check document structure\n",
              file=sys.stderr)
        raise

    return entity_value.strip() if entity_value else ''


def main():
    # parse(r"../_test_pages/list-org.com_company_4868135.htm")
    parse(r"../_test_pages/list-org.htm")


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
