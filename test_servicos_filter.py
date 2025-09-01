#!/usr/bin/env python3
"""
Script para testar o filtro cascata de serviços
"""

import requests
import json

def test_servicos_filter():
    base_url = "http://localhost:5000"
    
    try:
        # 1. Testar login para obter token
        print("🔍 Testando login...")
        login_data = {
            "email": "admin@example.com",
            "senha": "admin123"
        }
        
        login_response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.status_code}")
            print(f"Resposta: {login_response.text}")
            return
        
        token = login_response.json().get('token')
        if not token:
            print("❌ Token não encontrado na resposta")
            return
        
        print(f"✅ Login realizado com sucesso. Token: {token[:20]}...")
        
        # 2. Testar endpoint de tipos de atividade
        print("\n🔍 Testando tipos de atividade...")
        headers = {"Authorization": f"Bearer {token}"}
        
        tipos_response = requests.get(f"{base_url}/api/tipos-atividade", headers=headers)
        
        if tipos_response.status_code == 200:
            tipos = tipos_response.json()
            print(f"✅ Tipos de atividade carregados: {len(tipos)} tipos")
            for tipo in tipos[:3]:  # Mostrar apenas os 3 primeiros
                print(f"  - ID: {tipo.get('id')}, Código: {tipo.get('codigo')}, Nome: {tipo.get('nome')}")
        else:
            print(f"❌ Erro ao carregar tipos de atividade: {tipos_response.status_code}")
            return
        
        # 3. Testar endpoint de regimes tributários com primeiro tipo de atividade
        if tipos:
            primeiro_tipo_id = tipos[0].get('id')
            print(f"\n🔍 Testando regimes tributários para tipo de atividade ID: {primeiro_tipo_id}")
            
            regimes_response = requests.get(
                f"{base_url}/api/servicos/regimes-tributarios?tipo_atividade_id={primeiro_tipo_id}", 
                headers=headers
            )
            
            if regimes_response.status_code == 200:
                regimes = regimes_response.json()
                print(f"✅ Regimes tributários carregados: {len(regimes)} regimes")
                for regime in regimes:
                    print(f"  - ID: {regime.get('id')}, Código: {regime.get('codigo')}, Nome: {regime.get('nome')}")
            else:
                print(f"❌ Erro ao carregar regimes tributários: {regimes_response.status_code}")
                print(f"Resposta: {regimes_response.text}")
        
        # 4. Testar endpoint de serviços
        print("\n🔍 Testando serviços...")
        servicos_response = requests.get(f"{base_url}/api/servicos", headers=headers)
        
        if servicos_response.status_code == 200:
            servicos = servicos_response.json()
            print(f"✅ Serviços carregados: {len(servicos.get('items', []))} serviços")
        else:
            print(f"❌ Erro ao carregar serviços: {servicos_response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor. Certifique-se de que o backend está rodando em http://localhost:5000")
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado: {e}")

if __name__ == '__main__':
    test_servicos_filter()
