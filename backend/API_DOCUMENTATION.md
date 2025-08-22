# Documentação da API - Sistema de Propostas Contábeis

## Visão Geral

API REST para gerenciamento de propostas comerciais contábeis.

**URL Base:** `http://localhost:5000/api`

## Tecnologias Utilizadas

### Linguagem de Programação
- **Python 3.12+** - Linguagem principal do backend

### Framework Web
- **Flask 3.1.1** - Framework web para criação da API REST

### Banco de Dados
- **SQLite** - Banco de dados principal (padrão: `propostas.db`)
- **SQLAlchemy 2.0.41** - ORM para manipulação do banco
- **Alembic 1.16.4** - Ferramenta de migração de banco de dados

### Autenticação
- **Flask-JWT-Extended 4.7.1** - Autenticação via JWT (JSON Web Tokens)

### Principais Dependências
- **Flask-CORS 6.0.1** - Suporte a CORS para requisições cross-origin
- **Flask-Migrate 4.1.0** - Integração do Alembic com Flask
- **Flask-SQLAlchemy 3.1.1** - Integração do SQLAlchemy com Flask
- **PyJWT 2.10.1** - Manipulação de tokens JWT
- **Werkzeug 3.1.3** - Utilitários WSGI
- **Jinja2 3.1.6** - Template engine
- **cryptography 45.0.6** - Criptografia para senhas

## Arquitetura do Projeto

### Estrutura de Diretórios

```
backend/
├── 📁 models/                    # Modelos de dados (SQLAlchemy)
│   ├── __init__.py              # Exportação dos modelos
│   ├── base.py                  # Modelo base com campos comuns
│   ├── clientes.py              # Modelo de clientes
│   ├── organizacional.py        # Modelos organizacionais (funcionários, cargos)
│   ├── tributario.py            # Modelos tributários (regimes, atividades)
│   ├── servicos.py              # Modelo de serviços
│   ├── propostas.py             # Modelo de propostas
│   ├── services.py              # Serviços de negócio
│   ├── events.py                # Eventos do sistema
│   ├── initialization.py        # Inicialização de dados básicos
│   ├── README.md                # Documentação dos modelos
│   └── FAIXAS_FATURAMENTO.md    # Documentação de faixas
│
├── 📁 views/                     # Controladores da API (Blueprints)
│   ├── __init__.py              # Registro de blueprints
│   ├── auth.py                  # Autenticação (login/logout)
│   ├── funcionarios.py          # CRUD de funcionários
│   ├── clientes.py              # CRUD de clientes
│   ├── tipos_atividade.py       # CRUD de tipos de atividade
│   ├── regimes_tributarios.py   # CRUD de regimes tributários
│   ├── faixas_faturamento.py    # Listagem de faixas
│   ├── servicos.py              # CRUD de serviços
│   ├── propostas.py             # CRUD de propostas
│   ├── health.py                # Health check da API
│   ├── error_handlers.py        # Tratamento de erros
│   ├── utils.py                 # Utilitários compartilhados
│   └── README.md                # Documentação das views
│
├── 📁 migrations/                # Migrações do banco (Alembic)
│   ├── alembic.ini              # Configuração do Alembic
│   ├── env.py                   # Ambiente de migração
│   ├── script.py.mako           # Template de migração
│   └── 📁 versions/             # Arquivos de migração
│       ├── 20241220_000_create_initial_tables.py
│       ├── 20241220_001_insert_faixas_faturamento.py
│       └── d40f383ff0d1_add_abertura_empresa_to_clientes.py
│
├── 📁 instance/                  # Dados da aplicação
│   ├── propostas.db             # Banco SQLite principal
│   └── propostas_backup_*.db    # Backups automáticos
│
├── 📁 venv/                      # Ambiente virtual Python
├── 📁 __pycache__/              # Cache Python
│
├── main.py                       # Ponto de entrada da aplicação
├── config.py                     # Configuração da aplicação
├── requirements.txt              # Dependências Python
├── inicializar_sistema.py        # Script de inicialização
├── recriar_banco.py             # Script de recriação do banco
└── API_DOCUMENTATION.md          # Esta documentação
```

### Padrões Arquiteturais

#### **MVC (Model-View-Controller)**
- **Models** (`models/`): Entidades de negócio e lógica de dados
- **Views** (`views/`): Controladores da API (endpoints)
- **Controller**: Lógica de negócio distribuída entre models e views

#### **Blueprint Pattern**
- Organização modular por domínio de negócio
- Cada módulo tem seu próprio blueprint (ex: `clientes_bp`, `propostas_bp`)
- Registro centralizado em `views/__init__.py`

#### **Repository Pattern**
- Models encapsulam acesso aos dados
- Separação entre lógica de negócio e persistência
- Uso do SQLAlchemy como ORM

#### **Service Layer**
- `models/services.py`: Serviços de negócio complexos
- `models/events.py`: Sistema de eventos
- Separação de responsabilidades

