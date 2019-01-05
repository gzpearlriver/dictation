#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql
from sqlalchemy import *

#for command cls
import os

# fot text to voice
import pyttsx3


def get_words(student,oldwords,newwords):
    #get the number of new wornds
    wordlist = Table('wordlist', metadata, autoload=True, autoload_with=engine)
    stmt = text("SELECT count(*) as word_count FROM wordlist WHERE student = :x and new = True")
    stmt = stmt.bindparams(x=student)
    #print(str(stmt))
    result = conn.execute(stmt).fetchone()
    pending_new = result['word_count']
    print("There are %i new words to learn.\n" % pending_new)
    today_new = min(newwords, pending_new)
    print("Today you are goingt to pratice %i new words.\n " % today_new)
    today_old = oldwords + newwords - today_new
    print("Today you are goingt to pratice %i old words. \n " % today_old)

    if today_new > 0 :
        stmt = text("SELECT * FROM wordlist WHERE student = :x and value<0 order by value desc limit :y")
        stmt = stmt.bindparams(x=student, y=today_new)
        print(str(stmt))
        result = conn.execute(stmt).fetchall()
        print(result)
        

    if today_old > 0 :
        stmt = text("SELECT * FROM wordlist WHERE student = :x and new = False order by value limit :y")
        stmt = stmt.bindparams(x=student, y=today_old)
        print(str(stmt))
        result = conn.execute(stmt).fetchall()
        for row in result:
            word = row[wordlist.c.word]
            word = row['word']
            wrong = row[wordlist.c.wrong]
            correct = row[wordlist.c.correct]
            value = row[wordlist.c.value]
            
            dict_correct = dictate(word)  
            
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
            s = wordlist.update().where(and_(wordlist.c.student == student, wordlist.c.word == word)).values(value=value,wrong=wrong,correct=correct)
            #print(s)
            result = conn.execute(s)

            
def dictate(word):
    #print('working on word: %s' % word)
    #os.system("cls") # windows

    voice_engine.say('Now listen carefully and spell the word.')
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
   

    


        
engine = create_engine("mysql+pymysql://root:Frank123@104.225.154.46:3306/mysql", max_overflow=5)
metadata = MetaData(engine)
conn = engine.connect()
voice_engine = pyttsx3.init()

voice_engine.say("Welcome. Please enter your name")
voice_engine.runAndWait()
this_student = input('Your name is :')

#create_table()
#insert_user()
get_words(this_student,6,4)
