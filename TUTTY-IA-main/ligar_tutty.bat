@echo off
title Iniciando o TUTTY - Escola Roberto Tonellotti
echo =======================================================
echo    INICIANDO O TUTTY - ESCOLA ROBERTO TONELLOTTI
echo =======================================================
echo.
echo [1/3] Entrando na pasta do projeto...
cd /d "%~dp0"

echo [2/3] Iniciando o servidor Python em segundo plano...
:: Abre o servidor Python de forma assincrona para nao travar o script
start /b .\venv\Scripts\python.exe -m uvicorn main:app --port 8000

echo [3/3] Aguardando o sistema estabilizar...
:: Faz o computador esperar 2 segundos para o Python ligar totalmente
timeout /t 2 /nobreak >nul

echo 🎉 Pronto! Abrindo o ambiente no Google Chrome...
start chrome "http://127.0.0.1:8000"
