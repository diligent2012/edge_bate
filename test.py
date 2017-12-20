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

url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wx4834e00a5d81c714&secret=aab3dffdd0936152341a99c0dfd5e949"


def crawl_tags():
    response = request_util(url);
    try:
        print response
                
    except Exception, e:
        print traceback.format_exc()


def crawl_start():
    crawl_tags()


def main():
    crawl_start();

if __name__ == '__main__':
    main()