#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql
from datetime import date
from sqlalchemy import *

engine = create_engine("mysql+pymysql://root:Frank123@104.225.154.46:3306/mysql", max_overflow=5)
metadata = MetaData(engine)
conn = engine.connect()



def create_table():
    '''student = Table('student', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(50)),
    Column('role', String(10)),
    Column('password', String(50))
            )
    
    student.create(checkfirst=True
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
    

def insert_user(user,passwd,total,new):
    student = Table('student', metadata, autoload=True, autoload_with=engine)
    ins = student.insert().values(name=user, role='student',password=passwd,total_per_day=total,new_per_day=new)
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


user = 'Francis'
passwd = '2018'
total = 12
new = 5
#update_user(user,passwd,total,new)
#insert_user(user,passwd,total,new)

new_word_list_filename = 'matthew_0118.txt'
this_student = 'Francis'
insert_word(this_student,new_word_list_filename,new_or_old='new')
this_student = 'Peter'
insert_word(this_student,new_word_list_filename,new_or_old='new')
this_student = 'Matthew'
insert_word(this_student,new_word_list_filename,new_or_old='new')

