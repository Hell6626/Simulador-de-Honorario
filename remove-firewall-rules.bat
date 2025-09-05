@echo off
echo 🛡️ Removendo Regras de Firewall do Simulador de Honorários
echo ========================================================

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
echo 🗑️ Removendo regras do firewall...

REM Remover regra do Frontend
netsh advfirewall firewall show rule name="Simulador Honorários - Frontend (5173)" >nul 2>&1
if %errorlevel% equ 0 (
    echo 📝 Removendo regra do Frontend (porta 5173)...
    netsh advfirewall firewall delete rule name="Simulador Honorários - Frontend (5173)"
    if %errorlevel% equ 0 (
        echo ✅ Regra do Frontend removida com sucesso
    ) else (
        echo ❌ Erro ao remover regra do Frontend
    )
) else (
    echo ℹ️ Regra do Frontend não encontrada
)

REM Remover regra do Backend
netsh advfirewall firewall show rule name="Simulador Honorários - Backend (5000)" >nul 2>&1
if %errorlevel% equ 0 (
    echo 📝 Removendo regra do Backend (porta 5000)...
    netsh advfirewall firewall delete rule name="Simulador Honorários - Backend (5000)"
    if %errorlevel% equ 0 (
        echo ✅ Regra do Backend removida com sucesso
    ) else (
        echo ❌ Erro ao remover regra do Backend
    )
) else (
    echo ℹ️ Regra do Backend não encontrada
)

echo.
echo ✅ Remoção das regras concluída!
echo.
echo ⚠️  IMPORTANTE:
echo    - As regras de firewall foram removidas
echo    - A aplicação não será mais acessível pela rede local
echo    - Para reativar, execute: configure-firewall.bat
echo.
echo Pressione qualquer tecla para continuar...
pause >nul
