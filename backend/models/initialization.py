"""
Funções para inicialização de dados básicos do sistema.
"""

from config import db
from .tributario import TipoAtividade, RegimeTributario, FaixaFaturamento
from .servicos import Servico
from .organizacional import Empresa, Cargo, Funcionario
from werkzeug.security import generate_password_hash


def inicializar_dados_basicos():
    """Inicializa dados básicos do sistema"""
    
    # Tipos de Atividade
    tipos_atividade = [
        {
            'codigo': 'SERV',
            'nome': 'Serviços',
            'aplicavel_pf': False,
            'aplicavel_pj': True
        },
        {
            'codigo': 'COM',
            'nome': 'Comércio',
            'aplicavel_pf': False,
            'aplicavel_pj': True
        },
        {
            'codigo': 'IND',
            'nome': 'Indústria',
            'aplicavel_pf': False,
            'aplicavel_pj': True
        },
        {
            'codigo': 'PF',
            'nome': 'Pessoa Física',
            'aplicavel_pf': True,
            'aplicavel_pj': False
        }
    ]
    
    # Regimes Tributários
    regimes_tributarios = [
        {
            'codigo': 'SN',
            'nome': 'Simples Nacional',
            'descricao': 'Regime tributário simplificado para pequenas empresas',
            'aplicavel_pf': False,
            'aplicavel_pj': True
        },
        {
            'codigo': 'LP',
            'nome': 'Lucro Presumido',
            'descricao': 'Regime tributário baseado em presunção de lucro',
            'aplicavel_pf': False,
            'aplicavel_pj': True
        },
        {
            'codigo': 'LR',
            'nome': 'Lucro Real',
            'descricao': 'Regime tributário baseado no lucro real',
            'aplicavel_pf': False,
            'aplicavel_pj': True
        },
        {
            'codigo': 'MEI',
            'nome': 'Microempreendedor Individual',
            'descricao': 'Regime para microempreendedores individuais',
            'aplicavel_pf': False,
            'aplicavel_pj': True
        },
        {
            'codigo': 'PR',
            'nome': 'Produtor Rural',
            'descricao': 'Regime para produtores rurais',
            'aplicavel_pf': True,
            'aplicavel_pj': False
        },
        {
            'codigo': 'Aut',
            'nome': 'Autônomo',
            'descricao': 'Regime para autônomos',
            'aplicavel_pf': True,
            'aplicavel_pj': False
        },
        {
            'codigo': 'DOM',
            'nome': 'Empregador Doméstico',
            'descricao': 'Regime para empregador doméstico',
            'aplicavel_pf': True,
            'aplicavel_pj': False
        }
    ]
    
    # Serviços
    servicos = [
        {
            'codigo': 'BALANCETE-SN',
            'nome': 'Geração de Balancete Mensal para Simples Nacional',
            'categoria': 'CONTABIL',
            'tipo_cobranca': 'MENSAL',
            'valor_base': 50.00,
            'descricao': 'Serviços de geração balancete completa para Simples Nacional'
        },
        {
            'codigo': 'BALANCETE-LP-LR',
            'nome': 'Geração de Balancete Mensal para Lucro Presumido e Lucro Real',
            'categoria': 'CONTABIL',
            'tipo_cobranca': 'MENSAL',
            'valor_base': 100.00,
            'descricao': 'Serviços de geração balancete completa para LP e LR'
        },
        {
            'codigo': 'NF-e',
            'nome': 'Nota Fiscal Eletrônica',
            'categoria': 'FISCAL',
            'tipo_cobranca': 'POR_NF',
            'valor_base': 20.00,
            'descricao': 'Emissão de Nota Fiscal Eletrônica'
        },
        {
            'codigo': 'NFS-e',
            'nome': 'Nota Fiscal de Serviços Eletrônica',
            'categoria': 'FISCAL',
            'tipo_cobranca': 'POR_NF',
            'valor_base': 10.00,
            'descricao': 'Emissão de Nota Fiscal de Serviços'
        },
        {
            'codigo': 'CT-e',
            'nome': 'Conhecimento de Transporte Eletrônico',
            'categoria': 'FISCAL',
            'tipo_cobranca': 'POR_NF',
            'valor_base': 20.00,
            'descricao': 'Emissão de Conhecimento de Transporte Eletrônico'
        },
        {
            'codigo': 'FUNCIONARIO',
            'nome': 'Gestão de Funcionários',
            'categoria': 'PESSOAL',
            'tipo_cobranca': 'MENSAL',
            'valor_base': 50.00,
            'descricao': 'Gestão de funcionários'
        },
        {
            'codigo': 'PRO-LABORE',
            'nome': 'Retirada de Pró-labore',
            'categoria': 'PESSOAL',
            'tipo_cobranca': 'MENSAL',
            'valor_base': 30.00,
            'descricao': 'Retirada de pró-labore'
        },
        {
            'codigo': 'ORGAO-CLASSE',
            'nome': 'Registro de Orgão de Classe',
            'categoria': 'SOCIETARIO',
            'tipo_cobranca': 'VALOR_UNICO',
            'valor_base': 1000.00,
            'descricao': 'Realização de todo processo de registro de Orgão de Classe'
        }
    ]
    
    # Faixas de Faturamento por Regime Tributário
    # Baseado na legislação vigente de 2024
    
    # Simples Nacional - Faixas progressivas (Lei Complementar 123/2006)
    faixas_simples_nacional = [
        {
            'regime_tributario_id': None,  # Será definido dinamicamente
            'valor_minimo': 0.00,
            'valor_maximo': 180000.00,
            'aliquota': 4.00,
            'descricao': 'Simples Nacional - 1ª Faixa'
        },
        {
            'regime_tributario_id': None,
            'valor_minimo': 180000.01,
            'valor_maximo': 360000.00,
            'aliquota': 7.30,
            'descricao': 'Simples Nacional - 2ª Faixa'
        },
        {
            'regime_tributario_id': None,
            'valor_minimo': 360000.01,
            'valor_maximo': 720000.00,
            'aliquota': 9.50,
            'descricao': 'Simples Nacional - 3ª Faixa'
        },
        {
            'regime_tributario_id': None,
            'valor_minimo': 720000.01,
            'valor_maximo': 1800000.00,
            'aliquota': 10.70,
            'descricao': 'Simples Nacional - 4ª Faixa'
        },
        {
            'regime_tributario_id': None,
            'valor_minimo': 1800000.01,
            'valor_maximo': 3600000.00,
            'aliquota': 14.30,
            'descricao': 'Simples Nacional - 5ª Faixa'
        },
        {
            'regime_tributario_id': None,
            'valor_minimo': 3600000.01,
            'valor_maximo': 4800000.00,
            'aliquota': 19.00,
            'descricao': 'Simples Nacional - 6ª Faixa'
        }
    ]
    
    # Lucro Presumido - Alíquota fixa
    faixas_lucro_presumido = [
        {
            'regime_tributario_id': None,
            'valor_minimo': 0.00,
            'valor_maximo': None,  # Sem limite máximo
            'aliquota': 15.00,
            'descricao': 'Lucro Presumido - Alíquota Padrão'
        }
    ]
    
    # Lucro Real - Alíquota fixa
    faixas_lucro_real = [
        {
            'regime_tributario_id': None,
            'valor_minimo': 0.00,
            'valor_maximo': None,  # Sem limite máximo
            'aliquota': 15.00,
            'descricao': 'Lucro Real - Alíquota Padrão'
        }
    ]
    
    # MEI - Alíquota fixa (limite de faturamento)
    faixas_mei = [
        {
            'regime_tributario_id': None,
            'valor_minimo': 0.00,
            'valor_maximo': 81000.00,
            'aliquota': 5.00,
            'descricao': 'MEI - Alíquota Padrão'
        }
    ]
    
    try:
        # Inserir tipos de atividade
        for tipo_data in tipos_atividade:
            tipo_existente = TipoAtividade.query.filter_by(codigo=tipo_data['codigo']).first()
            if not tipo_existente:
                tipo = TipoAtividade(**tipo_data, ativo=True)
                db.session.add(tipo)
                print(f"Tipo de atividade '{tipo_data['nome']}' criado com sucesso.")
        
        # Inserir regimes tributários
        for regime_data in regimes_tributarios:
            regime_existente = RegimeTributario.query.filter_by(codigo=regime_data['codigo']).first()
            if not regime_existente:
                regime = RegimeTributario(**regime_data, ativo=True)
                db.session.add(regime)
                print(f"Regime tributário '{regime_data['nome']}' criado com sucesso.")
        
        # Inserir serviços
        for servico_data in servicos:
            servico_existente = Servico.query.filter_by(codigo=servico_data['codigo']).first()
            if not servico_existente:
                servico = Servico(**servico_data, ativo=True)
                db.session.add(servico)
                print(f"Serviço '{servico_data['nome']}' criado com sucesso.")
        
        # Inserir faixas de faturamento para cada regime
        regimes_faixas = {
            'SN': faixas_simples_nacional,
            'LP': faixas_lucro_presumido,
            'LR': faixas_lucro_real,
            'MEI': faixas_mei
        }
        
        for codigo_regime, faixas in regimes_faixas.items():
            regime = RegimeTributario.query.filter_by(codigo=codigo_regime).first()
            if regime:
                # Verificar se já existem faixas para este regime
                faixas_existentes = FaixaFaturamento.query.filter_by(regime_tributario_id=regime.id).count()
                
                if faixas_existentes == 0:
                    for faixa_data in faixas:
                        faixa = FaixaFaturamento(
                            regime_tributario_id=regime.id,
                            valor_inicial=faixa_data['valor_minimo'],
                            valor_final=faixa_data['valor_maximo'],
                            aliquota=faixa_data['aliquota'],
                            ativo=True
                        )
                        db.session.add(faixa)
                        print(f"Faixa de faturamento '{faixa_data['descricao']}' criada com sucesso.")
                else:
                    print(f"Faixas de faturamento para {regime.nome} já existem ({faixas_existentes} faixas).")
            else:
                print(f"Regime {codigo_regime} não encontrado. Faixas de faturamento não serão criadas.")
        
        db.session.commit()
        print("Dados básicos inicializados com sucesso!")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao inicializar dados básicos: {e}")
        return False


