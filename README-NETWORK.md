# 🌐 Simulador de Honorários - Acesso em Rede Local

Este guia explica como disponibilizar o Simulador de Honorários para acesso em rede local, permitindo que múltiplos usuários acessem simultaneamente.

## 📋 Pré-requisitos

- ✅ Python 3.8+ instalado
- ✅ Node.js 16+ instalado
- ✅ Todos os dispositivos na mesma rede local
- ✅ Firewall configurado para permitir conexões na porta 5173

## 🚀 Inicialização Rápida

### Opção 1: Script Automático (Recomendado)

**Windows (CMD):**
```bash
# Duplo clique no arquivo ou execute no terminal:
start-network.bat
```

**Windows (PowerShell):**
```powershell
# Execute no PowerShell:
.\start-network.ps1
```

### Opção 2: Inicialização Manual

**1. Iniciar Backend:**
```bash
cd backend
python main.py
```

**2. Iniciar Frontend (em outro terminal):**
```bash
cd frontend
npm run dev
```

## 🌐 URLs de Acesso

Após a inicialização, a aplicação estará disponível em:

- **Local:** `http://localhost:5173`
- **Rede:** `http://192.168.0.97:5173` (substitua pelo seu IP)

## 📱 Compartilhamento com Colegas

### Para Compartilhar:
1. Descubra seu IP local executando `ipconfig` (Windows) ou `ifconfig` (Linux/Mac)
2. Compartilhe a URL: `http://[SEU-IP]:5173`
3. Colegas acessam diretamente no navegador

### Exemplo:
- Seu IP: `192.168.0.97`
- URL para colegas: `http://192.168.0.97:5173`

## ⚙️ Configurações Implementadas

### Frontend (Vite)
- ✅ Host configurado para `0.0.0.0` (aceita conexões de qualquer IP)
- ✅ Porta 5173 configurada
- ✅ CORS habilitado para desenvolvimento

### Backend (Flask)
- ✅ Host configurado para `0.0.0.0` (aceita conexões de qualquer IP)
- ✅ Porta 5000 configurada
- ✅ CORS configurado para redes locais (192.168.x.x, 10.x.x.x)

### API (Frontend)
- ✅ Detecção automática de IP da rede
- ✅ Configuração dinâmica de URL base
- ✅ Fallback para localhost quando necessário

## 🛡️ Configuração de Firewall

### Windows (Firewall do Windows)

**Opção 1: Script Automático**
```bash
# Execute como administrador:
configure-firewall.bat
```

**Opção 2: Manual**
1. Abra "Firewall do Windows Defender"
2. Clique em "Configurações avançadas"
3. Clique em "Regras de entrada" → "Nova regra"
4. Selecione "Porta" → "Próximo"
5. Selecione "TCP" → "Portas específicas" → "5173" → "Próximo"
6. Selecione "Permitir a conexão" → "Próximo"
7. Marque todos os perfis → "Próximo"
8. Nome: "Simulador Honorários - Porta 5173" → "Concluir"

### Linux (UFW)
```bash
sudo ufw allow 5173
sudo ufw reload
```

### macOS (pfctl)
```bash
sudo pfctl -f /etc/pf.conf
```

## 🔧 Solução de Problemas

### ❌ "Não é possível conectar"

**Possíveis causas:**
1. **Firewall bloqueando:** Configure o firewall para permitir porta 5173
2. **IP incorreto:** Verifique o IP com `ipconfig` (Windows) ou `ifconfig` (Linux/Mac)
3. **Rede diferente:** Certifique-se de que todos estão na mesma rede local
4. **Serviços não iniciados:** Verifique se backend e frontend estão rodando

**Soluções:**
```bash
# Verificar IP atual
ipconfig | findstr "Endereço IPv4"

# Verificar se serviços estão rodando
netstat -an | findstr :5173
netstat -an | findstr :5000
```

### ❌ "CORS Error"

**Causa:** Backend não está permitindo requisições do frontend

**Solução:** Verifique se o backend está rodando com as configurações CORS atualizadas

### ❌ "Backend não responde"

**Possíveis causas:**
1. Backend não iniciado
2. Porta 5000 ocupada
3. Erro na configuração

**Soluções:**
```bash
# Verificar se porta está ocupada
netstat -an | findstr :5000

# Reiniciar backend
cd backend
python main.py
```

## 📊 Monitoramento

### Verificar Status dos Serviços

**Backend (Porta 5000):**
```bash
curl http://localhost:5000/api/health/health
```

**Frontend (Porta 5173):**
```bash
curl http://localhost:5173
```

### Logs de Acesso

Os logs de acesso aparecem nos terminais onde os serviços estão rodando:
- **Backend:** Logs de requisições HTTP
- **Frontend:** Logs de desenvolvimento do Vite

## 🔒 Segurança

### ⚠️ Importante para Produção

Esta configuração é **apenas para desenvolvimento e rede local**. Para produção:

1. **Nunca** exponha na internet pública
2. Use HTTPS com certificados válidos
3. Configure autenticação adequada
4. Implemente rate limiting
5. Use proxy reverso (Nginx/Apache)

### Configurações de Segurança Atuais

- ✅ Apenas rede local (192.168.x.x, 10.x.x.x)
- ✅ CORS restrito a IPs locais
- ✅ Sem exposição pública
- ✅ Configuração temporária

## 📞 Suporte

### Comandos Úteis

```bash
# Descobrir IP da máquina
ipconfig | findstr "Endereço IPv4"

# Verificar portas em uso
netstat -an | findstr :5173
netstat -an | findstr :5000

# Testar conectividade
ping 192.168.0.97
telnet 192.168.0.97 5173
```

### Logs de Debug

Para debug avançado, execute com logs detalhados:

```bash
# Backend com debug
cd backend
python main.py --debug

# Frontend com debug
cd frontend
npm run dev -- --debug
```

## 🎯 Resumo de URLs

| Serviço | Local | Rede |
|---------|-------|------|
| Frontend | http://localhost:5173 | http://192.168.0.97:5173 |
| Backend | http://localhost:5000 | http://192.168.0.97:5000 |
| API | http://localhost:5000/api | http://192.168.0.97:5000/api |

---

**✅ Configuração completa!** Sua aplicação agora está disponível para toda a equipe na rede local.

Para parar os serviços, feche as janelas do terminal ou pressione `Ctrl+C`.
