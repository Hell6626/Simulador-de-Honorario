# 💰 Sistema de Mensalidade Automática

## 📋 Visão Geral

O Sistema de Mensalidade Automática implementa a regra de negócio para cálculo automático de mensalidades baseadas na configuração tributária selecionada no Passo 2 da criação de propostas.

## 🏗️ Arquitetura

### 1. **Nova Tabela: `mensalidade_automatica`**

```sql
CREATE TABLE mensalidade_automatica (
    id INTEGER PRIMARY KEY,
    tipo_atividade_id INTEGER NOT NULL,
    regime_tributario_id INTEGER NOT NULL,
    faixa_faturamento_id INTEGER NOT NULL,
    valor_mensalidade DECIMAL(15,2) NOT NULL,
    observacoes TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    created_at DATETIME,
    updated_at DATETIME,
    UNIQUE(tipo_atividade_id, regime_tributario_id, faixa_faturamento_id)
);
```

### 2. **Modelo: `MensalidadeAutomatica`**

- **Localização:** `backend/models/tributario.py`
- **Relacionamentos:** TipoAtividade, RegimeTributario, FaixaFaturamento
- **Métodos:** `to_json()` para serialização

### 3. **API Endpoints**

- **Localização:** `backend/views/mensalidades.py`
- **Endpoints:**
  - `POST /api/mensalidades/buscar` - Buscar mensalidade por configuração
  - `GET /api/mensalidades/buscar-por-proposta/{id}` - Buscar por proposta específica
  - `GET /api/mensalidades/listar` - Listar todas as mensalidades
  - `POST /api/mensalidades/calcular-total` - Calcular total com mensalidade

### 4. **Serviço Frontend**

- **Localização:** `frontend/src/services/api.ts`
- **Métodos:** `buscarMensalidade()`, `calcularTotalComMensalidade()`

### 5. **Integração no Passo 4**

- **Localização:** `frontend/src/components/propostas/passos/Passo4RevisaoProposta.tsx`
- **Funcionalidades:**
  - Busca automática da mensalidade
  - Exibição em card destacado
  - Cálculo automático do total
  - Integração com desconto

## 📊 Regra de Negócio Implementada

### **Serviços**

| Regime | Até 180k | Até 360k | Até 720k | Acima 720k |
|--------|----------|----------|----------|------------|
| Simples Nacional | R$ 800,00 | R$ 1.200,00 | R$ 1.600,00 | R$ 2.000,00 |
| Lucro Presumido | R$ 1.000,00 | R$ 1.400,00 | R$ 1.800,00 | R$ 2.200,00 |
| Lucro Real | R$ 1.200,00 | R$ 1.600,00 | R$ 2.000,00 | R$ 2.400,00 |

### **Comércio**

| Regime | Até 180k | Até 360k | Até 720k | Acima 720k |
|--------|----------|----------|----------|------------|
| Simples Nacional | R$ 600,00 | R$ 900,00 | R$ 1.200,00 | R$ 1.500,00 |

### **Casos Especiais**

- **MEI - Serviços:** R$ 300,00
- **MEI - Comércio:** R$ 250,00
- **Pessoa Física:** "A Combinar" (valor 0,00)

## 🚀 Como Usar

### **1. Inicialização do Sistema**

```bash
# Executar migração e inicializar dados
python backend/inicializar_mensalidades.py
```

### **2. Uso no Frontend**

```typescript
// Buscar mensalidade automática
const response = await apiService.buscarMensalidade({
  tipo_atividade_id: 1,
  regime_tributario_id: 2,
  faixa_faturamento_id: 3
});

// Calcular total com mensalidade
const total = await apiService.calcularTotalComMensalidade({
  tipo_atividade_id: 1,
  regime_tributario_id: 2,
  faixa_faturamento_id: 3,
  valor_servicos: 1000.00
});
```

### **3. Integração Automática**

O sistema funciona automaticamente no **Passo 4 - Revisão**:

1. **Busca automática** da mensalidade baseada na configuração tributária
2. **Exibição em card destacado** com informações completas
3. **Cálculo automático** do total incluindo mensalidade
4. **Integração com desconto** aplicado sobre o total

## 🔧 Manutenção

### **Atualizar Valores**

Para atualizar os valores das mensalidades:

1. **Via Banco de Dados:**
```sql
UPDATE mensalidade_automatica 
SET valor_mensalidade = 1500.00 
WHERE tipo_atividade_id = 1 AND regime_tributario_id = 2;
```

2. **Via API (futuro):**
```typescript
// Endpoint para atualizar mensalidade
PUT /api/mensalidades/{id}
```

### **Adicionar Novas Regras**

1. **Adicionar dados** em `inicializar_mensalidades_automaticas()`
2. **Executar script** de inicialização
3. **Testar** no Passo 4

## 📈 Benefícios

### **✅ Automatização**
- Cálculo automático baseado na configuração
- Eliminação de erros manuais
- Consistência nos valores

### **✅ Flexibilidade**
- Suporte a todos os cenários da regra
- Fácil adição de novas regras
- Casos especiais tratados

### **✅ Transparência**
- Usuário vê exatamente como foi calculado
- Informações detalhadas no card
- Observações explicativas

### **✅ Escalabilidade**
- Estrutura preparada para futuras expansões
- API RESTful para integrações
- Modelo de dados normalizado

## 🧪 Testes

### **Cenários de Teste**

1. **Serviços - Simples Nacional - Até 180k**
   - Configuração: Serviços + SN + Faixa 1
   - Esperado: R$ 800,00

2. **Comércio - Lucro Presumido - Até 360k**
   - Configuração: Comércio + LP + Faixa 2
   - Esperado: Valor não encontrado (regra não implementada)

3. **MEI - Serviços**
   - Configuração: Serviços + MEI + Faixa MEI
   - Esperado: R$ 300,00

4. **Pessoa Física**
   - Configuração: PF + null + null
   - Esperado: "A Combinar"

### **Validação**

- ✅ Mensalidade aparece no Passo 4
- ✅ Valor correto baseado na configuração
- ✅ Total calculado corretamente
- ✅ Desconto aplicado sobre total com mensalidade
- ✅ Informações exibidas corretamente

## 📝 Logs e Monitoramento

### **Logs de Inicialização**
```
💰 Inicializando mensalidades automáticas...
✅ 25 mensalidades automáticas inicializadas com sucesso!
```

### **Logs de Busca**
```
Mensalidade automática não encontrada para esta configuração
```

### **Logs de Cálculo**
```
Serviços: R$ 1.000,00 + Mensalidade: R$ 800,00 = R$ 1.800,00
```

## 🔮 Futuras Melhorias

1. **Interface de Administração** para gerenciar mensalidades
2. **Histórico de Alterações** nos valores
3. **Validação de Regras** antes de salvar
4. **Relatórios** de mensalidades por período
5. **Integração com Contabilidade** para faturamento automático

---

**Sistema implementado com sucesso!** 🎉

Todas as funcionalidades estão operacionais e integradas ao fluxo de criação de propostas.