def inicializar_faixas_faturamento():
    """
    Inicializa apenas as faixas de faturamento baseadas na legislação vigente.
    Útil para atualizar faixas sem recriar todos os dados básicos.
    """
    
    # Faixas de Faturamento por Regime Tributário
    # Baseado na legislação vigente de 2024
    
    # Simples Nacional - Faixas progressivas (Lei Complementar 123/2006)
    faixas_simples_nacional = [
        {
            'regime_tributario_id': None,  # Será definido dinamicamente
            'valor_minimo': 0.00,
            'valor_maximo': 180000.00,
            'aliquota': 4.00,
            'descricao': 'Simples Nacional - 1ª Faixa'
        },
        {
            'regime_tributario_id': None,
            'valor_minimo': 180000.01,
            'valor_maximo': 360000.00,
            'aliquota': 7.30,
            'descricao': 'Simples Nacional - 2ª Faixa'
        },
        {
            'regime_tributario_id': None,
            'valor_minimo': 360000.01,
            'valor_maximo': 720000.00,
            'aliquota': 9.50,
            'descricao': 'Simples Nacional - 3ª Faixa'
        },
        {
            'regime_tributario_id': None,
            'valor_minimo': 720000.01,
            'valor_maximo': 1800000.00,
            'aliquota': 10.70,
            'descricao': 'Simples Nacional - 4ª Faixa'
        },
        {
            'regime_tributario_id': None,
            'valor_minimo': 1800000.01,
            'valor_maximo': 3600000.00,
            'aliquota': 14.30,
            'descricao': 'Simples Nacional - 5ª Faixa'
        },
        {
            'regime_tributario_id': None,
            'valor_minimo': 3600000.01,
            'valor_maximo': 4800000.00,
            'aliquota': 19.00,
            'descricao': 'Simples Nacional - 6ª Faixa'
        }
    ]
    
    # Lucro Presumido - Alíquota fixa
    faixas_lucro_presumido = [
        {
            'regime_tributario_id': None,
            'valor_minimo': 0.00,
            'valor_maximo': None,  # Sem limite máximo
            'aliquota': 15.00,
            'descricao': 'Lucro Presumido - Alíquota Padrão'
        }
    ]
    
    # Lucro Real - Alíquota fixa
    faixas_lucro_real = [
        {
            'regime_tributario_id': None,
            'valor_minimo': 0.00,
            'valor_maximo': None,  # Sem limite máximo
            'aliquota': 15.00,
            'descricao': 'Lucro Real - Alíquota Padrão'
        }
    ]
    
    # MEI - Alíquota fixa (limite de faturamento)
    faixas_mei = [
        {
            'regime_tributario_id': None,
            'valor_minimo': 0.00,
            'valor_maximo': 81000.00,
            'aliquota': 5.00,
            'descricao': 'MEI - Alíquota Padrão'
        }
    ]
    
    try:
        # Inserir faixas de faturamento para cada regime
        regimes_faixas = {
            'SN': faixas_simples_nacional,
            'LP': faixas_lucro_presumido,
            'LR': faixas_lucro_real,
            'MEI': faixas_mei
        }
        
        total_faixas_criadas = 0
        
        for codigo_regime, faixas in regimes_faixas.items():
            regime = RegimeTributario.query.filter_by(codigo=codigo_regime).first()
            if regime:
                # Verificar se já existem faixas para este regime
                faixas_existentes = FaixaFaturamento.query.filter_by(regime_tributario_id=regime.id).count()
                
                if faixas_existentes == 0:
                    for faixa_data in faixas:
                        faixa = FaixaFaturamento(
                            regime_tributario_id=regime.id,
                            valor_inicial=faixa_data['valor_minimo'],
                            valor_final=faixa_data['valor_maximo'],
                            aliquota=faixa_data['aliquota'],
                            ativo=True
                        )
                        db.session.add(faixa)
                        print(f"Faixa de faturamento '{faixa_data['descricao']}' criada com sucesso.")
                        total_faixas_criadas += 1
                    
                    db.session.commit()
                    print(f"✅ {len(faixas)} faixas de faturamento criadas para {regime.nome}!")
                else:
                    print(f"ℹ️  Faixas de faturamento para {regime.nome} já existem ({faixas_existentes} faixas).")
            else:
                print(f"❌ Regime {codigo_regime} não encontrado. Faixas de faturamento não serão criadas.")
        
        if total_faixas_criadas > 0:
            print(f"✅ Total de {total_faixas_criadas} faixas de faturamento criadas com sucesso!")
        else:
            print("ℹ️  Nenhuma nova faixa de faturamento foi criada (todas já existem).")
        
        return True
            
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao inicializar faixas de faturamento: {e}")
        return False


