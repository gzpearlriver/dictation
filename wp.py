#! /usr/bin/env python 
# -*- coding: utf-8 -*- 
import sys 
reload(sys) # Python2.5 初始化后删除了 sys.setdefaultencoding 方法，我们需要重新载入 
sys.setdefaultencoding('utf-8')

from urllib import request
import re
#import numpy as np
#import pandas as pd
from bs4 import BeautifulSoup


def gethtml(url):
    print("downloading  ", url)    
    #page =u rllib2.urlopen(url)  #python 2.7
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
    req = request.Request(url, headers=headers)
    page = request.urlopen(req).read()
    page = page.decode('utf-8')
    return page

bingurl=r'https://www.merriam-webster.com/dictionary/'


word = 'word'
html=gethtml(bingurl+word)
soup = BeautifulSoup(html, "html.parser")
result = soup.find('span',attrs={"class": "dtText"})
	