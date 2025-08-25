# Funcionalidade de Cadastro de Cargos para Administradores

## Resumo da Implementação

Foi implementada a funcionalidade completa para permitir que **administradores** cadastrem e gerenciem **cargos** no sistema de propostas contábeis. Cada cargo é automaticamente vinculado à empresa do administrador e possui código gerado automaticamente.

## Funcionalidades Implementadas

### 🔐 Autenticação e Autorização
- **Verificação de permissão de administrador**: Apenas usuários com `gerente = true` podem acessar as funcionalidades
- **Proteção de rotas**: Todas as operações de criação, edição e exclusão requerem autenticação JWT
- **Controle de acesso**: Usuários não-administradores veem mensagem de "Acesso Negado"
- **Isolamento por empresa**: Administradores só podem gerenciar cargos da sua própria empresa

### 👔 Gestão de Cargos
- **Listagem de cargos** com paginação e busca
- **Cadastro de novos cargos** com validação automática
- **Edição de cargos** existentes (apenas nome, descrição e nível)
- **Visualização detalhada** de cada cargo
- **Exclusão/desativação** de cargos (soft delete)
- **Campos obrigatórios**: Nome
- **Campos opcionais**: Descrição, Nível
- **Vinculação automática**: Cada cargo é vinculado automaticamente à empresa do administrador
- **Código automático**: Gerado com as 3 primeiras letras do nome + 3 números aleatórios

## Estrutura Técnica

### Backend (Python/Flask)

#### Modelos (`backend/models/organizacional.py`)
```python
class Cargo(db.Model):
    - id, codigo, nome, descricao, nivel, empresa_id
    - Relacionamento: funcionarios, empresa
```

#### Views (`backend/views/cargos.py`)
- **GET /api/cargos** - Listar cargos da empresa do admin
- **POST /api/cargos** - Criar cargo (apenas admin, código gerado automaticamente)
- **PUT /api/cargos/{id}** - Atualizar cargo (apenas admin, apenas nome/descrição/nível)
- **DELETE /api/cargos/{id}** - Excluir cargo (apenas admin da mesma empresa)

#### Verificação de Permissão
```python
def verificar_admin():
    funcionario_id = int(get_jwt_identity())
    funcionario = Funcionario.query.get(funcionario_id)
    return funcionario and funcionario.gerente

def gerar_codigo_cargo(nome: str) -> str:
    # 3 primeiras letras do nome + 3 números aleatórios
    letras = nome[:3].upper().replace(' ', '')
    numeros = ''.join([str(random.randint(0, 9)) for _ in range(3)])
    return f"{letras}{numeros}"
```

### Frontend (React/TypeScript)

#### Páginas Criadas
- **`CargosPage.tsx`** - Interface completa para gestão de cargos

#### Funcionalidades da Interface
- ✅ **Listagem responsiva** com tabelas
- ✅ **Busca e filtros** em tempo real
- ✅ **Paginação** para grandes volumes de dados
- ✅ **Modais de cadastro** com validação
- ✅ **Modais de edição** pré-preenchidos
- ✅ **Modais de confirmação** para exclusão
- ✅ **Modais de visualização** detalhada
- ✅ **Feedback visual** de status (ativo/inativo)
- ✅ **Mensagens de erro** e sucesso
- ✅ **Verificação de permissão** de administrador
- ✅ **Formulários funcionais** com estado controlado

#### Navegação
- **Menu lateral** atualizado com nova opção
- **Seção "Gestão"** com Cargos
- **Ícone intuitivo** (Briefcase para cargos)

## Como Usar

### 1. Acesso como Administrador
- Faça login com um usuário que tenha `gerente = true`
- Acesse o menu lateral → Seção "Gestão"
- Clique em "Cargos"

### 2. Cadastrar Novo Cargo
1. Clique em "Novo Cargo"
2. Preencha apenas o **nome do cargo** (obrigatório)
3. Opcionalmente, adicione descrição e nível
4. Clique em "Cadastrar"
5. O **código será gerado automaticamente** (ex: "ADM123" para "Administrador")

### 3. Editar Cargo
1. Clique no ícone de lápis na linha do cargo
2. Edite apenas: **nome**, **descrição** e **nível**
3. O **código não pode ser alterado** (gerado automaticamente)
4. Clique em "Salvar"

### 4. Gerenciar Registros
- **Visualizar**: Clique no ícone de olho
- **Editar**: Clique no ícone de lápis
- **Excluir**: Clique no ícone de lixeira
- **Buscar**: Use o campo de busca no topo

## Validações Implementadas

### Cargos
- ✅ Nome obrigatório
- ✅ Código único gerado automaticamente
- ✅ Vinculação automática à empresa do admin
- ✅ Verificação de funcionários vinculados antes da exclusão
- ✅ Isolamento por empresa (admin só vê/edita cargos da sua empresa)

## Segurança

- 🔒 **Autenticação JWT** obrigatória
- 🔒 **Verificação de permissão** de administrador
- 🔒 **Isolamento por empresa** (admin só acessa cargos da sua empresa)
- 🔒 **Validação de dados** no backend
- 🔒 **Sanitização de inputs**
- 🔒 **Soft delete** para preservar integridade

## Exemplos de Códigos Gerados

- **"Administrador"** → "ADM123"
- **"Contador"** → "CON456"
- **"Auxiliar"** → "AUX789"
- **"Gerente"** → "GER012"
- **"Diretor"** → "DIR345"

## Próximos Passos Sugeridos

1. **Adicionar máscaras** nos campos de entrada
2. **Implementar upload de ícone** para cargos
3. **Adicionar histórico de alterações** (audit log)
4. **Criar relatórios** de cargos
5. **Implementar importação em lote** via CSV/Excel
6. **Adicionar validação de duplicação** de nomes na mesma empresa

## Credenciais de Teste

Para testar a funcionalidade, use as credenciais do usuário administrador:
- **Email**: admin@gmail.com
- **Senha**: admin123
- **Tipo**: Administrador (gerente = true)

---

**Status**: ✅ Implementado e Funcional
**Versão**: 2.0
**Data**: Dezembro 2024
