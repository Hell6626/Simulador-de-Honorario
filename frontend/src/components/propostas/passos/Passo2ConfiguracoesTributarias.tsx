import React, { useState, useEffect } from 'react';
import { 
  ArrowLeft,
  Building,
  Calculator,
  TrendingUp,
  Check,
  AlertCircle
} from 'lucide-react';
import { apiService } from '../../../services/api';
import { LoadingSpinner } from '../../common/LoadingSpinner';

interface TipoAtividade {
  id: number;
  codigo: string;
  nome: string;
  aplicavel_pf: boolean;
  aplicavel_pj: boolean;
  ativo: boolean;
}

interface RegimeTributario {
  id: number;
  codigo: string;
  nome: string;
  descricao: string;
  aplicavel_pf: boolean;
  aplicavel_pj: boolean;
  ativo: boolean;
}

interface FaixaFaturamento {
  id: number;
  regime_tributario_id: number;
  valor_inicial: number;
  valor_final: number | null;
  aliquota: number;
  ativo: boolean;
}

interface ConfiguracoesTributarias {
  tipo_atividade_id: number;
  regime_tributario_id: number;
  faixa_faturamento_id: number | null; // ⚠️ Pode ser null se não houver faixas
}

interface Passo2Props {
  clienteId: number;
  onVoltar: () => void;
  onProximo: (dados: ConfiguracoesTributarias) => void;
}

// Função para formatar moeda
const formatarMoeda = (valor: number): string => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(valor);
};

