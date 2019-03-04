#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql
from datetime import date
from sqlalchemy import *

from urllib import request
import re

from bs4 import BeautifulSoup



def create_table():
    '''student = Table('student', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(50)),
    Column('role', String(10)),
    Column('password', String(50))
            )
    

	'''
	
    vocabulary = Table('vocabulary', metadata,
    Column('id', Integer, primary_key=True),
    Column('word', String(30)),
    Column('part_of_speech', String(10)),
    Column('definition', String(100)),
    Column('synonym', String(30)),
    Column('antonym', String(30)))
    '''
        
    vocabulary = Table('vocabulary', metadata,
    Column('id', Integer, primary_key=True),
    Column('word', String),
    Column('part_of_speech', String),
    Column('definition', String),
    Column('synonym', String),
    Column('antonym', String)
        )   '''
    vocabulary.create(checkfirst=True)
    

def insert_student(user,passwd,total,new):
    student = Table('student', metadata, autoload=True, autoload_with=engine)
    ins = student.insert().values(name=user, role='student',password=passwd,total_per_day=total,new_per_day=new)
    result = conn.execute(ins)

def insert_parent(user,passwd):
    student = Table('student', metadata, autoload=True, autoload_with=engine)
    ins = student.insert().values(name=user, role='parent',password=passwd,total_per_day=0,new_per_day=0)
    result = conn.execute(ins)

def add_relation(parentlist,studentlist):
    relationship = Table('relationship', metadata, autoload=True, autoload_with=engine)
    for parent in parentlist:
        for student in studentlist: 	
            ins = relationship.insert().values(parent=parent,student=student)
            result = conn.execute(ins)
	
def update_user(user,passwd,total,new):
    student = Table('student', metadata, autoload=True, autoload_with=engine)
    stmt = student.update().where(student.c.name == user).values(password=passwd,total_per_day=total,new_per_day=new)
    #print(s)
    result = conn.execute(stmt)


def insert_word(this_student,new_word_list_filename,new_or_old):
    today = date.today()
    if new_or_old == 'new' or new_or_old =='New' :
        itisnew=True
    elif new_or_old == 'old' or new_or_old =='OLD':
        itisnew=False
    else:
        print('\nPlease make clear whether they are new or old word for the sutdent.')
        return

        
    wordlist = Table('wordlist', metadata, autoload=True, autoload_with=engine)

    f = open(new_word_list_filename,'r')
    for line in f:
        line = line.strip()
    
        s = select([wordlist]).where(and_(wordlist.c.word == line , wordlist.c.student == this_student))
        result = conn.execute(s)
        print(line,result.rowcount)
        print(result)
    
        if result.rowcount > 0:
            print("already in the database")
        else:
            print("insert this word into wordlist", line)
            #for row in conn.execute(s):
            ins = wordlist.insert().values(word = line, student = this_student, practice=0, value =0, correct =0 , wrong =0 ,new= itisnew, lasttime = today)
            result = conn.execute(ins)

	
#create_table()

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
    webster_defintion_url = r'http://www.learnersdictionary.com/definition/'
    webster_defintion_backup = r'https://www.merriam-webster.com/dictionary/'
    webster_thesaurus_url = r'https://www.merriam-webster.com/thesaurus/'

    bing_url=r'https://cn.bing.com/search?q=definition+'

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

print("Welcom! This the program for parent. \n\n")
print("1) add new wordlist.")
print("2) add new student.")
choiced = input("Please enter your choice:")

if int(choiced) == 1:
    print("\n\nLet's extend vocabulary!\n")
    new_word_list_filename = input("Please enter worldlist filename:")
    print("\nWe are add new words from %s. \n" % new_word_list_filename)
    add_new_word(new_word_list_filename)
    student = input("Please enter the student name(all means every student):")
    
    if student == 'all':
        this_student = 'Francis'
        insert_word(this_student,new_word_list_filename,new_or_old='new')
        this_student = 'Peter'
        insert_word(this_student,new_word_list_filename,new_or_old='new')
        this_student = 'Matthew'
        insert_word(this_student,new_word_list_filename,new_or_old='new')
    else:
        insert_word(student,new_word_list_filename,new_or_old='new')
        
'''
add student or update user
user = 'Matthew'
passwd = '2018'
total = 10
new = 5
#update_user(user,passwd,total,new)
#insert_user(user,passwd,total,new)
'''


'''
#add parent
user = 'Jackie'
passwd = '2018'
#update_user(user,passwd,total,new)
insert_parent(user,passwd)
'''

'''
studentlist = ['Francis','Peter','Matthew']
parentlist = ['Jackie','Frank']
add_relation(parentlist,studentlist)
'''
