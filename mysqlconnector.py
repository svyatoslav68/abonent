# -*- coding: utf8 -*-
# В модуле описываются соединения с базой данных 'abonent'
import sqlite3
import pymysql.cursors  
 
# Функция возвращает connection.
def getConnection():
    connection = pymysql.connect(host='localhost',
                                 user='slava',
                                 password='677183',                             
                                 db='abonent',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

# Функция возвращает connection.
def getAdminConnection():
    admin_connection = pymysql.connect(host='localhost',
                                 user='admin_abonent',
                                 password='admin',                             
                                 db='abonent',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
    return admin_connection

# Функция осуществляет подключение к SQLite3  и возвращает connection
def getConnectionLite():
    connection = sqlite3.connect("abonent.db")
    return connection
