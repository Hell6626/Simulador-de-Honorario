# 🏢 OfficePro - Sistema de Gestão Empresarial

Sistema completo de gestão empresarial para escritórios modernos, desenvolvido com React + TypeScript no frontend e Flask + SQLAlchemy no backend.

## ✨ Características

- **Interface Moderna**: Design limpo e profissional inspirado em sistemas empresariais
- **Autenticação Segura**: Sistema de login com JWT
- **Gestão de Clientes**: Cadastro e gerenciamento completo de clientes
- **Propostas Comerciais**: Criação e gestão de propostas
- **Serviços**: Catálogo de serviços disponíveis
- **Responsivo**: Funciona em desktop e dispositivos móveis

## 🚀 Como Executar

### Pré-requisitos

- Node.js 18+ 
- Python 3.8+
- npm ou yarn

### Backend

1. **Navegue para a pasta do backend:**
   ```bash
   cd backend
   ```

2. **Ative o ambiente virtual:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Inicialize o banco de dados:**
   ```bash
   python config.py
   ```

5. **Inicie o servidor:**
   ```bash
   python config.py
   ```

O backend estará disponível em: `http://localhost:5000`

### Frontend

1. **Navegue para a pasta do frontend:**
   ```bash
   cd frontend
   ```

2. **Instale as dependências:**
   ```bash
   npm install
   ```

3. **Inicie o servidor de desenvolvimento:**
   ```bash
   npm run dev
   ```

O frontend estará disponível em: `http://localhost:5173` ou `http://192.168.2.109:5173`

## 🌐 Acesso em Rede Local

Para disponibilizar o sistema para acesso em rede local:

### Inicialização Rápida
```bash
# Windows - Execute o script automático:
start-network.bat

# Ou inicialização manual:
# Terminal 1 - Backend:
cd backend && python main.py

# Terminal 2 - Frontend:
cd frontend && npm run dev
```

### URLs de Acesso
- **Local:** `http://localhost:5173`
- **Rede:** `http://[SEU-IP]:5173` (substitua pelo seu IP local)

### Configuração de Firewall
```bash
# Windows - Configure automaticamente:
configure-firewall.bat
```

**Importante:** Esta configuração é apenas para desenvolvimento e rede local. Para produção, use HTTPS e configurações de segurança adequadas.

## 🔐 Credenciais de Acesso

**Usuário Administrador:**
- **Email:** admin@admin.com
- **Senha:** admin123

## 🎨 Nova Tela de Login

A tela de login foi completamente redesenhada para ficar idêntica à imagem de referência:

### Características do Design:
- **Layout Dividido**: Formulário à esquerda (60%) e imagem de fundo à direita (40%)
- **Logo Profissional**: "OfficePro #" com identidade visual moderna
- **Campos de Entrada**: Design minimalista com bordas inferiores
- **Ícones**: Ícones de usuário e olho para mostrar/ocultar senha
- **Imagem de Fundo**: Cena de escritório moderno com laptop, fones, lentes de câmera e outros elementos
- **Responsivo**: Adapta-se perfeitamente a diferentes tamanhos de tela

### Elementos Visuais:
- **Laptop**: Representa o trabalho digital
- **Headphones**: Comunicação e reuniões
- **Camera Lenses**: Profissionalismo e qualidade
- **Mouse**: Interface e controle
- **Mug**: Ambiente de trabalho acolhedor
- **Plant**: Toque de natureza e bem-estar
- **Documents**: Organização e documentação

## 🛠️ Tecnologias Utilizadas

### Frontend
- **React 18** com TypeScript
- **Vite** para build e desenvolvimento
- **Tailwind CSS** para estilização
- **Lucide React** para ícones
- **React Router** para navegação
- **Sonner** para notificações

### Backend
- **Flask** framework web
- **SQLAlchemy** ORM
- **Flask-JWT-Extended** para autenticação
- **Flask-CORS** para CORS
- **Flask-Migrate** para migrações
- **SQLite** banco de dados (desenvolvimento)

## 📁 Estrutura do Projeto

```
├── backend/
│   ├── config.py              # Configuração principal
│   ├── models/                # Modelos do banco de dados
│   ├── views/                 # Endpoints da API
│   └── migrations/            # Migrações do banco
├── frontend/
│   ├── src/
│   │   ├── pages/             # Páginas principais
│   │   ├── components/        # Componentes reutilizáveis
│   │   ├── features/          # Funcionalidades organizadas
│   │   └── shared/            # Código compartilhado
│   └── public/                # Arquivos estáticos
└── README.md
```

## 🔧 Configuração de Desenvolvimento

### Variáveis de Ambiente

Crie um arquivo `.env` na pasta `frontend`:

```env
VITE_API_URL=http://localhost:5000/api
```

### Banco de Dados

O sistema usa SQLite por padrão. Para produção, configure uma variável de ambiente:

```env
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## 📱 Funcionalidades Principais

1. **Autenticação**
   - Login seguro com JWT
   - Logout automático
   - Proteção de rotas

2. **Gestão de Clientes**
   - Cadastro completo
   - Busca e filtros
   - Histórico de propostas

3. **Propostas Comerciais**
   - Criação passo a passo
   - Cálculo automático
   - Aprovação e gestão

4. **Serviços**
   - Catálogo de serviços
   - Preços e descrições
   - Categorização

5. **Sistema de Mensalidade Automática**
   - Cálculo automático baseado na configuração tributária
   - Suporte a diferentes regimes (Simples Nacional, Lucro Presumido, Lucro Real)
   - Valores diferenciados por faixa de faturamento
   - Integração automática no Passo 4 da criação de propostas

6. **Gerador de PDF**
   - Geração automática de propostas em PDF
   - Layout profissional e responsivo
   - Logo da empresa integrada
   - Fallback inteligente para dados temporários

7. **Sistema de Chat**
   - Chat integrado com IA
   - Histórico de conversas
   - Respostas inteligentes baseadas em palavras-chave
   - Autenticação JWT obrigatória

8. **Gestão de Cargos (Administradores)**
   - Cadastro e gerenciamento de cargos
   - Código automático gerado
   - Vinculação automática à empresa
   - Controle de acesso por permissão de administrador

## 🎯 Próximos Passos

- [ ] Implementar dashboard com métricas
- [ ] Adicionar relatórios e exportação
- [ ] Sistema de notificações
- [ ] Integração com sistemas externos
- [ ] Testes automatizados

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

**Desenvolvido com ❤️ para escritórios modernos**
