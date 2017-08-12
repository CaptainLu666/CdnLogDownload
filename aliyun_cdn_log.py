#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys,os
import urllib, urllib2
import base64
import hmac
import hashlib
from hashlib import sha1
import time
import uuid
import json
#from optparse import OptionParser
#import ConfigParser
import traceback
import requests

#CONFIGFILE = os.getcwd() + '/config.ini'

class AliSign(object):
    def __init__(self, access_key_id, access_key_secret):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret

    def percent_encode(self, str):
        res = urllib.quote(str.decode(sys.stdin.encoding).encode('utf8'), '')
        res = res.replace('+', '%20')
        res = res.replace('*', '%2A')
        res = res.replace('%7E', '~')
        return res

    def compute_signature(self, parameters):
        sortedParameters = sorted(parameters.items(), key=lambda parameters: parameters[0])

        canonicalizedQueryString = ''
        for (k,v) in sortedParameters:
            canonicalizedQueryString += '&' + self.percent_encode(k) + '=' + self.percent_encode(v)

        stringToSign = 'GET&%2F&' + self.percent_encode(canonicalizedQueryString[1:])

        h = hmac.new(self.access_key_secret + "&", stringToSign, sha1)
        signature = base64.encodestring(h.digest()).strip()
        return signature

class AliCdn(object):
    def __init__(self, access_key_id, access_key_secret, host,
            cdn_server_address, StartTime, EndTime):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.host = host
        self.cdn_server_address = cdn_server_address
        self.StartTime = StartTime
        self.EndTime = EndTime
        self.user_params = { \
            'Action': 'DescribeCdnDomainLogs', \
            'DomainName' : self.host, \
            'StartTime' : self.StartTime, \
            'EndTime'   : self.EndTime, \
        }

    def compose_url(self):
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        parameters = { \
                'Format'        : 'JSON', \
                'Version'       : '2014-11-11', \
                'AccessKeyId'   : self.access_key_id, \
                'SignatureVersion'  : '1.0', \
                'SignatureMethod'   : 'HMAC-SHA1', \
                'SignatureNonce'    : str(uuid.uuid1()), \
                'TimeStamp'         : timestamp, \
        }
        for key in self.user_params.keys():
            parameters[key] = self.user_params[key]
        signature = AliSign(self.access_key_id,self.access_key_secret).compute_signature(parameters)
        parameters['Signature'] = signature
        url = self.cdn_server_address + '/?' + urllib.urlencode(parameters)
        try:
            res = requests.get(url)
            result = json.loads(res.text)
            url_list = []
            res_list = result['DomainLogModel']['DomainLogDetails']['DomainLogDetail']
            for url in res_list:
                url_list.append('http://' + url['LogPath'])
            return url_list
        except:
            print "download aliyun cdn logs error"


if __name__ == '__main__':
    print "aliyun cdn"
