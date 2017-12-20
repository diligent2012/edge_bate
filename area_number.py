#!/usr/bin/python
#coding:utf-8
#
import sys  
import sqlite3
import requests
import json
from bs4 import BeautifulSoup
import re
from datetime import datetime
from datetime import timedelta
import MySQLdb
import MySQLdb.cursors 
import traceback
from util import request_util


province_url = "http://www.stats.gov.cn/tjsj/tjbz/xzqhdm/201703/t20170310_1471429.html"

list_url = "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/index.html"

common_url_prefix = "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/"

# street_url_prefix = "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/11/"

# village_url_prefix = "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/11/90/"

code_list = []
province_code_list = []
city_code_list = []
district_code_list = []

def crawl_province_list():
    response = request_util(province_url);
    try:
        soup = BeautifulSoup(response, "lxml")
        info_list = soup.find('div',class_="TRS_PreAppend").find_all("p",class_="MsoNormal")
        for k,item in enumerate(info_list):
            
            code_item = {}
            code =  item.find("span",attrs={'lang':'EN-US'})
            code_item['code'] = code.get_text().strip() 
            content_list =  item.find_all("span")
            code_item['name'] = content_list[len(content_list)-1].get_text().strip()
            code_list.append(code_item)

        for k,item in enumerate(code_list):
            if item['code'].find("0000") > 0:
                code = item['code'].encode('utf8') + "000000"
                name = item['name'].encode('utf8')
                parent_code = 0
                level = 1

                p_code_item = {}
                p_code_item['code'] = code
                p_code_item['name'] = name
                province_code_list.append(p_code_item)
                #insert_data(code, name, parent_code, level)

    except Exception, e:
        print traceback.format_exc()











def crawl_city_list():
    response = request_util(list_url,'gb2312');
    try:
        soup = BeautifulSoup(response, "lxml")
        info_list = soup.find('table',class_="provincetable").find_all("tr",class_="provincetr")
        for k,item in enumerate(info_list):
            
            content_list = item.find_all("a")
            for c_k,c_item in enumerate(content_list):
                d_url = common_url_prefix + c_item.attrs['href'].encode('utf8')
                print d_url
                crawl_city_detail(d_url)
                if(c_k > 1):
                    break
            
            break

    except Exception, e:
        print traceback.format_exc()


def crawl_city_detail(url):

    response = request_util(url,'gb2312');
    try:
        soup = BeautifulSoup(response, "lxml")
        info_list = soup.find('table',class_="citytable").find_all("tr",class_="citytr")

        for k,item in enumerate(info_list):
            code = item.contents[0].a.get_text().encode('utf8')
            name = item.contents[1].a.get_text().encode('utf8')
            c_code_item = {}
            c_code_item['code'] = code
            c_code_item['name'] = name
            city_code_list.append(c_code_item)



        for k,item in enumerate(info_list):
            
            # print common_url_prefix + item.contents[0].a.attrs['href'].encode('utf8')
            # print item.contents[0].a.get_text().encode('utf8')
            # print item.contents[1].a.get_text().encode('utf8')

            code = item.contents[0].a.get_text().encode('utf8')
            name = item.contents[1].a.get_text().encode('utf8')
            parent_code,parent_name = get_province_code(code)
            level = 2
            insert_data(code, name, parent_code, parent_name, level)

            district_url = common_url_prefix + item.contents[0].a.attrs['href'].encode('utf8')
            #print district_url
            crawl_district_detail(district_url)

    except Exception, e:
        print traceback.format_exc()

def get_province_code(city_code):

    for k,item in enumerate(province_code_list):
        p_code = item['code']
        p_code_pre = p_code[0:2]

        c_code_pre = city_code[0:2]
        if p_code_pre == c_code_pre:
            return item['code'], item['name']
            


