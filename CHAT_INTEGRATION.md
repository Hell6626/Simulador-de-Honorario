# Integração do Chat com API Backend

## Visão Geral

O sistema de chat foi integrado com sucesso ao backend da aplicação de propostas. O chat agora funciona com autenticação JWT e mantém histórico de mensagens por sessão.

## Funcionalidades Implementadas

### Backend (Flask)

#### Endpoints Criados:
- `POST /api/chat/send-message` - Envia mensagem e recebe resposta do bot
- `GET /api/chat/messages` - Retorna histórico de mensagens
- `GET /api/chat/sessions` - Lista sessões de chat do usuário
- `POST /api/chat/clear-session` - Limpa uma sessão específica

#### Características:
- ✅ Autenticação JWT obrigatória
- ✅ Respostas inteligentes baseadas em palavras-chave
- ✅ Armazenamento em memória (simulado)
- ✅ Suporte a múltiplas sessões por usuário
- ✅ Timestamps ISO para todas as mensagens

### Frontend (React + TypeScript)

#### Componente ChatPage Atualizado:
- ✅ Integração com API backend
- ✅ Loading states durante envio de mensagens
- ✅ Scroll automático para última mensagem
- ✅ Botões para limpar chat e recarregar mensagens
- ✅ Tratamento de erros
- ✅ Interface responsiva e moderna

#### Serviço API Atualizado:
- ✅ Métodos para todas as operações de chat
- ✅ Headers de autenticação automáticos
- ✅ Tratamento de erros consistente

## Como Usar

### 1. Backend
```bash
cd backend
venv\Scripts\activate  # Ativar ambiente virtual
python main.py         # Executar servidor
```

### 2. Frontend
```bash
cd frontend
npm run dev           # Executar servidor de desenvolvimento
```

### 3. Acessar Chat
1. Faça login no sistema
2. Navegue para a página "Chat" no menu lateral
3. Comece a conversar com o bot!

## Palavras-chave Reconhecidas

O bot responde inteligentemente a:

- **Saudações**: "olá", "oi", "hello", "hi"
- **Propostas**: "proposta", "propostas"
- **Clientes**: "cliente", "clientes"
- **Serviços**: "serviço", "serviços"
- **Ajuda**: "ajuda", "help", "suporte"
- **Agradecimentos**: "obrigado", "valeu", "thanks"
- **Despedidas**: "tchau", "bye", "até"

## Estrutura de Dados

### Mensagem do Usuário
```json
{
  "id": "uuid",
  "user_id": "user_id_from_jwt",
  "message": "texto da mensagem",
  "sender": "user",
  "timestamp": "2025-08-21T20:49:37.611997",
  "session_id": "default"
}
```

### Resposta da API
```json
{
  "success": true,
  "user_message": {...},
  "bot_response": {...},
  "session_id": "default"
}
```

## Próximos Passos

Para melhorar ainda mais o sistema:

1. **Persistência**: Migrar de armazenamento em memória para banco de dados
2. **IA Avançada**: Integrar com APIs de IA como OpenAI ou Claude
3. **Contexto**: Manter contexto de conversas anteriores
4. **Arquivos**: Suporte a envio de imagens/documentos
5. **Notificações**: Sistema de notificações em tempo real
6. **Histórico**: Exportação de conversas

## Troubleshooting

### Erro de CORS
- Verificar se o backend está rodando na porta 5000
- Verificar se o frontend está configurado para acessar localhost:5000

### Erro de Autenticação
- Verificar se o token JWT está sendo enviado corretamente
- Verificar se o usuário está logado

### Erro de Conexão
- Verificar se ambos os servidores estão rodando
- Verificar se as portas estão corretas (5000 para backend, 5173 para frontend)

## Arquivos Modificados

### Backend
- `backend/views/chat.py` - Novo módulo de chat
- `backend/views/__init__.py` - Registro do blueprint de chat

### Frontend
- `frontend/src/services/api.ts` - Métodos de chat adicionados
- `frontend/src/components/pages/ChatPage.tsx` - Integração com API

## Status da Integração

✅ **COMPLETO** - O chat está totalmente integrado e funcional!
