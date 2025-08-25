"""
Views para gerenciamento de serviços
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from typing import List

from config import db
from models.servicos import Servico, ServicoRegime
from models.tributario import RegimeTributario, TipoAtividade, AtividadeRegime
from .utils import handle_api_errors

servicos_bp = Blueprint('servicos', __name__)


@servicos_bp.route('/', methods=['GET'])
@jwt_required()
@handle_api_errors
def get_servicos():
    """Busca todos os serviços ativos"""
    servicos = Servico.query.filter_by(ativo=True).all()
    return jsonify([servico.to_json() for servico in servicos])


@servicos_bp.route('/por-regime/<int:regime_id>', methods=['GET'])
@jwt_required()
@handle_api_errors
def get_servicos_por_regime(regime_id: int):
    """Busca serviços compatíveis com o regime tributário"""
    
    regime = RegimeTributario.query.get_or_404(regime_id)
    
    # Aplicar lógica de filtros por regime
    servicos_filtrados = aplicar_filtros_servicos_por_regime(regime.codigo)
    
    return jsonify({
        'regime': {
            'id': regime.id,
            'codigo': regime.codigo,
            'nome': regime.nome
        },
        'servicos': [servico.to_json() for servico in servicos_filtrados],
        'total': len(servicos_filtrados)
    })


@servicos_bp.route('/para-proposta', methods=['POST'])
@jwt_required()
@handle_api_errors
def get_servicos_para_proposta():
    """
    Retorna serviços disponíveis baseado nas configurações da proposta
    """
    data = request.get_json() or {}
    
    tipo_atividade_id = data.get('tipo_atividade_id')
    regime_tributario_id = data.get('regime_tributario_id')
    
    if not tipo_atividade_id or not regime_tributario_id:
        raise ValueError('tipo_atividade_id e regime_tributario_id são obrigatórios')
    
    # Buscar dados dos relacionamentos
    tipo_atividade = TipoAtividade.query.get_or_404(tipo_atividade_id)
    regime_tributario = RegimeTributario.query.get_or_404(regime_tributario_id)
    
    # Validar se a combinação é válida
    combinacao_valida = AtividadeRegime.query.filter_by(
        tipo_atividade_id=tipo_atividade_id,
        regime_tributario_id=regime_tributario_id,
        ativo=True
    ).first()
    
    if not combinacao_valida:
        return jsonify({
            'error': f'Combinação inválida: {tipo_atividade.nome} com {regime_tributario.nome}',
            'servicos': [],
            'total': 0
        }), 400
    
    # Filtrar serviços por regime
    servicos_filtrados = aplicar_filtros_servicos_por_regime(regime_tributario.codigo)
    
    # Filtrar adicionalmente por tipo de pessoa se necessário
    if tipo_atividade.aplicavel_pf:
        servicos_filtrados = filtrar_servicos_pessoa_fisica(servicos_filtrados)
    elif tipo_atividade.aplicavel_pj:
        servicos_filtrados = filtrar_servicos_pessoa_juridica(servicos_filtrados)
    
    return jsonify({
        'tipo_atividade': tipo_atividade.to_json(),
        'regime_tributario': regime_tributario.to_json(),
        'servicos': [servico.to_json() for servico in servicos_filtrados],
        'total': len(servicos_filtrados)
    })


def aplicar_filtros_servicos_por_regime(codigo_regime: str) -> List[Servico]:
    """
    Aplica filtros de serviços baseado no código do regime tributário
    Usa a tabela servico_regime para determinar compatibilidade
    
    Args:
        codigo_regime: Código do regime (MEI, SN, LP, LR, PR, Aut, DOM, CAT)
    
    Returns:
        List[Servico]: Lista de serviços compatíveis
    """
    # ⚠️ BUSCAR: Regime pelo código
    regime = RegimeTributario.query.filter_by(codigo=codigo_regime).first()
    if not regime:
        return []
    
    # ⚠️ BUSCAR: Serviços através da tabela servico_regime
    servicos_regime = ServicoRegime.query.filter_by(
        regime_tributario_id=regime.id,
        ativo=True
    ).all()
    
    # ⚠️ EXTRAIR: IDs dos serviços compatíveis
    servicos_ids = [sr.servico_id for sr in servicos_regime]
    
    # ⚠️ BUSCAR: Serviços ativos
    if servicos_ids:
        servicos = Servico.query.filter(
            Servico.id.in_(servicos_ids),
            Servico.ativo == True
        ).all()
    else:
        servicos = []
    
    return servicos


# ⚠️ REMOVIDO: Funções de filtro antigas - agora usando tabela servico_regime


def filtrar_servicos_pessoa_fisica(servicos: List[Servico]) -> List[Servico]:
    """Filtrar serviços aplicáveis para Pessoa Física"""
    # PF: Remover serviços exclusivos de PJ
    return [s for s in servicos if s.categoria not in ['SOCIETARIO']]


def filtrar_servicos_pessoa_juridica(servicos: List[Servico]) -> List[Servico]:
    """Filtrar serviços aplicáveis para Pessoa Jurídica"""
    # PJ: Todos os serviços são aplicáveis
    return servicos
