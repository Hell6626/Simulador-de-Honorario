#!/usr/bin/env python3
"""
🔍 SCRIPT: Verificar Mensalidades
================================
Verifica se as mensalidades foram criadas corretamente.
"""

import sqlite3
import os

def verificar_mensalidades():
    """
    Verifica as mensalidades no banco
    """
    print("🔍 VERIFICANDO MENSALIDADES...")
    
    # Caminho do banco
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'propostas.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Contar total
        cursor.execute("SELECT COUNT(*) FROM mensalidade_automatica")
        total = cursor.fetchone()[0]
        print(f"📊 Total de mensalidades: {total}")
        
        if total == 0:
            print("❌ Nenhuma mensalidade encontrada!")
            return
        
        # Buscar mensalidades com detalhes
        cursor.execute("""
            SELECT r.codigo, t.nome, f.valor_inicial, f.valor_final, m.valor_mensalidade
            FROM mensalidade_automatica m
            JOIN regime_tributario r ON m.regime_tributario_id = r.id
            JOIN tipo_atividade t ON m.tipo_atividade_id = t.id
            JOIN faixa_faturamento f ON m.faixa_faturamento_id = f.id
            ORDER BY r.codigo, t.nome, f.valor_inicial
        """)
        
        mensalidades = cursor.fetchall()
        
        # Agrupar por regime
        por_regime = {}
        for regime_codigo, tipo_nome, valor_min, valor_max, valor_mensal in mensalidades:
            if regime_codigo not in por_regime:
                por_regime[regime_codigo] = []
            por_regime[regime_codigo].append((tipo_nome, valor_min, valor_max, valor_mensal))
        
        # Mostrar detalhes
        for regime_codigo, mensalidades_regime in por_regime.items():
            print(f"\n📋 {regime_codigo} ({len(mensalidades_regime)} mensalidades):")
            for tipo_nome, valor_min, valor_max, valor_mensal in mensalidades_regime:
                valor_str = f"R$ {valor_mensal:,.2f}" if valor_mensal > 0 else "A combinar"
                print(f"   {tipo_nome}: R$ {valor_min:,.2f}-{valor_max:,.2f} = {valor_str}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")

if __name__ == "__main__":
    verificar_mensalidades()
