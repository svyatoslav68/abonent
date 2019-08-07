#!/usr/bin/env python3

import sys
import mysqlconnector
import argparse

version="0.0.2 beta"

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
    parent_group.add_argument('--datework', help='Дата ввода в эксплуатацию') 
    parent_group.add_argument('--date', help='Дата выпуска')
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

def init_table_phones(count, con, **dict_pars):
    """Функция заполняет таблицу "phones" однотипными записями"""
    try:
        cursor=connect.cursor()
        # Определяем идентификтор типа телефонного аппарата по названию
        id_typeTA = 'NULL'
        if dict_pars.get('cod_type_TA'):
            SQL = "SELECT `id` from `types_TA` WHERE `name_type` = '{}'".format(dict_pars['cod_type_TA'])
            if cursor.execute(SQL) == 1:
                id_typeTA = str(list(cursor.fetchone().values())[0])
        dict_pars['cod_type_TA'] = id_typeTA
        dict_pars['state']='0'
        print(dict_pars)
        #return
        SQL = "INSERT into `phones` ({}) VALUES({})".format(', '.join(map(lambda x:"`"+x+"`",tuple(dict_pars.keys()))), ', '.join(map(lambda x:"'"+x+"'",tuple(dict_pars.values()))))
        if dict_pars.get('inv_number'):
            number_iid = int(dict_pars['inv_number'][len(dict_pars['inv_number'])-2:])
        if dict_pars.get('product_number'):
            number_pid = int(dict_pars['product_number'][len(dict_pars['product_number'])-2:])
        print(f"number_pid = {number_pid}, number_iid = {number_iid}")
        #number_pid = int(dict_pars['product_number'][len(dict_pars['product_number'])-2:])
        for i in range(int(count)):
            #newiid = 
            if dict_pars.get('inv_number'):
                dict_pars['inv_number'] = dict_pars['inv_number'][:len(dict_pars['inv_number'])-2]+"{0:02}".format(number_iid+i)
            if dict_pars.get('product_number'):
                dict_pars['product_number'] = dict_pars['product_number'][:len(dict_pars['product_number'])-2]+"{0:02}".format(number_pid+i)
            SQL = "INSERT into `phones` ({}) VALUES({})".format(', '.join(map(lambda x:"`"+x+"`",tuple(dict_pars.keys()))), ', '.join(map(lambda x:"'"+x+"'",tuple(dict_pars.values()))))
            print(f"SQL={SQL}")
            cursor.execute(SQL)
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
        dict_parametrs = {} # Словарь в котором содержатся данные полученные из ключей командной строки
        if namespace.pid:
            dict_parametrs['product_number']=namespace.pid
        if namespace.iid:
            dict_parametrs['inv_number']=namespace.iid
        if namespace.typeta:
            dict_parametrs['cod_type_TA']=namespace.typeta
        if namespace.date:
            dict_parametrs['date_issue']=namespace.date
        if namespace.datework:
            dict_parametrs['date_work']=namespace.datework
        init_table_phones(count = namespace.count, con = connect, **dict_parametrs)
    if namespace.command == 'delete' and namespace.table == 'numbers':
        if namespace.bd == 'mysql':
            connect=mysqlconnector.getConnection()
        elif namespace.bd == 'sqlite3':
            connect=mysqlconnector.getConnectionLite()
        delete_records_from_numbers(namespace.begin, namespace.end, namespace.net, connect)
