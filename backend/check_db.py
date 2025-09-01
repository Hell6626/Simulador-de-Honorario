#!/usr/bin/env python3
"""
Script para verificar dados no banco de dados
"""

from config import create_app
from models import RegimeTributario

def check_database():
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar regimes tributários
            regimes = RegimeTributario.query.all()
            print(f"Total de regimes tributários: {len(regimes)}")
            
            if regimes:
                print("\nRegimes encontrados:")
                for regime in regimes:
                    print(f"- ID: {regime.id}, Nome: {regime.nome}, Código: {regime.codigo}, Ativo: {regime.ativo}")
            else:
                print("Nenhum regime tributário encontrado no banco!")
                
        except Exception as e:
            print(f"Erro ao verificar banco: {e}")

if __name__ == "__main__":
    check_database()
