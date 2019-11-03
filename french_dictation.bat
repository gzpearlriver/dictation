echo off
path=%path%;C:\Python;C:\Python\Lib;C:\Python\Scripts;D:\code\dictation;C:\Program Files\Git\cmd;
path=%path%;C:\Python36;C:\Python36\Lib;C:\Python36\Scripts;
path=%path%;C:\Python3;C:\Python3\Lib;C:\Python3\Scripts;
cd D:\code\dictation
git pull
python french_student.py
echo on
echo "finished!"
pause
