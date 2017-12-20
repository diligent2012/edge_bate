#!/usr/bin/python
#coding:utf-8
# 城市
import sys  
sys.path.append("..")
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
from db import insert_data, query_data


city_url = "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/index.html"
common_url_prefix = "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/"
province_code_list = []

def crawl_city_list():
    global province_code_list
    province_code_list = query_data(1)
    response = request_util(city_url,'gb2312');
    try:
        soup = BeautifulSoup(response, "lxml")
        info_list = soup.find('table',class_="provincetable").find_all("tr",class_="provincetr")
        for k,item in enumerate(info_list):
            content_list = item.find_all("a")
            for c_k,c_item in enumerate(content_list):
                d_url =  c_item.attrs['href'].encode('utf8')
                url_city_code =  c_item.attrs['href'].encode('utf8').split(".")[0]
                d_city_url = common_url_prefix + url_city_code + ".html"
                print d_city_url
                crawl_city_detail(d_city_url)
                # if(c_k > 1):
                #     break
            

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
            parent_code,parent_name = get_province_code(code)
            level = 2
            insert_data(code, name, parent_code, parent_name, level)

    except Exception, e:
        print traceback.format_exc()

def get_province_code(city_code):
    print province_code_list
    for k,item in enumerate(province_code_list):
        p_code = item['code']
        p_code_pre = p_code[0:2]

        c_code_pre = city_code[0:2]
        if p_code_pre == c_code_pre:
            return item['code'], item['name']

def main():
    crawl_city_list();

if __name__ == '__main__':
    main()