#!/usr/bin/env python
# coding=utf-8

import os
import re
import sys
import hashlib
import requests
import hmac
import random
import time
import base64
import json
import gzip
#from optparse import OptionParser
from datetime import datetime, timedelta
#from configparser import ConfigParser

#CONFIGFILE = os.getcwd() + '/config.ini'

class Sign(object):

    def __init__(self, secretId, secretKey):
        self.secretId = secretId
        self.secretKey = secretKey

    # 生成签名串
    def make(self, requestHost, requestUri, params, method='GET'):
        srcStr = method.upper() + requestHost + requestUri + '?' + "&".join(k.replace("_",".") + "=" + str(params[k]) for k in sorted(params.keys()))
        print srcStr
        hashed = hmac.new(self.secretKey, srcStr, hashlib.sha1)
        return base64.b64encode(hashed.digest())

class CdnHelper(object):

    def __init__(self, host, SecretId, SecretKey, requestHost, requestUri, startDate, endDate):
        self.SecretId = SecretId
        self.SecretKey = SecretKey
        self.requestHost = requestHost
        self.requestUri = requestUri
        self.host = host
        self.startDate = startDate
        self.endDate = endDate
        self.params = {
            'Timestamp': int(time.time()),
            'Action': 'GetCdnLogList',
            'SecretId': self.SecretId,
            'Nonce': random.randint(10000000,99999999),
            'host': self.host,
            'startDate': self.startDate,
            'endDate': self.endDate
        }
        self.params['Signature'] =  Sign(self.SecretId, self.SecretKey).make(self.requestHost,
                self.requestUri, self.params)
        self.url = 'https://%s%s' % (self.requestHost, self.requestUri)


    def GetCdnLogList(self):
        ret = requests.get(self.url, params=self.params,verify=False)
        #return ret.json()
        result = json.loads(ret.text)
        #result_list = result['data']['list'][0]
        result_list = result['data']['list']
        url_list = []
        for u in result_list:
            url_list.append(u['link'])
        return url_list

if __name__ == '__main__':
    print "tencent cdn"
