#! /usr/bin/env python 
# -*- coding: utf-8 -*- 

'''import sys 
reload(sys) # Python2.5 初始化后删除了 sys.setdefaultencoding 方法，我们需要重新载入 
sys.setdefaultencoding('utf-8')'''

from urllib import request
import re

from bs4 import BeautifulSoup
import pymysql
from sqlalchemy import *

webster_defintion_url = r'http://www.learnersdictionary.com/definition/'
webster_defintion_backup = r'https://www.merriam-webster.com/dictionary/'
webster_thesaurus_url = r'https://www.merriam-webster.com/thesaurus/'

bing_url=r'https://cn.bing.com/search?q=definition+'


def gethtml(url):
    print("downloading  ", url)    
    #page =u rllib2.urlopen(url)  #python 2.7
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
    try:
        req = request.Request(url, headers=headers)
        page = request.urlopen(req).read()
        page = page.decode('utf-8')
    except:
        page = None
    return page


def string_max(string,len_max):
    if len(string)>len_max:
        return string[0:len_max]
    else:
        return string


def dict(word):
    #get definition
    html = gethtml(webster_defintion_url + word)

    if not html is None : 
    #find definition in http://www.learnersdictionary.com
    
        soup = BeautifulSoup(html, "html.parser")
        #<div role="heading" aria-level="3" class="dc_sth">NOUN</div>
        part_of_speech_span = soup.find('span',attrs={"class": "fl"}) #dc_sth
        if part_of_speech_span is None:
            part_of_speech = 'NotFound'
        else:
            part_of_speech = part_of_speech_span.text.strip()
            part_of_speech = string_max(part_of_speech, 10)
            
        definition_span = soup.find('span',attrs={"class": "def_text"})
        if definition_span is None:
            definition = 'NotFound'
        else:
            #[s.extract() for s in definition_span('span')]
            #get rid of the example sentense quoted with span
            
            definition = definition_span.text.strip()
            definition = string_max(definition, 200)
    
    else:
        html = gethtml(webster_defintion_backup + word)
        if not html is None : 
            #find definition in http://www.learnersdictionary.com
            soup = BeautifulSoup(html, "html.parser")
            #<div role="heading" aria-level="3" class="dc_sth">NOUN</div>
            part_of_speech_span = soup.find('span',attrs={"class": "fl"}) #dc_sth
            if part_of_speech_span is None:
                part_of_speech = 'NotFound'
            else:
                part_of_speech = part_of_speech_span.text.strip()
                part_of_speech = string_max(part_of_speech, 10)
                
            definition_span = soup.find('span',attrs={"class": "dtText"})
            if definition_span is None:
                definition = 'NotFound'
            else:
                [s.extract() for s in definition_span('span')]
                #get rid of the example sentense quoted with span
                definition = definition_span.text.strip()
                definition = string_max(definition, 200)
                
        else:        
        #no definition!
            print ("%s is not in the dictionary" % word)
            return ( None, None, None , None)
    
    #get synonym and antonym
    html=gethtml(webster_thesaurus_url + word)
    synonym = 'Not Found'
    antonym = 'Not Found'

    if not html is None :
        soup = BeautifulSoup(html, "html.parser")
        #class="thes-list syn-list"
        synonym_span = soup.find('span',attrs={"class": "thes-list syn-list"})
        if not synonym_span is None:
            synonym_list = synonym_span.find('div',attrs={"class": "thes-list-content"})
            synonym = synonym_list.text.strip()
            synonym = string_max(synonym, 100)
        
        antonym_span = soup.find('span',attrs={"class": "thes-list ant-list"})
        if not antonym_span is None:
            antonym_list = antonym_span.find('div',attrs={"class": "thes-list-content"})
            antonym = antonym_list.text.strip()
            antonym = string_max(antonym, 100)
        
    print(part_of_speech)
    print(definition)
    print(synonym)
    print(antonym)
    return(part_of_speech,definition,synonym,antonym)


    
    
def add_new_word(new_word_list_filename):
    vocabulary = Table('vocabulary', metadata, autoload=True, autoload_with=engine)

    f = open(new_word_list_filename,'r')
    for line in f:
        print("\n\n")
        line = line.strip()
        s = select([vocabulary]).where(vocabulary.c.word == line)
        result = conn.execute(s)
        print(line,result.rowcount)
        if result.rowcount > 0:
            print("%s already in the database." % line)
        else:
            print("insert this word: %s !" % line)
            #for row in conn.execute(s):
            part_of_speech,definition,synonym,antonym = dict(line)
            if not definition is None :
                ins = vocabulary.insert().values(word = line,part_of_speech=part_of_speech,definition=definition,synonym=synonym,antonym=antonym)
                print(ins)
                result = conn.execute(ins)

engine = create_engine("mysql+pymysql://root:Frank123@104.225.154.46:3306/mysql", max_overflow=5)
metadata = MetaData(engine)
conn = engine.connect()

#new_word_list_filename = 'simplemath.txt'
#new_word_list_filename = 'peter_word.txt'
#new_word_list_filename = 'matthew_word.txt'
new_word_list_filename = 'matthew_0118.txt'

add_new_word(new_word_list_filename)
