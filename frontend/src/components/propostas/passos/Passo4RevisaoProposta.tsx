import React, { useState, useEffect } from 'react';
import { ArrowLeft, ArrowRight } from 'lucide-react';
import { LoadingSpinner } from '../../common/LoadingSpinner';
import { apiService } from '../../../services/api';
import { PropostaComDesconto, DadosPropostaCompleta } from '../../../types/propostas';
import { usePropostaCalculations } from '../../../hooks/usePropostaCalculations';

interface Passo4Props {
  dadosProposta: DadosPropostaCompleta;
  propostaId?: number;
  propostaNumero?: string;
  onVoltar: () => void;
  onProximo: (dadosComDesconto: PropostaComDesconto) => void;
  todosServicos: any[];
}

// Função para formatar moeda
const formatarMoeda = (valor: number): string => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(valor);
};

export const Passo4RevisaoProposta: React.FC<Passo4Props> = ({
  dadosProposta,
  propostaId,
  propostaNumero,
  onVoltar,
  onProximo,
  todosServicos
}) => {
  // Estados para desconto
  const [percentualDesconto, setPercentualDesconto] = useState(0);
  const [observacoes, setObservacoes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // ✅ CORREÇÃO: Usar mensalidade dos dados da proposta
  const valorMensalidade = dadosProposta.valor_mensalidade || 0;
  const mensalidadeEncontrada = dadosProposta.mensalidade_encontrada || false;

  console.log('💰 Passo 4 - Dados da mensalidade:', {
    valorMensalidade,
    mensalidadeEncontrada,
    dadosProposta: dadosProposta
  });

  // ✅ CORREÇÃO: Usar hook de cálculos com mensalidade dos dados
  const resumoFinanceiro = usePropostaCalculations(
    dadosProposta,
    percentualDesconto,
    todosServicos,
    valorMensalidade
  );

  const requerAprovacao = percentualDesconto > 20;

  const handleAvancar = async () => {
    if (requerAprovacao && !observacoes.trim()) {
      setError('Observações são obrigatórias para descontos acima de 20%');
      return;
    }

    if (!propostaId) {
      setError('ID da proposta não encontrado');
      return;
    }

    setLoading(true);
    setError('');

    try {
      console.log('✅ Atualizando proposta...');
      console.log('🔄 Proposta ID:', propostaId);
      console.log('🔄 Proposta Número:', propostaNumero);
      console.log('🔄 Novo status:', requerAprovacao ? 'PENDENTE' : 'APROVADA');

      // Atualizar proposta existente
      const dadosAtualizacao = {
        valor_total: resumoFinanceiro.totalFinal,
        percentual_desconto: percentualDesconto,
        valor_desconto: resumoFinanceiro.valorDesconto,
        valor_mensalidade: valorMensalidade,
        requer_aprovacao: requerAprovacao,
        observacoes: observacoes.trim() || null,
        status: requerAprovacao ? 'PENDENTE' : 'APROVADA'
      };

      await apiService.updateProposta(propostaId, dadosAtualizacao);
      console.log('✅ Proposta atualizada com sucesso');

      // Preparar dados completos para Passo 5
      const dadosComDesconto: PropostaComDesconto = {
        ...dadosProposta,
        percentualDesconto,
        valorDesconto: resumoFinanceiro.valorDesconto,
        totalFinal: resumoFinanceiro.totalFinal,
        requerAprovacao,
        observacoes: observacoes.trim() || undefined,
        propostaId,
        propostaNumero
      };

      console.log('✅ Dados preparados para Passo 5:', dadosComDesconto);

      // Avançar para o Passo 5
      onProximo(dadosComDesconto);

    } catch (error) {
      console.error('❌ Erro ao atualizar proposta:', error);
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">

      {/* ✅ HEADER PADRÃO como nos outros passos */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Nova Proposta - Passo 4</h1>
            <p className="text-sm text-gray-500">
              Revise todos os dados antes de finalizar a proposta
            </p>
          </div>
          <button
            onClick={onVoltar}
            className="text-gray-600 hover:text-gray-800 flex items-center space-x-2 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Voltar</span>
          </button>
        </div>
      </div>

      {/* ✅ Erro */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* ✅ DADOS DA PROPOSTA - Layout em grid como Passo 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Card do Cliente */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-4">
            <div className="w-10 h-10 bg-custom-blue-light rounded-lg flex items-center justify-center mr-3">
              <span className="text-custom-blue font-semibold">👤</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Cliente</h3>
          </div>

          <div className="space-y-3">
            <div>
              <p className="text-sm font-medium text-gray-700">Nome</p>
              <p className="text-gray-900">{dadosProposta.cliente.nome}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700">CPF/CNPJ</p>
              <p className="text-gray-900">{dadosProposta.cliente.cpf}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700">Email</p>
              <p className="text-gray-900">{dadosProposta.cliente.email}</p>
            </div>
            <div className="pt-2">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${dadosProposta.cliente.abertura_empresa
                ? 'bg-orange-100 text-orange-800'
                : 'bg-green-100 text-green-800'
                }`}>
                {dadosProposta.cliente.abertura_empresa ? 'Abertura de Empresa' : 'Cliente Existente'}
              </span>
            </div>
          </div>
        </div>

        {/* Card das Configurações Tributárias */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-4">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mr-3">
              <span className="text-green-600 font-semibold">⚖️</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Configurações Tributárias</h3>
          </div>

          <div className="space-y-3">
            <div>
              <p className="text-sm font-medium text-gray-700">Atividade</p>
              <p className="text-gray-900">
                {dadosProposta.tipoAtividade.nome}
                <span className="text-sm text-gray-500 ml-1">({dadosProposta.tipoAtividade.codigo})</span>
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700">Regime Tributário</p>
              <p className="text-gray-900">
                {dadosProposta.regimeTributario.nome}
                <span className="text-sm text-gray-500 ml-1">({dadosProposta.regimeTributario.codigo})</span>
              </p>
            </div>
            {dadosProposta.faixaFaturamento && (
              <div>
                <p className="text-sm font-medium text-gray-700">Faixa de Faturamento</p>
                <p className="text-gray-900">{dadosProposta.faixaFaturamento.nome}</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ✅ CORREÇÃO: MENSALIDADE AUTOMÁTICA - Card */}
      {(valorMensalidade > 0 || mensalidadeEncontrada) && (
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg shadow-sm border border-green-200">
          <div className="p-6">
            <div className="flex items-center mb-4">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mr-3">
                <span className="text-green-600 font-semibold">💰</span>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Mensalidade Automática</h3>
                <p className="text-sm text-gray-600">
                  {dadosProposta.tipoAtividade?.nome} - {dadosProposta.regimeTributario?.nome}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm font-medium text-gray-700">Tipo de Atividade</p>
                <p className="text-gray-900">{dadosProposta.tipoAtividade?.nome}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">Regime Tributário</p>
                <p className="text-gray-900">{dadosProposta.regimeTributario?.nome}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">Valor Mensal</p>
                <p className="text-lg font-semibold text-green-600">
                  {valorMensalidade === 0 ? 'A Combinar' : formatarMoeda(valorMensalidade)}
                </p>
              </div>
            </div>

            {valorMensalidade === 0 && (
              <div className="mt-4 p-3 bg-yellow-100 rounded-lg">
                <p className="text-sm text-yellow-800">
                  <strong>Observação:</strong> Valor será definido manualmente (Pessoa Física ou valores acima de R$ 720.000)
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ✅ SERVIÇOS SELECIONADOS - Card único */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
              <span className="text-purple-600 font-semibold">📋</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Serviços Selecionados</h3>
          </div>
        </div>

        <div className="p-6">
          <div className="space-y-4">
            {dadosProposta.servicosSelecionados.map((servico, index) => (
              <div key={index} className="flex justify-between items-center py-3 border-b border-gray-100 last:border-b-0">
                <div className="flex-1">
                  <p className="font-medium text-gray-900">
                    {todosServicos.find(s => s.id === servico.servico_id)?.nome || `Serviço ID: ${servico.servico_id}`}
                  </p>
                  <p className="text-sm text-gray-500">
                    Quantidade: {servico.quantidade} × {formatarMoeda(servico.valor_unitario)}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-medium text-gray-900">
                    {formatarMoeda(servico.subtotal)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ✅ APLICAR DESCONTO - Card */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center mb-4">
          <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center mr-3">
            <span className="text-yellow-600 font-semibold">%</span>
          </div>
          <h3 className="text-lg font-semibold text-gray-900">Aplicar Desconto</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Desconto (%)
            </label>
            <input
              type="number"
              min="0"
              max="100"
              step="0.01"
              value={percentualDesconto}
              onChange={(e) => setPercentualDesconto(Math.max(0, Math.min(100, Number(e.target.value))))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-custom-blue focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Valor do Desconto
            </label>
            <p className="px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-900">
              -{formatarMoeda(resumoFinanceiro.valorDesconto)}
            </p>
          </div>

          <div className="md:col-span-1">
            {requerAprovacao && (
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
                <p className="text-sm text-orange-800 font-medium">⚠️ Requer Aprovação</p>
                <p className="text-xs text-orange-700">Descontos acima de 20% precisam de aprovação</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ✅ RESUMO FINAL - Card destacado */}
      <div className="bg-gradient-to-r from-custom-blue to-custom-blue-light rounded-lg shadow-lg text-white p-6">
        <div className="flex justify-between items-center">
          <div>
            <p className="text-custom-blue-light text-sm">Total da Proposta</p>
            <p className="text-3xl font-bold">
              {formatarMoeda(resumoFinanceiro.totalFinal)}
            </p>
            {resumoFinanceiro.valorDesconto > 0 && (
              <p className="text-custom-blue-light text-sm">
                Subtotal: {formatarMoeda(resumoFinanceiro.subtotalGeral)}
                (-{percentualDesconto}%)
              </p>
            )}
            {valorMensalidade > 0 && (
              <p className="text-custom-blue-light text-sm">
                Serviços: {formatarMoeda(resumoFinanceiro.subtotalServicos)} + Mensalidade: {formatarMoeda(valorMensalidade)}
              </p>
            )}
          </div>
          <div className="text-right">
            <p className="text-custom-blue-light text-sm">Serviços</p>
            <p className="text-xl font-semibold">{dadosProposta.servicosSelecionados.length}</p>
          </div>
        </div>
      </div>

      {/* ✅ OBSERVAÇÕES - Se necessário */}
      {(requerAprovacao || observacoes) && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Observações Adicionais</h3>
          <textarea
            value={observacoes}
            onChange={(e) => setObservacoes(e.target.value)}
            placeholder={requerAprovacao
              ? "Observações são obrigatórias para descontos acima de 20%..."
              : "Adicione observações, condições especiais ou informações adicionais..."
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-custom-blue focus:border-transparent"
            rows={4}
          />
          {requerAprovacao && !observacoes.trim() && (
            <p className="text-red-600 text-sm mt-1">* Observações são obrigatórias</p>
          )}
        </div>
      )}

      {/* ✅ BOTÕES PADRÃO - Igual aos outros passos (NÃO FIXED) */}
      <div className="flex justify-between items-center pt-6 border-t">
        <button
          onClick={onVoltar}
          className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors flex items-center"
          disabled={loading}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Voltar
        </button>

        <div className="flex items-center space-x-4">
          <div className="text-right">
            <p className="text-sm text-gray-600">Total da Proposta</p>
            <p className="text-xl font-bold text-gray-900">
              {formatarMoeda(resumoFinanceiro.totalFinal)}
            </p>
          </div>
          <button
            onClick={handleAvancar}
            disabled={loading || (requerAprovacao && !observacoes.trim())}
            className="px-6 py-2 bg-custom-blue text-white rounded-lg hover:bg-custom-blue-light transition-colors flex items-center disabled:opacity-50"
          >
            {loading ? (
              <>
                <LoadingSpinner size="sm" />
                <span className="ml-2">Salvando...</span>
              </>
            ) : (
              <>
                <span>Finalizar</span>
                <ArrowRight className="w-4 h-4 ml-2" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
