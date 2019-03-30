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
	
def update_student(user,passwd,total,new):
    student = Table('student', metadata, autoload=True, autoload_with=engine)
    stmt = student.update().where(student.c.name == user).values(password=passwd,total_per_day=total,new_per_day=new)
    #print(s)
    result = conn.execute(stmt)

def list_student():
    wordlist = Table('student', metadata, autoload=True, autoload_with=engine)
    
    stmt = text("SELECT * FROM student")
    result = conn.execute(stmt)
    if result.rowcount > 0:
        print("%-30s%-20s%-20s" %("name","total_per_day","new_per_day"))
        for row in result:
            print("%-30s%-20s%-20s" %(row['name'],row['total_per_day'],row['new_per_day']))
        
    print("\nThat's all.")
    print("="*60)
    print("\n")
    
def insert_word(this_student,new_word_list_filename,new_or_old,value):
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
    
        vocabulary = Table('vocabulary', metadata, autoload=True, autoload_with=engine)
        s = select([vocabulary]).where(vocabulary.c.word == line)
        result = conn.execute(s)

        if result.rowcount <= 0:
            print("%s not in the vocabulary yet...." % line)
        else:
            #already in vocabulary
            s = select([wordlist]).where(and_(wordlist.c.word == line , wordlist.c.student == this_student))
            result = conn.execute(s)
            #print(line,result.rowcount)
            #print(result)
        
            if result.rowcount > 0:
                print("already in the database......update the value only")
                upd = wordlist.update().where(and_(wordlist.c.word == line , wordlist.c.student == this_student)).values(value=value)
                #print(upd)
                conn.execute(upd)
            else:
                print("insert this word into wordlist", line)
                #for row in conn.execute(s):
                ins=wordlist.insert().values(word=line, student=this_student, practice=0, value=value, correct=0 , wrong=0 ,new=itisnew,lasttime=today)
                result = conn.execute(ins)

	
#create_table()

def gethtml(url):
    print("downloading  ", url)    
    #page =u rllib2.urlopen(url)  #python 2.7
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
    #proxies = { "http": "proxy.gmcc.net:8081", "https": "proxy.gmcc.net:8081", } 
    try:
        req = request.Request(url,headers=headers)
        #req = request.Request(url,headers=headers,proxies=proxies)
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
    wordsmyth_url = 'https://kids.wordsmyth.net/we/?ent='
    bing_url = r'https://cn.bing.com/search?q=definition+'
    wordsmyth = r'https://kids.wordsmyth.net/we/?ent='
    
    #default value is None
    definition = None
    part_of_speech = None
    synonym = None
    antonym = None
    
    #get definition
    html = gethtml(webster_defintion_url + word)
    #find definition in http://www.learnersdictionary.com
    
    if not html is None : 
        soup = BeautifulSoup(html, "html.parser")
        #<div role="heading" aria-level="3" class="dc_sth">NOUN</div>
        part_of_speech_span = soup.find('span',attrs={"class": "fl"}) #dc_sth
        if not part_of_speech_span is None:
            part_of_speech = part_of_speech_span.text.strip()
            part_of_speech = string_max(part_of_speech, 10)
        
        div = soup.find('div',attrs={"class": "sblock_c"}) 
        if not div is None:
            definition_span = div.find('span',attrs={"class": "def_text"})
            if definition_span is None:
                #try antother tag
                definition_span = div.find('span',attrs={"class": "un_text"})
                
            if not definition_span is None:
                #[s.extract() for s in definition_span('span')]
                #get rid of the example sentense quoted with span          
                definition = definition_span.text.strip()
                definition = string_max(definition, 200)


    '''    
    #no defintion is found, so try bing.cn        
    if definition is None or part_of_speech is None:
        html = gethtml(bing_url + word)
        if not html is None : 
            soup = BeautifulSoup(html, "html.parser")
            #<div role="heading" aria-level="3" class="dc_sth">NOUN</div>
            part_of_speech_div = soup.find('div',attrs={"class": "dc_sth"})
            print(part_of_speech_div)
            if not part_of_speech_div is None:
                part_of_speech = part_of_speech_div.text.strip()
                part_of_speech = string_max(part_of_speech, 10)
                
            definition_div = soup.find('div',attrs={"class": "dc_mn"})
            print(definition_div)
            if not definition_div is None:
                definition = definition_div.text.strip()
                definition = string_max(definition, 200)'''
                
    if definition is None or part_of_speech is None:
        html = gethtml(wordsmyth + word)
        if not html is None : 
            try:
                soup = BeautifulSoup(html, "html.parser")
                tr = soup.find('tr',attrs={"class": "postitle"})
                td = tr.find('td',attrs={"class": "data"})
                #print(td.a.contents[0])
                if not td.a.contents[0] is None:
                    part_of_speech = td.a.contents[0].strip()
                    part_of_speech = string_max(part_of_speech, 10)
    
                tr = soup.find('tr',attrs={"class": "definition"})
                td = tr.find('td',attrs={"class": "data"})
                #print(td.contents[0])
                if not td.contents[0] is None:
                    definition = td.contents[0].strip()
                    definition = string_max(definition, 200)
            except:
                 print(wordsmyth,"parse error")

    #get synonym and antonym
    html=gethtml(webster_thesaurus_url + word)
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
            if (not definition is None) and (not part_of_speech is None):
                ins = vocabulary.insert().values(word = line,part_of_speech=part_of_speech,definition=definition,synonym=synonym,antonym=antonym)
                print(ins)
                result = conn.execute(ins)
            else:
                print("Sorry. I can not find the definiton for  %s! I have to skip it....." % line)
			
