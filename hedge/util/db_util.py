#!/usr/bin/python
#coding:utf-8
import sys  
import sqlite3
import requests
import json
from bs4 import BeautifulSoup
import re
import MySQLdb
import time
import random


def insert_binance_recent_trades_data(data_isBuyerMaker, data_price, data_qty, data_time, data_id, data_isBestMatch, sync_time):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor()
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "INSERT INTO `omni_btc_binance_recent_trades_data` (`data_isBuyerMaker`, `data_price`, `data_qty`, `data_time`, `data_id`, `data_isBestMatch`, `sync_time`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (data_isBuyerMaker, data_price, data_qty, data_time, data_id, data_isBestMatch, sync_time)
        #sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`) VALUES ('%s', '%s')" % (name, start_run_time)
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print e

def find_btc_binance_trade():
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor()
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "SELECT * FROM `omni_btc_binance_trade`  WHERE is_finish = 9 "
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        return result
        cur.close()
        conn.close()
    except Exception, e:
        print e.message
    return False

def insert_binance_rate(sell_avg_price, buy_avg_price, rate, sync_time):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor()
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "INSERT INTO `omni_btc_binance_rate` (`sell_avg_price`, `buy_avg_price`, `rate`, `sync_time`) VALUES ('%s', '%s', '%s', '%s')" % (sell_avg_price, buy_avg_price, rate, sync_time)
        #sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`) VALUES ('%s', '%s')" % (name, start_run_time)
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print e