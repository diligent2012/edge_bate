#!/usr/bin/python
#coding:utf-8
# 区、县
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

common_url_prefix = "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/"
city_code_list = []


def crawl_district_list():
    global city_code_list
    city_code_list = query_data(2)
   
    
    try:
        page_urls = generate_page_url()
        for k,page_url in enumerate(page_urls):
            print page_url
            response = request_util(page_url,'gbk');
            soup = BeautifulSoup(response, "lxml")
            info_list = soup.find('table',class_="countytable").find_all("tr",class_="countytr")
            for k,item in enumerate(info_list):


                if item.contents[0].find('a',{'href':True}):
                    #street_url = common_url_prefix + url_code + item.contents[0].a.attrs['href'].encode('utf8')
                    code = item.contents[0].a.get_text().encode('utf8')

                    name = item.contents[1].a.get_text().encode('utf8')
                    parent_code,parent_name = get_city_code(code)
                    level = 3 
                    print code, name, parent_code, parent_name
                    insert_data(code, name, parent_code, parent_name, level)

                    #crawl_street_detail(street_url)
           
    except Exception, e:
        print traceback.format_exc()



def generate_page_url():
    page_urs = []
    for k,item in enumerate(city_code_list):
        code = item['code']
        url_province_code =  item['code'][0:2]
        url_city_code = item['code'][0:4]
        print type(code)
        if (code not in ["441900000000","442000000000","460400000000"]):
            page_url = common_url_prefix + url_province_code + "/" + url_city_code + ".html"
            page_urs.append(page_url)

    return page_urs


def get_city_code(district_code):
    for k,item in enumerate(city_code_list):
        c_code = item['code']
        c_code_pre = c_code[0:4]

        d_code_pre = district_code[0:4]
        if c_code_pre == d_code_pre:
            return item['code'], item['name']

def main():
    crawl_district_list();

if __name__ == '__main__':
    main()
