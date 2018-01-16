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
from datetime import datetime
from datetime import timedelta


# 插入 github eos code 变动记录
def insert_btc_eos_github_code(watch, star, fork, commits, branches, releases, contributors, date):
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
        sql = "INSERT INTO `omni_btc_eos_github_code` (`watch`, `star`, `fork`, `commits`, `branches`, `releases`, `contributors`, `date`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (watch, star, fork, commits, branches, releases, contributors, date)
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        if result:
            return True
        cur.close()
        conn.close()
    except Exception as e:
        print e
    return False


# 查询 上一次 代码变更数据
def find_btc_eos_github_code_prev_one():
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "SELECT * FROM `omni_btc_eos_github_code`  order by date desc " 
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        print e
    return False


# 插入 github eos code 变动记录
def insert_btc_eos_github_code_tag(tag, date):
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
        sql = "INSERT INTO `omni_btc_eos_github_code_tag` (`tag`, `date`) VALUES ('%s', '%s')" % (tag, date)
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        if result:
            return True
        cur.close()
        conn.close()
    except Exception as e:
        print e
    return False

# 查询 
def find_btc_eos_github_code_tag(tag):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "SELECT * FROM `omni_btc_eos_github_code_tag` WHERE tag = '%s' order by date desc " % (tag)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        if result:
            return True
        cur.close()
        conn.close()
    except Exception as e:
        print e
    return False








def insert_otcbtc_trade_record_refer(flag, date):
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
        sql = "INSERT INTO `omni_btc_otcbtc_trade_record_refer` (`flag`, `date`) VALUES ('%s', '%s')" % (flag, date)
        #print sql
        #sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`) VALUES ('%s', '%s')" % (name, start_run_time)
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print e

def find_otcbtc_trade_record_refer(flag, crawl_date_refer):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor(MySQLdb.cursors.DictCursor)

        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "SELECT * FROM `omni_btc_otcbtc_trade_record_refer`  WHERE flag = '%s' and date >= '%s' " % (flag, crawl_date_refer)
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        if result:
            return False
        else:
            return True
        
        cur.close()
        conn.close()
    except Exception as e:
        print e
    return True

def insert_otcbtc_trade_record(quantity, currency, duration, date, crawl_date, date_hour):
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
        sql = "INSERT INTO `omni_btc_otcbtc_trade_record` (`quantity`, `currency`, `duration`, `date`, `crawl_date`, `date_hour`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (quantity, currency, duration, date, crawl_date, date_hour)
        #print sql
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print e


