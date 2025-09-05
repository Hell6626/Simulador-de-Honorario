@echo off
echo 🛡️ Configurando Firewall para Simulador de Honorários
echo ===================================================

REM Verificar se está rodando como administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Este script precisa ser executado como Administrador!
    echo.
    echo Para executar como administrador:
    echo 1. Clique com botão direito no arquivo
    echo 2. Selecione "Executar como administrador"
    echo.
    pause
    exit /b 1
)

echo ✅ Executando como administrador

echo.
echo 🔍 Verificando configurações atuais do firewall...

REM Verificar se as regras já existem
netsh advfirewall firewall show rule name="Simulador Honorários - Frontend (5173)" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Regra do Frontend já existe
) else (
    echo 📝 Criando regra para Frontend (porta 5173)...
    netsh advfirewall firewall add rule name="Simulador Honorários - Frontend (5173)" dir=in action=allow protocol=TCP localport=5173
    if %errorlevel% equ 0 (
        echo ✅ Regra do Frontend criada com sucesso
    ) else (
        echo ❌ Erro ao criar regra do Frontend
    )
)

netsh advfirewall firewall show rule name="Simulador Honorários - Backend (5000)" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Regra do Backend já existe
) else (
    echo 📝 Criando regra para Backend (porta 5000)...
    netsh advfirewall firewall add rule name="Simulador Honorários - Backend (5000)" dir=in action=allow protocol=TCP localport=5000
    if %errorlevel% equ 0 (
        echo ✅ Regra do Backend criada com sucesso
    ) else (
        echo ❌ Erro ao criar regra do Backend
    )
)

echo.
echo 🔍 Verificando regras criadas...

echo.
echo 📋 Regras do Frontend:
netsh advfirewall firewall show rule name="Simulador Honorários - Frontend (5173)"

echo.
echo 📋 Regras do Backend:
netsh advfirewall firewall show rule name="Simulador Honorários - Backend (5000)"

echo.
echo ✅ Configuração do firewall concluída!
echo.
echo 🌐 Sua aplicação agora pode ser acessada pela rede local:
echo    Frontend: http://[SEU-IP]:5173
echo    Backend:  http://[SEU-IP]:5000
echo.
echo ⚠️  IMPORTANTE:
echo    - Estas regras permitem acesso apenas da rede local
echo    - Para remover as regras, execute: remove-firewall-rules.bat
echo    - Sempre mantenha o firewall ativado
echo.
echo Pressione qualquer tecla para continuar...
pause >nul
