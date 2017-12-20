#!/usr/bin/python
#coding:utf-8
# 省份、自治区
# 
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
from db import insert_data


province_url = "http://www.stats.gov.cn/tjsj/tjbz/xzqhdm/201703/t20170310_1471429.html"

code_list = []

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
                parent_name = ""
                level = 1
                # p_code_item = {}
                # p_code_item['code'] = code
                # p_code_item['name'] = name
                # province_code_list.append(p_code_item)
                insert_data(code, name, parent_code, parent_name, level)

    except Exception, e:
        print traceback.format_exc()



def main():
    crawl_province_list();

if __name__ == '__main__':
    main()