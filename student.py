#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql
from sqlalchemy import *

from datetime import date

#for command cls
import os

# fot text to voice
import pyttsx3


def dictate(student,today_totol,today_new):
    today = date.today()
    
    #get the number of new wornds
    wordlist = Table('wordlist', metadata, autoload=True, autoload_with=engine)
    stmt = text("SELECT count(*) as word_count FROM wordlist WHERE student = :x and new = True")
    stmt = stmt.bindparams(x=student)
    #print(str(stmt))
    result = conn.execute(stmt).fetchone()
    pending_new = result['word_count']
    
    announcment = "There are %i new words on the list to learn." % pending_new
    print('\n',announcment)
    voice_engine.say(announcment)
    voice_engine.runAndWait()
    
    today_new = min(today_new, pending_new)
    announcment = "Today you are going to practice %i new words." % today_new
    print('\n',announcment)
    voice_engine.say(announcment)
    voice_engine.runAndWait()
 
    today_old = today_totol - today_new
    announcment = "Today you are going to practice %i old words. " % today_old
    print('\n',announcment)
    voice_engine.say(announcment)
    voice_engine.runAndWait()
    

    if today_new > 0 :
        announcment = "\nLet's begin to try the new words."
        print('\n',announcment)
        voice_engine.say(announcment)
        voice_engine.runAndWait()
        
        stmt = text("SELECT * FROM wordlist WHERE student = :x and new = True order by value desc limit :y")
        stmt = stmt.bindparams(x=student, y=today_new)
        #print(str(stmt))
        result = conn.execute(stmt).fetchall()
        for row in result:
            word = row[wordlist.c.word]
            word = row['word']
            wrong = row[wordlist.c.wrong]
            correct = row[wordlist.c.correct]
            value = row[wordlist.c.value]
            practice = row[wordlist.c.practice]
            
            dict_correct = dictate_oneword(word) 
            
            if dict_correct:
                #本次正确
                if correct >0 and wrong == 0:
                    #连续正确
                    correct += 1
                else:
                    #其他情况
                    correct = 1
                    wrong = 0
                value += 2**correct
                #提升value值，至少2
                
            else:
                #本次错误
                if wrong >0 and correct ==0 :
                    #连续错误
                    wrong += 1
                else:
                    #其他情况
                    wrong = 1
                    correct = 0
                value -= 5*wrong
                #降低value值，至少减5
                
            #print (value,correct,wrong)    
            s = wordlist.update().where(and_(wordlist.c.student == student, wordlist.c.word == word)).values(lasttime=today,value=value,wrong=wrong,correct=correct,practice=practice+1)
            #print(s)
            result = conn.execute(s)
        

    if today_old > 0 :
        announcment = "\nLet's pratice to spell words we have already learned."
        print('\n',announcment)
        voice_engine.say(announcment)
        voice_engine.runAndWait()
        
        stmt = text("SELECT * FROM wordlist WHERE student = :x and new = False order by value limit :y")
        stmt = stmt.bindparams(x=student, y=today_old)
        #print(str(stmt))
        result = conn.execute(stmt).fetchall()
        for row in result:
            word = row[wordlist.c.word]
            word = row['word']
            wrong = row[wordlist.c.wrong]
            correct = row[wordlist.c.correct]
            value = row[wordlist.c.value]
            practice = row[wordlist.c.practice]
           
            dict_correct = dictate_oneword(word)  
            
            if dict_correct:
                #本次正确
                if correct >0 and wrong == 0:
                    #连续正确
                    correct += 1
                else:
                    #其他情况
                    correct = 1
                    wrong = 0
                value += 2**correct
                #提升value值，至少2
                
            else:
                #本次错误
                if wrong >0 and correct ==0 :
                    #连续错误
                    wrong += 1
                else:
                    #其他情况
                    wrong = 1
                    correct = 0
                value -= 5*wrong
                #降低value值，至少减5
                
            #print (value,correct,wrong)
            s = wordlist.update().where(and_(wordlist.c.student == student, wordlist.c.word == word)).values(lasttime=today,value=value,wrong=wrong,correct=correct,practice=practice+1)
            #print(s)
            result = conn.execute(s)
			
    #summary the progress in recent days
    announcment = "Today you have practiced %i new words and %i old words." % (today_new,today_old)
    print('\n',announcment)
    voice_engine.say(announcment)
    voice_engine.runAndWait()

    stmt = text("SELECT count(*) as master_word FROM wordlist WHERE student = :x and value>0")
    stmt = stmt.bindparams(x=student)
    result = conn.execute(stmt).fetchone()
    master_word = result['master_word']
    announcment = "And your have already mastered %i words since the beginning." % master_word
    print('\n',announcment)
    voice_engine.say(announcment)
    voice_engine.runAndWait()


            
def dictate_oneword(word):
    #print('working on word: %s' % word)
    #os.system("cls") # windows

    voice_engine.say('\n\nNow listen carefully and spell the word.')
    voice_engine.runAndWait()

    stmt = text("SELECT * FROM vocabulary WHERE word = :x ")
    stmt = stmt.bindparams(x=word)
    #print(str(stmt))
    vocabulary_row = conn.execute(stmt).fetchone()
    definition = vocabulary_row['definition']
    part_of_speech = vocabulary_row['part_of_speech']
    antonym = vocabulary_row['antonym']
    synonym = vocabulary_row['synonym']
    
    #play announcment

    voice_engine.say(word)
    voice_engine.runAndWait()

    voice_engine.say("Repeat. The word is:")
    voice_engine.runAndWait()

    voice_engine.say(word)
    voice_engine.runAndWait()
    
    print("The word you are going to spell is a %s .\n" % part_of_speech)
    print("Its definition is '%s' .\n" %  definition)
    print("Its synonym are '%s' .\n" %  synonym)
    print("Its antonym are '%s' .\n" %  antonym)    
    answer = input("So the word is : ")
    if answer == word:
        print("Good! You spelt correctly. \n\n")
        #os.system("Any key to move on. \n")
        return True
    else:
        print("You spelt incorrectly. You have to practie it for 5 times.\n")
        for i in range(5):
            while(True):
                print("\nPlease type the word %s ! This is the %i time.   " % (word,i))
                answer = input()
                if answer == word:
                    break
        #os.system("Any key to move on. \n")
        return False        
   

def get_student(student):
    #get the number of new wornds
    wordlist = Table('student', metadata, autoload=True, autoload_with=engine)
    stmt = text("SELECT * FROM student WHERE name = :x ")
    stmt = stmt.bindparams(x=student)
    #print(str(stmt))
    result = conn.execute(stmt)
    if result.rowcount > 0:
        row =result.fetchone()
        total_today= row['total_per_day']
        new_today= row['new_per_day']
        passwd = row['password']   
        return passwd,total_today,new_today
    else:
        return None,None,None

        
engine = create_engine("mysql+pymysql://root:Frank123@104.225.154.46:3306/mysql", max_overflow=5)
metadata = MetaData(engine)
conn = engine.connect()
voice_engine = pyttsx3.init()

voice_engine.say("Please enter your name.")
voice_engine.runAndWait()
this_student = input('Your name is :')

passwd,today_totol,today_new = get_student(this_student)

if today_totol == None:
    announcment = "Sorry, student %s is not found in the database! " % this_student
    print('\n',announcment)
    voice_engine.say(announcment)
    voice_engine.runAndWait()
else:    
    announcment = "Welcome, %s! " % this_student
    print('\n',announcment)
    voice_engine.say(announcment)
    voice_engine.runAndWait()
    dictate(this_student,today_totol,today_new)
    
#create_table()
#insert_user()

