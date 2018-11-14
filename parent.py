#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql
from sqlalchemy import *

engine = create_engine("mysql+pymysql://root:Frank123@104.225.154.146:3306/mysql", max_overflow=5)
metadata = MetaData(engine)

student = Table('student', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(50)),
        Column('role', String(10)),
        Column('password', String(50))
        )

student.create(checkfirst=True)