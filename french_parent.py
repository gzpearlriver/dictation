#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql
from datetime import date
from sqlalchemy import *

from urllib import request
import urllib

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
    student = Table('french_student', metadata, autoload=True, autoload_with=engine)
    ins = student.insert().values(name=user, role='student',password=passwd,total_per_day=total,new_per_day=new)
    result = conn.execute(ins)

def insert_parent(user,passwd):
    student = Table('french_student', metadata, autoload=True, autoload_with=engine)
    ins = student.insert().values(name=user, role='parent',password=passwd,total_per_day=0,new_per_day=0)
    result = conn.execute(ins)

def add_relation(parentlist,studentlist):
    relationship = Table('french_relationship', metadata, autoload=True, autoload_with=engine)
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
    wordlist = Table('french_student', metadata, autoload=True, autoload_with=engine)
    
    stmt = text("SELECT * FROM french_student")
    result = conn.execute(stmt)
    if result.rowcount > 0:
        print("%-30s%-20s%-20s%-20s%-20s%-20s" %("name","total_per_day","new_per_day","practice_word","master_word","new_word"))
        for row in result:
            student = row['name']
            
            stmt_count = text("SELECT count(*) as practice_word FROM french_wordlist WHERE student = :x and new = False")
            stmt_count = stmt_count.bindparams(x=student)
            result_count = conn.execute(stmt_count).fetchone()
            practice_word = result_count['practice_word']

            stmt_count = text("SELECT count(*) as master_word FROM french_wordlist WHERE student = :x and value>0 and new = False")
            stmt_count = stmt_count.bindparams(x=student)
            result_count = conn.execute(stmt_count).fetchone()
            master_word = result_count['master_word']

            stmt_count = text("SELECT count(*) as new_word FROM french_wordlist WHERE student = :x and new = True")
            stmt_count = stmt_count.bindparams(x=student)
            result_count = conn.execute(stmt_count).fetchone()
            new_word = result_count['new_word']

            print("%-30s%-20s%-20s%-20s%-20s%-20s" %(row['name'],row['total_per_day'],row['new_per_day'],practice_word,master_word,new_word))
        
    print("\nThat's all student's config.")
    print("="*60)
    print("\n")

    
def insert_word(this_student,new_word_list_filename,new_or_old,initial):
    today = date.today()
    if new_or_old == 'new' or new_or_old =='New' :
        itisnew=True
    elif new_or_old == 'old' or new_or_old =='OLD':
        itisnew=False
    else:
        print('\nPlease make clear whether they are new or old word for the sutdent.')
        return

        
    wordlist = Table('french_wordlist', metadata, autoload=True, autoload_with=engine)

    f = open(new_word_list_filename,'r', encoding='utf-8')
    for line in f:
        line = line.strip()
    
        vocabulary = Table('french', metadata, autoload=True, autoload_with=engine)
        s = select([vocabulary]).where(vocabulary.c.french == line)
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
                print("%s already in the database......update the initial only" % line)
                upd = wordlist.update().where(and_(wordlist.c.word == line , wordlist.c.student == this_student)).values(initial=initial, new=itisnew, lasttime=today)
                #print(upd)
                conn.execute(upd)
            else:
                print("insert this word into wordlist", line)
                #for row in conn.execute(s):
                ins=wordlist.insert().values(word=line, student=this_student, practice=0, initial=initial, value =0, correct=0 , wrong=0 ,new=itisnew, lasttime=today)
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


