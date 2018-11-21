#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql
from sqlalchemy import *

engine = create_engine("mysql+pymysql://root:Frank123@104.225.154.146:3306/mysql", max_overflow=5)
metadata = MetaData(engine)
conn = engine.connect()

new_word_list_filename = 'peter_word.txt'

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
			Column('antonym', String(30))
		)
	'''

	vocabulary = Table('vocabulary', metadata,
			Column('id', Integer, primary_key=True),
			Column('word', String),
			Column('part_of_speech', String),
			Column('definition', String),
			Column('synonym', String),
			Column('antonym', String)
		)	'''
	vocabulary.create(checkfirst=True)
	

def insert_user():
	ins = student.insert().values(name='Peter', role='student',password='2018')
	result = conn.execute(ins)
	ins = student.insert().values(name='Mattew', role='student',password='2018')
	result = conn.execute(ins)

'''	
vocabulary = Table('vocabulary', metadata, autoload=True, autoload_with=engine)
	
f = open(new_word_list_filename,'r')
for line in f:
    line = line.strip()
    s = select([vocabulary]).where(vocabulary.c.word == line)
    result = conn.execute(s)
    print(line,result.rowcount)
    if result.rowcount > 0:
        print("already in the database")
    else:
        print("insert this word", line)
        #for row in conn.execute(s):
        ins = vocabulary.insert().values(word = line)
        result = conn.execute(ins)
	
'''
create_table()
