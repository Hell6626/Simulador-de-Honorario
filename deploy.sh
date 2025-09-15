#!/bin/bash

echo "🚀 Iniciando deploy do Simulador de Honorários..."

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Por favor, instale o Docker primeiro."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
    exit 1
fi

# Criar arquivo .env se não existir
if [ ! -f .env ]; then
    echo "📝 Criando arquivo .env a partir do env.example..."
    cp env.example .env
    echo "⚠️  IMPORTANTE: Edite o arquivo .env com suas configurações antes de continuar!"
    read -p "Pressione Enter para continuar após editar o .env..."
fi

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down

# Remover imagens antigas (opcional)
read -p "🗑️  Deseja remover imagens antigas? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose down --rmi all
fi

# Build e start dos containers
echo "🔨 Construindo e iniciando containers..."
docker-compose up --build -d

# Aguardar containers ficarem prontos
echo "⏳ Aguardando containers ficarem prontos..."
sleep 15

# Verificar status dos containers
echo "📊 Status dos containers:"
docker-compose ps

# Verificar logs
echo "📋 Logs dos serviços:"
docker-compose logs --tail=50

echo "✅ Deploy concluído!"
echo "🌐 Aplicação disponível em:"
echo "   - Frontend: http://localhost:8083"
echo "   - Backend API: http://localhost:5002"
echo "   - Domínio: https://propostas.christinocontabilidade.com.br"
echo ""
echo "📝 Para ver logs em tempo real: docker-compose logs -f"
echo "🛑 Para parar: docker-compose down"
