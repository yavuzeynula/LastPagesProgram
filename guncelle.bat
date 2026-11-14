@echo off
rem Tek tik guncelleme: son kodu ceker, derler, GitHub release olarak yayinlar
cd /d "%~dp0"
git pull || goto hata
python yayinla.py || goto hata
echo.
echo TAMAM: guncelleme yayinda.
pause
exit /b 0
:hata
echo.
echo HATA: yukaridaki yaziyi Claude a yapistir.
pause
exit /b 1