def french_dict(word):
    collins_french_url = 'https://www.collinsdictionary.com/dictionary/french-english/'
    
    #default value is None
    pos1,eng1,eng_sen1,fre_sen1,pos2,eng2,eng_sen2,fre_sen2,pos3,eng3,eng_sen3,fre_sen3 = None,None,None,None,None,None,None,None,None,None,None,None
    
    #get definition
    html = gethtml(collins_french_url + urllib.parse.quote(word))

    
    if not html is None : 
        soup = BeautifulSoup(html, "html.parser")
        part_of_speech_span = soup.find('span',attrs={"class": "pos"}) 
        
        div1 = soup.find('div',attrs={"class": "cB cB-def dictionary biling"})
        if not div1 is None:
        
            part_of_speech_span = div1.find('span',attrs={"class": "pos"}) 
            if not part_of_speech_span is None:
                pos1 = part_of_speech_span.text.strip()
                pos1 = string_max(pos1, 30)  #fix it someday, extend to 20 character
            
            english_span = div1.find('span',attrs={"class": "quote"}) 
            if not english_span is None:
                eng1 = english_span.text.strip()
                eng1 = string_max(eng1, 200)

            example_div = div1.find('div',attrs={"class": "cit type-example"}) 
            if not example_div is None:
                sentence_span = example_div.find_all('span',attrs={"class": "quote"}) 
                if not sentence_span is None:
                    fre_sen1 = sentence_span[0].text.strip()
                    fre_sen1 = string_max(fre_sen1, 300)  
            
                    eng_sen1 = sentence_span[1].text.strip()
                    eng_sen1 = string_max(eng_sen1, 300)  

        
    print(pos1,eng1,fre_sen1,eng_sen1)

    return(pos1,eng1,eng_sen1,fre_sen1,pos2,eng2,eng_sen2,fre_sen2,pos3,eng3,eng_sen3,fre_sen3)


    
    
def add_new_word(new_word_list_filename):
    vocabulary = Table('french', metadata, autoload=True, autoload_with=engine)

    f = open(new_word_list_filename,'r', encoding='utf-8')
    for line in f:
        print("\n\n %s" %line)
        line = line.strip()
        s = select([vocabulary]).where(vocabulary.c.french == line)
        result = conn.execute(s)
        print(line,result.rowcount)
        if result.rowcount > 0:
            print("%s already in the database." % line)
        else:
            print("insert this word: %s !" % line)
            #for row in conn.execute(s):
            pos1,eng1,eng_sen1,fre_sen1,pos2,eng2,eng_sen2,fre_sen2,pos3,eng3,eng_sen3,fre_sen3 = french_dict(line)
            
            if (not eng1 is None) :
                ins = vocabulary.insert().values(french= line,
                                                 part_of_speech1=pos1,
                                                 english1=eng1,
                                                 french_sentence1=fre_sen1,
                                                 english_sentence1=eng_sen1,
                                                 part_of_speech2=pos2,
                                                 english2=eng2,
                                                 french_sentence2=fre_sen2,
                                                 english_sentence2=eng_sen2,
                                                 part_of_speech3=pos3,
                                                 english3=eng3,
                                                 french_sentence3=fre_sen3,
                                                 english_sentence3=eng_sen3)
                                                 
                #print(ins)
                result = conn.execute(ins)
            else:
                print("Sorry. I can not find the definiton for  %s! I have to skip it....." % line)
			
            
def check_word(thisword):
    vocabulary = Table('french', metadata, autoload=True, autoload_with=engine)
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
    
    wordlist = Table('french_wordlist', metadata, autoload=True, autoload_with=engine)
    s = select([wordlist]).where(wordlist.c.word == thisword)
    result = conn.execute(s)
    if result.rowcount <= 0:
        print("%s is not in the talbe wordlist now." % thisword)
    else:
        for row in result:
            print(row)

def update_vocabulary():
    vocabulary = Table('french', metadata, autoload=True, autoload_with=engine)
    s = select([vocabulary])
    #.where(vocabulary.c.word == 'photo')
    result = conn.execute(s)
    if result.rowcount <= 0:
        print("no word is in the talbe vocabulary now." )
    else:
        for row in result:
            word = row['word']
            print("\nupdateing this word: %s !" % word)
            part_of_speech,definition,synonym,antonym =french_dict(word)
            if (not definition is None) and (not part_of_speech is None):
                upd = vocabulary.update().where(vocabulary.c.word == word).values(part_of_speech=part_of_speech,definition=definition,synonym=synonym,antonym=antonym)
                #print(upd)
                conn.execute(upd)            
			
def delete_french_word(thisword):
    vocabulary = Table('french', metadata, autoload=True, autoload_with=engine)
    stmt=vocabulary.delete().where(vocabulary.c.french == thisword)
    print(stmt)
    conn.execute(stmt)
    wordlist = Table('french_wordlist', metadata, autoload=True, autoload_with=engine)
    stmt=wordlist.delete().where(wordlist.c.word == thisword)
    print(stmt)
    conn.execute(stmt)

    
