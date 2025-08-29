import React, { useState } from 'react';
import { ArrowLeft, Save, MessageSquare, AlertTriangle } from 'lucide-react';
import { usePropostaStore } from '../../../store/PropostaStore';
import { useApi } from '../../../hooks/useApi';
import { apiService } from '../../../services/api';
import { usePropostaCalculations } from '../../../hooks/usePropostaCalculations';
// import { useSalvamentoAutomatico } from '../../../hooks/useSalvamentoAutomatico'; // ⚠️ REMOVIDO: Não precisamos de salvamento automático no Passo 4
import { validarDesconto } from '../../../utils/calculations';
import { PropostaComDesconto, DadosPropostaCompleta } from '../../../types/propostas';

// Componentes refatorados
import { PageHeader } from '../../layout/PageHeader';
import { Card } from '../../layout/Card';
import { Button } from '../../forms/Button';
import { FormField } from '../../forms/FormField';
import { Textarea } from '../../forms/Textarea';
import { StatusSalvamento } from '../../common/StatusSalvamento';
import { DadosProposta } from '../DadosProposta';
import { ServicosSelecionados } from '../ServicosSelecionados';
import { ResumoFinanceiro } from '../ResumoFinanceiro';

interface Passo4Props {
  dadosProposta: DadosPropostaCompleta;
  propostaId?: number; // ⚠️ NOVO: ID da proposta criada no Passo 3
  propostaNumero?: string; // ⚠️ NOVO: Número da proposta criada no Passo 3
  onAnterior: () => void;
  onProximo: (dadosCompletos: PropostaComDesconto) => void;
  todosServicos?: any[];
}

