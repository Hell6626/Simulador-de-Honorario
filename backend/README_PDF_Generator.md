# Gerador de PDF para Propostas

## Visão Geral

Este módulo gera PDFs de propostas comerciais com layout idêntico ao exemplo fornecido (`Proposta Comercial_8646906349221eiiii1_7683193268679ig0bji.pdf`).

## Características

- ✅ **Layout Exato**: Replica fielmente o design do PDF de referência
- ✅ **Margens Otimizadas**: 25mm laterais, 15mm superior/inferior para máximo aproveitamento
- ✅ **Estilos Profissionais**: Tipografia e espaçamentos profissionais
- ✅ **Fallback Inteligente**: Gera PDF temporário se dados reais não estiverem disponíveis
- ✅ **Logo Integrada**: Suporte para logo da empresa (quadrada laranja)

## Estrutura do PDF

### Página 1
1. **Cabeçalho**: Data (esquerda) + Logo (direita)
2. **Título**: "Proposta de Orçamento" (grande, duas linhas)
3. **Box Cliente**: "Preparado para: [Nome do Cliente]"
4. **Introdução**: Texto de apresentação
5. **Sobre Nós**: Informações da empresa
6. **Serviços**: Lista numerada dos serviços

### Página 2
1. **Orçamento**: Tabela com serviços, quantidades e valores
2. **Detalhes Adicionais**: Previsão de entrega e opções de pagamento

## Como Usar

### 1. Geração Simples (PDF Temporário)

```python
from services.pdf_generator import pdf_generator

# Gerar PDF temporário com dados de exemplo
caminho_pdf = pdf_generator.gerar_pdf_proposta_temp()
print(f"PDF gerado em: {caminho_pdf}")
```

### 2. Geração com Dados Reais

```python
from services.pdf_generator import pdf_generator

# Gerar PDF com dados de uma proposta existente
caminho_pdf = pdf_generator.gerar_pdf_proposta(proposta_id=123)
print(f"PDF gerado em: {caminho_pdf}")
```

### 3. Integração com Flask

```python
from flask import current_app
from services.pdf_generator import pdf_generator

@app.route('/gerar-pdf/<int:proposta_id>')
def gerar_pdf(proposta_id):
    try:
        with current_app.app_context():
            caminho_pdf = pdf_generator.gerar_pdf_proposta(proposta_id)
            return send_file(caminho_pdf, as_attachment=True)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500
```

## Configurações

### Margens do Documento
- **Esquerda/Direita**: 25mm (otimizado para mais espaço)
- **Superior/Inferior**: 15mm (otimizado para mais espaço)

### Estilos de Texto
- **Título Principal**: 42pt, Helvetica-Bold
- **Títulos de Seção**: 28pt, Helvetica-Bold
- **Texto Normal**: 10pt, Helvetica, justificado
- **Box Cliente**: 12pt, Helvetica-Bold

### Cores
- **Preto**: Texto principal
- **Branco**: Fundo
- **Laranja**: Logo da empresa

## Arquivos de Saída

Os PDFs são salvos em:
```
backend/uploads/pdfs/
```

### Nomenclatura
- **PDF Real**: `proposta_{numero}_{timestamp}.pdf`
- **PDF Temporário**: `proposta_temp_{timestamp}.pdf`

## Dependências

```bash
pip install reportlab
```

## Teste

Execute o arquivo de teste para verificar a funcionalidade:

```bash
cd backend
python test_pdf_generator.py
```

## Personalização

### Alterar Dados da Empresa

Edite o dicionário `self.empresa` no método `__init__`:

```python
self.empresa = {
    'nome': 'Sua Empresa LTDA',
    'cnpj': '11.111.111/1111-11',
    'endereco': 'Rua Exemplo, 123',
    'cidade': 'Sua Cidade - UF',
    'cep': '12345-678',
    'telefone': '(11) 11111-1111',
    'email': 'contato@suaempresa.com.br',
    'site': 'www.suaempresa.com.br'
}
```

### Alterar Logo

1. Coloque sua logo em `assets/images/Logo_Contabilidade.png`
2. Ou ajuste o método `_find_logo_path()` para apontar para o caminho correto

### Alterar Estilos

Modifique o método `_configurar_estilos()` para ajustar:
- Tamanhos de fonte
- Espaçamentos
- Cores
- Tipografia

## Solução de Problemas

### Erro: "Modelos não disponíveis"
- **Causa**: Banco de dados não acessível
- **Solução**: O sistema automaticamente gera PDF temporário

### Erro: "Logo não encontrada"
- **Causa**: Arquivo de logo não existe
- **Solução**: Sistema cria logo padrão (quadrado laranja com "C")

### PDF não abre
- **Causa**: Permissões de arquivo ou aplicativo não encontrado
- **Solução**: Verificar permissões e instalar leitor de PDF

## Exemplo de Saída

O PDF gerado terá:
- ✅ Layout profissional e limpo
- ✅ Tipografia consistente
- ✅ Espaçamentos equilibrados
- ✅ Tabela de orçamento bem formatada
- ✅ Informações organizadas em seções claras

## Suporte

Para dúvidas ou problemas:
1. Verifique os logs de erro
2. Execute o arquivo de teste
3. Verifique as dependências instaladas
4. Confirme as permissões de escrita no diretório de uploads