def criar_usuario_admin():
    """
    Cria um usuário administrador padrão no sistema.
    Útil para primeira inicialização ou reset do sistema.
    """
    print("\n👤 Criando usuário administrador...")
    
    try:
        # Verificar se já existe algum usuário
        if Funcionario.query.count() > 0:
            print("ℹ️  Usuários já existem no sistema")
            return True
        
        # Criar empresa padrão
        empresa = Empresa(
            nome="Empresa Administrativa",
            cnpj="00.000.000/0001-00",
            endereco="Endereço Administrativo, 123",
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
            email="admin@admin.com",
            senha_hash=generate_password_hash("admin123"),
            gerente=True,
            cargo_id=cargo.id,
            empresa_id=empresa.id
        )
        db.session.add(admin)
        
        # Salvar tudo
        db.session.commit()
        
        print(f"✅ Usuário administrador criado com sucesso!")
        print(f"📧 Email: admin@admin.com")
        print(f"🔐 Senha: admin123")
        print(f"🏢 Empresa: {empresa.nome}")
        print(f"👔 Cargo: {cargo.nome}")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao criar usuário administrador: {e}")
        return False


def inicializar_sistema_completo():
    """
    Inicializa o sistema completo com dados básicos e usuário administrador.
    """
    print("🚀 INICIALIZANDO SISTEMA COMPLETO")
    print("=" * 50)
    
    try:
        # 1. Inicializar dados básicos
        print("\n📋 Inicializando dados básicos...")
        if not inicializar_dados_basicos():
            print("❌ Falha ao inicializar dados básicos")
            return False
        
        # 2. Criar usuário administrador
        if not criar_usuario_admin():
            print("❌ Falha ao criar usuário administrador")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 SISTEMA INICIALIZADO COM SUCESSO!")
        print("\n📋 Credenciais de acesso:")
        print("  📧 Email: admin@admin.com")
        print("  🔐 Senha: admin123")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO na inicialização: {e}")
        import traceback
        traceback.print_exc()
        return False
