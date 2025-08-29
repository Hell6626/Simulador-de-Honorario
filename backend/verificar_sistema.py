#!/usr/bin/env python3
"""
Script para verificar se o sistema está funcionando corretamente
"""

from main import app
from models import (
    Funcionario, Cliente, TipoAtividade, RegimeTributario,
    FaixaFaturamento, Servico, Proposta, ItemProposta
)

def verificar_sistema():
    """Verifica se o sistema está funcionando corretamente"""
    with app.app_context():
        print("🔍 VERIFICANDO SISTEMA DE PROPOSTAS")
        print("=" * 50)
        
        # 1. Verificar funcionários
        print("\n👥 FUNCIONÁRIOS:")
        funcionarios = Funcionario.query.filter_by(ativo=True).all()
        if funcionarios:
            print(f"✅ {len(funcionarios)} funcionários encontrados")
            for func in funcionarios:
                print(f"  - {func.nome} ({func.email}) - Gerente: {'Sim' if func.gerente else 'Não'}")
        else:
            print("❌ Nenhum funcionário encontrado!")
            print("💡 Execute: python inicializar_sistema.py")
        
        # 2. Verificar clientes
        print("\n👤 CLIENTES:")
        clientes = Cliente.query.filter_by(ativo=True).all()
        if clientes:
            print(f"✅ {len(clientes)} clientes encontrados")
            for cliente in clientes[:3]:  # Mostrar apenas os 3 primeiros
                print(f"  - {cliente.nome} ({cliente.cpf})")
        else:
            print("❌ Nenhum cliente encontrado!")
            print("💡 Crie clientes através do frontend")
        
        # 3. Verificar tipos de atividade
        print("\n📋 TIPOS DE ATIVIDADE:")
        tipos = TipoAtividade.query.filter_by(ativo=True).all()
        if tipos:
            print(f"✅ {len(tipos)} tipos de atividade encontrados")
            for tipo in tipos:
                print(f"  - {tipo.nome} ({tipo.codigo})")
        else:
            print("❌ Nenhum tipo de atividade encontrado!")
            print("💡 Execute: python inicializar_sistema.py")
        
        # 4. Verificar regimes tributários
        print("\n💰 REGIMES TRIBUTÁRIOS:")
        regimes = RegimeTributario.query.filter_by(ativo=True).all()
        if regimes:
            print(f"✅ {len(regimes)} regimes tributários encontrados")
            for regime in regimes:
                print(f"  - {regime.nome} ({regime.codigo})")
        else:
            print("❌ Nenhum regime tributário encontrado!")
            print("💡 Execute: python inicializar_sistema.py")
        
        # 5. Verificar serviços
        print("\n🔧 SERVIÇOS:")
        servicos = Servico.query.filter_by(ativo=True).all()
        if servicos:
            print(f"✅ {len(servicos)} serviços encontrados")
            for servico in servicos[:3]:  # Mostrar apenas os 3 primeiros
                print(f"  - {servico.nome} (R$ {servico.valor_base:.2f})")
        else:
            print("❌ Nenhum serviço encontrado!")
            print("💡 Execute: python inicializar_sistema.py")
        
        # 6. Verificar propostas
        print("\n📄 PROPOSTAS:")
        propostas = Proposta.query.filter_by(ativo=True).all()
        if propostas:
            print(f"✅ {len(propostas)} propostas encontradas")
            for proposta in propostas:
                print(f"  - {proposta.numero} (R$ {proposta.valor_total:.2f}) - {proposta.status}")
        else:
            print("❌ Nenhuma proposta encontrada!")
            print("💡 Crie propostas através do frontend")
        
        # 7. Verificar autenticação
        print("\n🔐 AUTENTICAÇÃO:")
        admin = Funcionario.query.filter_by(email="admin@gmail.com").first()
        if admin:
            print("✅ Usuário admin encontrado")
            print(f"  - Email: admin@gmail.com")
            print(f"  - Senha: admin123")
            print("💡 Use estas credenciais para fazer login")
        else:
            print("❌ Usuário admin não encontrado!")
            print("💡 Execute: python inicializar_sistema.py")
        
        print("\n" + "=" * 50)
        print("🎯 PRÓXIMOS PASSOS:")
        print("1. Faça login com admin@gmail.com / admin123")
        print("2. Crie um cliente se não houver")
        print("3. Tente criar uma proposta")
        print("4. Verifique se aparece na lista")

if __name__ == "__main__":
    verificar_sistema()
