#!/usr/bin/env python3
"""
Script para inicializar o sistema do zero
- Cria todas as tabelas
- Insere dados básicos
- Cria usuário administrador
"""

from config import create_app, db
from models import *
from models.servicos import ServicoRegime
from models.initialization import inicializar_dados_basicos, inicializar_faixas_faturamento, inicializar_relacionamentos_atividade_regime, inicializar_relacionamentos_servico_regime
from werkzeug.security import generate_password_hash
from datetime import datetime

def criar_tabelas():
    """Cria todas as tabelas do banco de dados"""
    print("📋 Criando tabelas...")
    
    with app.app_context():
        # Criar todas as tabelas
        db.create_all()
        print("✅ Todas as tabelas criadas com sucesso!")

def criar_usuario_admin():
    """Cria o usuário administrador padrão"""
    print("\n👤 Criando usuário administrador...")
    
    with app.app_context():
        # Verificar se já existe algum usuário
        if Funcionario.query.count() > 0:
            print("ℹ️  Usuários já existem no sistema")
            return
        
        # Criar empresa padrão
        empresa = Empresa(
            nome="Empresa Admin",
            cnpj="00.000.000/0001-00",
            endereco="Endereço Padrão, 123",
            telefone="(11) 99999-9999",
            email="admin@empresa.com.br"
        )
        db.session.add(empresa)
        db.session.flush()  # Para obter o ID
        
        # Criar cargo administrador
        cargo = Cargo(
            codigo="ADMIN",
            nome="Administrador",
            descricao="Cargo de administrador do sistema",
            nivel="Sênior",
            empresa_id=empresa.id
        )
        db.session.add(cargo)
        db.session.flush()  # Para obter o ID
        
        # Criar usuário administrador
        admin = Funcionario(
            nome="Administrador",
            email="admin@gmail.com",
            senha_hash=generate_password_hash("admin123"),
            gerente=True,
            cargo_id=cargo.id,
            empresa_id=empresa.id
        )
        db.session.add(admin)
        
        # Salvar tudo
        db.session.commit()
        
        print(f"✅ Usuário administrador criado!")
        print(f"📧 Email: admin@gmail.com")
        print(f"🔐 Senha: admin123")

def inicializar_dados():
    """Inicializa os dados básicos do sistema"""
    print("\n📊 Inicializando dados básicos...")
    
    with app.app_context():
        # Inicializar tipos de atividade, regimes tributários e serviços
        inicializar_dados_basicos()
        print("✅ Dados básicos inicializados!")
        
        # Inicializar relacionamentos atividade x regime
        inicializar_relacionamentos_atividade_regime()
        print("✅ Relacionamentos atividade x regime inicializados!")
        
        # Inicializar faixas de faturamento
        inicializar_faixas_faturamento()
        print("✅ Faixas de faturamento inicializadas!")
        
        # Inicializar relacionamentos serviço x regime
        inicializar_relacionamentos_servico_regime()
        print("✅ Relacionamentos serviço x regime inicializados!")

def verificar_sistema():
    """Verifica se o sistema foi inicializado corretamente"""
    print("\n🔍 Verificando sistema...")
    
    with app.app_context():
        # Contar registros
        counts = {
            'empresas': Empresa.query.count(),
            'cargos': Cargo.query.count(),
            'funcionarios': Funcionario.query.count(),
            'tipos_atividade': TipoAtividade.query.count(),
            'regimes_tributarios': RegimeTributario.query.count(),
            'atividades_regime': AtividadeRegime.query.count(),
            'faixas_faturamento': FaixaFaturamento.query.count(),
            'servicos': Servico.query.count(),
            'servico_regime': ServicoRegime.query.count()
        }
        
        print("📊 Contagem de registros:")
        for tabela, count in counts.items():
            print(f"  - {tabela}: {count}")
        
        # Verificar relacionamentos específicos
        print("\n🔗 Verificando relacionamentos:")
        for atividade in TipoAtividade.query.all():
            regimes = AtividadeRegime.query.filter_by(tipo_atividade_id=atividade.id).all()
            regime_nomes = [rel.regime_tributario.nome for rel in regimes if rel.regime_tributario]
            print(f"  - {atividade.nome}: {', '.join(regime_nomes) if regime_nomes else 'Nenhum regime'}")
        
        # Verificar usuário admin
        admin = Funcionario.query.filter_by(email="admin@gmail.com").first()
        if admin:
            print(f"\n✅ Usuário admin encontrado:")
            print(f"  - Nome: {admin.nome}")
            print(f"  - Email: {admin.email}")
            print(f"  - Gerente: {'Sim' if admin.gerente else 'Não'}")
            print(f"  - Cargo: {admin.cargo.nome}")
            print(f"  - Empresa: {admin.empresa.nome}")
        else:
            print("\n❌ Usuário admin não encontrado!")

def main():
    """Função principal"""
    print("🚀 INICIALIZANDO SISTEMA COMPLETO")
    print("=" * 50)
    
    try:
        # 1. Criar tabelas
        criar_tabelas()
        
        # 2. Inicializar dados básicos
        inicializar_dados()
        
        # 3. Criar usuário administrador
        criar_usuario_admin()
        
        # 4. Verificar sistema
        verificar_sistema()
        
        print("\n" + "=" * 50)
        print("🎉 SISTEMA INICIALIZADO COM SUCESSO!")
        print("\n📋 Credenciais de acesso:")
        print("  📧 Email: admin@gmail.com")
        print("  🔐 Senha: admin123")
        print("\n🌐 Para testar:")
        print("  1. Execute: python main.py")
        print("  2. Acesse: http://localhost:5000/api/health/health")
        print("  3. Faça login com as credenciais acima")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO na inicialização: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Criar aplicação
    app = create_app()
    
    # Executar inicialização
    success = main()
    
    if success:
        exit(0)
    else:
        exit(1)
