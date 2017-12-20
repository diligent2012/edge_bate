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
import traceback
from util import request_util

#prefix = 'http://www.runchina.org.cn/portal.php?mod=calendar&ac=list'
book_tags_url = "https://book.douban.com/tag/"
book_url = "https://book.douban.com"


def crawl_tags():
    response = request_util(book_tags_url);
    try:
        soup = BeautifulSoup(response, "html.parser")
        info_list = soup.find_all('table',class_="tagCol")
        for item in info_list:
            content_list = item.find_all("a")
            for content in content_list:
                page_url_prefix = book_url + content.attrs['href'].encode('utf8')
                tag = page_url_prefix.split("tag/",1)[1]
                crawl_book_list(page_url_prefix,tag)
                
    except Exception, e:
        print traceback.format_exc()



def crawl_book_list(page_url_prefix = '',tag = ''):

    try:
        page_url_list.append(page_url_prefix)
        for page in range(0, 101):
            if(page == 0 ):
                page_url = page_url_prefix
            else:
                start_num = 20 * page
                suffix = "?start=" + str(start_num) + "&amp;type=T"
                page_url = page_url_prefix + suffix
            
            print page_url + tag

            insert_data(page_url,tag)


    except Exception, e:
        print traceback.format_exc()


def crawl_page(url):
   

    try:
        response = request_util(url);
        soup = BeautifulSoup(response, "html.parser")
        info_list = soup.find('ul',class_="subject-list").find_all('li')
        for item in info_list:
            print item.find('div',class_="info").find("h2").find("a").get_text().strip().replace('\n', '').replace(' ', '').encode('utf8')
            print item.find("div",class_="star").find("span",class_="rating_nums").get_text().strip()
            authors = item.find("div",class_="pub").get_text().strip().split("/")

            new_authors = []
            for item in authors:
                new_authors.append(item.strip())


            for i in range(-3,0):
                new_authors.pop(i)

            print new_authors
            #print '/'.join(new_authors)


    except Exception, e:
        print traceback.format_exc()

def insert_data(url,tag):

    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='develop',
            passwd='!123456Mysql.',
            db ='t_drp_system',
        )
        cur = conn.cursor()
        print type(url)
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "INSERT INTO `ecs_t_book_url` (`url`,`tag`) VALUES ('%s', '%s')" % (url, tag)
        print sql
        #sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`) VALUES ('%s', '%s')" % (name, start_run_time)
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    except Exception, e:
        print e.message


def crawl_start():
    #crawl_tags()
    url = "https://book.douban.com/tag/%E5%B0%8F%E8%AF%B4?start=80&type=T"
    crawl_page(url)


def main():
    crawl_start();

if __name__ == '__main__':
    main()