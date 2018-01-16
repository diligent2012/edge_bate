#!/usr/bin/python
#coding:utf-8
# OTCBTC 
# 市场价格、最近成交价格、 当前卖出价格、当前买入价格

import sys,os
# sys.path.append("../../platform/")
sys.path.append("../../common/otcbtc")
sys.path.append("../../common")
reload(sys)
sys.setdefaultencoding('utf-8')

import sys  
import sqlite3
import requests
import json
from bs4 import BeautifulSoup
import re
from datetime import datetime
from datetime import timedelta
import MySQLdb
import time

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from decimal import *

import urllib
import urllib2
import json
import requests

import random

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



from global_setting import *
from util import *
from db import * 


user_agent_list = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11"
]


def get_github_eos_code():
    result={}
    header = {
    }
    header['User-Agent'] = random.sample(user_agent_list, 1)
    url = 'https://github.com/EOSIO/eos/tree/eos-noon'
    response = requests.get(url, headers=header, verify=False, allow_redirects=False)
    if response.status_code != 200:
        return result

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        info_list = soup.find('ul',class_="pagehead-actions").find_all('li')
        watch = info_list[0].find('a',class_="social-count").get_text().strip().replace(',','')
        star = info_list[1].find('a',class_="social-count").get_text().strip().replace(',','')
        fork = info_list[2].find('a',class_="social-count").get_text().strip().replace(',','')
        # print "Watch(查看): " + watch
        # print "Star(点赞): " + star
        # print "Fork(收藏): " + fork
        info_list_branch = soup.find('ul',class_="numbers-summary").find_all('li')
        commits = info_list_branch[0].find('span',class_="num").get_text().strip().replace(',','')
        branches = info_list_branch[1].find('span',class_="num").get_text().strip().replace(',','')
        releases = info_list_branch[2].find('span',class_="num").get_text().strip().replace(',','')
        contributors = info_list_branch[3].find('span',class_="num").get_text().strip().replace(',','')
        # print "commits(提交): " + commits
        # print "branches(分支): " + branches
        # print "releases(发布): " + releases
        # print "contributors(贡献者): " + contributors
        date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        content = get_send_content(watch, star, fork, commits, branches, releases, contributors)
        insert_btc_eos_github_code(watch, star, fork, commits, branches, releases, contributors, date)
        if (allow_send_time()):
            send_wechat(content)

    except Exception, e:
        print e.message

    return 0

def get_send_content(watch, star, fork, commits, branches, releases, contributors):
    prev_data = find_btc_eos_github_code_prev_one()

    prev_commits = prev_data['commits']
    prev_branches = prev_data['branches']
    prev_releases = prev_data['releases']
    prev_contributors = prev_data['contributors']

    prev_watch = prev_data['watch']
    prev_star = prev_data['star']
    prev_fork = prev_data['fork']

    commits_rate = round( (float(commits) - prev_commits) / prev_commits, 4) 
    branches_rate = round( (float(branches) - prev_branches) / prev_branches, 4)
    releases_rate = round( (float(releases) - prev_releases) / prev_releases, 4)
    contributors_rate = round( (float(contributors) - prev_contributors) / prev_contributors,4)

    watch_rate =  round( (float(watch) - prev_watch) / prev_watch,4 )
    star_rate = round( (float(star) - prev_star) / prev_star,4 )
    fork_rate = round( (float(fork) - prev_fork) / prev_fork,4 )

    content = "\nGitHub EOS 代码变更"
    content += "\ncommits: 上次:" + str(prev_commits) + " 当前: " + str(commits) + " 涨幅:" + str(commits_rate)
    content += "\nbranches: 上次:" + str(prev_branches) + " 当前: " + str(branches) + " 涨幅:" + str(branches_rate)
    content += "\nreleases: 上次:" + str(prev_releases) + " 当前: " + str(releases) + " 涨幅:" + str(releases_rate)
    content += "\ncontributors: 上次:" + str(prev_contributors) + " 当前: " + str(contributors) + " 涨幅:" + str(contributors_rate)
    
    content += "\nwatch: 上次:" + str(prev_watch) + " 当前: " + str(watch) + " 涨幅:" + str(watch_rate)
    content += "\nstar: 上次:" + str(prev_star) + " 当前: " + str(star) + " 涨幅:" + str(star_rate)
    content += "\nfork: 上次:" + str(prev_fork) + " 当前: " + str(fork) + " 涨幅:" + str(fork_rate)
    return  content

    

#入口
def start():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    get_github_eos_code()
    print "end : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

    

def main():
    start();

if __name__ == '__main__':
    main()