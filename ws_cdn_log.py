#!/usr/bin/env python
# encoding: utf-8
import os
import json
import requests
import time
import datetime
from configparser import ConfigParser


#CONFIGFILE = os.getcwd() + '/config.ini'



def request_url(query_url,user,passwd,start_time,end_time,channels):
    r1 = requests.get(query_url,allow_redirects = False)
    r_url1 = r1.headers['Location']
    r_url1_https = r_url1.replace('http','https')
    rq_params = {'u': user,'p': passwd,'channel': channels}
    r2 = requests.get(r_url1_https,params=rq_params,allow_redirects = False)
    rq_params2 = {'start_time': start_time,'end_time': end_time,'channels': channels}
    r_url2 = r2.headers['Location']
    r3 = requests.get(r_url2,params=rq_params2,allow_redirects = False)
    print r_url2
    result = json.loads(r3.text)
    result_list = result['logs'][0]['files']
    url_list = []
    for u in result_list:
        url_list.append(u['url'])
    return url_list


if __name__ == '__main__':
    print 'wangsu cdn'
