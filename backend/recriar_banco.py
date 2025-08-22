#!/usr/bin/env python3
"""
Script para recriar o banco de dados do zero
- Remove o banco atual
- Cria novas tabelas
- Inicializa dados básicos
- Cria usuário administrador
"""

import os
import shutil
from datetime import datetime
from config import create_app, db
from models import *
from models.initialization import inicializar_sistema_completo

def backup_banco_atual():
    """Faz backup do banco atual se existir"""
    db_path = 'instance/propostas.db'
    
    if os.path.exists(db_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f'instance/propostas_backup_{timestamp}.db'
        
        try:
            shutil.copy2(db_path, backup_path)
            print(f"✅ Backup criado: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"⚠️  Erro ao criar backup: {e}")
            return None
    else:
        print("ℹ️  Nenhum banco existente para backup")
        return None

def remover_banco_atual():
    """Remove o banco de dados atual"""
    db_path = 'instance/propostas.db'
    
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"🗑️  Banco removido: {db_path}")
            return True
        except Exception as e:
            print(f"❌ Erro ao remover banco: {e}")
            return False
    else:
        print("ℹ️  Banco não existe, prosseguindo...")
        return True

def criar_tabelas():
    """Cria todas as tabelas do banco de dados"""
    print("\n📋 Criando tabelas...")
    
    try:
        with app.app_context():
            # Criar todas as tabelas
            db.create_all()
            print("✅ Todas as tabelas criadas com sucesso!")
            return True
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

def verificar_sistema():
    """Verifica se o sistema foi inicializado corretamente"""
    print("\n🔍 Verificando sistema...")
    
    try:
        with app.app_context():
            # Contar registros
            counts = {
                'empresas': Empresa.query.count(),
                'cargos': Cargo.query.count(),
                'funcionarios': Funcionario.query.count(),
                'tipos_atividade': TipoAtividade.query.count(),
                'regimes_tributarios': RegimeTributario.query.count(),
                'faixas_faturamento': FaixaFaturamento.query.count(),
                'servicos': Servico.query.count()
            }
            
            print("📊 Contagem de registros:")
            for tabela, count in counts.items():
                print(f"  - {tabela}: {count}")
            
            # Verificar usuário admin
            admin = Funcionario.query.filter_by(email="admin@admin.com").first()
            if admin:
                print(f"\n✅ Usuário admin encontrado:")
                print(f"  - Nome: {admin.nome}")
                print(f"  - Email: {admin.email}")
                print(f"  - Gerente: {'Sim' if admin.gerente else 'Não'}")
                print(f"  - Cargo: {admin.cargo.nome}")
                print(f"  - Empresa: {admin.empresa.nome}")
            else:
                print("\n❌ Usuário admin não encontrado!")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao verificar sistema: {e}")
        return False

def main():
    """Função principal"""
    print("🔄 RECRIANDO BANCO DE DADOS")
    print("=" * 50)
    
    try:
        # 1. Backup do banco atual
        backup_banco_atual()
        
        # 2. Remover banco atual
        if not remover_banco_atual():
            print("❌ Não foi possível remover o banco atual")
            return False
        
        # 3. Criar tabelas
        if not criar_tabelas():
            print("❌ Falha ao criar tabelas")
            return False
        
        # 4. Inicializar sistema completo
        with app.app_context():
            if not inicializar_sistema_completo():
                print("❌ Falha ao inicializar sistema")
                return False
        
        # 5. Verificar sistema
        if not verificar_sistema():
            print("❌ Falha na verificação do sistema")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 BANCO DE DADOS RECRIADO COM SUCESSO!")
        print("\n📋 Credenciais de acesso:")
        print("  📧 Email: admin@admin.com")
        print("  🔐 Senha: admin123")
        print("\n🌐 Para testar:")
        print("  1. Execute: python main.py")
        print("  2. Acesse: http://localhost:5000/api/health/health")
        print("  3. Faça login com as credenciais acima")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO na recriação: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Criar aplicação
    app = create_app()
    
    # Executar
    success = main()
    
    if success:
        print("\n✅ Processo concluído com sucesso!")
    else:
        print("\n❌ Processo falhou!")
        exit(1)
