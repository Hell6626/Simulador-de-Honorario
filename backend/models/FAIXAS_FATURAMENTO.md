# Faixas de Faturamento por Regime Tributário

Este documento descreve as faixas de faturamento implementadas no sistema, organizadas por regime tributário específico.

## Estrutura das Faixas

As faixas de faturamento são organizadas por regime tributário, conforme a legislação vigente:

### Simples Nacional (SN)
- **1ª Faixa**: R$ 0,00 a R$ 180.000,00 = 4,00%
- **2ª Faixa**: R$ 180.000,01 a R$ 360.000,00 = 7,30%
- **3ª Faixa**: R$ 360.000,01 a R$ 720.000,00 = 9,50%
- **4ª Faixa**: R$ 720.000,01 a R$ 1.800.000,00 = 10,70%
- **5ª Faixa**: R$ 1.800.000,01 a R$ 3.600.000,00 = 14,30%
- **6ª Faixa**: R$ 3.600.000,01 a R$ 4.800.000,00 = 19,00%

### Lucro Presumido (LP)
- **Alíquota Padrão**: R$ 0,00 em diante = 15,00% (sem limite máximo)

### Lucro Real (LR)
- **Alíquota Padrão**: R$ 0,00 em diante = 15,00% (sem limite máximo)

### Microempreendedor Individual (MEI)
- **Alíquota Padrão**: R$ 0,00 a R$ 81.000,00 = 5,00% (limite máximo de faturamento)

## Implementação no Sistema

### Modelo de Dados
```python
class FaixaFaturamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    regime_tributario_id = db.Column(db.Integer, db.ForeignKey('regime_tributario.id'))
    valor_inicial = db.Column(db.Numeric(precision=15, scale=2))
    valor_final = db.Column(db.Numeric(precision=15, scale=2))
    aliquota = db.Column(db.Numeric(precision=5, scale=2))
```

### Inicialização
As faixas são inicializadas automaticamente através da função:
```python
from models import inicializar_faixas_faturamento

# Inicializa apenas as faixas de faturamento
inicializar_faixas_faturamento()
```

### Consulta de Faixas
```python
from models import FaixaFaturamento, RegimeTributario

# Buscar faixas do Simples Nacional
regime_sn = RegimeTributario.query.filter_by(codigo='SN').first()
faixas = FaixaFaturamento.query.filter_by(regime_tributario_id=regime_sn.id).all()
```

## Atualizações Legais

As faixas implementadas são baseadas na legislação vigente de 2024. Para atualizações futuras:

1. Verificar a legislação atual no site da Receita Federal
2. Atualizar os valores no arquivo `models/initialization.py`
3. Executar a função de inicialização novamente

## Observações Importantes

- **Limite Máximo**: R$ 4.800.000,00 (limite do Simples Nacional)
- **Alíquotas Progressivas**: As alíquotas aumentam conforme o faturamento
- **Validação**: O sistema valida que valor_final > valor_inicial
- **Unicidade**: Não podem existir faixas duplicadas para o mesmo regime

## API Endpoints

- `GET /api/faixas-faturamento/` - Listar todas as faixas
- `GET /api/faixas-faturamento/?regime_id=1` - Filtrar por regime tributário
- `GET /api/faixas-faturamento/<id>` - Obter faixa específica