### Fluxo de Requisição

```
1. Cliente → HTTP Request
2. Flask Router → Blueprint específico
3. View (Controller) → Validação e autorização
4. Service Layer → Lógica de negócio
5. Model → Acesso aos dados (SQLAlchemy)
6. SQLite Database → Persistência
7. Response → JSON para o cliente
```

### Configuração e Inicialização

- **`config.py`**: Factory pattern para criação da aplicação
- **`main.py`**: Ponto de entrada e inicialização do banco
- **`inicializar_sistema.py`**: Script para setup inicial
- **Migrations**: Controle de versão do banco via Alembic

## Autenticação

A API utiliza JWT (JSON Web Tokens) para autenticação. Inclua o token no header `Authorization: Bearer <token>`.

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "usuario@exemplo.com",
  "senha": "senha123"
}
```

**Resposta:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Logout
```http
POST /api/auth/logout
Authorization: Bearer <token>
```

## Endpoints

### 1. Health Check

#### Verificar Status da API
```http
GET /api/health/health
```

**Resposta:**
```json
{
  "status": "OK",
  "message": "API funcionando corretamente!",
  "timestamp": "2024-01-01T12:00:00",
  "database": "OK"
}
```

#### Informações da API
```http
GET /api/health/info
```

#### Ping
```http
GET /api/health/ping
```

### 2. Funcionários

#### Listar Funcionários
```http
GET /api/funcionarios?page=1&per_page=20&ativo=true&search=nome
Authorization: Bearer <token>
```

**Parâmetros:**
- `page` (int): Página atual (padrão: 1)
- `per_page` (int): Itens por página (padrão: 20)
- `ativo` (bool): Filtrar por status ativo
- `search` (string): Buscar por nome ou email

#### Buscar Funcionário
```http
GET /api/funcionarios/{id}
Authorization: Bearer <token>
```

#### Criar Funcionário
```http
POST /api/funcionarios
Authorization: Bearer <token>
Content-Type: application/json

{
  "nome": "João Silva",
  "email": "joao@exemplo.com",
  "senha": "senha123",
  "cargo_id": 1,
  "empresa_id": 1,
  "gerente": false,
  "ativo": true
}
```

#### Atualizar Funcionário
```http
PUT /api/funcionarios/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "nome": "João Silva Atualizado",
  "email": "joao.novo@exemplo.com",
  "gerente": true
}
```

#### Deletar Funcionário
```http
DELETE /api/funcionarios/{id}
Authorization: Bearer <token>
```

### 3. Clientes

#### Listar Clientes
```http
GET /api/clientes?page=1&per_page=20&ativo=true&search=nome
Authorization: Bearer <token>
```

**Parâmetros:**
- `page` (int): Página atual (padrão: 1)
- `per_page` (int): Itens por página (padrão: 20)
- `ativo` (bool): Filtrar por status ativo
- `search` (string): Buscar por nome, CPF ou email

#### Buscar Cliente
```http
GET /api/clientes/{id}
Authorization: Bearer <token>
```

#### Criar Cliente
```http
POST /api/clientes
Authorization: Bearer <token>
Content-Type: application/json

{
  "nome": "Empresa ABC Ltda",
  "cpf": "12345678901",
  "email": "contato@empresa.com",
  "abertura_empresa": false,
  "ativo": true
}
```

#### Atualizar Cliente
```http
PUT /api/clientes/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "nome": "Empresa ABC Ltda - Atualizada",
  "email": "novo@empresa.com",
  "abertura_empresa": true
}
```

#### Deletar Cliente
```http
DELETE /api/clientes/{id}
Authorization: Bearer <token>
```

### 4. Tipos de Atividade

#### Listar Tipos de Atividade
```http
GET /api/tipos-atividade?ativo=true&aplicavel_pf=true&aplicavel_pj=true&search=nome
```

**Parâmetros:**
- `ativo` (bool): Filtrar por status ativo
- `aplicavel_pf` (bool): Filtrar por aplicável a pessoa física
- `aplicavel_pj` (bool): Filtrar por aplicável a pessoa jurídica
- `search` (string): Buscar por nome, código ou descrição

#### Buscar Tipo de Atividade
```http
GET /api/tipos-atividade/{id}
```

#### Criar Tipo de Atividade
```http
POST /api/tipos-atividade
Content-Type: application/json

{
  "nome": "Comércio",
  "codigo": "COM",
  "descricao": "Atividade comercial",
  "aplicavel_pf": false,
  "aplicavel_pj": true,
  "ativo": true
}
```

#### Atualizar Tipo de Atividade
```http
PUT /api/tipos-atividade/{id}
Content-Type: application/json