def check_word(thisword):
    vocabulary = Table('vocabulary', metadata, autoload=True, autoload_with=engine)
    s = select([vocabulary]).where(vocabulary.c.word == thisword)
    result = conn.execute(s)
    if result.rowcount <= 0:
        print("%s is not in the talbe vocabulary now." % thisword)
    else:
        for row in result:
            print("\npart of speech  ")
            print(row['part_of_speech'])
            print("\ndefinition ") 
            print(row['definition'])
            print("\nsynonym ")
            print(row['synonym'])
            print("\nantonym") 
            print(row['antonym'])
    
    wordlist = Table('wordlist', metadata, autoload=True, autoload_with=engine)
    s = select([wordlist]).where(wordlist.c.word == thisword)
    result = conn.execute(s)
    if result.rowcount <= 0:
        print("%s is not in the talbe wordlist now." % thisword)
    else:
        for row in result:
            print(row)

def update_vocabulary():
    vocabulary = Table('vocabulary', metadata, autoload=True, autoload_with=engine)
    s = select([vocabulary])
    #.where(vocabulary.c.word == 'photo')
    result = conn.execute(s)
    if result.rowcount <= 0:
        print("no word is in the talbe vocabulary now." )
    else:
        for row in result:
            word = row['word']
            print("\nupdateing this word: %s !" % word)
            part_of_speech,definition,synonym,antonym = dict(word)
            if (not definition is None) and (not part_of_speech is None):
                upd = vocabulary.update().where(vocabulary.c.word == word).values(part_of_speech=part_of_speech,definition=definition,synonym=synonym,antonym=antonym)
                #print(upd)
                conn.execute(upd)            
			
def delete_word(thisword):
    vocabulary = Table('vocabulary', metadata, autoload=True, autoload_with=engine)
    stmt=vocabulary.delete().where(vocabulary.c.word == thisword)
    print(stmt)
    conn.execute(stmt)
    wordlist = Table('wordlist', metadata, autoload=True, autoload_with=engine)
    stmt=wordlist.delete().where(wordlist.c.word == thisword)
    print(stmt)
    conn.execute(stmt)

    
