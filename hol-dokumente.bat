@echo off
rem Doppelklicken. Ruft hol-dokumente.ps1 auf und umgeht dabei die
rem Ausfuehrungssperre von PowerShell, die fuer Skripte aus dem Netz gilt.
rem Erzeugt wird die .ps1 von build.py aus vorlage/dokumente.py.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0hol-dokumente.ps1"
