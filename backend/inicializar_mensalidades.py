#!/usr/bin/env python3
"""
Script para inicializar o sistema de mensalidades automáticas.
Executa a migração do banco de dados e inicializa os dados.
"""

import sys
import os

# Adicionar o diretório backend ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import create_app, db
from models.initialization import inicializar_mensalidades_automaticas
from flask_migrate import upgrade

def main():
    """Função principal para inicializar mensalidades"""
    print("🚀 INICIALIZANDO SISTEMA DE MENSALIDADES AUTOMÁTICAS")
    print("=" * 60)
    
    # Criar aplicação Flask
    app = create_app()
    
    with app.app_context():
        try:
            # 1. Executar migração do banco de dados
            print("\n📋 Executando migração do banco de dados...")
            upgrade()
            print("✅ Migração executada com sucesso!")
            
            # 2. Inicializar dados das mensalidades
            print("\n💰 Inicializando dados das mensalidades...")
            if inicializar_mensalidades_automaticas():
                print("✅ Dados das mensalidades inicializados com sucesso!")
            else:
                print("❌ Falha ao inicializar dados das mensalidades")
                return False
            
            print("\n" + "=" * 60)
            print("🎉 SISTEMA DE MENSALIDADES INICIALIZADO COM SUCESSO!")
            print("\n📋 Funcionalidades disponíveis:")
            print("  • Mensalidade automática baseada em configuração tributária")
            print("  • Valores fixos por tipo de atividade e regime")
            print("  • Suporte a casos especiais (MEI, Pessoa Física)")
            print("  • Integração automática no Passo 4 - Revisão")
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERRO na inicialização: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
