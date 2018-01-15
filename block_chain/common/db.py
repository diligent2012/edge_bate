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

# 插入 买入时, 止盈设置纪录
def insert_btc_binance_order_stop_buy_record(data):
    try:
        
        orderId = data['orderId']
        clientOrderId = data['clientOrderId']

        origQty = data['origQty']
        symbol = data['symbol']

        side = data['side']
        timeInForce = data['timeInForce']

        status = data['status']
        stopPrice = data['stopPrice']

        transactTime = data['transactTime']
        o_type = data['type']

        price = data['price']
        executedQty = data['executedQty']

        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor()
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "INSERT INTO `omni_btc_binance_order_stop_buy_record` (`orderId`,`clientOrderId`,`origQty`,`executedQty`,`symbol`,`side`,`timeInForce`,`status`,`stopPrice`,`transactTime`,`o_type`,`price`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (orderId,clientOrderId,origQty,executedQty,symbol,side,timeInForce,status,stopPrice,transactTime,o_type,price)
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        print e
    return False
