#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql
from sqlalchemy import *

engine = create_engine("mysql+pymysql://root:Frank123@104.225.154.146:3306/mysql", max_overflow=5)
metadata = MetaData(engine)
conn = engine.connect()

def create_table():
	student = Table('student', metadata,
			Column('id', Integer, primary_key=True),
			Column('name', String(50)),
			Column('role', String(10)),
			Column('password', String(50))
			)
	
	student.create(checkfirst=True)
	
	vocabulary = Table('vocabulary', metadata,
			Column('id', Integer, primary_key=True),
			Column('word', String(30)),
			Column('definition', String(100)),
			Column('synonym', String(30)),
			Column('antonym', String(30))
		)
	
	vocabulary.create(checkfirst=True)
	

def insert_user():
	ins = student.insert().values(name='Peter', role='student',password='2018')
	result = conn.execute(ins)
	ins = student.insert().values(name='Mattew', role='student',password='2018')
	result = conn.execute(ins)

	