{
  "nome": "Comércio Atualizado",
  "descricao": "Nova descrição"
}
```

#### Deletar Tipo de Atividade
```http
DELETE /api/tipos-atividade/{id}
```

### 5. Regimes Tributários

#### Listar Regimes Tributários
```http
GET /api/regimes-tributarios?ativo=true&aplicavel_pf=true&aplicavel_pj=true&atividades_ids=1,2&search=nome
```

**Parâmetros:**
- `ativo` (bool): Filtrar por status ativo
- `aplicavel_pf` (bool): Filtrar por aplicável a pessoa física
- `aplicavel_pj` (bool): Filtrar por aplicável a pessoa jurídica
- `atividades_ids` (array): Filtrar por IDs de atividades
- `search` (string): Buscar por nome, código ou descrição

#### Buscar Regime Tributário
```http
GET /api/regimes-tributarios/{id}
```

#### Criar Regime Tributário
```http
POST /api/regimes-tributarios
Content-Type: application/json

{
  "nome": "Simples Nacional",
  "codigo": "SN",
  "descricao": "Regime do Simples Nacional",
  "aplicavel_pf": false,
  "aplicavel_pj": true,
  "requer_definicoes_fiscais": true,
  "ativo": true
}
```

### 6. Faixas de Faturamento

#### Listar Faixas de Faturamento
```http
GET /api/faixas-faturamento?regime_tributario_id=1
```

**Parâmetros:**
- `regime_tributario_id` (int): Filtrar por regime tributário

#### Buscar Faixa de Faturamento
```http
GET /api/faixas-faturamento/{id}
```

### 7. Serviços

#### Listar Serviços
```http
GET /api/servicos?categoria=FISCAL
```

**Parâmetros:**
- `categoria` (string): Filtrar por categoria (ex: FISCAL)

#### Listar Serviços Fiscais
```http
GET /api/servicos/fiscais
```

#### Buscar Serviço
```http
GET /api/servicos/{id}
Authorization: Bearer <token>
```

### 8. Propostas

#### Listar Propostas
```http
GET /api/propostas?page=1&per_page=20&status=RASCUNHO&cliente_id=1&funcionario_id=1&search=numero
```

**Parâmetros:**
- `page` (int): Página atual (padrão: 1)
- `per_page` (int): Itens por página (padrão: 20)
- `status` (string): Filtrar por status
- `cliente_id` (int): Filtrar por cliente
- `funcionario_id` (int): Filtrar por funcionário responsável
- `search` (string): Buscar por número ou observações

#### Buscar Proposta
```http
GET /api/propostas/{id}
```

#### Criar Proposta
```http
POST /api/propostas
Authorization: Bearer <token>
Content-Type: application/json

{
  "cliente_id": 1,
  "tipo_atividade_id": 1,
  "regime_tributario_id": 1,
  "faixa_faturamento_id": 1,
  "valor_total": 5000.00,
  "data_validade": "2024-12-31T23:59:59",
  "status": "RASCUNHO",
  "observacoes": "Observações da proposta"
}
```

#### Calcular Serviços da Proposta
```http
POST /api/propostas/{id}/calcular-servicos
```

## Códigos de Status HTTP

- `200` - Sucesso
- `201` - Criado com sucesso
- `400` - Requisição inválida
- `401` - Não autorizado
- `404` - Não encontrado
- `500` - Erro interno do servidor

## Estrutura de Resposta de Erro

```json
{
  "error": "Descrição do erro",
  "message": "Mensagem detalhada"
}
```

## Estrutura de Resposta Paginada

```json
{
  "items": [...],
  "total": 100,
  "pages": 5,
  "current_page": 1,
  "per_page": 20
}
```

## Configuração

### Variáveis de Ambiente

- `SECRET_KEY`: Chave secreta da aplicação
- `DATABASE_URL`: URL do banco de dados (padrão: `sqlite:///propostas.db`)
- `JWT_SECRET_KEY`: Chave secreta para JWT

### Banco de Dados

O sistema utiliza **SQLite** como banco de dados padrão, localizado em `backend/instance/propostas.db`.

**Estrutura do Banco:**
- Tabelas principais: `funcionarios`, `clientes`, `tipos_atividade`, `regimes_tributarios`, `faixas_faturamento`, `servicos`, `propostas`, `item_proposta`, `proposta_log`
- Migrações gerenciadas pelo Alembic
- Backup automático em `backend/instance/propostas_backup_*.db`

### CORS

A API está configurada para aceitar requisições dos seguintes domínios:
- `http://localhost:5173`
- `http://127.0.0.1:5173`
- `http://192.168.0.99:5173`

## Instalação e Execução

### Pré-requisitos
- Python 3.12 ou superior
- pip (gerenciador de pacotes Python)

### Instalação
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### Execução
```bash
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
python main.py
```

A API estará disponível em `http://localhost:5000`

### Migrações de Banco
```bash
# Criar nova migração
flask db migrate -m "Descrição da migração"

# Aplicar migrações
flask db upgrade
```
