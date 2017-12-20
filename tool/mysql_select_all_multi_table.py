#!/usr/bin/python
#coding:utf-8
import sys  
import sqlite3
import requests
import json
from bs4 import BeautifulSoup
import re
from datetime import datetime
from datetime import timedelta
import MySQLdb



def get_table():
    

def select_data(name , start_run_time, start_apply_time, city, group_info, level, website):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='develop',
            passwd='!123456Mysql.',
            db ='t_drp_system',
        )
        cur = conn.cursor()
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`, `start_apply_time`, `city`, `group_info`, `level`, `website`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (name, start_run_time, start_apply_time, city, group_info, level, website)
        #sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`) VALUES ('%s', '%s')" % (name, start_run_time)
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    except Exception, e:
        print e.message


def main():
    crawl_start();

if __name__ == '__main__':
    main()