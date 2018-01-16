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
