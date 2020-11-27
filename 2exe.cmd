rem проверка на переданные параметры:
if x%1==x goto Err01
set fname=%1
set PathTo=%2
set ArcName=%3

set da=%date%
set dd=%da:~0,2%
set mm=%da:~3,2%
set gg=%da:~6,4%
set ArcName=%3%dd%

pyinstaller --onedir --onefile --name=%1 %1.py 

rem б ®™Ѓ≠™Ѓ©:
rem pyinstaller --onedir --onefile --name=%1 %1.py -i "C:\Data\Icon.ico 
exit

:Err01
echo No parms! (Н•в ѓ†а†ђ•ва†!)