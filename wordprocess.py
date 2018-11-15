#! /usr/bin/env python 
# -*- coding: utf-8 -*- 
import sys 
reload(sys) # Python2.5 初始化后删除了 sys.setdefaultencoding 方法，我们需要重新载入 
sys.setdefaultencoding('utf-8')

import urllib2
import MySQLdb
import re
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup


def getantonym(html):
    print "get antonym"
    antonymlist=[' ',' ',' ']
    print '[2]=', antonymlist[2]
    se1=re.search(r'<div id="antoid".*?</div></div></div>' , html)
    if se1 is None:
        print "no antonym."
        return antonymlist
    text1=se1.group(0)
    #find antonym list text

    se2=re.findall(r'<span class="p1-4">.*?</span>' , text1)
    if se2 is None:
        return antonymlist
    
    print "antonym list:", se2
	
    i=0
    for text in se:
        if i>2:
            break
        antonym=re.sub(r'<span class="p1-4">' , "" , text)
        #cut head
        antonym=re.sub(r'</span>' , "" , antonym)
        #cut tail
        antonymlist[i]=antonym
        print "found antonym", i , ":" , antonym
        i=i+1
    return antonymlist

def getsynonym(html):
    print "get synonym"
    synonymlist=[' ',' ',' ']
    se1=re.search(r'<div id="synoid".*?</div></div></div>' , html)
    if se1 is None:
        print "no synomym."
        return synonymlist
    text1=se1.group(0)
    #find synonym list text
    
    se2=re.findall(r'<span class="p1-4">.*?</span>' , text1)
    print "se2=", se2
    if se2 is None:
        return synonymlist
    
    print "synonym list:", se2
	
    i=0
    for text in se2:
        if i>2:
            break
        synonym=re.sub(r'<span class="p1-4">',"",text)
        print synonym
        #cut head
        synonym=re.sub(r'</span>' , "" , synonym)
        #cut tail
        synonymlist[i]=synonym
        print "found synonym" , i , ":" , synonym
        i=i+1
    return synonymlist

def getchiexp(html):
    print "get chinese expernation\n"
    text=re.search(r'<span class="def"><span>.*?</span></span>' , html)
    print text
    chiexp=re.sub(r'<span class="def"><span>' , "" , text.group(0))
    chiexp=re.sub(r'</span></span>' , "" , chiexp)
    print "found chinese explanation:" , chiexp
    return chiexp

def getengexp(html):
    print "get english expernation\n"
    text=re.search(r'definition 1:</a></td>[\s\S]*?<div class=|definition:</a></td>[\s\S]*?<div class=' , html)
    print "1st get:", text
    if text is None:
        print "multi word encounter!"
        #find url,then cut tail
        text1=re.search(r'http://www.wordsmyth.net/\Slevel=1&amp;rid=.*?"',html)
        print "2nd get", text1
        newurl=re.sub(r'"',"",text1.group(0))
        newurl=re.sub(r'&amp;',"&",newurl)
        print "multi explantion. downloand new url\n" , newurl
        html=gethtml(newurl)
        #print html
        text=re.search(r'definition 1:</a></td>[\s\S]*?<div class=|definition:</a></td>[\s\S]*?<div class=' , html)
        print "2nd get result text:", text.group(0)
        print text.group(0)
    text=re.search(r'<td class="data">.*?<' , text.group(0))
    engexp=re.sub(r'<td class="data">' , "" , text.group(0))
    engexp=re.sub(r'<' , "" , engexp)
    print "found english explanation:" , engexp
    return engexp


def gethtml(url):
    print "downloading  ", url    
    html=urllib2.urlopen(url)
    #print(html)
    return html
		
def getmp3(word):
    url=wordurl + word
    print url
    request=urllib2.Request(url,headers=myheaders)
    txt=urllib2.urlopen(request).read()
    #print txt
    p=rex.search(txt)
    if p:  
        mp3url=p.group(0)
        print mp3url
        #try 3 times to get 
        for i in range(3):
            try:
                print "the " , i , " times try"  
                f1 = urllib2.urlopen(mp3url) 
                data = f1.read()
                mp3file=mp3location + word + '.mp3'
                print "writing ", mp3file
                with open(mp3file, "wb") as f2:     
                    f2.write(data)
                break                    
            except:
                print "get mp3 file error"
            else:
                break
         
    else:
        print "word not found\n"
 
bingurl=r'https://www.merriam-webster.com/dictionary/'
wordsmythurl=r'http://www.wordsmyth.net/?level=1&ent='
wordurl=r'http://dict.hjenglish.com/w/'
mp3location=r'/media/mp3/'
myheaders={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}


rex=re.compile("http.*?mp3")


db=MySQLdb.connect(host="104.225.154.146",user="root",passwd="Frank123",db="mysql",charset='utf8')
cursor=db.cursor(MySQLdb.cursors.DictCursor)
sql= "select * from wordlist where is_frozen is null;"

 
#cursor.execute(sql)
#results=cursor.fetchallDict()
#for row in results:
for i in range(1):
    #word=row['word']
    #wordlist=row['wordlist']
    word = 'word'
    #getmp3(word)
    html=gethtml(bingurl+word)
    soup = BeautifulSoup(html, "html.parser")
    result = soup.find('span',attrs={"class": "dtText"})
    print(result)
    print("text" + .result.text)
    tag = soup.span
    #print(tag)
    #<span class="dtText"><strong class="mw_t_bc">: </strong>a round or roundish body or mass: such as</span>
    '''#chiexp=getchiexp(html)
    #antonymlist=getantonym(html)
    #synonymlist=getsynonym(html)

    html=gethtml(wordsmythurl+word)
    engexp=getengexp(html)
  
    print "update database."
    
    sql="UPDATE wordlist SET is_frozen=TRUE, chi_exp='%s', eng_exp='%s',\
 synonym1='%s',synonym2='%s',synonym3='%s',antonym1='%s',antonym2='%s',antonym3='%s' \
 where word='%s' and wordlist='%s'; " % ( chiexp, engexp, synonymlist[0], synonymlist[1],\
 synonymlist[2], antonymlist[0], antonymlist[1], antonymlist[2], word, wordlist)
    print sql'''
    try:
        cursor.execute(sql)
        print "update database success"
        db.commit() 
    except:
        print "update database fail"


db.close()
