rem �������������� ����� � .py
rem �������� �� ���������� ���������:
rem if x%1==x goto Err01

rem C:\Users\user\AppData\Local\Programs\Python\Python38\Lib\site-packages\qt5_applications\Qt\bin
pyuic5 mydesign.ui -o mydesign.py
exit

:Err01
echo No parms! (��� ���������!)