def crawl_district_detail(url, url_code):
    response = request_util(url,'gb2312');
    try:
        soup = BeautifulSoup(response, "lxml")
        info_list = soup.find('table',class_="countytable").find_all("tr",class_="countytr")


        for k,item in enumerate(info_list):
            code = item.contents[0].a.get_text().encode('utf8')
            name = item.contents[1].a.get_text().encode('utf8')
            d_code_item = {}
            d_code_item['code'] = code
            d_code_item['name'] = name
            district_code_list.append(d_code_item)


        for k,item in enumerate(info_list):

            if item.contents[0].find('a',{'href':True}):
                street_url = common_url_prefix + url_code + item.contents[0].a.attrs['href'].encode('utf8')
                code = item.contents[0].a.get_text().encode('utf8')
                name = item.contents[1].a.get_text().encode('utf8')
                parent_code,parent_name = get_city_code(code)
                level = 3 
                #print code, name, parent_code, parent_name
                insert_data(code, name, parent_code, parent_name, level)

                crawl_street_detail(street_url)
           
    except Exception, e:
        print traceback.format_exc()

def get_city_code(district_code):
    for k,item in enumerate(city_code_list):
        c_code = item['code']
        c_code_pre = c_code[0:4]

        d_code_pre = district_code[0:4]
        if c_code_pre == d_code_pre:
            return item['code'], item['name']




def crawl_street_detail(url):
    response = request_util(url,'gb2312');
    try:
        soup = BeautifulSoup(response, "lxml")
        info_list = soup.find('table',class_="towntable").find_all("tr",class_="towntr")
        for k,item in enumerate(info_list):

            if item.contents[0].find('a',{'href':True}):
                #street_url = street_url_prefix + item.contents[0].a.attrs['href'].encode('utf8')
                code = item.contents[0].a.get_text().encode('utf8')
                name = item.contents[1].a.get_text().encode('utf8')
                parent_code,parent_name = get_city_code(code)
                level = 4
                print code, name, parent_code, parent_name
                #insert_data(code, name, parent_code, parent_name, level)
           
    except Exception, e:
        print traceback.format_exc()


def get_district_code(street_code):
    for k,item in enumerate(district_code_list):
        d_code = item['code']
        d_code_pre = d_code[0:6]

        s_code_pre = street_code[0:6]
        if d_code_pre == s_code_pre:
            return item['code'], item['name']



# code_s = []

# def normalize_code():
#     for k,item in enumerate(code_list):
#         #print item
#         if item['code'].find("0000") > 0:
#             #print item['name']
#             code = int(item['code'].encode('utf8'))
#             # name = item['name'].encode('utf8')
#             # parent_code = 0
#             # level = 1
#             # insert_data(code, name, parent_code, level)
#             code_s.append(code)
#             code_list.remove(code_list[k])

    
#     for s_k,s_code in enumerate(code_s):
#         for k,item in enumerate(code_list):
#             name = item['name'].encode('utf8')
#             code = item['code'].encode('utf8')
#             before_two_code = code[0:2]
#             after_two_code = code[4:6]
#             flag_s_code = str(s_code)[0:2] 

#             if(flag_s_code == before_two_code and after_two_code == "00"):
#                 print name
#         if(s_k > 1):
#             break


def query_data():
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='develop',
            passwd='!123456Mysql.',
            db ='t_drp_system',
            cursorclass = MySQLdb.cursors.DictCursor
        )
        cur = conn.cursor()
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "SELECT * FROM `ecs_t_area` "
        #sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`) VALUES ('%s', '%s')" % (name, start_run_time)
        cur.execute(sql)
        result = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return result
    except Exception, e:
        print e.message
    return False

def insert_data(code, name, parent_code, parent_name, level):

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
        sql = "INSERT INTO `ecs_t_area` (`code`,`name`,`parent_code`,`parent_name`,`level`) VALUES ('%s', '%s', '%s', '%s', '%s')" % (code, name, parent_code, parent_name, level)
        #sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`) VALUES ('%s', '%s')" % (name, start_run_time)
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    except Exception, e:
        print e.message

def crawl_start():
    crawl_province_list()
    crawl_city_list()
    #query_data()


def main():
    crawl_start();

if __name__ == '__main__':
    main()