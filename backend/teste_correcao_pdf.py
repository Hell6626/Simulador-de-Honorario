#!/usr/bin/env python3
"""
🧪 TESTE DA CORREÇÃO DOS CAMPOS PDF
==================================

Este script testa se a correção dos campos PDF foi aplicada corretamente
e se a exclusão de propostas funcionará sem erro 500.
"""

import os
import sys
import re

def testar_correcao_campos_pdf():
    """
    🧪 Testa se a correção dos campos PDF foi aplicada corretamente
    """
    print("🧪 TESTANDO CORREÇÃO DOS CAMPOS PDF")
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
        
        # Verificar se as correções foram aplicadas
        correcoes_esperadas = [
            ('proposta.pdf_caminho', 'Campo PDF caminho corrigido'),
            ('proposta.pdf_gerado', 'Campo PDF gerado corrigido'),
            ('proposta.pdf_data_geracao', 'Campo PDF data corrigido')
        ]
        
        print("\n✅ VERIFICANDO CORREÇÕES APLICADAS:")
        todas_corrigidas = True
        
        for campo, descricao in correcoes_esperadas:
            if campo in conteudo:
                print(f"   ✅ {descricao}: {campo}")
            else:
                print(f"   ❌ {descricao}: {campo} - NÃO ENCONTRADO")
                todas_corrigidas = False
        
        # Verificar se ainda há campos problemáticos
        campos_problematicos = [
            'proposta.caminho_pdf',
            'proposta.nome_arquivo_pdf', 
            'proposta.data_geracao_pdf'
        ]
        
        print("\n🔍 VERIFICANDO CAMPOS PROBLEMÁTICOS RESTANTES:")
        campos_problematicos_encontrados = []
        
        for campo in campos_problematicos:
            if campo in conteudo:
                print(f"   ⚠️  {campo} - AINDA PRESENTE")
                campos_problematicos_encontrados.append(campo)
            else:
                print(f"   ✅ {campo} - CORRIGIDO")
        
        # Verificar estrutura da função delete_proposta
        print("\n🔍 VERIFICANDO ESTRUTURA DA FUNÇÃO DELETE_PROPOSTA:")
        
        # Buscar a função delete_proposta
        funcao_match = re.search(r'def delete_proposta\(proposta_id: int\):.*?(?=def|\Z)', conteudo, re.DOTALL)
        
        if funcao_match:
            funcao_conteudo = funcao_match.group(0)
            
            # Verificar elementos críticos
            elementos_criticos = [
                ('proposta.pdf_caminho', 'Verificação de PDF'),
                ('proposta.pdf_gerado = False', 'Limpeza de PDF gerado'),
                ('proposta.pdf_data_geracao = None', 'Limpeza de data PDF'),
                ('db.session.commit()', 'Commit da transação'),
                ('Notificacao.criar_notificacao_exclusao_proposta', 'Criação de notificação')
            ]
            
            for elemento, descricao in elementos_criticos:
                if elemento in funcao_conteudo:
                    print(f"   ✅ {descricao}: {elemento}")
                else:
                    print(f"   ❌ {descricao}: {elemento} - NÃO ENCONTRADO")
                    todas_corrigidas = False
        else:
            print("   ❌ Função delete_proposta não encontrada")
            todas_corrigidas = False
        
        # Resultado final
        print("\n📊 RESULTADO DO TESTE:")
        if todas_corrigidas and not campos_problematicos_encontrados:
            print("   ✅ TODAS AS CORREÇÕES FORAM APLICADAS COM SUCESSO!")
            print("   ✅ Nenhum campo problemático restante")
            print("   ✅ Estrutura da função está correta")
            print("\n🎉 ERRO 500 DEVE ESTAR RESOLVIDO!")
            return True
        else:
            print("   ❌ ALGUMAS CORREÇÕES FALTAM")
            if campos_problematicos_encontrados:
                print(f"   ❌ Campos problemáticos restantes: {campos_problematicos_encontrados}")
            print("\n⚠️  ERRO 500 PODE AINDA OCORRER!")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar correção: {str(e)}")
        return False

def gerar_relatorio_teste():
    """
    📊 Gera relatório do teste de correção
    """
    print("\n📊 RELATÓRIO DO TESTE DE CORREÇÃO")
    print("=" * 50)
    
    print("🔧 CORREÇÕES TESTADAS:")
    print("   1. proposta.caminho_pdf → proposta.pdf_caminho")
    print("   2. proposta.nome_arquivo_pdf → proposta.pdf_gerado = False")
    print("   3. proposta.data_geracao_pdf → proposta.pdf_data_geracao")
    
    print("\n✅ FUNCIONALIDADES VERIFICADAS:")
    print("   - Verificação de PDF vinculado")
    print("   - Limpeza de campos PDF no banco")
    print("   - Commit da transação")
    print("   - Criação de notificação")
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("   1. Reiniciar o servidor Flask")
    print("   2. Testar exclusão de propostas no frontend")
    print("   3. Verificar logs do servidor")
    print("   4. Confirmar que não há mais erro 500")
    
    print("\n🚀 TESTE CONCLUÍDO!")

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE DA CORREÇÃO DOS CAMPOS PDF")
    print("=" * 50)
    
    # Executar teste
    sucesso = testar_correcao_campos_pdf()
    
    if sucesso:
        gerar_relatorio_teste()
    else:
        print("\n❌ TESTE FALHOU!")
        print("Verifique os logs de erro acima.")
    
    print("\n" + "=" * 50)
