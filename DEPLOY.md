# 🚀 Guia de Deploy - Simulador de Honorários

## 📋 Arquivos Criados

Os seguintes arquivos foram criados para o deploy com Docker:

### Backend
- `backend/Dockerfile` - Container do Flask na porta 5002
- `frontend/Dockerfile` - Container do React com Nginx na porta 8083
- `frontend/nginx.conf` - Configuração do Nginx para o frontend

### Orquestração
- `docker-compose.yml` - Orquestração dos containers
- `.dockerignore` - Arquivos ignorados no build
- `env.example` - Exemplo de variáveis de ambiente

### Deploy
- `deploy.sh` - Script automatizado de deploy
- `nginx-propostas.conf` - Configuração do Nginx para o domínio
- `simulador-propostas.service` - Service do systemd para auto-start

## 🔧 Configuração do Servidor

### 1. Instalar Docker e Docker Compose

```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Configurar SSL

```bash
# Gerar certificado SSL para o domínio
sudo certbot --nginx -d propostas.christinocontabilidade.com.br -d www.propostas.christinocontabilidade.com.br
```

### 3. Configurar Nginx

```bash
# Adicionar a configuração ao nginx.conf
sudo nano /etc/nginx/sites-available/default

# Adicionar o conteúdo do arquivo nginx-propostas.conf ao final do arquivo

# Testar configuração
sudo nginx -t

# Recarregar nginx
sudo systemctl reload nginx
```

## 🚀 Deploy da Aplicação

### 1. Preparar o Ambiente

```bash
# Clonar o repositório
git clone <seu-repositorio>
cd Prj-Simulador-de-Honor-rios

# Configurar variáveis de ambiente
cp env.example .env
nano .env  # Editar com suas configurações
```

### 2. Executar Deploy

```bash
# Tornar script executável
chmod +x deploy.sh

# Executar deploy
./deploy.sh
```

### 3. Verificar Status

```bash
# Verificar containers
docker-compose ps

# Ver logs
docker-compose logs -f

# Testar endpoints
curl http://localhost:5002/health
curl http://localhost:8083/health
```

## 🔄 Configurar Auto-start

### 1. Configurar Service do Systemd

```bash
# Copiar o service file
sudo cp simulador-propostas.service /etc/systemd/system/

# Editar o caminho no service file
sudo nano /etc/systemd/system/simulador-propostas.service
# Alterar WorkingDirectory para o caminho correto do projeto

# Ativar o service
sudo systemctl enable simulador-propostas.service
sudo systemctl start simulador-propostas.service
```

### 2. Verificar Service

```bash
# Ver status do service
sudo systemctl status simulador-propostas.service

# Ver logs do service
sudo journalctl -u simulador-propostas.service -f
```

## 🌐 Acessos

Após o deploy, a aplicação estará disponível em:

- **Frontend**: https://propostas.christinocontabilidade.com.br
- **Backend API**: https://propostas.christinocontabilidade.com.br/api/
- **Portas locais**: 
  - Frontend: http://localhost:8083
  - Backend: http://localhost:5002

## 📝 Comandos Úteis

```bash
# Ver logs em tempo real
docker-compose logs -f

# Parar aplicação
docker-compose down

# Reiniciar aplicação
docker-compose restart

# Atualizar aplicação
git pull
./deploy.sh

# Ver status dos containers
docker-compose ps

# Acessar container do backend
docker exec -it simulador-backend bash

# Acessar container do frontend
docker exec -it simulador-frontend sh
```

## 🔧 Troubleshooting

### Container não inicia
```bash
# Ver logs detalhados
docker-compose logs backend
docker-compose logs frontend

# Verificar se as portas estão livres
sudo netstat -tlnp | grep :5002
sudo netstat -tlnp | grep :8083
```

### Problemas de SSL
```bash
# Renovar certificado
sudo certbot renew

# Testar configuração do nginx
sudo nginx -t
```

### Problemas de permissão
```bash
# Verificar permissões do Docker
sudo usermod -aG docker $USER
# Fazer logout e login novamente
```

## 📊 Monitoramento

### Health Checks
- Backend: http://localhost:5002/health
- Frontend: http://localhost:8083/health
- Domínio: https://propostas.christinocontabilidade.com.br/health

### Logs
- Docker: `docker-compose logs -f`
- Systemd: `sudo journalctl -u simulador-propostas.service -f`
- Nginx: `sudo tail -f /var/log/nginx/access.log`

## 🔄 Backup

### Banco de Dados
```bash
# Backup automático (adicionar ao crontab)
docker exec simulador-backend cp /app/instance/propostas.db /app/uploads/backup_$(date +%Y%m%d_%H%M%S).db
```

### Arquivos de Upload
```bash
# Backup dos uploads
tar -czf backup_uploads_$(date +%Y%m%d_%H%M%S).tar.gz backend/uploads/
```