def list_wordlist(student,orderby = 'value'):
    wordlist = Table('french_wordlist', metadata, autoload=True, autoload_with=engine)
    
    #new words
    print("\n%s 's top 10 new words in his or her list: \n" %student)
    stmt = text("SELECT * FROM french_wordlist WHERE student = :x and new = True order by initial limit 10 ")
    stmt = stmt.bindparams(x=student)
    print(str(stmt))
    result = conn.execute(stmt)
    if result.rowcount > 0:
        print("%-30s%-30s%-10s%-10s%-10s%-10s" %("word","lasttime","practiced","correct","wrong","initial"))
        for row in result:
            print("%-30s%-30s%-10s%-10s%-10s%-10s" %(row['word'],row['lasttime'],row['practice'],row['correct'],row['wrong'],row['initial']))
        
    print("\nThat's all.")
    print("="*60)
    print("\n")
    
    #old words
    print("\n%s 's old words in his or her list: \n" %student)
    stmt = text("SELECT * FROM french_wordlist WHERE student = :x  and new = False order by (value+initial) ")
    stmt = stmt.bindparams(x=student)
    print(str(stmt))
    result = conn.execute(stmt)
    if result.rowcount > 0:
        print("%-30s%-30s%-10s%-10s%-10s%-10s%-20s" %("word","lasttime","practiced","correct","wrong","initial","value+initial"))
        for row in result:
            print("%-30s%-30s%-10s%-10s%-10s%-10s%-20s" %(row['word'],row['lasttime'],row['practice'],row['correct'],row['wrong'],row['initial'],row['value']+row['initial']))
        
    print("\nThat's all.")
    print("="*60)    
    print("\n")

def init_user():
    #add parent
    user = 'Jackie'
    passwd = '2018'
    insert_parent(user,passwd)
    
    user = 'Frank'
    passwd = '2018'
    insert_parent(user,passwd)
    
    #add student
    user = 'Peter'
    passwd = '2018'
    total = 8
    new =2
    insert_student(user,passwd,total,new)
    
    user = 'Francis'
    passwd = '2018'
    total = 8
    new =2
    insert_student(user,passwd,total,new)
    
    user = 'Matthew'
    passwd = '2018'
    total = 8
    new =2
    insert_student(user,passwd,total,new)
    
    studentlist = ['Francis','Peter','Matthew']
    parentlist = ['Jackie','Frank']
    add_relation(parentlist,studentlist)
	
engine = create_engine("mysql+pymysql://root:Frank123@66.98.125.27:3306/dictation", max_overflow=5)
metadata = MetaData(engine)
conn = engine.connect()

print("\nWelcome! This the program for parent. \n\n")

while True:
    print("0) quit.")
    print("1) add new wordlist.")
    print("2) delete word.")
    print("3) check word definition.")
    print("4) add new student.")
    print("5) update all definiton in the database(don't do that).")
    print("6) list student's wordlist.")
    print("7) list students.")
    print("8) update student's config.")
    print("9) initiate student and parent's config.")
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
        initial = input("Please enter initial value for the new worldlist(default is 0, high priorty with negative number):")
        new_word_list_filename = input("Please enter worldlist filename:")
        print("\nWe are add new words from %s. \n" % new_word_list_filename)
        add_new_word(new_word_list_filename)
        student = input("Please enter the student name(all means every student):")
        
        if student == 'all':
            this_student = 'Francis'
            insert_word(this_student,new_word_list_filename,new_or_old='new',initial=initial)
            this_student = 'Peter'
            insert_word(this_student,new_word_list_filename,new_or_old='new',initial=initial)
            this_student = 'Matthew'
            insert_word(this_student,new_word_list_filename,new_or_old='new',initial=initial)
        else:
            insert_word(student,new_word_list_filename,new_or_old='new',initial=initial)
    
    elif choiced == 2:
        thisword = input("Please enter the word to check: ")
        delete_french_word(thisword)    
    
    elif choiced == 3:
        thisword = input("Please enter the word to check: ")
        check_word(thisword)    
        part_of_speech,definition,synonym,antonym =french_dict(thisword)
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
        student = input("Please enter the student name: ")
        #password = input("Please enter the password: ")
        total = input("Please enter how many words to practice: (recommend 10) ")
        new = input("Please enter how many new words to learn: (recommed 5)")
        update_student(student,'2018',total,new)

    elif choiced == 9:
        init_user()
