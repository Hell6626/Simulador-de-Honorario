# Estrutura Modular dos Modelos

Este diretório contém os modelos do sistema organizados de forma modular por domínios de negócio.

## Estrutura de Arquivos

```
models/
├── __init__.py           # Arquivo principal que importa todos os modelos
├── base.py              # Mixins e classes base (TimestampMixin, ActiveMixin)
├── organizacional.py    # Modelos da estrutura organizacional
├── clientes.py         # Modelos relacionados aos clientes
├── tributario.py       # Modelos do sistema tributário
├── servicos.py         # Modelos de serviços
├── propostas.py        # Modelos de propostas comerciais
├── events.py           # Event listeners do SQLAlchemy
├── initialization.py   # Funções de inicialização de dados
└── README.md           # Esta documentação
```

## Organização por Domínios

### 1. **Base** (`base.py`)
- **TimestampMixin**: Adiciona campos de data de criação/atualização
- **ActiveMixin**: Adiciona funcionalidade de soft delete

### 2. **Organizacional** (`organizacional.py`)
- **Empresa**: Dados da empresa
- **Cargo**: Cargos disponíveis na empresa
- **Funcionario**: Funcionários da empresa

### 3. **Clientes** (`clientes.py`)
- **Cliente**: Dados dos clientes
- **Endereco**: Endereços dos clientes
- **EntidadeJuridica**: Empresas dos clientes

### 4. **Tributário** (`tributario.py`)
- **TipoAtividade**: Tipos de atividade econômica
- **RegimeTributario**: Regimes tributários disponíveis
- **AtividadeRegime**: Relacionamento entre atividades e regimes
- **FaixaFaturamento**: Faixas de faturamento por regime

### 5. **Serviços** (`servicos.py`)
- **Servico**: Catálogo de serviços oferecidos

### 6. **Propostas** (`propostas.py`)
- **Proposta**: Propostas comerciais
- **ItemProposta**: Itens das propostas
- **PropostaLog**: Log de alterações nas propostas

## Como Usar

### Importação Simples
```python
from models import Empresa, Cliente, Proposta
```

### Importação Específica
```python
from models.organizacional import Empresa, Funcionario
from models.clientes import Cliente, Endereco
from models.propostas import Proposta, ItemProposta
```

### Inicialização de Dados
```python
from models import inicializar_dados_basicos

# Inicializa dados básicos do sistema
inicializar_dados_basicos()
```

## Vantagens da Estrutura Modular

1. **Organização**: Código organizado por domínios de negócio
2. **Manutenibilidade**: Mais fácil de manter e modificar
3. **Legibilidade**: Código mais limpo e legível
4. **Reutilização**: Imports específicos quando necessário
5. **Escalabilidade**: Fácil adicionar novos domínios
6. **Separação de Responsabilidades**: Cada arquivo tem uma responsabilidade específica

## Event Listeners

Os event listeners estão em `events.py` e automatizam:
- Cálculo do valor total dos itens de proposta
- Atualização do valor total da proposta

## Inicialização

O arquivo `initialization.py` contém dados básicos para:
- Tipos de atividade
- Regimes tributários
- Serviços padrão

## Migração do Arquivo Único

Para migrar do arquivo `models.py` único para esta estrutura:

1. Substitua imports de `from models import ...` por `from models import ...`
2. Os imports continuam funcionando da mesma forma
3. A funcionalidade permanece idêntica
4. Apenas a organização interna mudou
