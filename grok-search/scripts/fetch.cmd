@echo off
rem Windows wrapper for fetch.js - the .js file is a Node ES module, not JScript.
rem Running it directly (double-click / start) hands it to WScript.exe and fails with 800A03F6.
node "%~dp0fetch.js" %*
exit /b %ERRORLEVEL%
