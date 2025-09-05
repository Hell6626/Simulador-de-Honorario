@echo off
echo 🌐 Iniciando Simulador de Honorários na Rede Local
echo ================================================

echo.
echo 📋 Verificando configurações...
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado! Instale Python 3.8+ primeiro.
    pause
    exit /b 1
)

REM Verificar se Node.js está instalado
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js não encontrado! Instale Node.js 16+ primeiro.
    pause
    exit /b 1
)

echo ✅ Python e Node.js encontrados!

echo.
echo 🔍 Descobrindo IP da máquina...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"Endereço IPv4"') do (
    set "ip=%%a"
    set "ip=!ip: =!"
    goto :found_ip
)
:found_ip

echo ✅ IP da máquina: %ip%

echo.
echo 🚀 Iniciando Backend (Flask)...
start "Backend - Flask" cmd /k "cd backend && python main.py"

echo ⏳ Aguardando backend inicializar...
timeout /t 3 /nobreak >nul

echo.
echo 🚀 Iniciando Frontend (Vite)...
start "Frontend - Vite" cmd /k "cd frontend && npm run dev"

echo.
echo ✅ Aplicação iniciada com sucesso!
echo.
echo 🌐 URLs de Acesso:
echo    Local:    http://localhost:5173
echo    Rede:     http://%ip%:5173
echo.
echo 📱 Para compartilhar com colegas:
echo    Colegas acessam: http://%ip%:5173
echo.
echo ⚠️  IMPORTANTE:
echo    - Certifique-se de que o firewall permite conexões na porta 5173
echo    - Todos os dispositivos devem estar na mesma rede local
echo    - Para parar os serviços, feche as janelas do terminal
echo.
echo Pressione qualquer tecla para continuar...
pause >nul
