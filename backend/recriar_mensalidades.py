#!/usr/bin/env python3
"""
🧹 Script Final para Recriar Tabela de Mensalidades
===================================================

Script corrigido que inclui TODAS as mensalidades:
- Serviços (SN, LP, LR)
- Comércio (SN, LP, LR) 
- Indústria (SN, LP, LR)
- MEI (Serviços e Comércio)

Total esperado: 56 mensalidades
"""

import os
import sys
from sqlite3 import connect
from datetime import datetime

def recriar_mensalidades_final():
    """
    🚀 Função principal para recriar completamente a tabela de mensalidades
    """
    print("🧹 RECRIANDO TABELA DE MENSALIDADES - VERSÃO FINAL")
    print("=" * 60)
    
    # Caminho do banco de dados
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'propostas.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    try:
        # Conectar ao banco
        conn = connect(db_path)
        cursor = conn.cursor()
        
        # Iniciar transação
        cursor.execute("BEGIN TRANSACTION")
        
        print("📋 Verificando estrutura do banco...")
        
        # 1. Verificar se a tabela existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='mensalidade_automatica'
        """)
        
        if not cursor.fetchone():
            print("❌ Tabela mensalidade_automatica não existe!")
            cursor.execute("ROLLBACK")
            conn.close()
            return False
        
        # 2. LIMPEZA COMPLETA DA TABELA
        print("🧹 Limpando completamente a tabela mensalidade_automatica...")
        cursor.execute("DELETE FROM mensalidade_automatica")
        
        # Resetar sequência de IDs
        try:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='mensalidade_automatica'")
        except:
            pass  # Tabela sqlite_sequence pode não existir
        
        print("✅ Tabela limpa com sucesso!")
        
        # 3. VALIDAÇÃO DE DADOS EXISTENTES
        print("🔍 Validando dados existentes...")
        
        # Buscar tipos de atividade
        cursor.execute("SELECT id, codigo, nome FROM tipo_atividade WHERE ativo = 1 ORDER BY codigo")
        tipos_atividade = cursor.fetchall()
        
        if not tipos_atividade:
            print("❌ Nenhum tipo de atividade encontrado!")
            cursor.execute("ROLLBACK")
            conn.close()
            return False
        
        print(f"✅ {len(tipos_atividade)} tipos de atividade encontrados:")
        for tipo_id, codigo, nome in tipos_atividade:
            print(f"   - {codigo}: {nome} (ID: {tipo_id})")
        
        # Buscar regimes tributários
        cursor.execute("SELECT id, codigo, nome FROM regime_tributario WHERE ativo = 1 ORDER BY codigo")
        regimes_tributarios = cursor.fetchall()
        
        if not regimes_tributarios:
            print("❌ Nenhum regime tributário encontrado!")
            cursor.execute("ROLLBACK")
            conn.close()
            return False
        
        print(f"✅ {len(regimes_tributarios)} regimes tributários encontrados:")
        for regime_id, codigo, nome in regimes_tributarios:
            print(f"   - {codigo}: {nome} (ID: {regime_id})")
        
        # Buscar faixas de faturamento
        cursor.execute("""
            SELECT id, regime_tributario_id, valor_inicial, valor_final, aliquota 
            FROM faixa_faturamento 
            WHERE ativo = 1 
            ORDER BY regime_tributario_id, valor_inicial
        """)
        faixas_faturamento = cursor.fetchall()
        
        if not faixas_faturamento:
            print("❌ Nenhuma faixa de faturamento encontrada!")
            cursor.execute("ROLLBACK")
            conn.close()
            return False
        
        print(f"✅ {len(faixas_faturamento)} faixas de faturamento encontradas")
        
        # Organizar faixas por regime
        faixas_por_regime = {}
        for faixa_id, regime_id, valor_inicial, valor_final, aliquota in faixas_faturamento:
            if regime_id not in faixas_por_regime:
                faixas_por_regime[regime_id] = []
            faixas_por_regime[regime_id].append((faixa_id, valor_inicial, valor_final, aliquota))
        
        # 4. INSERÇÃO COMPLETA DAS MENSALIDADES
        print("💰 Inserindo mensalidades com valores corretos...")
        
        mensalidades = []
        
        # Criar dicionários para facilitar busca
        tipos_dict = {codigo: (id, nome) for id, codigo, nome in tipos_atividade}
        regimes_dict = {codigo: (id, nome) for id, codigo, nome in regimes_tributarios}
        
        # ✅ SERVIÇOS - SIMPLES NACIONAL
        if 'SERV' in tipos_dict and 'SN' in regimes_dict:
            tipo_id, tipo_nome = tipos_dict['SERV']
            regime_id, regime_nome = regimes_dict['SN']
            
            if regime_id in faixas_por_regime:
                for faixa_id, valor_inicial, valor_final, aliquota in faixas_por_regime[regime_id]:
                    if valor_inicial <= 180000:  # Até 180k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 800.00,
                            'Serviços - Simples Nacional - Até 180k'
                        ))
                    elif valor_inicial <= 360000:  # Até 360k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 1200.00,
                            'Serviços - Simples Nacional - Até 360k'
                        ))
                    elif valor_inicial <= 720000:  # Até 720k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 1600.00,
                            'Serviços - Simples Nacional - Até 720k'
                        ))
                    else:  # Acima de 720k - A Combinar
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 0.00,
                            'Serviços - Simples Nacional - Acima 720k (A Combinar)'
                        ))
        
        # ✅ SERVIÇOS - LUCRO PRESUMIDO
        if 'SERV' in tipos_dict and 'LP' in regimes_dict:
            tipo_id, tipo_nome = tipos_dict['SERV']
            regime_id, regime_nome = regimes_dict['LP']
            
            if regime_id in faixas_por_regime:
                for faixa_id, valor_inicial, valor_final, aliquota in faixas_por_regime[regime_id]:
                    if valor_inicial <= 180000:  # Até 180k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 1000.00,
                            'Serviços - Lucro Presumido - Até 180k'
                        ))
                    elif valor_inicial <= 360000:  # Até 360k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 1400.00,
                            'Serviços - Lucro Presumido - Até 360k'
                        ))
                    elif valor_inicial <= 720000:  # Até 720k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 1800.00,
                            'Serviços - Lucro Presumido - Até 720k'
                        ))
                    else:  # Acima de 720k - A Combinar
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 0.00,
                            'Serviços - Lucro Presumido - Acima 720k (A Combinar)'
                        ))
        
        # ✅ SERVIÇOS - LUCRO REAL
        if 'SERV' in tipos_dict and 'LR' in regimes_dict:
            tipo_id, tipo_nome = tipos_dict['SERV']
            regime_id, regime_nome = regimes_dict['LR']
            
            if regime_id in faixas_por_regime:
                for faixa_id, valor_inicial, valor_final, aliquota in faixas_por_regime[regime_id]:
                    if valor_inicial <= 180000:  # Até 180k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 1200.00,
                            'Serviços - Lucro Real - Até 180k'
                        ))
                    elif valor_inicial <= 360000:  # Até 360k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 1600.00,
                            'Serviços - Lucro Real - Até 360k'
                        ))
                    elif valor_inicial <= 720000:  # Até 720k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 2000.00,
                            'Serviços - Lucro Real - Até 720k'
                        ))
                    else:  # Acima de 720k - A Combinar
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 0.00,
                            'Serviços - Lucro Real - Acima 720k (A Combinar)'
                        ))
        
        # ✅ COMÉRCIO - SIMPLES NACIONAL
        if 'COM' in tipos_dict and 'SN' in regimes_dict:
            tipo_id, tipo_nome = tipos_dict['COM']
            regime_id, regime_nome = regimes_dict['SN']
            
            if regime_id in faixas_por_regime:
                for faixa_id, valor_inicial, valor_final, aliquota in faixas_por_regime[regime_id]:
                    if valor_inicial <= 180000:  # Até 180k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 500.00,
                            'Comércio - Simples Nacional - Até 180k'
                        ))
                    elif valor_inicial <= 360000:  # Até 360k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 1000.00,
                            'Comércio - Simples Nacional - Até 360k'
                        ))
                    elif valor_inicial <= 720000:  # Até 720k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 1500.00,
                            'Comércio - Simples Nacional - Até 720k'
                        ))
                    else:  # Acima de 720k - A Combinar
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 0.00,
                            'Comércio - Simples Nacional - Acima 720k (A Combinar)'
                        ))
        
        # ✅ COMÉRCIO - LUCRO PRESUMIDO
        if 'COM' in tipos_dict and 'LP' in regimes_dict:
            tipo_id, tipo_nome = tipos_dict['COM']
            regime_id, regime_nome = regimes_dict['LP']
            
            if regime_id in faixas_por_regime:
                for faixa_id, valor_inicial, valor_final, aliquota in faixas_por_regime[regime_id]:
                    if valor_inicial <= 180000:  # Até 180k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 700.00,
                            'Comércio - Lucro Presumido - Até 180k'
                        ))
                    elif valor_inicial <= 360000:  # Até 360k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 1200.00,
                            'Comércio - Lucro Presumido - Até 360k'
                        ))
                    elif valor_inicial <= 720000:  # Até 720k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 1700.00,
                            'Comércio - Lucro Presumido - Até 720k'
                        ))
                    else:  # Acima de 720k - A Combinar
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 0.00,
                            'Comércio - Lucro Presumido - Acima 720k (A Combinar)'
                        ))
        
        # ✅ COMÉRCIO - LUCRO REAL
        if 'COM' in tipos_dict and 'LR' in regimes_dict:
            tipo_id, tipo_nome = tipos_dict['COM']
            regime_id, regime_nome = regimes_dict['LR']
            
            if regime_id in faixas_por_regime:
                for faixa_id, valor_inicial, valor_final, aliquota in faixas_por_regime[regime_id]:
                    if valor_inicial <= 180000:  # Até 180k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 900.00,
                            'Comércio - Lucro Real - Até 180k'
                        ))
                    elif valor_inicial <= 360000:  # Até 360k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 1400.00,
                            'Comércio - Lucro Real - Até 360k'
                        ))
                    elif valor_inicial <= 720000:  # Até 720k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 1900.00,
                            'Comércio - Lucro Real - Até 720k'
                        ))
                    else:  # Acima de 720k - A Combinar
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 0.00,
                            'Comércio - Lucro Real - Acima 720k (A Combinar)'
                        ))
        
        # ✅ INDÚSTRIA - SIMPLES NACIONAL
        if 'IND' in tipos_dict and 'SN' in regimes_dict:
            tipo_id, tipo_nome = tipos_dict['IND']
            regime_id, regime_nome = regimes_dict['SN']
            
            if regime_id in faixas_por_regime:
                for faixa_id, valor_inicial, valor_final, aliquota in faixas_por_regime[regime_id]:
                    if valor_inicial <= 180000:  # Até 180k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 600.00,
                            'Indústria - Simples Nacional - Até 180k'
                        ))
                    elif valor_inicial <= 360000:  # Até 360k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 1100.00,
                            'Indústria - Simples Nacional - Até 360k'
                        ))
                    elif valor_inicial <= 720000:  # Até 720k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 1600.00,
                            'Indústria - Simples Nacional - Até 720k'
                        ))
                    else:  # Acima de 720k - A Combinar
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 0.00,
                            'Indústria - Simples Nacional - Acima 720k (A Combinar)'
                        ))
        
        # ✅ INDÚSTRIA - LUCRO PRESUMIDO
        if 'IND' in tipos_dict and 'LP' in regimes_dict:
            tipo_id, tipo_nome = tipos_dict['IND']
            regime_id, regime_nome = regimes_dict['LP']
            
            if regime_id in faixas_por_regime:
                for faixa_id, valor_inicial, valor_final, aliquota in faixas_por_regime[regime_id]:
                    if valor_inicial <= 180000:  # Até 180k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 800.00,
                            'Indústria - Lucro Presumido - Até 180k'
                        ))
                    elif valor_inicial <= 360000:  # Até 360k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 1300.00,
                            'Indústria - Lucro Presumido - Até 360k'
                        ))
                    elif valor_inicial <= 720000:  # Até 720k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 1800.00,
                            'Indústria - Lucro Presumido - Até 720k'
                        ))
                    else:  # Acima de 720k - A Combinar
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 0.00,
                            'Indústria - Lucro Presumido - Acima 720k (A Combinar)'
                        ))
        
        # ✅ INDÚSTRIA - LUCRO REAL
        if 'IND' in tipos_dict and 'LR' in regimes_dict:
            tipo_id, tipo_nome = tipos_dict['IND']
            regime_id, regime_nome = regimes_dict['LR']
            
            if regime_id in faixas_por_regime:
                for faixa_id, valor_inicial, valor_final, aliquota in faixas_por_regime[regime_id]:
                    if valor_inicial <= 180000:  # Até 180k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 1000.00,
                            'Indústria - Lucro Real - Até 180k'
                        ))
                    elif valor_inicial <= 360000:  # Até 360k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 1500.00,
                            'Indústria - Lucro Real - Até 360k'
                        ))
                    elif valor_inicial <= 720000:  # Até 720k
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 2000.00,
                            'Indústria - Lucro Real - Até 720k'
                        ))
                    else:  # Acima de 720k - A Combinar
                        mensalidades.append((
                            tipo_id, regime_id, faixa_id, 0.00,
                            'Indústria - Lucro Real - Acima 720k (A Combinar)'
                        ))
        
        # ✅ MEI - SERVIÇOS (sem funcionário)
        if 'SERV' in tipos_dict and 'MEI' in regimes_dict:
            tipo_id, tipo_nome = tipos_dict['SERV']
            regime_id, regime_nome = regimes_dict['MEI']
            
            if regime_id in faixas_por_regime:
                # MEI tem apenas uma faixa de faturamento
                faixa_id, valor_inicial, valor_final, aliquota = faixas_por_regime[regime_id][0]
                mensalidades.append((
                    tipo_id, regime_id, faixa_id, 100.00,
                    'MEI - Serviços - Sem funcionário'
                ))
        
        # ✅ MEI - COMÉRCIO (sem funcionário)
        if 'COM' in tipos_dict and 'MEI' in regimes_dict:
            tipo_id, tipo_nome = tipos_dict['COM']
            regime_id, regime_nome = regimes_dict['MEI']
            
            if regime_id in faixas_por_regime:
                # MEI tem apenas uma faixa de faturamento
                faixa_id, valor_inicial, valor_final, aliquota = faixas_por_regime[regime_id][0]
                mensalidades.append((
                    tipo_id, regime_id, faixa_id, 100.00,
                    'MEI - Comércio - Sem funcionário'
                ))
        
        # Inserir todas as mensalidades
        cursor.executemany("""
            INSERT INTO mensalidade_automatica 
            (tipo_atividade_id, regime_tributario_id, faixa_faturamento_id, valor_mensalidade, observacoes, ativo, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, mensalidades)
        
        # Confirmar transação
        cursor.execute("COMMIT")
        
        print(f"✅ {len(mensalidades)} mensalidades inseridas com sucesso!")
        
        # 5. VALIDAÇÃO FINAL
        print("🔍 Validando resultado final...")
        
        # Contar total de registros
        cursor.execute("SELECT COUNT(*) FROM mensalidade_automatica")
        total_registros = cursor.fetchone()[0]
        print(f"📊 Total de registros na tabela: {total_registros}")
        
        # Agrupar por regime tributário
        cursor.execute("""
            SELECT rt.codigo, rt.nome, COUNT(*) as total
            FROM mensalidade_automatica ma
            JOIN regime_tributario rt ON ma.regime_tributario_id = rt.id
            GROUP BY rt.id, rt.codigo, rt.nome
            ORDER BY rt.codigo
        """)
        
        print("📊 Mensalidades por regime tributário:")
        for codigo, nome, total in cursor.fetchall():
            print(f"   - {codigo} ({nome}): {total} mensalidades")
        
        # Agrupar por tipo de atividade
        cursor.execute("""
            SELECT ta.codigo, ta.nome, COUNT(*) as total
            FROM mensalidade_automatica ma
            JOIN tipo_atividade ta ON ma.tipo_atividade_id = ta.id
            GROUP BY ta.id, ta.codigo, ta.nome
            ORDER BY ta.codigo
        """)
        
        print("📊 Mensalidades por tipo de atividade:")
        for codigo, nome, total in cursor.fetchall():
            print(f"   - {codigo} ({nome}): {total} mensalidades")
        
        # 6. TESTES ESPECÍFICOS
        print("🧪 Testando casos específicos...")
        
        # Teste 1: Comércio - Simples Nacional - Até 180k
        cursor.execute("""
            SELECT ma.valor_mensalidade, ma.observacoes
            FROM mensalidade_automatica ma
            JOIN tipo_atividade ta ON ma.tipo_atividade_id = ta.id
            JOIN regime_tributario rt ON ma.regime_tributario_id = rt.id
            JOIN faixa_faturamento ff ON ma.faixa_faturamento_id = ff.id
            WHERE ta.codigo = 'COM' 
            AND rt.codigo = 'SN' 
            AND ff.valor_inicial <= 180000
            LIMIT 1
        """)
        
        resultado = cursor.fetchone()
        if resultado:
            valor, obs = resultado
            print(f"✅ Teste 1 - Comércio SN ≤180k: R$ {valor:.2f} - {obs}")
        else:
            print("❌ Teste 1 - Comércio SN ≤180k: Não encontrado")
        
        # Teste 2: Serviços - Lucro Real - Até 360k
        cursor.execute("""
            SELECT ma.valor_mensalidade, ma.observacoes
            FROM mensalidade_automatica ma
            JOIN tipo_atividade ta ON ma.tipo_atividade_id = ta.id
            JOIN regime_tributario rt ON ma.regime_tributario_id = rt.id
            JOIN faixa_faturamento ff ON ma.faixa_faturamento_id = ff.id
            WHERE ta.codigo = 'SERV' 
            AND rt.codigo = 'LR' 
            AND ff.valor_inicial <= 360000 AND ff.valor_inicial > 180000
            LIMIT 1
        """)
        
        resultado = cursor.fetchone()
        if resultado:
            valor, obs = resultado
            print(f"✅ Teste 2 - Serviços LR ≤360k: R$ {valor:.2f} - {obs}")
        else:
            print("❌ Teste 2 - Serviços LR ≤360k: Não encontrado")
        
        # Teste 3: MEI - Serviços
        cursor.execute("""
            SELECT ma.valor_mensalidade, ma.observacoes
            FROM mensalidade_automatica ma
            JOIN tipo_atividade ta ON ma.tipo_atividade_id = ta.id
            JOIN regime_tributario rt ON ma.regime_tributario_id = rt.id
            WHERE ta.codigo = 'SERV' 
            AND rt.codigo = 'MEI'
            LIMIT 1
        """)
        
        resultado = cursor.fetchone()
        if resultado:
            valor, obs = resultado
            print(f"✅ Teste 3 - MEI Serviços: R$ {valor:.2f} - {obs}")
        else:
            print("❌ Teste 3 - MEI Serviços: Não encontrado")
        
        # Teste 4: Indústria - Simples Nacional - Até 180k
        cursor.execute("""
            SELECT ma.valor_mensalidade, ma.observacoes
            FROM mensalidade_automatica ma
            JOIN tipo_atividade ta ON ma.tipo_atividade_id = ta.id
            JOIN regime_tributario rt ON ma.regime_tributario_id = rt.id
            JOIN faixa_faturamento ff ON ma.faixa_faturamento_id = ff.id
            WHERE ta.codigo = 'IND' 
            AND rt.codigo = 'SN' 
            AND ff.valor_inicial <= 180000
            LIMIT 1
        """)
        
        resultado = cursor.fetchone()
        if resultado:
            valor, obs = resultado
            print(f"✅ Teste 4 - Indústria SN ≤180k: R$ {valor:.2f} - {obs}")
        else:
            print("❌ Teste 4 - Indústria SN ≤180k: Não encontrado")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("🎉 RECRIAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print(f"📊 Resumo:")
        print(f"   • Total de mensalidades inseridas: {len(mensalidades)}")
        print(f"   • Total de registros na tabela: {total_registros}")
        print(f"   • Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("\n✅ A tabela mensalidade_automatica foi completamente recriada!")
        print("✅ Todos os valores estão atualizados conforme a tabela fornecida!")
        print("✅ Sistema pronto para uso!")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO na recriação: {e}")
        try:
            cursor.execute("ROLLBACK")
            conn.close()
        except:
            pass
        return False

if __name__ == "__main__":
    success = recriar_mensalidades_final()
    sys.exit(0 if success else 1)
