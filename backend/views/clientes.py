"""
Views relacionadas aos clientes.
"""

from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import or_
from datetime import datetime
from flask_jwt_extended import jwt_required

from config import db
from models import Cliente, Endereco, EntidadeJuridica
from .utils import handle_api_errors, validate_required_fields, paginate_query

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('/', methods=['GET'])
@jwt_required()
@handle_api_errors
def get_clientes():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    ativo = request.args.get('ativo', type=bool)
    search = request.args.get('search', '').strip()

    query = Cliente.query

    if ativo is not None:
        query = query.filter(Cliente.ativo == ativo)
    if search:
        query = query.filter(
            or_(
                Cliente.nome.ilike(f'%{search}%'),
                Cliente.cpf.ilike(f'%{search}%'),
                Cliente.email.ilike(f'%{search}%')
            )
        )

    clientes = paginate_query(
        query.order_by(Cliente.nome.asc()),
        page, per_page
    )

    data = [c.to_json_completo() for c in clientes.items]
    return jsonify({
        'items': data,
        'clientes': data,
        'total': clientes.total,
        'pages': clientes.pages,
        'current_page': page,
        'per_page': per_page
    })

@clientes_bp.route('/<int:cliente_id>', methods=['GET'])
@jwt_required()
@handle_api_errors
def get_cliente(cliente_id: int):
    cliente = Cliente.query.get_or_404(cliente_id)
    return jsonify(cliente.to_json_completo())

@clientes_bp.route('/', methods=['POST'])
@jwt_required()
@handle_api_errors
def create_cliente():
    data = request.get_json() or {}
    
    current_app.logger.info(f"=== INICIANDO CRIAÇÃO DE CLIENTE ===")
    current_app.logger.info(f"Dados recebidos: {data}")
    
    # Validação de campos obrigatórios
    validation_error = validate_required_fields(data, ['nome', 'cpf'])
    if validation_error:
        return validation_error

    # Verificar se CPF já existe
    cpf_existente = Cliente.query.filter_by(cpf=data['cpf'].strip()).first()
    if cpf_existente:
        raise ValueError('CPF já cadastrado')

    try:
        # === ETAPA 1: CRIAR CLIENTE ===
        current_app.logger.info("ETAPA 1: Criando cliente")
        cliente = Cliente(
            nome=(data['nome'] or '').strip(),
            cpf=(data['cpf'] or '').strip(),
            email=(data.get('email') or '').strip().lower() or None,
            abertura_empresa=bool(data.get('abertura_empresa', False)),
            ativo=data.get('ativo', True)
        )

        db.session.add(cliente)
        db.session.flush()  # Para obter o ID do cliente
        current_app.logger.info(f"Cliente criado com ID: {cliente.id}")

        # === ETAPA 2: PROCESSAR ENDEREÇO ===
        current_app.logger.info("ETAPA 2: Processando endereço")
        novo_endereco = None
        if 'endereco' in data and data['endereco']:
            endereco_data = data['endereco']
            current_app.logger.info(f"Dados do endereço: {endereco_data}")
            
            novo_endereco = Endereco(
                rua=endereco_data.get('rua', '').strip(),
                numero=endereco_data.get('numero', '').strip(),
                cidade=endereco_data.get('cidade', '').strip(),
                estado=endereco_data.get('estado', '').strip(),
                cep=endereco_data.get('cep', '').strip(),
                cliente_id=cliente.id,
                ativo=True
            )
            db.session.add(novo_endereco)
            current_app.logger.info(f"Endereço criado: {novo_endereco.rua}, {novo_endereco.numero}")

        # === ETAPA 3: PROCESSAR EMPRESA ===
        current_app.logger.info("ETAPA 3: Processando empresa")
        current_app.logger.info(f"Campo entidade_juridica nos dados: {data.get('entidade_juridica')}")
        current_app.logger.info(f"Campo abertura_empresa nos dados: {data.get('abertura_empresa')}")
        
        # Só criar entidade jurídica se não for abertura de empresa E tiver dados
        if not data.get('abertura_empresa', False) and 'entidade_juridica' in data and data['entidade_juridica']:
            entidade_data = data['entidade_juridica']
            current_app.logger.info(f"Processando entidade jurídica: {entidade_data}")
            
            # Verificar se CNPJ já existe
            if entidade_data.get('cnpj'):
                cnpj_limpo = entidade_data.get('cnpj', '').strip()
                current_app.logger.info(f"Validando CNPJ: '{cnpj_limpo}'")
                
                if cnpj_limpo:
                    cnpj_existente = EntidadeJuridica.query.filter_by(
                        cnpj=cnpj_limpo
                    ).first()
                    
                    if cnpj_existente:
                        current_app.logger.error(f"CNPJ '{cnpj_limpo}' já cadastrado")
                        raise ValueError('CNPJ já cadastrado')
            
            # Criar entidade jurídica (pode ter ou não endereço)
            if entidade_data.get('nome') or entidade_data.get('cnpj') or entidade_data.get('tipo'):
                # Tratar CNPJ vazio ou nulo
                cnpj_value = entidade_data.get('cnpj', '').strip()
                if not cnpj_value or cnpj_value == "":
                    cnpj_value = None
                    current_app.logger.info("CNPJ vazio, definindo como None")
                else:
                    current_app.logger.info(f"CNPJ válido: {cnpj_value}")
                
                nova_entidade = EntidadeJuridica(
                    nome=entidade_data.get('nome', '').strip(),
                    cnpj=cnpj_value,
                    tipo=entidade_data.get('tipo', '').strip(),
                    cliente_id=cliente.id,
                    endereco_id=novo_endereco.id if novo_endereco else None,
                    ativo=True
                )
                db.session.add(nova_entidade)
                current_app.logger.info(f"Entidade jurídica criada: {nova_entidade.nome}, CNPJ: {nova_entidade.cnpj}")
            else:
                current_app.logger.info("Nenhum dado de empresa fornecido")
        else:
            current_app.logger.info("Cliente para abertura de empresa ou sem dados de empresa")

        # Commit final
        db.session.commit()
        current_app.logger.info(f"=== CRIAÇÃO CONCLUÍDA: Cliente {cliente.nome} (ID: {cliente.id}) ===")
        return jsonify(cliente.to_json_completo()), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao criar cliente: {str(e)}")
        current_app.logger.error(f"Detalhes do erro: {type(e).__name__}: {str(e)}")
        raise ValueError(f'Erro ao criar cliente: {str(e)}')

