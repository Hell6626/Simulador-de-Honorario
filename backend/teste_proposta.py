#!/usr/bin/env python3
"""
Script para testar se a proposta está sendo salva corretamente
"""

from main import app
from models import Proposta, Cliente, Funcionario, TipoAtividade, RegimeTributario, Servico

def testar_proposta():
    """Testa se a proposta está sendo salva corretamente"""
    with app.app_context():
        print("🧪 TESTANDO SISTEMA DE PROPOSTAS")
        print("=" * 50)
        
        # 1. Verificar se há dados básicos
        print("\n📋 DADOS BÁSICOS:")
        
        funcionarios = Funcionario.query.filter_by(ativo=True).all()
        print(f"✅ {len(funcionarios)} funcionários encontrados")
        
        clientes = Cliente.query.filter_by(ativo=True).all()
        print(f"✅ {len(clientes)} clientes encontrados")
        
        tipos = TipoAtividade.query.filter_by(ativo=True).all()
        print(f"✅ {len(tipos)} tipos de atividade encontrados")
        
        regimes = RegimeTributario.query.filter_by(ativo=True).all()
        print(f"✅ {len(regimes)} regimes tributários encontrados")
        
        servicos = Servico.query.filter_by(ativo=True).all()
        print(f"✅ {len(servicos)} serviços encontrados")
        
        # 2. Verificar propostas existentes
        print("\n📄 PROPOSTAS EXISTENTES:")
        propostas = Proposta.query.filter_by(ativo=True).all()
        if propostas:
            print(f"✅ {len(propostas)} propostas encontradas")
            for proposta in propostas:
                print(f"  - {proposta.numero} (R$ {proposta.valor_total:.2f}) - {proposta.status}")
                print(f"    Cliente: {proposta.cliente.nome if proposta.cliente else 'N/A'}")
                print(f"    Funcionário: {proposta.funcionario_responsavel.nome if proposta.funcionario_responsavel else 'N/A'}")
                print(f"    Itens: {len(proposta.itens)}")
        else:
            print("❌ Nenhuma proposta encontrada!")
            print("💡 Crie propostas através do frontend")
        
        # 3. Testar criação de proposta
        if clientes and funcionarios and tipos and regimes and servicos:
            print("\n🧪 TESTE DE CRIAÇÃO DE PROPOSTA:")
            try:
                # Criar proposta de teste
                proposta_teste = Proposta(
                    numero="TESTE-001",
                    cliente_id=clientes[0].id,
                    funcionario_responsavel_id=funcionarios[0].id,
                    tipo_atividade_id=tipos[0].id,
                    regime_tributario_id=regimes[0].id,
                    valor_total=1000.00,
                    status="RASCUNHO"
                )
                
                from config import db
                db.session.add(proposta_teste)
                db.session.commit()
                
                print("✅ Proposta de teste criada com sucesso!")
                print(f"  - ID: {proposta_teste.id}")
                print(f"  - Número: {proposta_teste.numero}")
                print(f"  - Valor: R$ {proposta_teste.valor_total:.2f}")
                
                # Limpar proposta de teste
                db.session.delete(proposta_teste)
                db.session.commit()
                print("✅ Proposta de teste removida")
                
            except Exception as e:
                print(f"❌ Erro ao criar proposta de teste: {e}")
        else:
            print("❌ Dados insuficientes para teste")
        
        print("\n" + "=" * 50)
        print("🎯 PRÓXIMOS PASSOS:")
        print("1. Faça login com admin@gmail.com / admin123")
        print("2. Crie uma proposta através do frontend")
        print("3. Verifique se aparece na lista")
        print("4. Execute este script novamente para verificar")

if __name__ == "__main__":
    testar_proposta()
