"""
Serviços e lógica de negócio para propostas comerciais.
"""

from datetime import datetime
from typing import List, Optional
from config import db
from .propostas import Proposta, ItemProposta, PropostaLog
from .tributario import AtividadeRegime, RegimeTributario
from .servicos import Servico


class PropostaService:
    """Classe com métodos estáticos para lógica de negócio das propostas"""
    
    @staticmethod
    def gerar_numero_proposta() -> str:
        """Gera o próximo número de proposta no formato AAAA0001"""
        ano_atual = datetime.now().year
        
        # Busca o último número do ano
        ultima_proposta = db.session.query(Proposta)\
            .filter(Proposta.numero.like(f'{ano_atual}%'))\
            .order_by(Proposta.numero.desc())\
            .first()
        
        if ultima_proposta:
            try:
                ultimo_numero = int(ultima_proposta.numero[-4:])
                proximo_numero = ultimo_numero + 1
            except ValueError:
                proximo_numero = 1
        else:
            proximo_numero = 1
            
        return f'{ano_atual}{proximo_numero:04d}'
    
    @staticmethod
    def validar_regime_para_atividades(proposta: Proposta) -> bool:
        """Valida se o regime tributário é compatível com as atividades selecionadas"""
        if not proposta.regime_tributario_id:
            return True
            
        # Verifica se existe pelo menos uma combinação válida
        combinacao_valida = db.session.query(AtividadeRegime)\
            .filter(
                AtividadeRegime.tipo_atividade_id == proposta.tipo_atividade_id,
                AtividadeRegime.regime_tributario_id == proposta.regime_tributario_id,
                AtividadeRegime.ativo == True
            ).first()
            
        return combinacao_valida is not None
    
    @staticmethod
    def get_regimes_disponiveis_para_atividades(
        tipo_atividade_id: int, 
        tipo_pessoa: str = 'J'
    ) -> List[RegimeTributario]:
        """Retorna regimes tributários disponíveis para a atividade selecionada"""
        query = db.session.query(RegimeTributario)\
            .join(AtividadeRegime)\
            .filter(
                AtividadeRegime.tipo_atividade_id == tipo_atividade_id,
                AtividadeRegime.ativo == True,
                RegimeTributario.ativo == True
            )
        
        if tipo_pessoa == 'F':
            query = query.filter(RegimeTributario.aplicavel_pf == True)
        elif tipo_pessoa == 'J':
            query = query.filter(RegimeTributario.aplicavel_pj == True)
            
        return query.distinct().all()
    
    @staticmethod
    def calcular_servicos_automaticos(proposta: Proposta):
        """Calcula e adiciona serviços automaticamente baseado nas configurações"""
        # Remove itens automáticos existentes
        ItemProposta.query.filter_by(
            proposta_id=proposta.id, 
            descricao_personalizada='Serviço Automático'
        ).delete()
        
        servicos_adicionados = []
        
        # Contabilidade Mensal (sempre inclui para regimes empresariais)
        servico_contabil = Servico.query.filter_by(
            nome='Contabilidade Mensal', 
            ativo=True
        ).first()
        
        if servico_contabil:
            item = ItemProposta(
                proposta_id=proposta.id,
                servico_id=servico_contabil.id,
                quantidade=1,
                valor_unitario=servico_contabil.valor_base,
                valor_total=servico_contabil.valor_base,
                descricao_personalizada='Serviço Automático'
            )
            db.session.add(item)
            servicos_adicionados.append('Contabilidade Mensal')
        
        # Adiciona outros serviços automáticos conforme necessário
        # ...
        
        if servicos_adicionados:
            db.session.commit()
            PropostaService.adicionar_historico(
                proposta, 
                None, 
                'SERVIÇOS_AUTOMATICOS', 
                f'Serviços automáticos adicionados: {", ".join(servicos_adicionados)}'
            )
    
    @staticmethod
    def adicionar_historico(
        proposta: Proposta, 
        funcionario_id: Optional[int], 
        acao: str, 
        detalhes: Optional[str] = None
    ):
        """Adiciona um registro no histórico da proposta"""
        log = PropostaLog(
            proposta_id=proposta.id,
            funcionario_id=funcionario_id or proposta.funcionario_responsavel_id,
            acao=acao,
            detalhes=detalhes
        )
        db.session.add(log)
        db.session.commit()
    
    @staticmethod
    def atualizar_totais(proposta: Proposta):
        """Atualiza o valor total da proposta baseado nos itens"""
        total = db.session.query(
            db.func.coalesce(db.func.sum(ItemProposta.valor_total), 0)
        ).filter(
            ItemProposta.proposta_id == proposta.id,
            ItemProposta.ativo == True
        ).scalar()
        
        proposta.valor_total = total
        db.session.commit()
