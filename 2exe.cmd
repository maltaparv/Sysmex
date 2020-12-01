rem яЁютхЁър эр яхЁхфрээ√х ярЁрьхЄЁ√:
if x%1==x goto Err01

set fname=%1
set fn=%fname:~0,-3%
rem fn - если в качестве параметра ввидить имя файла с расширением .py - три последних символа отсекаются.

set PathTo=%2
set ArcName=%3

set da=%date%
set dd=%da:~0,2%
set mm=%da:~3,2%
set gg=%da:~6,4%
set ArcName=%3%dd%

echo pyinstaller --onedir --onefile --name=%1 %1.py 
rem pyinstaller --onedir --onefile --name=%fn% %fn%.py
pyinstaller --onedir --onefile --name=%fn% -i "C:\DRV\Sysmex550\sysmex550.ico" %fn%.py

rem с иконкой:
rem pyinstaller --onedir --onefile --name=%1 -i "C:\Data\Icon.ico" %1.py
exit

:Err01
echo No parms! (Нет параметра!)