#! /usr/bin/env python 
# -*- coding: utf-8 -*- 

'''import sys 
reload(sys) # Python2.5 初始化后删除了 sys.setdefaultencoding 方法，我们需要重新载入 
sys.setdefaultencoding('utf-8')'''

from urllib import request
import re
#import numpy as np
#import pandas as pd
from bs4 import BeautifulSoup

webster_defintion_url = r'https://www.merriam-webster.com/dictionary/'
webster_thesaurus_url = r'https://www.merriam-webster.com/thesaurus/'

bing_url=r'https://cn.bing.com/search?q=definition+'


def gethtml(url):
    print("downloading  ", url)    
    #page =u rllib2.urlopen(url)  #python 2.7
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
    req = request.Request(url, headers=headers)
    page = request.urlopen(req).read()
    page = page.decode('utf-8')
    return page



def dict(word):
	html = gethtml(webster_defintion_url + word)
	soup = BeautifulSoup(html, "html.parser")
	
	#<div role="heading" aria-level="3" class="dc_sth">NOUN</div>
	part_of_speech_span = soup.find('span',attrs={"class": "fl"}) #dc_sth
	if part_of_speech_span is None:
	    part_of_speech = 'NotFound'
	else:
	    part_of_speech = part_of_speech_span.text.strip()

	definition_span = soup.find('span',attrs={"class": "dtText"})
	if definition_span is None:
	    definition = 'NotFound'
	else:
	    [s.extract() for s in definition_span('span')]
	    #get rid of the example sentense quoted with span
	    definition = definition_span.text.strip()
	
	
	html=gethtml(webster_thesaurus_url + word)
	soup = BeautifulSoup(html, "html.parser")
	#class="thes-list syn-list"
	
	synonym_span = soup.find('span',attrs={"class": "thes-list syn-list"})
	if synonym_span is None:
	    synonym = 'NotFound'
	else:
	    synonym_list = synonym_span.find('div',attrs={"class": "thes-list-content"})
	    synonym = synonym_list.text.strip()
	
	
	antonym_span = soup.find('span',attrs={"class": "thes-list ant-list"})
	if antonym_span is None:
	    antonym = 'NotFound'
	else:
	    antonym_list = antonym_span.find('div',attrs={"class": "thes-list-content"})
	    antonym = antonym_list.text.strip()
	
	print(part_of_speech,definition,synonym,antonym)
	return(part_of_speech,definition,synonym,antonym)
	
word = 'love'
print(dict(word))