@clientes_bp.route('/<int:cliente_id>', methods=['PUT'])
@jwt_required()
@handle_api_errors
def update_cliente(cliente_id: int):
    cliente = Cliente.query.get_or_404(cliente_id)
    data = request.get_json() or {}

    current_app.logger.info(f"=== INICIANDO ATUALIZAÇÃO DO CLIENTE {cliente_id} ===")
    current_app.logger.info(f"Dados recebidos: {data}")
    current_app.logger.info(f"Estado atual do cliente - abertura_empresa: {cliente.abertura_empresa}")

    try:
        # === ETAPA 1: ATUALIZAR CLIENTE ===
        current_app.logger.info("ETAPA 1: Atualizando dados do cliente")
        for field in ['nome', 'email', 'abertura_empresa', 'ativo']:
            if field in data:
                value = data[field]
                if field == 'email' and value:
                    value = value.strip().lower()
                elif field == 'nome' and value:
                    value = value.strip()
                setattr(cliente, field, value)
                current_app.logger.info(f"Campo '{field}' atualizado para: {value}")

        # Commit das alterações do cliente
        db.session.commit()
        current_app.logger.info("ETAPA 1 CONCLUÍDA: Cliente atualizado")

        # === ETAPA 2: PROCESSAR ENDEREÇO ===
        current_app.logger.info("ETAPA 2: Processando endereço")
        novo_endereco = None
        
        if 'endereco' in data and data['endereco']:
            endereco_data = data['endereco']
            current_app.logger.info(f"Dados do endereço: {endereco_data}")
            
            # Remover endereços existentes
            for endereco in cliente.enderecos:
                current_app.logger.info(f"Removendo endereço existente: {endereco.id}")
                db.session.delete(endereco)
            
            # Criar novo endereço
            novo_endereco = Endereco(
                rua=endereco_data.get('rua', '').strip(),
                numero=endereco_data.get('numero', '').strip(),
                cidade=endereco_data.get('cidade', '').strip(),
                estado=endereco_data.get('estado', '').strip(),
                cep=endereco_data.get('cep', '').strip(),
                cliente_id=cliente.id,
                ativo=True
            )
            db.session.add(novo_endereco)
            current_app.logger.info(f"Novo endereço criado: {novo_endereco.rua}, {novo_endereco.numero}")
        else:
            current_app.logger.info("Nenhum endereço fornecido")

        # Commit das alterações do endereço
        db.session.commit()
        current_app.logger.info("ETAPA 2 CONCLUÍDA: Endereço processado")

        # === ETAPA 3: PROCESSAR EMPRESA ===
        current_app.logger.info("ETAPA 3: Processando empresa")
        current_app.logger.info(f"Campo entidade_juridica nos dados: {data.get('entidade_juridica')}")
        current_app.logger.info(f"Campo abertura_empresa nos dados: {data.get('abertura_empresa')}")
        
        # SEMPRE remover entidades jurídicas existentes primeiro
        if cliente.entidades_juridicas:
            current_app.logger.info("Removendo entidades jurídicas existentes")
            for entidade in cliente.entidades_juridicas:
                current_app.logger.info(f"Removendo entidade: {entidade.id}")
                db.session.delete(entidade)
            db.session.commit()
            current_app.logger.info("Entidades jurídicas removidas")
        
        # Se não for abertura de empresa E tiver dados de empresa, criar nova entidade
        if not data.get('abertura_empresa', False) and 'entidade_juridica' in data and data['entidade_juridica']:
            entidade_data = data['entidade_juridica']
            current_app.logger.info(f"Processando entidade jurídica: {entidade_data}")
            
            # Verificar se CNPJ já existe em outra entidade (exceto a atual do cliente)
            if entidade_data.get('cnpj'):
                cnpj_limpo = entidade_data.get('cnpj', '').strip()
                current_app.logger.info(f"Validando CNPJ: '{cnpj_limpo}'")
                
                if cnpj_limpo:  # Só validar se CNPJ não estiver vazio
                    # Obter IDs das entidades jurídicas atuais do cliente
                    ids_entidades_cliente = [ej.id for ej in cliente.entidades_juridicas]
                    current_app.logger.info(f"IDs das entidades do cliente: {ids_entidades_cliente}")
                    
                    # Verificar se CNPJ já existe em outra entidade (excluindo as do cliente atual)
                    query = EntidadeJuridica.query.filter(EntidadeJuridica.cnpj == cnpj_limpo)
                    if ids_entidades_cliente:
                        query = query.filter(~EntidadeJuridica.id.in_(ids_entidades_cliente))
                    
                    cnpj_existente = query.first()
                    current_app.logger.info(f"CNPJ existente encontrado: {cnpj_existente}")
                    
                    if cnpj_existente:
                        current_app.logger.error(f"CNPJ '{cnpj_limpo}' já cadastrado em outra entidade (ID: {cnpj_existente.id})")
                        raise ValueError('CNPJ já cadastrado em outra entidade')
                else:
                    current_app.logger.info("CNPJ vazio, pulando validação")
            
            # Criar nova entidade jurídica (pode ter ou não endereço)
            if entidade_data.get('nome') or entidade_data.get('cnpj') or entidade_data.get('tipo'):
                endereco_id = None
                if novo_endereco:
                    endereco_id = novo_endereco.id
                    current_app.logger.info(f"Usando endereço criado: {endereco_id}")
                
                # Tratar CNPJ vazio ou nulo
                cnpj_value = entidade_data.get('cnpj', '').strip()
                if not cnpj_value or cnpj_value == "":
                    cnpj_value = None
                    current_app.logger.info("CNPJ vazio, definindo como None")
                else:
                    current_app.logger.info(f"CNPJ válido: {cnpj_value}")
                
                nova_entidade = EntidadeJuridica(
                    nome=entidade_data.get('nome', '').strip(),
                    cnpj=cnpj_value,
                    tipo=entidade_data.get('tipo', '').strip(),
                    cliente_id=cliente.id,
                    endereco_id=endereco_id,
                    ativo=True
                )
                current_app.logger.info(f"Criando nova entidade: {nova_entidade.nome}, CNPJ: {nova_entidade.cnpj}, endereco_id: {nova_entidade.endereco_id}")
                db.session.add(nova_entidade)
                db.session.commit()
                current_app.logger.info("Nova entidade jurídica criada")
            else:
                current_app.logger.info("Nenhum dado de empresa fornecido")
        else:
            current_app.logger.info("Cliente para abertura de empresa ou sem dados de empresa")

        # Commit final
        cliente.updated_at = datetime.utcnow()
        db.session.commit()
        current_app.logger.info("ETAPA 3 CONCLUÍDA: Empresa processada")
        current_app.logger.info(f"=== ATUALIZAÇÃO CONCLUÍDA: Cliente {cliente.nome} (ID: {cliente.id}) ===")
        return jsonify(cliente.to_json_completo())
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao atualizar cliente: {str(e)}")
        current_app.logger.error(f"Detalhes do erro: {type(e).__name__}: {str(e)}")
        raise ValueError(f'Erro ao atualizar cliente: {str(e)}')

@clientes_bp.route('/<int:cliente_id>', methods=['DELETE'])
@jwt_required()
@handle_api_errors
def delete_cliente(cliente_id: int):
    cliente = Cliente.query.get_or_404(cliente_id)

    if cliente.propostas:
        cliente.ativo = False
        cliente.updated_at = datetime.utcnow()
        db.session.commit()
        current_app.logger.info(f"Cliente desativado: {cliente.nome} (ID: {cliente.id})")
        return jsonify({'message': 'Cliente desativado (possui propostas associadas)'})
    else:
        nome = cliente.nome
        db.session.delete(cliente)
        db.session.commit()
        current_app.logger.info(f"Cliente removido: {nome} (ID: {cliente_id})")
        return jsonify({'message': 'Cliente removido'})
