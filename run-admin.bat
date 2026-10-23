@echo off
title AURA — Admin Governance Console
cd /d "%~dp0"
if not exist "%JAVA_HOME%\bin\java.exe" (
    set "JAVA_HOME="
    for /d %%J in (".tools\jdk17-download\jdk-*") do set "JAVA_HOME=%%~fJ"
)
if defined JAVA_HOME set "PATH=%JAVA_HOME%\bin;%PATH%"
echo ========================================================
echo   Launching AURA Admin Governance Console (Slide 22)
echo   Logged in as: Campus Maintenance (Administrator)
echo   Connected to: Supabase Cloud PostgreSQL
echo ========================================================
if exist "target\aura.jar" (
    java -jar target\aura.jar --admin
) else (
    ".tools\apache-maven-3.9.9\bin\mvn.cmd" compile exec:java -Dexec.args="--admin"
)
pause