export const Passo2ConfiguracoesTributarias: React.FC<Passo2Props> = ({
  onVoltar,
  onProximo
}) => {
  const [abaAtiva, setAbaAtiva] = useState(0);
  const [selectedTipoAtividade, setSelectedTipoAtividade] = useState<number | null>(null);
  const [selectedRegimeTributario, setSelectedRegimeTributario] = useState<number | null>(null);
  const [selectedFaixaFaturamento, setSelectedFaixaFaturamento] = useState<number | null>(null);
  
  const [tiposAtividade, setTiposAtividade] = useState<TipoAtividade[]>([]);
  const [regimesCompativeis, setRegimesCompativeis] = useState<RegimeTributario[]>([]);
  const [faixasFaturamento, setFaixasFaturamento] = useState<FaixaFaturamento[]>([]);
  
  const [loading, setLoading] = useState(false);
  const [loadingRegimes, setLoadingRegimes] = useState(false);
  const [loadingFaixas, setLoadingFaixas] = useState(false);
  const [error, setError] = useState('');

  // ⚠️ NOVA LÓGICA: Verificar se há faixas disponíveis
  const hasFaixasFaturamento = faixasFaturamento.length > 0;

  // ⚠️ NOVA LÓGICA: Condições para prosseguir
  const podeProximo = React.useMemo(() => {
    const temTipoAtividade = !!selectedTipoAtividade;
    const temRegimeTributario = !!selectedRegimeTributario;
    
    // Se não há faixas disponíveis, não precisa selecionar
    if (!hasFaixasFaturamento) {
      return temTipoAtividade && temRegimeTributario;
    }
    
    // Se há faixas disponíveis, precisa selecionar uma
    const temFaixaFaturamento = !!selectedFaixaFaturamento;
    return temTipoAtividade && temRegimeTributario && temFaixaFaturamento;
  }, [selectedTipoAtividade, selectedRegimeTributario, selectedFaixaFaturamento, hasFaixasFaturamento]);

  // Carregar tipos de atividade ao montar o componente
  useEffect(() => {
    carregarTiposAtividade();
  }, []);

  // Carregar regimes compatíveis quando tipo de atividade for selecionado
  useEffect(() => {
    if (selectedTipoAtividade) {
      carregarRegimesCompativeis(selectedTipoAtividade);
    } else {
      setRegimesCompativeis([]);
    }
  }, [selectedTipoAtividade]);

  // Carregar faixas de faturamento quando regime tributário for selecionado
  useEffect(() => {
    if (selectedRegimeTributario) {
      carregarFaixasFaturamento(selectedRegimeTributario);
    } else {
      setFaixasFaturamento([]);
    }
  }, [selectedRegimeTributario]);

  // Navegar automaticamente para a aba de faixas se houver faixas disponíveis
  useEffect(() => {
    if (selectedRegimeTributario && hasFaixasFaturamento && abaAtiva === 1) {
      setAbaAtiva(2);
    }
  }, [selectedRegimeTributario, hasFaixasFaturamento, abaAtiva]);

  const carregarTiposAtividade = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await apiService.getTiposAtividade({ ativo: true });
      setTiposAtividade(response.items || response || []);
    } catch (err: unknown) {
      console.error('Erro ao carregar tipos de atividade:', err);
      
      // Dados mockados para demonstração
      const errorMessage = (err as Error)?.message || '';
      if (errorMessage.includes('401') || errorMessage.includes('UNAUTHORIZED') || errorMessage.includes('Failed to fetch')) {
        setError('API não disponível. Usando dados de demonstração.');
        
        const tiposMockados: TipoAtividade[] = [
          {
            id: 1,
            codigo: 'COM-VAR',
            nome: 'Comércio Varejista',
            aplicavel_pf: false,
            aplicavel_pj: true,
            ativo: true
          },
          {
            id: 2,
            codigo: 'SERV-GER',
            nome: 'Prestação de Serviços',
            aplicavel_pf: true,
            aplicavel_pj: true,
            ativo: true
          },
          {
            id: 3,
            codigo: 'IND-GER',
            nome: 'Indústria',
            aplicavel_pf: false,
            aplicavel_pj: true,
            ativo: true
          },
          {
            id: 4,
            codigo: 'CONS-GER',
            nome: 'Consultoria',
            aplicavel_pf: true,
            aplicavel_pj: true,
            ativo: true
          }
        ];
        
        setTiposAtividade(tiposMockados);
      } else {
        setError(errorMessage || 'Erro ao carregar tipos de atividade');
        setTiposAtividade([]);
      }
    } finally {
      setLoading(false);
    }
  };

  const carregarRegimesCompativeis = async (tipoAtividadeId: number) => {
    setLoadingRegimes(true);
    
    try {
      // Buscar regimes compatíveis com o tipo de atividade
      const response = await apiService.getRegimesTributarios({ 
        ativo: true,
        atividades_ids: [tipoAtividadeId]
      });
      setRegimesCompativeis(response.items || response || []);
    } catch (err: unknown) {
      console.error('Erro ao carregar regimes:', err);
      
      // Dados mockados para demonstração
      const regimesMockados: RegimeTributario[] = [
        {
          id: 1,
          codigo: 'SIMPLES',
          nome: 'Simples Nacional',
          descricao: 'Regime simplificado para pequenas empresas',
          aplicavel_pf: false,
          aplicavel_pj: true,
          ativo: true
        },
        {
          id: 2,
          codigo: 'LUCRO-PRESUMIDO',
          nome: 'Lucro Presumido',
          descricao: 'Regime baseado em presunção de lucro',
          aplicavel_pf: true,
          aplicavel_pj: true,
          ativo: true
        },
        {
          id: 3,
          codigo: 'LUCRO-REAL',
          nome: 'Lucro Real',
          descricao: 'Regime baseado no lucro real da empresa',
          aplicavel_pf: false,
          aplicavel_pj: true,
          ativo: true
        }
      ];
      
      setRegimesCompativeis(regimesMockados);
    } finally {
      setLoadingRegimes(false);
    }
  };

  // ⚠️ ATUALIZADA: Função para carregar faixas
  const carregarFaixasFaturamento = async (regimeTributarioId: number) => {
    setLoadingFaixas(true);
    
    try {
      const response = await apiService.getFaixasFaturamento({ regime_tributario_id: regimeTributarioId });
      const faixas = response.items || response || [];
      
      setFaixasFaturamento(faixas);
      
      // Log para debugging
      console.log(`Regime ${regimeTributarioId}: ${faixas.length} faixas encontradas`);
      
    } catch (err: unknown) {
      console.error('Erro ao carregar faixas:', err);
      
      // Dados mockados para demonstração
      const faixasMockadas: FaixaFaturamento[] = [
        {
          id: 1,
          regime_tributario_id: regimeTributarioId,
          valor_inicial: 0,
          valor_final: 180000,
          aliquota: 4.5,
          ativo: true
        },
        {
          id: 2,
          regime_tributario_id: regimeTributarioId,
          valor_inicial: 180000.01,
          valor_final: 360000,
          aliquota: 7.5,
          ativo: true
        },
        {
          id: 3,
          regime_tributario_id: regimeTributarioId,
          valor_inicial: 360000.01,
          valor_final: 720000,
          aliquota: 10.5,
          ativo: true
        },
        {
          id: 4,
          regime_tributario_id: regimeTributarioId,
          valor_inicial: 720000.01,
          valor_final: null,
          aliquota: 14.5,
          ativo: true
        }
      ];
      
      setFaixasFaturamento(faixasMockadas);
    } finally {
      setLoadingFaixas(false);
    }
  };

  const handleTipoAtividadeChange = (tipoAtividadeId: number) => {
    setSelectedTipoAtividade(tipoAtividadeId);
    setSelectedRegimeTributario(null);
    setSelectedFaixaFaturamento(null);
    
    // Navegar automaticamente para a próxima aba
    setAbaAtiva(1);
  };

  const handleRegimeTributarioChange = async (regimeId: number) => {
    setSelectedRegimeTributario(regimeId);
    setSelectedFaixaFaturamento(null);
    
    // Carregar faixas de faturamento
    await carregarFaixasFaturamento(regimeId);
    
    // Navegar para a aba 3 se houver faixas (será verificado no useEffect)
  };

  const handleProximo = () => {
    if (podeProximo) {
      onProximo({
        tipo_atividade_id: selectedTipoAtividade!,
        regime_tributario_id: selectedRegimeTributario!,
        faixa_faturamento_id: selectedFaixaFaturamento // Pode ser null
      });
    }
  };

  const getTabState = (tabIndex: number) => {
    switch (tabIndex) {
      case 0: // Tipo de Atividade
        return { enabled: true, required: true };
      
      case 1: // Regime Tributário
        return { 
          enabled: !!selectedTipoAtividade,
          required: true,
          tooltip: !selectedTipoAtividade ? "Selecione um tipo de atividade primeiro" : ""
        };
      
      case 2: // Faixa de Faturamento
        return { 
          enabled: !!selectedRegimeTributario && hasFaixasFaturamento,
          required: false, // ⚠️ NÃO é mais obrigatória
          tooltip: !selectedRegimeTributario 
            ? "Selecione um regime tributário primeiro" 
            : !hasFaixasFaturamento 
              ? "Este regime não possui faixas de faturamento configuradas"
              : ""
        };
      
      default:
        return { enabled: false, required: false };
    }
  };

  return (
    <div>
      {/* Header da Página */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Nova Proposta - Passo 2</h1>
            <p className="text-sm text-gray-500">Configure as informações tributárias</p>
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

      {/* Erro */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* ⚠️ NOVO: Indicadores de Progresso com Lógica Condicional */}
      <div className="flex items-center justify-center space-x-4 mb-6">
        {/* Tipo de Atividade - Sempre obrigatório */}
        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
          selectedTipoAtividade ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-600'
        }`}>
          {selectedTipoAtividade ? <Check className="w-4 h-4" /> : '1'}
        </div>
        <div className={`h-1 w-16 ${selectedTipoAtividade ? 'bg-green-500' : 'bg-gray-300'}`} />
        
        {/* Regime Tributário - Sempre obrigatório */}
        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
          selectedRegimeTributario ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-600'
        }`}>
          {selectedRegimeTributario ? <Check className="w-4 h-4" /> : '2'}
        </div>
        
        {/* Faixa de Faturamento - Condicional */}
        {hasFaixasFaturamento && (
          <>
            <div className={`h-1 w-16 ${selectedRegimeTributario ? 'bg-green-500' : 'bg-gray-300'}`} />
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
              selectedFaixaFaturamento ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-600'
            }`}>
              {selectedFaixaFaturamento ? <Check className="w-4 h-4" /> : '3'}
            </div>
          </>
        )}
        
        {/* Indicador quando não há faixas */}
        {!hasFaixasFaturamento && selectedRegimeTributario && (
          <>
            <div className="h-1 w-16 bg-yellow-300" />
            <div className="w-8 h-8 rounded-full flex items-center justify-center bg-yellow-100 text-yellow-700">
              <span className="text-xs">N/A</span>
            </div>
          </>
        )}
      </div>

      {/* Abas */}
      <div className="flex border-b border-gray-200 mb-6">
        <button
          onClick={() => setAbaAtiva(0)}
          className={`flex items-center space-x-2 px-6 py-3 text-sm font-medium transition-colors ${
            abaAtiva === 0
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <Building className="w-4 h-4" />
          <span>Tipo de Atividade</span>
        </button>
        <button
          onClick={() => setAbaAtiva(1)}
          disabled={!getTabState(1).enabled}
          className={`flex items-center space-x-2 px-6 py-3 text-sm font-medium transition-colors ${
            abaAtiva === 1
              ? 'text-blue-600 border-b-2 border-blue-600'
              : getTabState(1).enabled
              ? 'text-gray-500 hover:text-gray-700'
              : 'text-gray-300 cursor-not-allowed'
          }`}
          title={getTabState(1).tooltip}
        >
          <Calculator className="w-4 h-4" />
          <span>Regime Tributário</span>
        </button>
        <button
          onClick={() => setAbaAtiva(2)}
          disabled={!getTabState(2).enabled}
          className={`flex items-center space-x-2 px-6 py-3 text-sm font-medium transition-colors ${
            abaAtiva === 2
              ? 'text-blue-600 border-b-2 border-blue-600'
              : getTabState(2).enabled
              ? 'text-gray-500 hover:text-gray-700'
              : 'text-gray-300 cursor-not-allowed'
          }`}
          title={getTabState(2).tooltip}
        >
          <TrendingUp className="w-4 h-4" />
          <span>Faixa de Faturamento</span>
        </button>
      </div>

      {/* Conteúdo das Abas */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
        {/* Aba Tipo de Atividade */}
        {abaAtiva === 0 && (
          <div className="p-6">
            {loading ? (
              <div className="flex items-center justify-center py-16">
                <div className="flex items-center">
                  <LoadingSpinner size="md" />
                  <span className="ml-3 text-gray-500">Carregando tipos de atividade...</span>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {tiposAtividade.map((tipo) => (
                  <div key={tipo.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <label className="flex items-center cursor-pointer">
                      <input
                        type="radio"
                        name="tipo_atividade"
                        value={tipo.id}
                        checked={selectedTipoAtividade === tipo.id}
                        onChange={() => handleTipoAtividadeChange(tipo.id)}
                        className="h-5 w-5 text-blue-600 focus:ring-blue-500"
                      />
                      <div className="ml-4 flex-1">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-lg font-medium text-gray-900">{tipo.nome}</p>
                            <p className="text-sm text-gray-500">Código: {tipo.codigo}</p>
                          </div>
                          <div className="text-right">
                            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                              Aplicável: {[tipo.aplicavel_pf && 'PF', tipo.aplicavel_pj && 'PJ'].filter(Boolean).join(', ')}
                            </span>
                          </div>
                        </div>
                      </div>
                    </label>
                  </div>
                ))}
              </div>
            )}

            {tiposAtividade.length === 0 && !loading && (
              <div className="text-center py-16">
                <Building className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-lg text-gray-500 mb-2">Nenhum tipo de atividade encontrado</p>
                <p className="text-sm text-gray-400">Entre em contato com o suporte</p>
              </div>
            )}
          </div>
        )}

        {/* Aba Regime Tributário */}
        {abaAtiva === 1 && (
          <div className="p-6">
            {loadingRegimes ? (
              <div className="flex items-center justify-center py-16">
                <div className="flex items-center">
                  <LoadingSpinner size="md" />
                  <span className="ml-3 text-gray-500">Carregando regimes tributários...</span>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {regimesCompativeis.map((regime) => (
                  <div key={regime.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <label className="flex items-center cursor-pointer">
                      <input
                        type="radio"
                        name="regime_tributario"
                        value={regime.id}
                        checked={selectedRegimeTributario === regime.id}
                        onChange={() => handleRegimeTributarioChange(regime.id)}
                        className="h-5 w-5 text-blue-600 focus:ring-blue-500"
                      />
                      <div className="ml-4 flex-1">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-lg font-medium text-gray-900">{regime.nome}</p>
                            <p className="text-sm text-gray-500">Código: {regime.codigo}</p>
                            {regime.descricao && (
                              <p className="text-sm text-gray-600 mt-1">{regime.descricao}</p>
                            )}
                          </div>
                          <div className="text-right">
                            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                              {[regime.aplicavel_pf && 'PF', regime.aplicavel_pj && 'PJ'].filter(Boolean).join(', ')}
                            </span>
                          </div>
                        </div>
                      </div>
                    </label>
                  </div>
                ))}
              </div>
            )}

            {regimesCompativeis.length === 0 && !loadingRegimes && (
              <div className="text-center py-16">
                <Calculator className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-lg text-gray-500 mb-2">
                  {selectedTipoAtividade ? 'Nenhum regime tributário compatível encontrado' : 'Selecione um tipo de atividade primeiro'}
                </p>
                <p className="text-sm text-gray-400">
                  {selectedTipoAtividade ? 'Entre em contato com o suporte' : 'Volte para a aba anterior e selecione um tipo de atividade'}
                </p>
              </div>
            )}
          </div>
        )}

        {/* ⚠️ NOVA: Aba Faixa de Faturamento com Estado Vazio */}
        {abaAtiva === 2 && (
          <div className="p-6">
            {loadingFaixas ? (
              <div className="flex items-center justify-center py-16">
                <div className="flex items-center">
                  <LoadingSpinner size="md" />
                  <span className="ml-3 text-gray-500">Carregando faixas de faturamento...</span>
                </div>
              </div>
            ) : hasFaixasFaturamento ? (
              <div className="space-y-4">
                {faixasFaturamento.map((faixa) => (
                  <div key={faixa.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <label className="flex items-center cursor-pointer">
                      <input
                        type="radio"
                        name="faixa_faturamento"
                        value={faixa.id}
                        checked={selectedFaixaFaturamento === faixa.id}
                        onChange={() => setSelectedFaixaFaturamento(faixa.id)}
                        className="h-5 w-5 text-blue-600 focus:ring-blue-500"
                      />
                      <div className="ml-4 flex-1">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-lg font-medium text-gray-900">
                              {formatarMoeda(faixa.valor_inicial)} 
                              {faixa.valor_final ? ` até ${formatarMoeda(faixa.valor_final)}` : ' ou mais'}
                            </p>
                            <p className="text-sm text-gray-500">
                              Alíquota: {faixa.aliquota}%
                            </p>
                          </div>
                          <div className="text-right">
                            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
                              {faixa.aliquota}%
                            </span>
                          </div>
                        </div>
                      </div>
                    </label>
                  </div>
                ))}
              </div>
            ) : (
              // Estado quando não há faixas de faturamento
              <div className="text-center py-16">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl text-gray-400">📊</span>
                </div>
                <p className="text-lg text-gray-500 mb-2">
                  Nenhuma faixa de faturamento configurada
                </p>
                <p className="text-sm text-gray-400">
                  Este regime tributário não possui faixas de faturamento específicas.
                  Você pode continuar para o próximo passo.
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Botões de Ação Fixos */}
      <div className="fixed bottom-0 left-64 right-0 bg-white border-t border-gray-200 px-6 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4">
            {selectedTipoAtividade && (
              <span className="text-sm text-gray-600">
                Tipo: {tiposAtividade.find(t => t.id === selectedTipoAtividade)?.nome}
              </span>
            )}
            {selectedRegimeTributario && (
              <span className="text-sm text-gray-600">
                Regime: {regimesCompativeis.find(r => r.id === selectedRegimeTributario)?.nome}
              </span>
            )}
            {selectedFaixaFaturamento && hasFaixasFaturamento && (
              <span className="text-sm text-gray-600">
                Faixa: {formatarMoeda(faixasFaturamento.find(f => f.id === selectedFaixaFaturamento)?.valor_inicial || 0)}
              </span>
            )}
            {selectedRegimeTributario && !hasFaixasFaturamento && (
              <span className="text-sm text-yellow-600">
                Sem faixas específicas
              </span>
            )}
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={onVoltar}
              className="px-6 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Anterior
            </button>
            <button
              onClick={handleProximo}
              disabled={!podeProximo}
              className="px-6 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
            >
              <span>Próximo</span>
              {!podeProximo && <AlertCircle className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
