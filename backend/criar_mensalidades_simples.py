#!/usr/bin/env python3
"""
🎯 SCRIPT SIMPLES: Mensalidades Automáticas
===========================================
Cria mensalidades baseadas na tabela fornecida pelo usuário.
"""

import sqlite3
import os

def criar_mensalidades_simples():
    """
    Cria mensalidades usando SQL direto no banco
    """
    print("🎯 INICIANDO CRIAÇÃO SIMPLES DE MENSALIDADES...")
    
    # Caminho do banco
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'propostas.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    # Dados da tabela fornecida
    mensalidades_data = [
        # SIMPLES NACIONAL
        ('SN', 'Serviços', 0, 180000, 400.00),
        ('SN', 'Comércio', 0, 180000, 500.00),
        ('SN', 'Indústria', 0, 180000, 500.00),
        ('SN', 'Serviços', 180000.01, 360000, 800.00),
        ('SN', 'Comércio', 180000.01, 360000, 1000.00),
        ('SN', 'Indústria', 180000.01, 360000, 1000.00),
        ('SN', 'Serviços', 360000.01, 720000, 1200.00),
        ('SN', 'Comércio', 360000.01, 720000, 1500.00),
        ('SN', 'Indústria', 360000.01, 720000, 1500.00),
        # Acima de 720k = A combinar (valor 0)
        ('SN', 'Serviços', 720000.01, 1800000, 0.00),
        ('SN', 'Comércio', 720000.01, 1800000, 0.00),
        ('SN', 'Indústria', 720000.01, 1800000, 0.00),
        ('SN', 'Serviços', 1800000.01, 3600000, 0.00),
        ('SN', 'Comércio', 1800000.01, 3600000, 0.00),
        ('SN', 'Indústria', 1800000.01, 3600000, 0.00),
        ('SN', 'Serviços', 3600000.01, 4800000, 0.00),
        ('SN', 'Comércio', 3600000.01, 4800000, 0.00),
        ('SN', 'Indústria', 3600000.01, 4800000, 0.00),
        
        # LUCRO PRESUMIDO
        ('LP', 'Serviços', 0, 180000, 500.00),
        ('LP', 'Comércio', 0, 180000, 600.00),
        ('LP', 'Indústria', 0, 180000, 600.00),
        ('LP', 'Serviços', 180000.01, 360000, 900.00),
        ('LP', 'Comércio', 180000.01, 360000, 1100.00),
        ('LP', 'Indústria', 180000.01, 360000, 1100.00),
        ('LP', 'Serviços', 360000.01, 720000, 1300.00),
        ('LP', 'Comércio', 360000.01, 720000, 1500.00),
        ('LP', 'Indústria', 360000.01, 720000, 1500.00),
        # Acima de 720k = A combinar
        ('LP', 'Serviços', 720000.01, 1800000, 0.00),
        ('LP', 'Comércio', 720000.01, 1800000, 0.00),
        ('LP', 'Indústria', 720000.01, 1800000, 0.00),
        ('LP', 'Serviços', 1800000.01, 3600000, 0.00),
        ('LP', 'Comércio', 1800000.01, 3600000, 0.00),
        ('LP', 'Indústria', 1800000.01, 3600000, 0.00),
        ('LP', 'Serviços', 3600000.01, 4800000, 0.00),
        ('LP', 'Comércio', 3600000.01, 4800000, 0.00),
        ('LP', 'Indústria', 3600000.01, 4800000, 0.00),
        
        # LUCRO REAL
        ('LR', 'Serviços', 0, 180000, 1300.00),
        ('LR', 'Comércio', 0, 180000, 1300.00),
        ('LR', 'Indústria', 0, 180000, 1300.00),
        ('LR', 'Serviços', 180000.01, 360000, 1500.00),
        ('LR', 'Comércio', 180000.01, 360000, 1500.00),
        ('LR', 'Indústria', 180000.01, 360000, 1500.00),
        ('LR', 'Serviços', 360000.01, 720000, 2500.00),
        ('LR', 'Comércio', 360000.01, 720000, 2500.00),
        ('LR', 'Indústria', 360000.01, 720000, 2500.00),
        # Acima de 720k = A combinar
        ('LR', 'Serviços', 720000.01, 1800000, 0.00),
        ('LR', 'Comércio', 720000.01, 1800000, 0.00),
        ('LR', 'Indústria', 720000.01, 1800000, 0.00),
        ('LR', 'Serviços', 1800000.01, 3600000, 0.00),
        ('LR', 'Comércio', 1800000.01, 3600000, 0.00),
        ('LR', 'Indústria', 1800000.01, 3600000, 0.00),
        ('LR', 'Serviços', 3600000.01, 4800000, 0.00),
        ('LR', 'Comércio', 3600000.01, 4800000, 0.00),
        ('LR', 'Indústria', 3600000.01, 4800000, 0.00),
        
        # MEI
        ('MEI', 'Serviços', 0, 81000, 100.00),
        ('MEI', 'Comércio', 0, 81000, 100.00),
        ('MEI', 'Indústria', 0, 81000, 100.00),
    ]
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Limpar mensalidades existentes
        print("🧹 Limpando mensalidades existentes...")
        cursor.execute("DELETE FROM mensalidade_automatica")
        
        # Buscar IDs dos regimes e tipos
        print("📋 Buscando regimes e tipos...")
        
        # Regimes
        cursor.execute("SELECT id, codigo FROM regime_tributario")
        regimes = {codigo: id for id, codigo in cursor.fetchall()}
        print(f"Regimes encontrados: {list(regimes.keys())}")
        
        # Tipos de atividade
        cursor.execute("SELECT id, nome FROM tipo_atividade")
        tipos = {nome: id for id, nome in cursor.fetchall()}
        print(f"Tipos encontrados: {list(tipos.keys())}")
        
        # Criar mensalidades
        mensalidades_criadas = 0
        for regime_codigo, tipo_nome, valor_min, valor_max, valor_mensal in mensalidades_data:
            # Buscar IDs
            regime_id = regimes.get(regime_codigo)
            tipo_id = tipos.get(tipo_nome)
            
            if not regime_id:
                print(f"⚠️  Regime não encontrado: {regime_codigo}")
                continue
                
            if not tipo_id:
                print(f"⚠️  Tipo não encontrado: {tipo_nome}")
                continue
            
            # Buscar ou criar faixa de faturamento
            cursor.execute("""
                SELECT id FROM faixa_faturamento 
                WHERE regime_tributario_id = ? AND valor_inicial = ? AND valor_final = ?
            """, (regime_id, valor_min, valor_max))
            
            faixa = cursor.fetchone()
            if not faixa:
                cursor.execute("""
                    INSERT INTO faixa_faturamento (regime_tributario_id, valor_inicial, valor_final, aliquota, ativo, created_at, updated_at)
                    VALUES (?, ?, ?, 0.0, 1, datetime('now'), datetime('now'))
                """, (regime_id, valor_min, valor_max))
                faixa_id = cursor.lastrowid
            else:
                faixa_id = faixa[0]
            
            # Criar mensalidade
            cursor.execute("""
                INSERT INTO mensalidade_automatica 
                (tipo_atividade_id, regime_tributario_id, faixa_faturamento_id, valor_mensalidade, ativo, created_at, updated_at)
                VALUES (?, ?, ?, ?, 1, datetime('now'), datetime('now'))
            """, (tipo_id, regime_id, faixa_id, valor_mensal))
            
            mensalidades_criadas += 1
            valor_str = f"R$ {valor_mensal:,.2f}" if valor_mensal > 0 else "A combinar"
            print(f"✅ {regime_codigo} + {tipo_nome} + R$ {valor_min:,.2f}-{valor_max:,.2f} = {valor_str}")
        
        # Commit
        conn.commit()
        
        print(f"\n🎉 SUCESSO! {mensalidades_criadas} mensalidades criadas!")
        
        # Verificar resultado
        cursor.execute("SELECT COUNT(*) FROM mensalidade_automatica")
        total = cursor.fetchone()[0]
        print(f"📊 Total de mensalidades no banco: {total}")
        
        # Mostrar resumo por regime
        for regime_codigo in ['SN', 'LP', 'LR', 'MEI']:
            regime_id = regimes.get(regime_codigo)
            if regime_id:
                cursor.execute("SELECT COUNT(*) FROM mensalidade_automatica WHERE regime_tributario_id = ?", (regime_id,))
                count = cursor.fetchone()[0]
                print(f"   {regime_codigo}: {count} mensalidades")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    print("🚀 EXECUTANDO SCRIPT SIMPLES DE MENSALIDADES...")
    criar_mensalidades_simples()
    print("\n✅ SCRIPT CONCLUÍDO!")
