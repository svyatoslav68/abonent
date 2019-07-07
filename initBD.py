#!/usr/bin/env python3

import sys
import mysqlconnector
import argparse

version="0.0.1 alpha"

def createParser():
    # Создаем класс парсера
    parser = argparse.ArgumentParser(
            prog="initBD",
            description="""Программа предназначена для инициализации базы данных для работы 
            программы abobent. Программа заполняет таблицу numbers. Эта таблица содержит 
            список номеров станции.""",
            add_help=False,
            )
    parent_group = parser.add_argument_group(title='Параметры')
    parent_group.add_argument('--help', '-h', action='help', help='Справка')
    parent_group.add_argument('--bd', '-d', choices=('mysql', 'sqlite3'), default='mysql', help="Драйвер базы данный MySQL или SQLITE3")
    parent_group.add_argument('--table', '-t', help='Название таблицы БД', default='numbers')
    parent_group.add_argument('--net', '-n', help='Название сети, например, `ПТС`')
    parent_group.add_argument('--typeta', help='Тип телефонного аппарата')
    parent_group.add_argument('--pid', help='Заводской номера телефонного аппарата')
    parent_group.add_argument('--iid', help='Инвентарный номер телефонного аппарата')
    parent_group.add_argument('--count', '-c', help='Количество одинаковых записей, добавляемых в таблицу')
    parent_group.add_argument('--version', 
            action = 'version',
            help = 'Выводится номер версии программы', 
            version = '%(prog)s {}'.format(version))
    # Создаем подпарсер, здесь будут определены команды программе
    command_subparser = parser.add_subparsers(help='команды пользователей', dest='command')
    parser_create = command_subparser.add_parser('create', help="Создание блока записей")
    parser_create.add_argument('-b', '--begin', required=False, type=int)
    parser_create.add_argument('-e', '--end', required=False, type=int)
    parser_create = command_subparser.add_parser('delete', help="Удаление блока записей")
    parser_create.add_argument('-b', '--begin', required=False, type=int)
    parser_create.add_argument('-e', '--end', required=False, type=int)
    return parser

def init_table_phones(counter, pid, iid, typeTA, connect):
    """Функция заполняет таблицу "phones" однотипными записями"""
    try:
        cursor=connect.cursor()
        # Опдределяем идентификтор типа телефонного аппарата по названию
        SQL = "SELECT `id` from `types_TA` WHERE `name_type` = '{}'".format(typeTA)
        if cursor.execute(SQL) == 1:
            id_typeTA = list(cursor.fetchone().values())[0]
            SQL = "INSERT into {0} (`state`, `product_number`, `inv_number`, `cod_type_TA`) VALUES(0,'{{0}}', '{{1}}', '{1}')".format('phones', id_typeTA)
        else:
            id_typeTA = 'NULL'
            SQL = "INSERT into {0} (`state`, `product_number`, `inv_number`) VALUES(0,'{{0}}', '{{1}}')".format('phones')
        for i in range(int(counter)):
            resSQL=SQL.format(pid+'*'+str(i), iid+str(i))
            print(resSQL)
            cursor.execute(resSQL)
        connect.commit()
    finally:
        connect.close()
    return 1


def init_table_numbers(beginNumber, endNumber, net, connect):
    """Функция заполняет таблицу "numbers" базы данных пустыми записями
    с телефонными номерами в диапазоне: beginNumber - endNumber"""
    try:
        cursor=connect.cursor()
        SQL = "INSERT into {0} (`name_net`, `number`) VALUES('{1}', '{2}')"
        for num in [beginNumber+i for i in range(endNumber-beginNumber+1)]:
            real_SQL=SQL.format('numbers', net, num)
            print(real_SQL)
            cursor.execute(real_SQL)
        connect.commit()
    finally:
        connect.close()
    return 1

def delete_records_from_numbers(beginNumber, endNumber, net, connect):
    """Функция удаляет записи из таблицы `numbers`, ограниченные 
    номерами beginNumber и endNumber """
    try:
        cursor=connect.cursor()
        SQL = "DELETE from `{0}` WHERE `name_net`='{1}' AND `number` >= '{2}' AND `number` <= '{3}'"
        real_SQL=SQL.format('numbers', net, beginNumber, endNumber)
        print(real_SQL)
        cursor.execute(real_SQL)
        connect.commit()
    finally:
        connect.close()
    return 1;

def init_servtables(adminConnect):
    """Функция создает и заполняет служебные таблицы базы данных:
    t1, t10, t100 """
    try:
        cursor=adminConnect.cursor()
        for size_table in (1, 10, 100):
            print("Создается таблица t{}\n".format(size_table))
            SQL="CREATE TABLE IF NOT EXISTS t{size}(id smallint)".format(size=size_table)
            print(SQL)
            result=cursor.execute(SQL)
            if result:
                print("Таблица {} создана\n".format(size_table))
            else:
                print("Таблица {} уже существует\n".format(size_table))
            print("Заполнение таблицы t{}\n".format(size_table))
            SQL="DELETE FROM t{}".format(size_table)
            print(SQL)
            result=cursor.execute(SQL)
            for i in range(size_table):
                SQL="INSERT into t{size} (id) VALUES({value})".format(size=size_table, value=i)
                print(SQL)
                result=cursor.execute(SQL)
            adminConnect.commit()
    finally:
        adminConnect:close()
    return(1)

def delete_servtables():
    """Функция удаляет служебные таблицы.
    Не знаю, зачем она нужна."""
    
if __name__== '__main__':
    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])
    print("Выбрана команда {}".format(namespace.command))
    print (namespace)
    if namespace.table == 't':
        if namespace.command =='create':
            adminConnect=mysqlconnector.getAdminConnection()
            init_servtables(adminConnect)
        if namespace.command == 'delete':
            delete_servtables()
    if namespace.command == 'create' and namespace.table == 'numbers':
        if namespace.bd == 'mysql':
            connect=mysqlconnector.getConnection()
        elif namespace.bd == 'sqlite3':
            connect=mysqlconnector.getConnectionLite()
        init_table_numbers(namespace.begin, namespace.end, namespace.net, connect)
    if namespace.command == 'create' and namespace.table == 'phones':
        if namespace.bd == 'mysql':
            connect=mysqlconnector.getConnection()
        elif namespace.bd == 'sqlite3':
            connect=mysqlconnector.getConnectionLite()
        init_table_phones(namespace.count, namespace.pid, namespace.iid, namespace.typeta, connect)
    if namespace.command == 'delete' and namespace.table == 'numbers':
        if namespace.bd == 'mysql':
            connect=mysqlconnector.getConnection()
        elif namespace.bd == 'sqlite3':
            connect=mysqlconnector.getConnectionLite()
        delete_records_from_numbers(namespace.begin, namespace.end, namespace.net, connect)
