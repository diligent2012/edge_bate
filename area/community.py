#!/usr/bin/python
#coding:utf-8
# 居委会、社区

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
street_code_list = []


special_url_conn = ["http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/42/06/84/420684103.html","http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/50/01/53/500153108.html"]

special_url = [
    {
        "page_url" : "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/42/06/84/420684103.html",
        "encoding" : "gb18030"
    },
    {
        "page_url" : "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/50/01/53/500153108.html",
        "encoding" : "gb18030"
    }
]


def crawl_community_list():
   
    global street_code_list
    street_code_list = query_data(4)
    
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
            info_list = soup.find('table',class_="villagetable").find_all("tr",class_="villagetr")
            for k,item in enumerate(info_list):
               
                #street_url = street_url_prefix + item.contents[0].a.attrs['href'].encode('utf8')
                code = item.contents[0].get_text().encode('utf8')
                name = item.contents[2].get_text().encode('utf8')
                parent_code,parent_name = get_street_code(code)
                level = 5
                print code, name, parent_code, parent_name
                insert_data(code, name, parent_code, parent_name, level)
           
    except Exception, e:
        print traceback.format_exc()

def generate_page_url():
    page_urs = []
    for k,item in enumerate(street_code_list):
        #code = item['code']
        url_province_code =  item['code'][0:2]
        url_city_code = item['code'][2:4]
        url_district_code = item['code'][4:6]
        url_street_code = item['code'][0:9]

        temp_code = item['code'][0:6]
        if(int(temp_code) > 522324):
            page_url = common_url_prefix + url_province_code + "/" + url_city_code + "/" + url_district_code + '/' + url_street_code + ".html"
            page_item = {}
            page_item['code'] = item['code']
            page_item['page_url'] = page_url
            page_urs.append(page_item)

    return page_urs

def get_street_code(community_code):
    for k,item in enumerate(street_code_list):
        s_code = item['code']
        s_code_pre = s_code[0:9]
        c_code_pre = community_code[0:9]
        if s_code_pre == c_code_pre:
            return item['code'], item['name']

def main():
    crawl_community_list();

if __name__ == '__main__':
    main()