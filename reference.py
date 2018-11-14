
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pymysql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:Frank123@104.225.154.146:3306/mysql", max_overflow=5)
#Declare a Mapping
Base = declarative_base()
metadata = MetaData()

#############################
from sqlalchemy import inspect
inspector = inspect(engine)

#打印所有database
for database in inspector.get_schema_names():
    print(database)
    
#打印所有表
for table_name in inspector.get_table_names():
    print(table_name)
    
#打印所有表的所有列
for table_name in inspector.get_table_names():
   for column in inspector.get_columns(table_name):
       print("Column: %s" % column['name'])

for column in inspector.get_columns('users'):
    print("Column: %s" % column['name'])
       
#另一种形式
from sqlalchemy import MetaData
m = MetaData()
m.reflect(engine)
for table in m.tables.values():
    print(table.name)
    for column in table.c:
        print(column.name)
        
        
        
def init_db():
    Base.metadata.create_all(engine)

def drop_db():
    Base.metadata.drop_all(engine)
    
# 创建单表, 感觉不大好
class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    extra = Column(String(16))
    __table_args__ = (
    UniqueConstraint('id', 'name', name='uix_id_name'),
    Index('ix_id_name', 'name', 'extra'),
    )
    
#步骤1：创建session
Session = sessionmaker(bind=engine)
session = Session()

Users.create(engine) # creates the users table
Users.drop(engine) # drops the users table

SQL expession 
#另一种创建单表的方法：Table()  推荐
from sqlalchemy import MetaData 
engine = create_engine("mysql+pymysql://root:Frank123@104.225.154.146:3306/mysql", max_overflow=5)
metadata = MetaData(engine)

users = Table('user', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(50)),
        Column('fullname', String(100))
        )

address = Table('address', metadata,
        Column('id', Integer, primary_key=True),
        Column('user_id', None, ForeignKey('user.id')),
        Column('email', String(128), nullable=False)
        )

#全部创建
metadata.create_all()
#单独创建
user_table.create(checkfirst=True)
address_table.create(checkfirst=True)

#插入
ins = users.insert()
str(ins)
'INSERT INTO users (id, name, fullname) VALUES (:id, :name, :fullname)'
Notice above that the INSERT statement names every column in the users table. This can be limited by using the values() method, which establishes the VALUES clause of the INSERT explicitly:

#执行和执行
ins = users.insert().values(name='jack', extra='Jack Jones')
conn = engine.connect()
result = conn.execute(ins)

#另一种插入
>>> ins = users.insert()
>>> conn.execute(ins, id=2, name='wendy', fullname='Wendy Williams')

#执行多条插入
>>> conn.execute(addresses.insert(), [
...    {'user_id': 1, 'email_address' : 'jack@yahoo.com'},
...    {'user_id': 1, 'email_address' : 'jack@msn.com'},
...    {'user_id': 2, 'email_address' : 'www@www.org'},
...    {'user_id': 2, 'email_address' : 'wendy@aol.com'},
... ])

#发射已存在的表，不用自己重新定义
users = Table('users', metadata, autoload=True, autoload_with=engine)

#查询
from sqlalchemy.sql import select
s = select([users])
result = conn.execute(s)
#SELECT users.id, users.name, users.fullname
#FROM users
#()

#注意result只能逐行提取一次，提完就消失了。即for循环只能做一次
for row in result:
    print(row)
(1, u'jack', u'Jack Jones')
(2, u'wendy', u'Wendy Williams')

#按列名取值
row = result.fetchone()
print("name:", row['name'], "; extra:", row['extra'])
name: jack ; fullname: Jack Jones

#按列号取值
row = result.fetchone()
print("name:", row[1], "; fullname:", row[2])
name: wendy ; fullname: Wendy Williams

#对象取值
>>> for row in conn.execute(s):
...     print("name:", row[users.c.name], "; fullname:", row[users.c.fullname])
name: jack ; fullname: Jack Jones
name: wendy ; fullname: Wendy Williams

#遍历所有行
>>> s = select([users.c.name, users.c.fullname])
SQL>>> result = conn.execute(s)
>>> for row in result:
...     print(row)
(u'jack', u'Jack Jones')
(u'wendy', u'Wendy Williams')

#两表叉乘
>>> for row in conn.execute(select([users, addresses])):
...     print(row)
(1, u'jack', u'Jack Jones', 1, 1, u'jack@yahoo.com')
(1, u'jack', u'Jack Jones', 2, 1, u'jack@msn.com')
(1, u'jack', u'Jack Jones', 3, 2, u'www@www.org')
(1, u'jack', u'Jack Jones', 4, 2, u'wendy@aol.com')
(2, u'wendy', u'Wendy Williams', 1, 1, u'jack@yahoo.com')
(2, u'wendy', u'Wendy Williams', 2, 1, u'jack@msn.com')
(2, u'wendy', u'Wendy Williams', 3, 2, u'www@www.org')
(2, u'wendy', u'Wendy Williams', 4, 2, u'wendy@aol.com')

#两表关联
>>> s = select([users, addresses]).where(users.c.id == addresses.c.user_id)
SQL>>> for row in conn.execute(s):
...     print(row)
(1, u'jack', u'Jack Jones', 1, 1, u'jack@yahoo.com')
(1, u'jack', u'Jack Jones', 2, 1, u'jack@msn.com')
(2, u'wendy', u'Wendy Williams', 3, 2, u'www@www.org')
(2, u'wendy', u'Wendy Williams', 4, 2, u'wendy@aol.com')

#关联词
>>> from sqlalchemy.sql import and_, or_, not_
>>> print(and_(
...         users.c.name.like('j%'),
...         users.c.id == addresses.c.user_id,
...         or_(
...              addresses.c.email_address == 'wendy@aol.com',
...              addresses.c.email_address == 'jack@yahoo.com'
...         ),
...         not_(users.c.id > 5)
...       )
...  )

#多行插入
>>> stmt = users.insert().\
...         values(name=bindparam('_name') + " .. name")
>>> conn.execute(stmt, [
...        {'id':4, '_name':'name1'},
...        {'id':5, '_name':'name2'},
...        {'id':6, '_name':'name3'},
...     ])

#更新
>>> stmt = users.update().\
...             where(users.c.name == 'jack').\
...             values(name='ed')

>>> conn.execute(stmt)
UPDATE users SET name=? WHERE users.name = ?
('ed', 'jack')
COMMIT

#删除表内容
>>> conn.execute(addresses.delete())
DELETE FROM addresses
()
COMMIT


# 新增单条数据
obj = Users(name="Peter", extra='children')
session.add(obj)

ret = session.query(Users).all() # 查询所有
sql = session.query(Users) # 查询生成的sql
print(sql)
ret = session.query(Users.name, Users.extra).all() #查询User表的name和extra列的所有数据
ret = session.query(Users).filter_by(name='Peter').all()  # 取全部name列为alex的数据


        
        
#表的反射（Table Reflection）
#表创建好了，一般也就不动了。所以实际应用时，往往表都已经存在，并不需要创建，只需把它们”导入”进来即可，这时就得使用 autoload 参数。

from sqlalchemy import create_engine, MetaData, Table

engine = create_engine('mysql+mysqldb://root:******@localhost/sa_test', echo=False)
metadata = MetaData(engine)

user_table = Table('user', metadata, autoload=True)

print 'user' in metadata.tables
print [c.name for c in user_table.columns]

address_table = Table('address', metadata, autoload=True)
print 'address' in metadata.tables