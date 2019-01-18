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


def insert_word(this_student,new_word_list_filename):
    today = date.today()
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
            ins = wordlist.insert().values(word = line, student = this_student, value =0, correct =0 , wrong =0 ,new= False, lasttime = today)
            result = conn.execute(ins)

	
#create_table()


user = 'Francis'
passwd = '2018'
total = 12
new = 5
#update_user(user,passwd,total,new)
#insert_user(user,passwd,total,new)


this_student = 'Francis'
new_word_list_filename = 'peter_word.txt'
insert_word(this_student,new_word_list_filename)
new_word_list_filename = 'simplemath.txt'
insert_word(this_student,new_word_list_filename)
new_word_list_filename = 'matthew_word.txt'
insert_word(this_student,new_word_list_filename)

