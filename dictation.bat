echo off
path=%path%;C:\Python;C:\Python\Lib;C:\Python\Scripts;D:\code\dictation;C:\Program Files\Git\cmd;
cd D:\code\dictation
git pull
python student.py
echo on
echo "finished!"
pause
