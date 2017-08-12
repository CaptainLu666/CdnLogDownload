#!/usr/bin/env python
# encoding: utf-8
import os
import time
import datetime
from configparser import ConfigParser
from optparse import OptionParser
from tencent_cdn_log import *
from ws_cdn_log import *
from aliyun_cdn_log import *

CONFIGFILE = os.getcwd() + '/config.ini'


def download(link, name):
    try:
        r = requests.get(link)
        with open(name, 'ab') as f:
            f.write(r.content)
        return True
    except:
        return False
    finally:
        f.close()

def local2utc(local_st):
    '''本地时间转UTC时间（-8:00)'''
    local_time = datetime.datetime.strptime(local_st,'%Y-%m-%d %H:%M:%S')
    time_struct = time.mktime(local_time.timetuple())
    utc_st = datetime.datetime.utcfromtimestamp(time_struct)
    utc_time = utc_st.strftime("%Y-%m-%dT%H:%M:%SZ")
    return utc_time

def local2ws(local_st):
    local_time = datetime.datetime.strptime(local_st,'%Y-%m-%d %H:%M:%S')
    ws_time = local_time.strftime('%Y-%m-%d-%H%M')
    return ws_time

if __name__ == '__main__':
    log_dir = '/data/logs/cdn'

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    usage = "usage: %prog [options] args"
    parser = OptionParser(usage=usage)
    parser.add_option("-s", "--start", action="store",type="string",dest="startTime",help="input start time:' yyyy-MM-dd HH:mm:ss',for example: '2017-07-17 00:00:00'")
    parser.add_option("-e", "--end", action="store",type="string",dest="endTime",help="input end time: 'yyyy-MM-dd HH:mm:ss',for example: '2017-07-18 00:00:00'")
    (options, args) = parser.parse_args()
    s_t = options.startTime.replace(' ','').replace('-','').replace(':','')
    e_t = options.endTime.replace(' ','').replace('-','').replace(':','')
    host = ''.join(args)
    log_name = log_dir + '/' + host + '-' + s_t + '-' + e_t + '.gz'
    cfg = ConfigParser()
    cfg.read(CONFIGFILE)
    tencent_host = str(cfg.get("tencentcdn","host")).split(",")
    ws_host = str(cfg.get("wscdn","host")).split(",")
    aliyun_host = str(cfg.get("aliyuncdn","host")).split(",")
    if host in tencent_host:
        SecretId = str(cfg.get("tencentcdn","SecretId"))
        SecretKey = str(cfg.get("tencentcdn","SecretKey"))
        requestHost = str(cfg.get("tencentcdn","requestHost"))
        requestUri = str(cfg.get("tencentcdn","requestUri"))
        startTime = options.startTime
        endTime = options.endTime
        obj = CdnHelper(host, SecretId, SecretKey, requestHost,
                requestUri, startTime, endTime)
        res = obj.GetCdnLogList()
        print log_name
        for d_list in res:
            download(d_list,log_name)
    elif host in ws_host:
        user = str(cfg.get('wscdn','user'))
        passwd = str(cfg.get('wscdn','password'))
        query_url = str(cfg.get('wscdn','query_url'))
        start_time = local2ws(options.startTime)
        end_time = local2ws(options.endTime)
        link = request_url(query_url,user,passwd,start_time,end_time,host)
        print log_name
        for d_list in link:
            download(d_list,log_name)

    elif host in aliyun_host:
        cdn_server_address = str(cfg.get('aliyuncdn','requestHost'))
        access_key_id = str(cfg.get('aliyuncdn','SecretId'))
        access_key_secret = str(cfg.get('aliyuncdn','SecretKey'))
        StartTime = local2utc(options.startTime)
        EndTime = local2utc(options.endTime)
        obj = AliCdn(access_key_id, access_key_secret, host,
                cdn_server_address, StartTime, EndTime)
        res = obj.compose_url()
        print log_name
        for d_list in res:
            download(d_list,log_name)
    else:
        print 'donmain is non-existent'
