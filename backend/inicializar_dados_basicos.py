#!/usr/bin/env python3
"""
Script para inicializar dados básicos do sistema.
Cria empresas e cargos padrão para o funcionamento do sistema.
"""

import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import db, app
from models.organizacional import Empresa, Cargo
from datetime import datetime

def inicializar_empresas():
    """Inicializa empresas básicas do sistema"""
    print("Inicializando empresas...")
    
    # Verificar se já existem empresas
    if Empresa.query.first():
        print("Empresas já existem. Pulando inicialização.")
        return
    
    # Empresa principal
    empresa_principal = Empresa(
        nome="Empresa Principal",
        cnpj="12.345.678/0001-90",
        endereco="Rua Principal, 123 - Centro",
        telefone="(11) 1234-5678",
        email="contato@empresa.com",
        ativo=True
    )
    
    db.session.add(empresa_principal)
    db.session.commit()
    
    print(f"Empresa criada: {empresa_principal.nome} (ID: {empresa_principal.id})")

def inicializar_cargos():
    """Inicializa cargos básicos do sistema"""
    print("Inicializando cargos...")
    
    # Verificar se já existem cargos
    if Cargo.query.first():
        print("Cargos já existem. Pulando inicialização.")
        return
    
    # Buscar empresa principal
    empresa = Empresa.query.filter_by(cnpj="12.345.678/0001-90").first()
    if not empresa:
        print("Empresa principal não encontrada. Criando primeiro...")
        inicializar_empresas()
        empresa = Empresa.query.filter_by(cnpj="12.345.678/0001-90").first()
    
    # Cargos básicos
    cargos = [
        {
            'codigo': 'ADM',
            'nome': 'Administrador',
            'descricao': 'Administrador do sistema com acesso total',
            'nivel': 'Sênior',
            'empresa_id': empresa.id
        },
        {
            'codigo': 'GER',
            'nome': 'Gerente',
            'descricao': 'Gerente com acesso a gestão de funcionários',
            'nivel': 'Sênior',
            'empresa_id': empresa.id
        },
        {
            'codigo': 'CONT',
            'nome': 'Contador',
            'descricao': 'Contador responsável por propostas e clientes',
            'nivel': 'Pleno',
            'empresa_id': empresa.id
        },
        {
            'codigo': 'AUX',
            'nome': 'Auxiliar Contábil',
            'descricao': 'Auxiliar para tarefas básicas',
            'nivel': 'Júnior',
            'empresa_id': empresa.id
        }
    ]
    
    for cargo_data in cargos:
        cargo = Cargo(
            codigo=cargo_data['codigo'],
            nome=cargo_data['nome'],
            descricao=cargo_data['descricao'],
            nivel=cargo_data['nivel'],
            empresa_id=cargo_data['empresa_id'],
            ativo=True
        )
        db.session.add(cargo)
        print(f"Cargo criado: {cargo.nome} ({cargo.codigo})")
    
    db.session.commit()
    print("Cargos inicializados com sucesso!")

def main():
    """Função principal"""
    print("=== Inicialização de Dados Básicos ===")
    
    with app.app_context():
        try:
            # Inicializar empresas
            inicializar_empresas()
            
            # Inicializar cargos
            inicializar_cargos()
            
            print("\n✅ Inicialização concluída com sucesso!")
            print("\nDados criados:")
            print("- 1 Empresa")
            print("- 4 Cargos (ADM, GER, CONT, AUX)")
            
        except Exception as e:
            print(f"❌ Erro durante a inicialização: {e}")
            db.session.rollback()
            sys.exit(1)

if __name__ == "__main__":
    main()
