@echo off
echo 🚀 Iniciando deploy do Simulador de Honorários...

REM Verificar se Docker está instalado
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker não está instalado. Por favor, instale o Docker primeiro.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro.
    pause
    exit /b 1
)

REM Criar arquivo .env se não existir
if not exist .env (
    echo 📝 Criando arquivo .env a partir do env.example...
    copy env.example .env
    echo ⚠️  IMPORTANTE: Edite o arquivo .env com suas configurações antes de continuar!
    pause
)

REM Parar containers existentes
echo 🛑 Parando containers existentes...
docker-compose down

REM Build e start dos containers
echo 🔨 Construindo e iniciando containers...
docker-compose up --build -d

REM Aguardar containers ficarem prontos
echo ⏳ Aguardando containers ficarem prontos...
timeout /t 15 /nobreak >nul

REM Verificar status dos containers
echo 📊 Status dos containers:
docker-compose ps

REM Verificar logs
echo 📋 Logs dos serviços:
docker-compose logs --tail=50

echo ✅ Deploy concluído!
echo 🌐 Aplicação disponível em:
echo    - Frontend: http://localhost:8083
echo    - Backend API: http://localhost:5002
echo    - Domínio: https://propostas.christinocontabilidade.com.br
echo.
echo 📝 Para ver logs em tempo real: docker-compose logs -f
echo 🛑 Para parar: docker-compose down
pause
