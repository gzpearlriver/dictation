echo off
path=%path%;C:\Python;C:\Python\Lib;C:\Python\Scripts;C:\Program Files\Git\cmd;
cd C:\code\dictation
git pull
python student.py
echo on
echo "finished!"
pause
