#!/usr/bin/env python3
"""
Script para testar a API de regimes tributários
"""

import requests
import json

def test_api():
    base_url = "http://localhost:5000"
    
    try:
        # Testar endpoint de regimes tributários
        print("🔍 Testando API de regimes tributários...")
        response = requests.get(f"{base_url}/api/regimes-tributarios?page=1&per_page=10&ativo=true")
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Resposta: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"Erro: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor. Verifique se está rodando na porta 5000.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_api()
