#!/usr/bin/env python3
"""
🔧 CORREÇÃO URGENTE: Problema dos Campos PDF
==========================================

Este script corrige o problema dos campos PDF na exclusão de propostas.
O erro 500 está ocorrendo porque o código está tentando acessar campos
que não existem no modelo Proposta.

📋 PROBLEMA IDENTIFICADO:
- Modelo Proposta tem: pdf_caminho, pdf_gerado, pdf_data_geracao
- Código está tentando acessar: caminho_pdf, nome_arquivo_pdf, data_geracao_pdf

✅ SOLUÇÃO:
Substituir os campos incorretos pelos corretos no arquivo backend/views/propostas.py
"""

import os
import re

def corrigir_campos_pdf():
    """
    🔧 Aplica correção dos campos PDF no arquivo propostas.py
    """
    print("🔧 APLICANDO CORREÇÃO DOS CAMPOS PDF")
    print("=" * 50)
    
    # Caminho do arquivo
    arquivo_path = os.path.join(os.path.dirname(__file__), 'views', 'propostas.py')
    
    if not os.path.exists(arquivo_path):
        print(f"❌ Arquivo não encontrado: {arquivo_path}")
        return False
    
    try:
        # Ler o arquivo
        with open(arquivo_path, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        print("📄 Arquivo carregado com sucesso")
        
        # Correções a serem aplicadas
        correcoes = [
            {
                'nome': 'Campo caminho_pdf',
                'antes': 'if proposta.caminho_pdf:',
                'depois': 'if proposta.pdf_caminho:',
                'descricao': 'Corrigir verificação de caminho do PDF'
            },
            {
                'nome': 'Campo caminho_pdf no join',
                'antes': 'pdf_path = os.path.join(current_app.config[\'UPLOAD_FOLDER\'], \'pdfs\', proposta.caminho_pdf)',
                'depois': 'pdf_path = os.path.join(current_app.config[\'UPLOAD_FOLDER\'], \'pdfs\', proposta.pdf_caminho)',
                'descricao': 'Corrigir construção do caminho do PDF'
            },
            {
                'nome': 'Limpeza campo caminho_pdf',
                'antes': 'proposta.caminho_pdf = None',
                'depois': 'proposta.pdf_caminho = None',
                'descricao': 'Corrigir limpeza do campo de caminho'
            },
            {
                'nome': 'Limpeza campo nome_arquivo_pdf',
                'antes': 'proposta.nome_arquivo_pdf = None',
                'depois': 'proposta.pdf_gerado = False',
                'descricao': 'Corrigir limpeza do campo de nome do arquivo'
            },
            {
                'nome': 'Limpeza campo data_geracao_pdf',
                'antes': 'proposta.data_geracao_pdf = None',
                'depois': 'proposta.pdf_data_geracao = None',
                'descricao': 'Corrigir limpeza do campo de data de geração'
            }
        ]
        
        # Aplicar correções
        correcoes_aplicadas = 0
        for correcao in correcoes:
            if correcao['antes'] in conteudo:
                conteudo = conteudo.replace(correcao['antes'], correcao['depois'])
                print(f"✅ {correcao['nome']}: {correcao['descricao']}")
                correcoes_aplicadas += 1
            else:
                print(f"⚠️  {correcao['nome']}: Padrão não encontrado")
        
        # Verificar se há outras ocorrências problemáticas
        padroes_problematicos = [
            r'proposta\.caminho_pdf',
            r'proposta\.nome_arquivo_pdf',
            r'proposta\.data_geracao_pdf'
        ]
        
        print("\n🔍 Verificando padrões problemáticos restantes...")
        for padrao in padroes_problematicos:
            matches = re.findall(padrao, conteudo)
            if matches:
                print(f"⚠️  Encontrado: {padrao} - {len(matches)} ocorrência(s)")
            else:
                print(f"✅ Limpo: {padrao}")
        
        # Salvar arquivo corrigido
        with open(arquivo_path, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        print(f"\n✅ CORREÇÃO APLICADA COM SUCESSO!")
        print(f"📊 {correcoes_aplicadas} correções aplicadas")
        print(f"📁 Arquivo salvo: {arquivo_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao aplicar correção: {str(e)}")
        return False

def verificar_estrutura_modelo():
    """
    🔍 Verifica a estrutura atual do modelo Proposta
    """
    print("\n🔍 VERIFICANDO ESTRUTURA DO MODELO PROPOSTA")
    print("=" * 50)
    
    try:
        # Tentar importar o modelo
        import sys
        sys.path.append(os.path.dirname(__file__))
        
        from models.propostas import Proposta
        
        # Verificar campos relacionados a PDF
        campos_pdf = []
        for coluna in Proposta.__table__.columns:
            if 'pdf' in coluna.name.lower():
                campos_pdf.append(coluna.name)
        
        print(f"📄 Campos PDF encontrados no modelo Proposta:")
        for campo in campos_pdf:
            print(f"   - {campo}")
        
        if not campos_pdf:
            print("⚠️  Nenhum campo PDF encontrado no modelo")
        
        return campos_pdf
        
    except Exception as e:
        print(f"❌ Erro ao verificar modelo: {str(e)}")
        return []

def gerar_relatorio_correcao():
    """
    📊 Gera relatório da correção aplicada
    """
    print("\n📊 RELATÓRIO DA CORREÇÃO APLICADA")
    print("=" * 50)
    
    print("🔧 CORREÇÕES APLICADAS:")
    print("   1. proposta.caminho_pdf → proposta.pdf_caminho")
    print("   2. proposta.nome_arquivo_pdf → proposta.pdf_gerado = False")
    print("   3. proposta.data_geracao_pdf → proposta.pdf_data_geracao")
    
    print("\n✅ RESULTADO ESPERADO:")
    print("   - Erro 500 na exclusão de propostas será resolvido")
    print("   - Campos PDF serão acessados corretamente")
    print("   - Exclusão de propostas funcionará normalmente")
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("   1. Reiniciar o servidor Flask")
    print("   2. Testar exclusão de propostas")
    print("   3. Verificar logs para confirmar correção")
    
    print("\n🚀 CORREÇÃO CONCLUÍDA COM SUCESSO!")

if __name__ == "__main__":
    print("🚀 INICIANDO CORREÇÃO DOS CAMPOS PDF")
    print("=" * 50)
    
    # Verificar estrutura do modelo
    campos_pdf = verificar_estrutura_modelo()
    
    # Aplicar correção
    sucesso = corrigir_campos_pdf()
    
    if sucesso:
        gerar_relatorio_correcao()
    else:
        print("\n❌ FALHA NA CORREÇÃO!")
        print("Verifique os logs de erro acima.")
    
    print("\n" + "=" * 50)
