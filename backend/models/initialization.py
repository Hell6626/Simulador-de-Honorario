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
        },
        {
            'codigo': 'CAT',
            'nome': 'Cartório',
            'descricao': 'Regime para Cartórios',
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
        },
        {
            'codigo': 'INSCRICAO-PRODUTOR-RURAL_C_CERTIFICADO',
            'nome': 'Inscrição Produtores Rurais com Certificado',
            'categoria': 'FISCAL',
            'tipo_cobranca': 'VALOR_UNICO',
            'valor_base': 750.00,
            'descricao': 'Realização de todo processo de inscrição de Produtores Rurais com Certificado'
        },
        {
            'codigo': 'INSCRICAO-PRODUTOR-RURAL_SEM_CERTIFICADO',
            'nome': 'Inscrição Produtores Rurais sem Certificado',
            'categoria': 'FISCAL',
            'tipo_cobranca': 'VALOR_UNICO',
            'valor_base': 550.00,
            'descricao': 'Realização de todo processo de inscrição de Produtores Rurais sem Certificado'
        },
        {
            'codigo': 'OPERACAO-INSCRICAO-PRODUTOR-RURAL',
            'nome': 'Operação de Inscrição de Produtores Rurais',
            'categoria': 'FISCAL',
            'tipo_cobranca': 'VALOR_UNICO',
            'valor_base': 300.00,
            'descricao': 'Realização de todo processo de operação de inscrição de Produtores Rurais'
        },
        {
            'codigo': 'BAIXA-INSCRICAO-PRODUTOR-RURAL',
            'nome': 'Baixa de Inscrição de Produtores Rurais',
            'categoria': 'FISCAL',
            'tipo_cobranca': 'VALOR_UNICO',
            'valor_base': 400.00,
            'descricao': 'Realização de todo processo de baixa de inscrição de Produtores Rurais'
        },
        {
            'codigo': 'HONORARIO-C-FUNCIONARIO-PRODUTOR-RURAL',
            'nome': 'Honorário de Funcionário - Produtor Rural',
            'categoria': 'PESSOAL',
            'tipo_cobranca': 'MENSAL',
            'valor_base': 200.00,
            'descricao': 'Honorário de departamento pessoal por funcionário - Produtor Rural'
        },
        {
            'codigo': 'HONORARIO-C-DOIS-FUNCIONARIOS-PRODUTOR-RURAL',
            'nome': 'Honorário de Dois Funcionários - Produtor Rural',
            'categoria': 'PESSOAL',
            'tipo_cobranca': 'MENSAL',
            'valor_base': 240.00,
            'descricao': 'Honorário de departamento pessoal por dois funcionários - Produtor Rural'
        },
        {
            'codigo': 'HONORARIO-C-TRES-FUNCIONARIOS-PRODUTOR-RURAL',
            'nome': 'Honorário de Três Funcionários - Produtor Rural',
            'categoria': 'PESSOAL',
            'tipo_cobranca': 'MENSAL',
            'valor_base': 290.00,
            'descricao': 'Honorário de departamento pessoal por três funcionários - Produtor Rural'
        },
        {
            'codigo': 'HONORARIO-DEMAIS-FUNCIONARIOS-PRODUTOR-RURAL',
            'nome': 'Honorário de Funcionários (acima de 3) - Produtor Rural',
            'categoria': 'PESSOAL',
            'tipo_cobranca': 'MENSAL',
            'valor_base': 30.00,
            'descricao': 'Honorário de departamento pessoal por funcionários (acima de 3, Acrescido de R$30.00 por funcionário) - Produtor Rural'
        },
        {
            'codigo': 'CALCULO-DE-INSS-AUTONOMO',
            'nome': 'Cálculo de INSS - Autônomo',
            'categoria': 'PESSOAL',
            'tipo_cobranca': 'MENSAL',
            'valor_base': 100.00,
            'descricao': 'Cálculo de INSS - Autônomo'
        },
        {
            'codigo': 'HONORARIO-C-UNICO-FUNCIONARIO-EMPREGADOR-DOMÉSTICO',
            'nome': 'Honorário de Funcionário - Empregador Doméstico',
            'categoria': 'PESSOAL',
            'tipo_cobranca': 'MENSAL',
            'valor_base': 110.00,
            'descricao': 'Honorário de departamento pessoal por funcionário - Empregador Doméstico'
        },
        {
            'codigo': 'HONORARIO-C-DOIS-FUNCIONARIOS-EMPREGADOR-DOMÉSTICO',
            'nome': 'Honorário de Dois Funcionários - Empregador Doméstico',
            'categoria': 'PESSOAL',
            'tipo_cobranca': 'MENSAL',
            'valor_base': 150.00,
            'descricao': 'Honorário de departamento pessoal por dois funcionários - Empregador Doméstico'
        },
        {
            'codigo': 'HONORARIO-C-TRES-FUNCIONARIOS-EMPREGADOR-DOMÉSTICO',
            'nome': 'Honorário de Três Funcionários - Empregador Doméstico',
            'categoria': 'PESSOAL',
            'tipo_cobranca': 'MENSAL',
            'valor_base': 170.00,
            'descricao': 'Honorário de departamento pessoal por três funcionários - Empregador Doméstico'
        },
        {
            'codigo': 'HONORARIO-DEMAIS-FUNCIONARIOS-EMPREGADOR-DOMÉSTICO',
            'nome': 'Honorário de Funcionários (acima de 3) - Empregador Doméstico',
            'categoria': 'PESSOAL',
            'tipo_cobranca': 'MENSAL',
            'valor_base': 30.00,
            'descricao': 'Honorário de departamento pessoal por funcionários (acima de 3, Acrescido de R$30.00 por funcionário) - Empregador Doméstico'
        },
        {
            'codigo': 'BASE+UM-FUNCIONARIO-CARTORIO',
            'nome': 'Base + 1 Funcionário - Cartório',
            'categoria': 'CARTORIO',
            'tipo_cobranca': 'MENSAL',
            'valor_base': 450.00,
            'descricao': 'Base + 1 Funcionário - Cartório'
        },
        {
            'codigo': 'BASE+DOIS-FUNCIONARIOS-CARTORIO',
            'nome': 'Base + 2 Funcionários - Cartório',
            'categoria': 'CARTORIO',
            'tipo_cobranca': 'MENSAL',
            'valor_base': 490.00,
            'descricao': 'Base + 2 Funcionários - Cartório'
        },
        {
            'codigo': 'BASE+TRES-FUNCIONARIOS-CARTORIO',
            'nome': 'Base + 3 Funcionários - Cartório',
            'categoria': 'CARTORIO',
            'tipo_cobranca': 'MENSAL',
            'valor_base': 520.00,
            'descricao': 'Base + 3 Funcionários - Cartório'
        },
        {
            'codigo': 'BASE+DEMAIS-FUNCIONARIOS-CARTORIO',
            'nome': 'Base + Funcionários (acima de 3) - Cartório',
            'categoria': 'CARTORIO',
            'tipo_cobranca': 'MENSAL',
            'valor_base': 30.00,
            'descricao': 'Base + Funcionários (acima de 3, Acrescido de R$30.00 por funcionário) - Cartório'
        },
        {
            'codigo': 'CARNE-LEAO-CARTORIO',
            'nome': 'Carne-Leão - Cartório',
            'categoria': 'CARTORIO',
            'tipo_cobranca': 'MENSAL',
            'valor_base': 200.00,
            'descricao': 'Carne-Leão - Cartório'
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


def inicializar_relacionamentos_atividade_regime():
    """
    Inicializa os relacionamentos entre tipos de atividade e regimes tributários.
    Define quais combinações são permitidas no sistema.
    """
    print("\n🔗 Inicializando relacionamentos atividade x regime...")
    
    try:
        from .tributario import AtividadeRegime
        
        # Relacionamentos permitidos
        relacionamentos = [
            # Serviços, Comércio, Indústria podem ser: MEI, SN, LP, LR
            ('SERV', ['MEI', 'SN', 'LP', 'LR']),
            ('COM', ['MEI', 'SN', 'LP', 'LR']),
            ('IND', ['MEI', 'SN', 'LP', 'LR']),
            # Pessoa Física pode ser: PR, Aut, DOM, CAT
            ('PF', ['PR', 'Aut', 'DOM', 'CAT']),
        ]
        
        relacionamentos_criados = 0
        
        for atividade_codigo, regimes_codigos in relacionamentos:
            atividade = TipoAtividade.query.filter_by(codigo=atividade_codigo).first()
            if not atividade:
                print(f"⚠️  Tipo de atividade '{atividade_codigo}' não encontrado")
                continue
                
            for regime_codigo in regimes_codigos:
                regime = RegimeTributario.query.filter_by(codigo=regime_codigo).first()
                if not regime:
                    print(f"⚠️  Regime tributário '{regime_codigo}' não encontrado")
                    continue
                
                # Verificar se o relacionamento já existe
                if not AtividadeRegime.query.filter_by(
                    tipo_atividade_id=atividade.id,
                    regime_tributario_id=regime.id
                ).first():
                    rel = AtividadeRegime(
                        tipo_atividade_id=atividade.id,
                        regime_tributario_id=regime.id
                    )
                    db.session.add(rel)
                    relacionamentos_criados += 1
                    print(f"✅ Criado relacionamento: {atividade.nome} x {regime.nome}")
        
        db.session.commit()
        print(f"✅ {relacionamentos_criados} relacionamentos criados com sucesso!")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao inicializar relacionamentos: {e}")
        return False


def inicializar_relacionamentos_servico_regime():
    """
    Inicializa os relacionamentos entre serviços e regimes tributários.
    Define quais serviços são compatíveis com cada regime.
    """
    print("\n🔗 Inicializando relacionamentos serviço x regime...")
    
    try:
        from .servicos import ServicoRegime
        
        # Mapeamento de serviços por regime tributário
        relacionamentos = {
            # MEI - Serviços básicos
            'MEI': [
                'BALANCETE-SN',  # Balancete para Simples Nacional
                'NF-e',          # Nota Fiscal Eletrônica
                'NFS-e',         # Nota Fiscal de Serviços
                'CT-e',          # Conhecimento de Transporte
                'FUNCIONARIO',   # Gestão de Funcionários
            ],
            
            # Simples Nacional - Serviços completos para PJ
            'SN': [
                'BALANCETE-SN',  # Balancete para Simples Nacional
                'NF-e',          # Nota Fiscal Eletrônica
                'NFS-e',         # Nota Fiscal de Serviços
                'CT-e',          # Conhecimento de Transporte
                'FUNCIONARIO',   # Gestão de Funcionários
                'PRO-LABORE',    # Retirada de Pró-labore
                'ORGAO-CLASSE',  # Registro de Órgão de Classe
            ],
            
            # Lucro Presumido - Serviços complexos
            'LP': [
                'BALANCETE-LP-LR',  # Balancete para LP/LR
                'NF-e',             # Nota Fiscal Eletrônica
                'NFS-e',            # Nota Fiscal de Serviços
                'CT-e',             # Conhecimento de Transporte
                'FUNCIONARIO',      # Gestão de Funcionários
                'PRO-LABORE',       # Retirada de Pró-labore
                'ORGAO-CLASSE',     # Registro de Órgão de Classe
            ],
            
            # Lucro Real - Serviços complexos
            'LR': [
                'BALANCETE-LP-LR',  # Balancete para LP/LR
                'NF-e',             # Nota Fiscal Eletrônica
                'NFS-e',            # Nota Fiscal de Serviços
                'CT-e',             # Conhecimento de Transporte
                'FUNCIONARIO',      # Gestão de Funcionários
                'PRO-LABORE',       # Retirada de Pró-labore
                'ORGAO-CLASSE',     # Registro de Órgão de Classe
            ],
            
            # Produtor Rural - Serviços específicos
            'PR': [
                'INSCRICAO-PRODUTOR-RURAL_C_CERTIFICADO',
                'INSCRICAO-PRODUTOR-RURAL_SEM_CERTIFICADO',
                'OPERACAO-INSCRICAO-PRODUTOR-RURAL',
                'BAIXA-INSCRICAO-PRODUTOR-RURAL',
                'HONORARIO-C-FUNCIONARIO-PRODUTOR-RURAL',
                'HONORARIO-C-DOIS-FUNCIONARIOS-PRODUTOR-RURAL',
                'HONORARIO-C-TRES-FUNCIONARIOS-PRODUTOR-RURAL',
                'HONORARIO-DEMAIS-FUNCIONARIOS-PRODUTOR-RURAL',
            ],
            
            # Autônomo - Serviços específicos
            'Aut': [
                'CALCULO-DE-INSS-AUTONOMO',
            ],
            
            # Empregador Doméstico - Serviços específicos
            'DOM': [
                'HONORARIO-C-UNICO-FUNCIONARIO-EMPREGADOR-DOMÉSTICO',
                'HONORARIO-C-DOIS-FUNCIONARIOS-EMPREGADOR-DOMÉSTICO',
                'HONORARIO-C-TRES-FUNCIONARIOS-EMPREGADOR-DOMÉSTICO',
                'HONORARIO-DEMAIS-FUNCIONARIOS-EMPREGADOR-DOMÉSTICO',
            ],
            
            # Cartório - Serviços específicos
            'CAT': [
                'BASE+UM-FUNCIONARIO-CARTORIO',
                'BASE+DOIS-FUNCIONARIOS-CARTORIO',
                'BASE+TRES-FUNCIONARIOS-CARTORIO',
                'BASE+DEMAIS-FUNCIONARIOS-CARTORIO',
                'CARNE-LEAO-CARTORIO',
            ]
        }
        
        relacionamentos_criados = 0
        
        for regime_codigo, servicos_codigos in relacionamentos.items():
            regime = RegimeTributario.query.filter_by(codigo=regime_codigo).first()
            if not regime:
                print(f"⚠️  Regime tributário '{regime_codigo}' não encontrado")
                continue
                
            for servico_codigo in servicos_codigos:
                servico = Servico.query.filter_by(codigo=servico_codigo).first()
                if not servico:
                    print(f"⚠️  Serviço '{servico_codigo}' não encontrado")
                    continue
                
                # Verificar se o relacionamento já existe
                if not ServicoRegime.query.filter_by(
                    servico_id=servico.id,
                    regime_tributario_id=regime.id
                ).first():
                    rel = ServicoRegime(
                        servico_id=servico.id,
                        regime_tributario_id=regime.id
                    )
                    db.session.add(rel)
                    relacionamentos_criados += 1
                    print(f"✅ Criado relacionamento: {servico.nome} x {regime.nome}")
        
        db.session.commit()
        print(f"✅ {relacionamentos_criados} relacionamentos serviço x regime criados com sucesso!")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao inicializar relacionamentos serviço x regime: {e}")
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
        
        # 2. Inicializar relacionamentos atividade x regime
        print("\n🔗 Inicializando relacionamentos...")
        if not inicializar_relacionamentos_atividade_regime():
            print("❌ Falha ao inicializar relacionamentos")
            return False
        
        # 3. Inicializar relacionamentos serviço x regime
        print("\n🔗 Inicializando relacionamentos serviço x regime...")
        if not inicializar_relacionamentos_servico_regime():
            print("❌ Falha ao inicializar relacionamentos serviço x regime")
            return False
        
        # 4. Criar usuário administrador
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
