#!/usr/bin/python
#coding:utf-8
# 乡镇、街道

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
from db import insert_data, query_data, get_data

common_url_prefix = "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/"
district_code_list = []


special_url_conn = ["http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/52/03/520324.html"]

special_url = [
    {
        "page_url" : "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/52/03/520324.html",
        "encoding" : "gb18030"
    }
]

def crawl_street_list():
    # page_url = "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/52/03/520324.html"
    # response = request_util(page_url,'gb18030');
    # print response
    # return
    global district_code_list
    district_code_list = query_data(3)

    
    try:
        page_urls = generate_page_url()
        for k,page_item in enumerate(page_urls):
            page_url = page_item['page_url']
            print page_url
            if (page_url in special_url_conn):
                for item in special_url:
                    response = request_util(item['page_url'],item['encoding']);
            else:
                response = request_util(page_url,'gbk');
            soup = BeautifulSoup(response, "lxml")
            info_list = soup.find('table',class_="towntable").find_all("tr",class_="towntr")
            for k,item in enumerate(info_list):

                if item.contents[0].find('a',{'href':True}):
                    #street_url = street_url_prefix + item.contents[0].a.attrs['href'].encode('utf8')
                    code = item.contents[0].a.get_text().encode('utf8')
                    name = item.contents[1].a.get_text().encode('utf8')
                    parent_code,parent_name = get_district_code(code)
                    level = 4
                    print code, name, parent_code, parent_name
                    insert_data(code, name, parent_code, parent_name, level)
           
    except Exception, e:
        print traceback.format_exc()

def generate_page_url():
    page_urs = []
    for k,item in enumerate(district_code_list):
        #code = item['code']
        url_province_code =  item['code'][0:2]
        url_city_code = item['code'][2:4]
        url_district_code = item['code'][0:6]
        if(int(url_province_code) > 64):
            #print type(code)
            #if (code not in ["441900000000","442000000000","460400000000"]):
            page_url = common_url_prefix + url_province_code + "/" + url_city_code + "/" + url_district_code + ".html"
            #print page_url
            page_item = {}
            page_item['code'] = item['code']
            page_item['page_url'] = page_url
            page_urs.append(page_item)

    return page_urs

def get_district_code(street_code):
    for k,item in enumerate(district_code_list):
        d_code = item['code']
        d_code_pre = d_code[0:6]

        s_code_pre = street_code[0:6]
        if d_code_pre == s_code_pre:
            return item['code'], item['name']

def main():
    crawl_street_list();

if __name__ == '__main__':
    main()