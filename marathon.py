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



prefix = 'http://www.runchina.org.cn/portal.php?mod=calendar&ac=list'
year = []
month = []

def crawl_enter_year():
    result={}
    ses = requests.session()
    data = {
            }
    response = ses.post(prefix,data = data)
    if response.status_code != 200:
        return result

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        info_list = soup.find('div',id="cldr-year").find_all('a')
        for item in info_list:
            year.append(item.string)
    except Exception, e:
        return result

def crawl_enter_month():
    result={}
    ses = requests.session()
    data = {
            }
    response = ses.post(prefix,data = data)
    if response.status_code != 200:
        return result

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        info_list = soup.find('div',id="cldr-month").find_all('a')
        for item in info_list:
            month.append(item.string)
        print month
    except Exception, e:
        return result


def crawl_enter_list():
    result={}
    ses = requests.session()
    data = {
            }
    response = ses.post(prefix,data = data)
    if response.status_code != 200:
        return result

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        info_list = soup.find('ul',class_="match-list").find_all('li')
        for item in info_list:
            #print item.find('span',class_="date").string #天
            #print item.find('span',class_="day").string #周几
            name = item.find('div',class_="match-item").find('span',class_="match-name").get_text().encode('utf8')  # 赛事名称
            level = item.find('div',class_="match-item").find('span',class_="match-types").find("img").attrs['alt'].encode('utf8') # 赛事级别
            detail_info = item.find('div',class_="match-item").find_all('span',class_="match-info")
            city = detail_info[0].get_text() #地址
            start_run_time = detail_info[1].get_text() #起跑时间
            group = detail_info[3].get_text() #项目内容
            scale = detail_info[4].get_text() #规模
            #print name
            normalize_data(name , level, city, start_run_time, group, scale)

    except Exception, e:
        return result

def normalize_data(name , level, city, start_run_time, group, scale):
    try:
        #print name
        #print level
        #print city[3:]
        #print start_run_time[6:]
        city = city[3:].encode('utf8')
        
        start_run_time = start_run_time[6:].encode('utf8')
        start_apply_time = before_time(start_run_time)
        start_run_time = formate_time(start_run_time)

        #print group[3:].split("/")
        #print scale[3:].split("/")
        group_info = assembly_info(group[3:], scale[3:])
        #print group_info

        insert_data(name, start_run_time, start_apply_time, city, group_info,level, '')

    except Exception, e:
        print e.message

def formate_time(time):
    time = time.replace('年','-').replace('月','-').replace('日','')
    now = datetime.strptime(time,'%Y-%m-%d')
    return now

def before_time(time):
    try:

        #start_run_time = start_run_time[6:].encode('utf8')
        time = time.replace('年','-').replace('月','-').replace('日','')
        now = datetime.strptime(time,'%Y-%m-%d')
        aDay = timedelta(days=-90)
        now = now + aDay
        return now
    except Exception, e:
        print e.message

def assembly_info(group, scale):
    try:
        #print group
        group_arr = group.split("/")
        scale_arr = scale.split("/")
        #print group_arr
        #print scale_arr
        group_info = ""
        for k,g_item in enumerate(group_arr):

            group_info +=g_item + " : "+ scale_arr[k] + "; "
            #print scale_arr[]
        #print group_info
        return group_info.encode('utf8')
    except Exception, e:
        print e.message


def crawl_start():
    #crawl_enter_year()
    #crawl_enter_month()
    crawl_enter_list()


def insert_data(name , start_run_time, start_apply_time, city, group_info, level, website):
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