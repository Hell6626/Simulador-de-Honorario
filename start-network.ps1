# 🌐 Script PowerShell para iniciar Simulador de Honorários na Rede Local
# =======================================================================

Write-Host "🌐 Iniciando Simulador de Honorários na Rede Local" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "📋 Verificando configurações..." -ForegroundColor Yellow

# Verificar se Python está instalado
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado! Instale Python 3.8+ primeiro." -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Verificar se Node.js está instalado
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js encontrado: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js não encontrado! Instale Node.js 16+ primeiro." -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host ""
Write-Host "🔍 Descobrindo IP da máquina..." -ForegroundColor Yellow

# Descobrir IP da máquina
$networkAdapters = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*" }
$ip = $networkAdapters[0].IPAddress

if (-not $ip) {
    Write-Host "❌ Não foi possível descobrir o IP da rede local" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host "✅ IP da máquina: $ip" -ForegroundColor Green

Write-Host ""
Write-Host "🚀 Iniciando Backend (Flask)..." -ForegroundColor Yellow

# Iniciar Backend
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Set-Location backend
    python main.py
}

Write-Host "⏳ Aguardando backend inicializar..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "🚀 Iniciando Frontend (Vite)..." -ForegroundColor Yellow

# Iniciar Frontend
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Set-Location frontend
    npm run dev
}

Write-Host ""
Write-Host "✅ Aplicação iniciada com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 URLs de Acesso:" -ForegroundColor Cyan
Write-Host "   Local:    http://localhost:5173" -ForegroundColor White
Write-Host "   Rede:     http://$ip:5173" -ForegroundColor White
Write-Host ""
Write-Host "📱 Para compartilhar com colegas:" -ForegroundColor Cyan
Write-Host "   Colegas acessam: http://$ip:5173" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  IMPORTANTE:" -ForegroundColor Yellow
Write-Host "   - Certifique-se de que o firewall permite conexões na porta 5173" -ForegroundColor White
Write-Host "   - Todos os dispositivos devem estar na mesma rede local" -ForegroundColor White
Write-Host "   - Para parar os serviços, pressione Ctrl+C" -ForegroundColor White
Write-Host ""

# Aguardar entrada do usuário para parar
Write-Host "Pressione Ctrl+C para parar os serviços..." -ForegroundColor Yellow
try {
    while ($true) {
        Start-Sleep -Seconds 1
        
        # Verificar se os jobs ainda estão rodando
        if ($backendJob.State -eq "Failed") {
            Write-Host "❌ Backend falhou!" -ForegroundColor Red
            break
        }
        
        if ($frontendJob.State -eq "Failed") {
            Write-Host "❌ Frontend falhou!" -ForegroundColor Red
            break
        }
    }
} catch {
    Write-Host ""
    Write-Host "🛑 Parando serviços..." -ForegroundColor Yellow
    
    # Parar jobs
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Stop-Job $frontendJob -ErrorAction SilentlyContinue
    
    # Remover jobs
    Remove-Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job $frontendJob -ErrorAction SilentlyContinue
    
    Write-Host "✅ Serviços parados com sucesso!" -ForegroundColor Green
}