def list_wordlist(student,orderby = 'value'):
    wordlist = Table('wordlist', metadata, autoload=True, autoload_with=engine)
    
    #new words
    print("\n%s 's top 10 new words in his or her list: \n" %student)
    stmt = text("SELECT * FROM wordlist WHERE student = :x and new = True order by value limit 10 ")
    stmt = stmt.bindparams(x=student)
    print(str(stmt))
    result = conn.execute(stmt)
    if result.rowcount > 0:
        print("%-30s%-30s%-10s%-10s%-10s%-10s" %("word","lasttime","practiced","correct","wrong","value"))
        for row in result:
            print("%-30s%-30s%-10s%-10s%-10s%-10s" %(row['word'],row['lasttime'],row['practice'],row['correct'],row['wrong'],row['value']))
        
    print("\nThat's all.")
    print("="*60)
    print("\n")
    
    #old words
    print("\n%s 's old words in his or her list: \n" %student)
    stmt = text("SELECT * FROM wordlist WHERE student = :x  and new = False order by value ")
    stmt = stmt.bindparams(x=student)
    print(str(stmt))
    result = conn.execute(stmt)
    if result.rowcount > 0:
        print("%-30s%-30s%-10s%-10s%-10s%-10s" %("word","lasttime","practiced","correct","wrong","value"))
        for row in result:
            print("%-30s%-30s%-10s%-10s%-10s%-10s" %(row['word'],row['lasttime'],row['practice'],row['correct'],row['wrong'],row['value']))
        
    print("\nThat's all.")
    print("="*60)    
    print("\n")
	
engine = create_engine("mysql+pymysql://root:Frank123@104.225.154.46:3306/mysql", max_overflow=5)
metadata = MetaData(engine)
conn = engine.connect()

print("\nWelcome! This the program for parent. \n\n")

while True:
    print("0) quit.")
    print("1) add new wordlist.")
    print("2) delete word.")
    print("3) check word definition.")
    print("4) add new student.")
    print("5) update definiton.")
    print("6) list student's wordlist.")
    print("7) list students.")
    print("8) update student's config.")
    choiced = input("Please enter your choice:")

    if not choiced.isdigit():
        print("Please input a digit.\n")
        continue
              
    choiced = int(choiced)
    if choiced == 0:
        print("see you .....")
        break
    
    elif choiced == 1:
        print("\n\nLet's extend vocabulary!\n")
        value = input("Please enter value for the new worldlist(default is 0, high priorty with negative number):")
        new_word_list_filename = input("Please enter worldlist filename:")
        print("\nWe are add new words from %s. \n" % new_word_list_filename)
        add_new_word(new_word_list_filename)
        student = input("Please enter the student name(all means every student):")
        
        if student == 'all':
            this_student = 'Francis'
            insert_word(this_student,new_word_list_filename,new_or_old='new',value=value)
            this_student = 'Peter'
            insert_word(this_student,new_word_list_filename,new_or_old='new',value=value)
            this_student = 'Matthew'
            insert_word(this_student,new_word_list_filename,new_or_old='new',value=value)
        else:
            insert_word(student,new_word_list_filename,new_or_old='new',value=value)
    
    elif choiced == 2:
        thisword = input("Please enter the word to check: ")
        delete_word(thisword)    
    
    elif choiced == 3:
        thisword = input("Please enter the word to check: ")
        check_word(thisword)    
        part_of_speech,definition,synonym,antonym = dict(thisword)
        print("="*60)
        print(part_of_speech,definition,synonym,antonym)
    
    elif choiced == 4:
        student = input("Please enter the student name: ")
        password = input("Please enter the password: ")
        total = input("Please enter how many words to practice: (recommend 10) ")
        new = input("Please enter how many new words to learn: (recommed 5)")
        insert_user(user,passwd,total,new)
	
    elif choiced == 5:
        update_vocabulary()

    elif choiced == 6:
        student = input("Please enter the student name: ")
        list_wordlist(student)
        
    elif choiced == 7:
        list_student()

    elif choiced == 8:
        update_student('Peter','2018',12,5)

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
