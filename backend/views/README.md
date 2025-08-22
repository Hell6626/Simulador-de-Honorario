# Estrutura de Views Organizadas

Este diretório contém as views da API organizadas por domínio de negócio para facilitar a manutenção e desenvolvimento.

## Estrutura de Arquivos

```
views/
├── __init__.py              # Arquivo principal que organiza todos os blueprints
├── utils.py                 # Utilitários e decoradores compartilhados
├── funcionarios.py          # Views relacionadas aos funcionários
├── clientes.py             # Views relacionadas aos clientes
├── tipos_atividade.py      # Views relacionadas aos tipos de atividade
├── regimes_tributarios.py  # Views relacionadas aos regimes tributários
├── faixas_faturamento.py   # Views relacionadas às faixas de faturamento
├── propostas.py            # Views relacionadas às propostas
├── auth.py                 # Views relacionadas à autenticação
├── health.py               # Views relacionadas ao health check
├── error_handlers.py       # Error handlers da API
└── README.md               # Esta documentação
```

## Organização por Domínio

### 1. **funcionarios.py**
- `GET /api/funcionarios/` - Listar funcionários
- `GET /api/funcionarios/<id>` - Obter funcionário específico
- `POST /api/funcionarios/` - Criar funcionário
- `PUT /api/funcionarios/<id>` - Atualizar funcionário
- `DELETE /api/funcionarios/<id>` - Remover funcionário

### 2. **clientes.py**
- `GET /api/clientes/` - Listar clientes
- `GET /api/clientes/<id>` - Obter cliente específico
- `POST /api/clientes/` - Criar cliente
- `PUT /api/clientes/<id>` - Atualizar cliente
- `DELETE /api/clientes/<id>` - Remover cliente

### 3. **tipos_atividade.py**
- `GET /api/tipos-atividade/` - Listar tipos de atividade
- `GET /api/tipos-atividade/<id>` - Obter tipo de atividade específico
- `POST /api/tipos-atividade/` - Criar tipo de atividade
- `PUT /api/tipos-atividade/<id>` - Atualizar tipo de atividade
- `DELETE /api/tipos-atividade/<id>` - Remover tipo de atividade

### 4. **regimes_tributarios.py**
- `GET /api/regimes-tributarios/` - Listar regimes tributários
- `GET /api/regimes-tributarios/<id>` - Obter regime tributário específico
- `POST /api/regimes-tributarios/` - Criar regime tributário

### 5. **faixas_faturamento.py**
- `GET /api/faixas-faturamento/` - Listar faixas de faturamento
- `GET /api/faixas-faturamento/<id>` - Obter faixa de faturamento específica

### 6. **propostas.py**
- `GET /api/propostas/` - Listar propostas
- `GET /api/propostas/<id>` - Obter proposta específica
- `POST /api/propostas/` - Criar proposta
- `POST /api/propostas/<id>/calcular-servicos` - Calcular serviços automáticos

### 7. **auth.py**
- `POST /api/auth/login` - Login de funcionário
- `POST /api/auth/logout` - Logout de funcionário (invalida token JWT)

### 8. **health.py**
- `GET /api/health/health` - Health check da API
- `GET /api/health/info` - Informações da API
- `GET /api/health/ping` - Ping simples

## Utilitários Compartilhados

### **utils.py**
Contém funções e decoradores utilizados por todas as views:

- `@handle_api_errors` - Decorator para tratamento padronizado de erros
- `validate_required_fields()` - Validação de campos obrigatórios
- `paginate_query()` - Paginação padronizada para queries
- `build_search_filters()` - Construção de filtros de busca dinâmicos

## Como Adicionar Novas Views

1. **Crie um novo arquivo** para o domínio (ex: `servicos.py`)
2. **Importe as dependências** necessárias:
   ```python
   from flask import Blueprint, request, jsonify
   from models import Servico
   from .utils import handle_api_errors, validate_required_fields
   ```
3. **Crie o blueprint**:
   ```python
   servicos_bp = Blueprint('servicos', __name__)
   ```
4. **Defina as rotas** com o decorator `@handle_api_errors`
5. **Registre o blueprint** no `__init__.py`:
   ```python
   from .servicos import servicos_bp
   api_bp.register_blueprint(servicos_bp, url_prefix='/servicos')
   ```

## Vantagens da Organização

1. **Manutenibilidade**: Cada domínio tem seu próprio arquivo
2. **Escalabilidade**: Fácil adicionar novos endpoints
3. **Reutilização**: Utilitários compartilhados
4. **Clareza**: Estrutura clara e organizada
5. **Testabilidade**: Cada módulo pode ser testado independentemente

## Convenções

- Use o decorator `@handle_api_errors` em todas as views
- Valide campos obrigatórios com `validate_required_fields()`
- Use paginação para listagens com `paginate_query()`
- Mantenha logs informativos com `current_app.logger.info()`
- Retorne JSON padronizado com `jsonify()`
