#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 01:32:02 2017

@author: star
"""

import re
import time
from datetime import datetime
from bs4 import BeautifulSoup

def value(element):
    article = str(element)
    classtext = ''
    if len(re.findall('(苹果|iPhone|诺基亚|华为|三星|Oppo|Vivo|小米|一加|智能手机)', article, re.I)) >= 5:
        classtext += 'smartphone,'
    if len(re.findall('(百度|阿里|腾讯|支付宝|微信)', article)) >= 5:
        classtext += 'bat,'
    if len(re.findall('(共享单车|摩拜|ofo|小蓝单车)', article, re.I)) >= 5:
        classtext += 'bikesharing,'
    if len(re.findall('(人工智能|深度学习|图像识别|语音识别|机器人)', article, re.I)) >= 5:
        classtext += 'ai,'
    if len(re.findall('(英特尔|英伟达|NVIDA|CPU|GPU|FPGA|芯片)', article, re.I)) >= 5:
        classtext += 'hardware,'
    if classtext == '':
        if len(re.findall('(区块链|比特币|虚拟货币|数字货币|加密货币|微软|电脑|笔记本|游戏|手游|电池|VR|AR)', article, re.I)) >= 5:
            classtext += 'others,'
    elif len(classtext[:-1].split(',')) == 5:
        classtext = ''
    if classtext:
        classtext += 'general,'
    return classtext

def detecttime(soup):
    possibletimelist = re.findall('\d{2,4}\s?\D\s?\d{1,2}\s?\D\s?\d{1,2}', str(soup))
    timemark = 0
    for eachtime in possibletimelist:
        if re.search(':', eachtime):
            continue
        timegruop = [int(d) for d in re.findall('\d+', eachtime)]
        try:
            stime = tuple(timegruop)+(0, 0, 1, 0, 0, 0)
            timeinsecondformat = time.mktime(stime)
        except OverflowError or ValueError:
            continue
        unixtimestamp = time.time()
        # 以距离1970年1月1日的秒数为单位的时间，用来与time.time()比较
        if 0 < unixtimestamp - timeinsecondformat < 31536000:
            # 如果文章发布时间与现在时间的间隔小于一年（31536000秒）
            if timeinsecondformat > timemark:
                timemark = timeinsecondformat
    if timemark != 0:
        return timemark
    else:
        return 'cannot detect time'

if __name__ == '__main__':
    tsoup = BeautifulSoup('<html></html>', 'html.parser')
    print(detecttime(tsoup))