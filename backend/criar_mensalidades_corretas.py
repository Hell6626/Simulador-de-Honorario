#!/usr/bin/env python3
"""
🎯 SCRIPT CORRIGIDO: Mensalidades Automáticas
============================================
Baseado na tabela fornecida pelo usuário:
- Simples Nacional: Serviço, Comércio, Indústria
- Lucro Presumido: Serviço, Comércio, Indústria  
- Lucro Real: Serviço, Comércio, Indústria
- MEI: Serviço, Comércio, Indústria
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import create_app, db
from models.tributario import MensalidadeAutomatica, RegimeTributario, TipoAtividade, FaixaFaturamento

def criar_mensalidades_corretas():
    """
    Cria mensalidades baseadas na tabela exata fornecida
    """
    print("🎯 INICIANDO CRIAÇÃO DE MENSALIDADES CORRETAS...")
    
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
    
    app = create_app()
    
    with app.app_context():
        try:
            # Limpar mensalidades existentes
            print("🧹 Limpando mensalidades existentes...")
            MensalidadeAutomatica.query.delete()
            db.session.commit()
            
            # Buscar regimes tributários
            regimes = {r.codigo: r for r in RegimeTributario.query.all()}
            print(f"📋 Regimes encontrados: {list(regimes.keys())}")
            
            # Buscar tipos de atividade
            tipos = {t.nome: t for t in TipoAtividade.query.all()}
            print(f"📋 Tipos encontrados: {list(tipos.keys())}")
            
            # Criar faixas de faturamento se não existirem
            faixas = {}
            for regime_codigo, tipo_nome, valor_min, valor_max, valor_mensal in mensalidades_data:
                # Criar faixa se não existir
                faixa_key = f"{regime_codigo}_{valor_min}_{valor_max}"
                if faixa_key not in faixas:
                    faixa = FaixaFaturamento.query.filter_by(
                        valor_inicial=valor_min,
                        valor_final=valor_max
                    ).first()
                    
                    if not faixa:
                        faixa = FaixaFaturamento(
                            regime_tributario_id=regime.id,
                            valor_inicial=valor_min,
                            valor_final=valor_max,
                            aliquota=0.0  # Não usado para mensalidades
                        )
                        db.session.add(faixa)
                        db.session.flush()  # Para obter o ID
                    
                    faixas[faixa_key] = faixa
            
            # Commit das faixas
            db.session.commit()
            
            # Criar mensalidades
            mensalidades_criadas = 0
            for regime_codigo, tipo_nome, valor_min, valor_max, valor_mensal in mensalidades_data:
                # Buscar regime
                regime = regimes.get(regime_codigo)
                if not regime:
                    print(f"⚠️  Regime não encontrado: {regime_codigo}")
                    continue
                
                # Buscar tipo de atividade
                tipo = tipos.get(tipo_nome)
                if not tipo:
                    print(f"⚠️  Tipo não encontrado: {tipo_nome}")
                    continue
                
                # Buscar faixa
                faixa_key = f"{regime_codigo}_{valor_min}_{valor_max}"
                faixa = faixas.get(faixa_key)
                if not faixa:
                    print(f"⚠️  Faixa não encontrada: {faixa_key}")
                    continue
                
                # Criar mensalidade
                mensalidade = MensalidadeAutomatica(
                    regime_tributario_id=regime.id,
                    tipo_atividade_id=tipo.id,
                    faixa_faturamento_id=faixa.id,
                    valor_mensalidade=valor_mensal,
                    ativo=True
                )
                
                db.session.add(mensalidade)
                mensalidades_criadas += 1
                
                print(f"✅ {regime_codigo} + {tipo_nome} + R$ {valor_min:,.2f}-{valor_max:,.2f} = R$ {valor_mensal:,.2f}")
            
            # Commit final
            db.session.commit()
            
            print(f"\n🎉 SUCESSO! {mensalidades_criadas} mensalidades criadas!")
            
            # Verificar resultado
            total_mensalidades = MensalidadeAutomatica.query.count()
            print(f"📊 Total de mensalidades no banco: {total_mensalidades}")
            
            # Mostrar resumo por regime
            for regime_codigo in ['SN', 'LP', 'LR', 'MEI']:
                regime = regimes.get(regime_codigo)
                if regime:
                    count = MensalidadeAutomatica.query.filter_by(regime_tributario_id=regime.id).count()
                    print(f"   {regime_codigo}: {count} mensalidades")
            
        except Exception as e:
            print(f"❌ ERRO: {str(e)}")
            db.session.rollback()
            raise

def verificar_mensalidades():
    """
    Verifica se as mensalidades foram criadas corretamente
    """
    print("\n🔍 VERIFICANDO MENSALIDADES...")
    
    app = create_app()
    
    with app.app_context():
        # Buscar todas as mensalidades
        mensalidades = MensalidadeAutomatica.query.join(RegimeTributario).join(TipoAtividade).join(FaixaFaturamento).all()
        
        print(f"📊 Total: {len(mensalidades)} mensalidades")
        
        # Agrupar por regime
        por_regime = {}
        for m in mensalidades:
            regime_codigo = m.regime_tributario.codigo
            if regime_codigo not in por_regime:
                por_regime[regime_codigo] = []
            por_regime[regime_codigo].append(m)
        
        # Mostrar detalhes
        for regime_codigo, mensalidades_regime in por_regime.items():
            print(f"\n📋 {regime_codigo} ({len(mensalidades_regime)} mensalidades):")
            for m in sorted(mensalidades_regime, key=lambda x: (x.tipo_atividade.nome, x.faixa_faturamento.valor_inicial)):
                valor_str = f"R$ {m.valor_mensalidade:,.2f}" if m.valor_mensalidade > 0 else "A combinar"
                print(f"   {m.tipo_atividade.nome}: R$ {m.faixa_faturamento.valor_inicial:,.2f}-{m.faixa_faturamento.valor_final:,.2f} = {valor_str}")

if __name__ == "__main__":
    print("🚀 EXECUTANDO SCRIPT DE MENSALIDADES CORRETAS...")
    criar_mensalidades_corretas()
    verificar_mensalidades()
    print("\n✅ SCRIPT CONCLUÍDO!")