export const Passo4RevisaoProposta: React.FC<Passo4Props> = ({
  dadosProposta: dadosPropostaProps,
  propostaId,
  propostaNumero,
  onAnterior,
  onProximo,
  todosServicos = []
}) => {
  // Store global
  const { state, setDadosProposta, setDesconto, setObservacoes, setLoading, setError } = usePropostaStore();
  const { dadosProposta, percentualDesconto, observacoes, loading, error } = state;

  // Initialize store with props data if store is empty
  React.useEffect(() => {
    if (!dadosProposta && dadosPropostaProps) {
      setDadosProposta(dadosPropostaProps);
    }
  }, [dadosProposta, dadosPropostaProps, setDadosProposta]);

  // Use props data as fallback if store is not initialized yet
  const dadosPropostaToUse = dadosProposta || dadosPropostaProps;

  // Hook de cálculos
  const resumoFinanceiro = usePropostaCalculations(
    dadosPropostaToUse!,
    percentualDesconto,
    todosServicos
  );



  // ⚠️ REMOVIDO: Hook de salvamento automático (estava criando propostas duplicadas)
  // const { estadoSalvamento, salvarComoRascunho } = useSalvamentoAutomatico(dadosPropostaToUse);

  // Estado simples para controle de loading e salvamento
  const [estadoSalvamento] = useState({
    salvando: false,
    propostaSalva: false
  });

  // Estado para controle de salvamento
  const [salvandoProposta, setSalvandoProposta] = useState(false);

  // Debug: verificar token de autenticação
  React.useEffect(() => {
    const token = apiService.getToken();
    console.log('🔐 Token de autenticação:', token ? 'Presente' : 'Ausente');
    if (token) {
      console.log('🔐 Token (primeiros 20 chars):', token.substring(0, 20) + '...');
    }
  }, []);

  // Validação de desconto
  const validacaoDesconto = validarDesconto(percentualDesconto);
  const requerAprovacao = validacaoDesconto.requerAprovacao;

  // ⚠️ SIMPLIFICADO: Função para apenas atualizar status da proposta existente
  const handleProximo = async () => {
    if (!propostaId) {
      setError('ID da proposta não encontrado');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      console.log('✅ Atualizando apenas status da proposta...');
      console.log('🔄 Proposta ID:', propostaId);
      console.log('🔄 Proposta Número:', propostaNumero);
      console.log('📊 Status atual: RASCUNHO');
      console.log('🔄 Novo status:', requerAprovacao ? 'PENDENTE' : 'APROVADA');

      // ⚠️ SIMPLIFICADO: Apenas atualizar status e valores finais - SEM ITENS
      const dadosAtualizacao = {
        valor_total: resumoFinanceiro.totalFinal,
        percentual_desconto: percentualDesconto,
        valor_desconto: resumoFinanceiro.valorDesconto,
        requer_aprovacao: requerAprovacao,
        observacoes: observacoes.trim() || null,
        status: requerAprovacao ? 'PENDENTE' : 'APROVADA'
        // ⚠️ NÃO enviar itens - manter os que já existem do Passo 3
      };

      console.log('🔄 Dados de atualização simplificados (sem itens):', dadosAtualizacao);

      // Atualizar proposta existente
      await apiService.updateProposta(propostaId, dadosAtualizacao);
      console.log('✅ Proposta atualizada com sucesso para status:', dadosAtualizacao.status);

      // Preparar dados completos para Passo 5
      const dadosCompletos: PropostaComDesconto = {
        ...dadosPropostaToUse,
        percentualDesconto,
        valorDesconto: resumoFinanceiro.valorDesconto,
        totalFinal: resumoFinanceiro.totalFinal,
        requerAprovacao,
        observacoes: observacoes.trim() || undefined
      };

      console.log('✅ Dados preparados para Passo 5:', dadosCompletos);

      // Avançar para o Passo 5
      onProximo(dadosCompletos);

    } catch (error) {
      console.error('❌ Erro ao atualizar proposta:', error);
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // ⚠️ REMOVIDO: Função não é mais necessária
  // const tentarSalvarNovamente = () => {
  //   setError(null);
  //   salvarComoRascunho(dadosPropostaToUse);
  // };



  if (!dadosPropostaToUse) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <Card>
          <div className="text-center py-12">
            <p className="text-gray-500">Dados da proposta não encontrados</p>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <PageHeader
        title="Revisão da Proposta"
        subtitle="Revise todos os dados antes de finalizar a proposta"
      />

      {/* Status de Salvamento */}
      <StatusSalvamento
        estado={estadoSalvamento}
      />

      {/* Dados da Proposta */}
      <Card>
        <DadosProposta dadosProposta={dadosPropostaToUse} />
      </Card>

      {/* Serviços Selecionados */}
      <Card>
        <ServicosSelecionados
          dadosProposta={dadosPropostaToUse}
          resumoFinanceiro={resumoFinanceiro}
          todosServicos={todosServicos}
        />
      </Card>

      {/* Resumo Financeiro */}
      <Card>
        <ResumoFinanceiro
          resumo={resumoFinanceiro}
          percentualDesconto={percentualDesconto}
          onDescontoChange={setDesconto}
        />
      </Card>

      {/* Observações */}
      <Card>
        <FormField
          label="Observações Adicionais"
          helpText="Adicione observações, condições especiais ou informações adicionais para o cliente"
        >
          <Textarea
            value={observacoes}
            onChange={(e) => setObservacoes(e.target.value)}
            placeholder="Adicione observações, condições especiais ou informações adicionais para o cliente..."
            className="h-32"
          />
        </FormField>
      </Card>

      {/* Aviso de Aprovação */}
      {requerAprovacao && (
        <Card className="border-orange-200 bg-orange-50">
          <div className="flex items-start">
            <AlertTriangle className="w-5 h-5 text-orange-600 mt-0.5 mr-3 flex-shrink-0" />
            <div>
              <h3 className="text-sm font-medium text-orange-800">
                Aprovação Administrativa Necessária
              </h3>
              <p className="text-sm text-orange-700 mt-1">
                O desconto de {percentualDesconto}% excede o limite de 20% e requer aprovação do administrador.
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Botões de Navegação */}
      <div className="flex justify-between items-center pt-6 border-t border-gray-200">
        <button
          type="button"
          className="px-4 py-2 border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:outline-none rounded-lg flex items-center space-x-2"
          onClick={onAnterior}
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Anterior</span>
        </button>

        <div className="flex items-center space-x-4">
          {error && (
            <div className="text-red-600 text-sm">
              Erro: {error}
            </div>
          )}

          <Button
            leftIcon={<Save className="w-4 h-4" />}
            onClick={handleProximo}
            disabled={loading || salvandoProposta || !validacaoDesconto.valido}
            loading={salvandoProposta}
          >
            Confirmar e Continuar
          </Button>
        </div>
      </div>
    </div>
  );
};
