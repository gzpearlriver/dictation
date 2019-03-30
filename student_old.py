#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql
from sqlalchemy import *

#for command cls
import os

#for song
import random, sys
from ctypes import windll, c_buffer

from gtts import gTTS

#to play mp3
class Song(object):
    def __init__(self, filename):
        self._mci = windll.winmm.mciSendStringW
        self._mcierr = windll.winmm.mciGetErrorStringA

        self.filename = filename
        self._alias = 'song_{}'.format(random.random())

        self._send('open {} alias {}'.format(self.filename, self._alias ))
        self._send('set {} time format milliseconds'.format(self._alias))
        # todo: 以下两行代码无法返回正确结果
        mcicode, mcistr=self._send('status {} length'.format(self._alias))
        self._length_ms = int(mcistr)

    def _send(self, command):
        buffer = c_buffer(1024)
        mcicode = self._mci(command, buffer, 1023, 0)
        mcistr = buffer.value.decode('gbk')
        if mcicode:
            self._mcierr(int(mcicode), buffer, 1023)
            mcistr = buffer.value.decode('gbk')
            print('Error: {}'.format(mcistr))
        return mcicode, mcistr

    def play(self):
        self._send('play {}'.format(self._alias))

    def pause(self):
        self._send('pause {}'.format(self._alias))

    def resume(self):
        self._send('resume {}'.format(self._alias))

    def stop(self):
        self._send('stop {}'.format(self._alias))
        # 不明白seek指令
        self._send('seek {} to start'.format(self._alias))

    def _mode(self):
        mcicode, mcistr = self._send('status {} mode'.format(self._alias))
        # 返回值: p:正在播放(包括暂停) s:停止播放 
        # todo: 检测暂停
        return mcistr

    def isplaying(self):
        return self._mode() == 'p'

    # 无法返回正确值
    # todo: 返回正确值
    def milliseconds(self):
        return self._length_ms

    # 无法返回正确值
    # todo: 返回正确值
    def seconds(self):
        return int(float(self.milliseconds()) / 1000)

    def volume(self, level):
        # todo: 添加错误处理
        # assert level >=0 and level <= 100
        self._send('setaudio {} volume to {}'.format(self._alias, level * 10))

    # del Song的时候执行
    def __del__(self):
        if self.isplaying():
            self.stop()
        else:
            self._send('close {}'.format(self._alias))


def getvoice(words,filename):
    tts = gTTS(words)
    tts.save('1.mp3')
    return(filename + '.mp3')

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
        stmt = text("SELECT * FROM wordlist WHERE student = :x and new == False order by value limit :y")
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
                    correct == 1
                    wrong == 0
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
                
            s = wordlist.update().where(and_(wordlist.c.student == student, wordlist.c.word == word)).values(value=value,wrong=wrong,correct=correct)
            print(s)
            result = conn.execute(s)

            
def dictate(word):
    #print('working on word: %s' % word)
    os.system("cls") # windows
    announcment = Song(announcment_file)
    announcment.play()
    
    stmt = text("SELECT * FROM vocabulary WHERE word = :x ")
    stmt = stmt.bindparams(x=word)
    #print(str(stmt))
    vocabulary_row = conn.execute(stmt).fetchone()
    definition = vocabulary_row['definition']
    part_of_speech = vocabulary_row['part_of_speech']
    antonym = vocabulary_row['antonym']
    synonym = vocabulary_row['synonym']

    print("The word you are going to spell is a %s .\n" % part_of_speech)
    print("Its definition is '%s' .\n" %  definition)
    print("Its synonym are '%s' .\n" %  synonym)
    print("Its antonym are '%s' .\n" %  antonym)
    
    #play announcment

    voicefile = getvoice(word, "voice\\" + word)
    voice = Song(voicefile)
    voice.play()
    
    answer = input("So the word is : ")
    if answer == word:
        print("Good! You spelt correctly. \n\n")
        os.system("Any key to move on. \n")
        return True
    else:
        print("You spelt incorrectly. You have to practie it for 5 times.\n")
        for i in range(5):
            while(True):
                print("\nPlease type the word %s ! This is the %i time.   " % (word,i))
                answer = input()
                if answer == word:
                    break
        os.system("Any key to move on. \n")
        return False        
   

    


        
engine = create_engine("mysql+pymysql://root:Frank123@104.225.154.46:3306/mysql", max_overflow=5)
metadata = MetaData(engine)
conn = engine.connect()

this_student = 'Peter'
announcment_file = getvoice("Now listen carefully and spell the word:","dict_announcment")
announcment = Song(announcment_file)
#create_table()
#insert_user()
get_words('Peter',6,4)
