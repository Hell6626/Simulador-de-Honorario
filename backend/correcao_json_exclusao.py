#!/usr/bin/env python3
"""
🔧 CORREÇÃO URGENTE: Problema de JSON na Exclusão
===============================================

Este script corrige o problema de JSON na exclusão de propostas.
O erro 400 Bad Request está ocorrendo porque request.get_json() falha
quando não há JSON válido na requisição.

📋 PROBLEMA IDENTIFICADO:
- Erro: 400 Bad Request: Failed to decode JSON object: Expecting value: line 1 column 1 (char 0)
- Causa: request.get_json() falha quando não há JSON válido na requisição
- Linha problemática: 926 em backend/views/propostas.py

✅ SOLUÇÃO:
Substituir o tratamento de JSON por uma versão mais robusta com try/except
"""

import os
import re

def corrigir_problema_json():
    """
    🔧 Aplica correção do problema de JSON na exclusão de propostas
    """
    print("🔧 APLICANDO CORREÇÃO DO PROBLEMA DE JSON")
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
        
        # Função corrigida completa
        funcao_corrigida = '''@propostas_bp.route('/<int:proposta_id>', methods=['DELETE'])
@jwt_required()
@handle_api_errors
def delete_proposta(proposta_id: int):
    """Soft delete de uma proposta - marca como inativa"""
    try:
        # 1. Carregar proposta com verificação de existência
        proposta = Proposta.query.get_or_404(proposta_id)
        if not proposta:
            raise ValueError('Proposta não encontrada')
        
        # 2. Verificar funcionário atual
        funcionario_id = int(get_jwt_identity())
        funcionario = Funcionario.query.get(funcionario_id)
        if not funcionario or not funcionario.ativo:
            raise ValueError('Funcionário não encontrado ou inativo')

        # 3. Obter dados da requisição com tratamento seguro de JSON
        observacao = ''
        try:
            data = request.get_json() or {}
            observacao = data.get('observacao', '').strip()
        except Exception as e:
            current_app.logger.warning(f"Erro ao processar JSON da requisição: {str(e)}")
            # Continuar com observação vazia se não conseguir processar JSON
        
        # 4. Verificar se é proposta de outro funcionário
        is_propria_proposta = proposta.funcionario_responsavel_id == funcionario_id
        
        # 5. Validação de observação para proposta de outro funcionário
        if not is_propria_proposta and not observacao:
            raise ValueError('Observação é obrigatória para exclusão de proposta de outro funcionário')

        # 6. Excluir PDF vinculado com verificação segura de campos
        pdf_excluido = False
        try:
            # Verificar campos de PDF disponíveis
            pdf_caminho = None
            if hasattr(proposta, 'pdf_caminho') and proposta.pdf_caminho:
                pdf_caminho = proposta.pdf_caminho
            elif hasattr(proposta, 'caminho_pdf') and proposta.caminho_pdf:
                pdf_caminho = proposta.caminho_pdf
            
            if pdf_caminho:
                import os
                pdf_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'pdfs', pdf_caminho)
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                    pdf_excluido = True
                    current_app.logger.info(f"PDF excluído: {pdf_path}")
                else:
                    current_app.logger.warning(f"PDF não encontrado no caminho: {pdf_path}")
        except Exception as e:
            current_app.logger.warning(f"Erro ao excluir PDF: {str(e)}")
        
        # 7. Limpar campos de PDF no banco (compatibilidade)
        try:
            if hasattr(proposta, 'pdf_caminho'):
                proposta.pdf_caminho = None
            if hasattr(proposta, 'caminho_pdf'):
                proposta.caminho_pdf = None
            if hasattr(proposta, 'pdf_gerado'):
                proposta.pdf_gerado = False
            if hasattr(proposta, 'pdf_data_geracao'):
                proposta.pdf_data_geracao = None
            if hasattr(proposta, 'data_geracao_pdf'):
                proposta.data_geracao_pdf = None
        except Exception as e:
            current_app.logger.warning(f"Erro ao limpar campos de PDF: {str(e)}")

        # 8. Soft delete - marcar como inativa
        proposta.ativo = False
        
        # 9. Commit das alterações
        db.session.commit()
        current_app.logger.info(f"Proposta {proposta_id} marcada como inativa")

        # 10. Criar notificação se não for própria proposta
        notificacao_enviada = False
        if not is_propria_proposta and proposta.funcionario_responsavel_id:
            try:
                from models.notificacoes import Notificacao
                Notificacao.criar_notificacao_exclusao_proposta(
                    proposta=proposta,
                    de_funcionario_id=funcionario_id,
                    observacao=observacao
                )
                notificacao_enviada = True
                current_app.logger.info(f"Notificação de exclusão criada para funcionário {proposta.funcionario_responsavel_id}")
            except Exception as e:
                current_app.logger.error(f"Erro ao criar notificação: {str(e)}")

        # 11. Log detalhado com verificação segura
        try:
            funcionario_responsavel = None
            if proposta.funcionario_responsavel_id:
                funcionario_responsavel = Funcionario.query.get(proposta.funcionario_responsavel_id)
            
            responsavel_nome = "própria" if is_propria_proposta else f"de {funcionario_responsavel.nome if funcionario_responsavel else 'N/A'}"
        except Exception as e:
            current_app.logger.warning(f"Erro ao carregar funcionário responsável: {str(e)}")
            responsavel_nome = "própria" if is_propria_proposta else "de funcionário desconhecido"
            
        current_app.logger.info(
            f"Proposta marcada como inativa: #{proposta.numero} "
            f"(ID: {proposta.id}, Funcionário: {funcionario.nome}, "
            f"Proposta: {responsavel_nome}, PDF excluído: {pdf_excluido}, "
            f"Notificação enviada: {notificacao_enviada})"
        )
        
        return jsonify({
            'message': 'Proposta excluída com sucesso',
            'pdf_excluido': pdf_excluido,
            'notificacao_enviada': notificacao_enviada,
            'is_propria_proposta': is_propria_proposta
        })
        
    except ValueError as ve:
        # Erros de validação - retornar 400
        current_app.logger.warning(f"Erro de validação ao excluir proposta {proposta_id}: {str(ve)}")
        db.session.rollback()
        return jsonify({'error': str(ve)}), 400
        
    except Exception as e:
        # Erros gerais - retornar 500
        current_app.logger.error(f"Erro interno ao excluir proposta {proposta_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500'''
        
        # Encontrar e substituir a função delete_proposta
        padrao_funcao = r'@propostas_bp\.route\(\'/<int:proposta_id>\', methods=\[\'DELETE\'\]\).*?def delete_proposta\(proposta_id: int\):.*?(?=def|\Z)'
        
        if re.search(padrao_funcao, conteudo, re.DOTALL):
            # Substituir a função
            conteudo = re.sub(padrao_funcao, funcao_corrigida, conteudo, flags=re.DOTALL)
            print("✅ Função delete_proposta substituída com sucesso")
        else:
            print("⚠️  Padrão da função não encontrado, tentando substituição manual")
            # Tentar substituição manual por linhas
            linhas = conteudo.split('\n')
            nova_conteudo = []
            dentro_funcao = False
            indentacao_funcao = 0
            
            for i, linha in enumerate(linhas):
                if '@propostas_bp.route(\'/<int:proposta_id>\', methods=[\'DELETE\'])' in linha:
                    dentro_funcao = True
                    indentacao_funcao = len(linha) - len(linha.lstrip())
                    # Adicionar a nova função
                    nova_conteudo.append(funcao_corrigida)
                    continue
                elif dentro_funcao and linha.strip() and not linha.startswith(' ' * (indentacao_funcao + 1)):
                    dentro_funcao = False
                    nova_conteudo.append(linha)
                elif not dentro_funcao:
                    nova_conteudo.append(linha)
            
            conteudo = '\n'.join(nova_conteudo)
        
        # Salvar arquivo corrigido
        with open(arquivo_path, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        print("✅ CORREÇÃO APLICADA COM SUCESSO!")
        print("📁 Arquivo salvo com tratamento robusto de JSON")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao aplicar correção: {str(e)}")
        return False

def verificar_correcao_aplicada():
    """
    🔍 Verifica se a correção foi aplicada corretamente
    """
    print("\n🔍 VERIFICANDO CORREÇÃO APLICADA")
    print("=" * 50)
    
    arquivo_path = os.path.join(os.path.dirname(__file__), 'views', 'propostas.py')
    
    try:
        with open(arquivo_path, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Verificar elementos da correção
        elementos_verificacao = [
            ('try:\n            data = request.get_json() or {}', 'Tratamento seguro de JSON'),
            ('except Exception as e:\n            current_app.logger.warning', 'Tratamento de exceção JSON'),
            ('proposta.pdf_caminho', 'Campo PDF caminho correto'),
            ('proposta.pdf_gerado', 'Campo PDF gerado correto'),
            ('proposta.pdf_data_geracao', 'Campo PDF data correto'),
            ('return jsonify({\n            \'message\': \'Proposta excluída com sucesso\'', 'Retorno JSON correto')
        ]
        
        print("✅ VERIFICANDO ELEMENTOS DA CORREÇÃO:")
        todos_presentes = True
        
        for elemento, descricao in elementos_verificacao:
            if elemento in conteudo:
                print(f"   ✅ {descricao}")
            else:
                print(f"   ❌ {descricao} - NÃO ENCONTRADO")
                todos_presentes = False
        
        return todos_presentes
        
    except Exception as e:
        print(f"❌ Erro ao verificar correção: {str(e)}")
        return False

def gerar_relatorio_correcao():
    """
    📊 Gera relatório da correção aplicada
    """
    print("\n📊 RELATÓRIO DA CORREÇÃO APLICADA")
    print("=" * 50)
    
    print("🔧 CORREÇÕES APLICADAS:")
    print("   1. Tratamento seguro de JSON com try/except")
    print("   2. Campos PDF corretos: pdf_caminho, pdf_gerado, pdf_data_geracao")
    print("   3. Tratamento de exceções para carregamento do funcionário responsável")
    print("   4. Compatibilidade: Funciona com ou sem JSON na requisição")
    
    print("\n✅ FUNCIONALIDADES CORRIGIDAS:")
    print("   - Exclusão de propostas próprias (sem JSON)")
    print("   - Exclusão de propostas de outros funcionários (com JSON)")
    print("   - Tratamento robusto de erros de JSON")
    print("   - Logs detalhados para debug")
    
    print("\n🎯 RESULTADO ESPERADO:")
    print("   - Erro 400 Bad Request resolvido")
    print("   - Exclusão de propostas funcionará corretamente")
    print("   - Sistema mais robusto e estável")
    
    print("\n🚀 CORREÇÃO CONCLUÍDA COM SUCESSO!")

if __name__ == "__main__":
    print("🚀 INICIANDO CORREÇÃO DO PROBLEMA DE JSON")
    print("=" * 50)
    
    # Aplicar correção
    sucesso = corrigir_problema_json()
    
    if sucesso:
        # Verificar se foi aplicada corretamente
        verificacao_ok = verificar_correcao_aplicada()
        
        if verificacao_ok:
            gerar_relatorio_correcao()
        else:
            print("\n⚠️  CORREÇÃO APLICADA MAS VERIFICAÇÃO FALHOU")
    else:
        print("\n❌ FALHA NA CORREÇÃO!")
        print("Verifique os logs de erro acima.")
    
    print("\n" + "=" * 50)
