#!/usr/bin/python
#coding:utf-8
import sys  
import urllib2
from urllib2 import HTTPError
import traceback
import random
import socket
import time
socket.setdefaulttimeout(60)

USER_AGENT_LIST = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17',
    'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)',
    'Mozilla/5.0 (Windows; U; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9a3pre) Gecko/20070330',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.13; ) Gecko/20101203',
    'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
    'Opera/9.80 (X11; Linux x86_64; U; fr) Presto/2.9.168 Version/11.50',
    'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; de) Presto/2.9.168 Version/11.52',
    'Mozilla/5.0 (Windows; U; Win 9x 4.90; SG; rv:1.9.2.4) Gecko/20101104 Netscape/9.1.0285',
    'Mozilla/5.0 (Macintosh; U; PPC Mac OS X Mach-O; en-US; rv:1.8.1.7pre) Gecko/20070815 Firefox/2.0.0.6 Navigator/9.0b3',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.12) Gecko/20080219 Firefox/2.0.0.12 Navigator/9.0.0.6',
]

def request_util(url, encoding_set = 'utf8', is_loop = False, proxy_port = None):
    try:
        req_header = {
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': None,
            'Connection': 'close',
            'Referer': None
        }
        if is_loop:
            pass
            #conf_ip,conf_port = get_proxy_conf()
            #socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, PROXY_IP_CONF, proxy_port)
            #socket.socket = socks.socksocket

        ua  = random.sample(USER_AGENT_LIST,1)[0]
        # for ua in USER_AGENT_LIST:
        #     req_header['User-Agent'] = ua
        req_header['User-Agent'] = ua
        print ua
        req = urllib2.Request(url, None, req_header)
        req_timeout = 60

        try:
            resp = urllib2.urlopen(req, None, timeout = req_timeout)
        except socket.timeout, e:
            time.sleep(3)
            #request_util(url, encoding_set, is_loop, proxy_port)
            resp = urllib2.urlopen(req, None, timeout = req_timeout)
        # except HTTPError, e:
        #     if e.code == 429:
        #         time.sleep(5)
        #         resp = urllib2.urlopen(req, None, timeout = req_timeout)
        #     else:
        #         resp = urllib2.urlopen(req, None, timeout =req_timeout)

        try:
            encoding = resp.headers['content-type'].split('charset=')[-1]
            #print sys.getfilesystemencoding()
            #for item in resp.headers:
                #print resp.headers[item]
            encoding = encoding_set
            html_content = unicode(resp.read(), encoding)

            #html_content = resp.read().decode('utf-8','replace').encode(sys.getfilesystemencoding())

            return html_content
        except LookupError, e:
           print traceback.format_exc()

        return ""

    except Exception, e:
        print traceback.format_exc()

    return None