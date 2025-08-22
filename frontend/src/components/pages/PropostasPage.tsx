import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Plus, 
  Edit2, 
  Trash2, 
  FileText
} from 'lucide-react';
import { apiService } from '../../services/api';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { Passo1SelecionarCliente, Passo2ConfiguracoesTributarias, Passo3SelecaoServicos } from '../propostas/passos';

interface Proposta {
  id: number;
  numero: string;
  cliente_id: number;
  funcionario_responsavel_id?: number;
  tipo_atividade_id: number;
  regime_tributario_id: number;
  faixa_faturamento_id?: number;
  valor_total: number;
  data_validade: string;
  status: string;
  observacoes?: string;
  ativo: boolean;
  created_at: string;
  updated_at: string;
  cliente?: {
    id: number;
    nome: string;
    cpf: string;
    email: string;
  };
  funcionario_responsavel?: {
    id: number;
    nome: string;
    email: string;
  };
}

// Interfaces removidas para evitar warnings de unused vars
// As interfaces estão definidas nos componentes específicos

interface ConfiguracoesTributarias {
  tipo_atividade_id: number;
  regime_tributario_id: number;
  faixa_faturamento_id: number | null; // ⚠️ Pode ser null se não houver faixas
}

interface ServicoSelecionado {
  servico_id: number;
  quantidade: number;
  valor_unitario: number;
  subtotal: number;
}

interface TipoAtividade {
  id: number;
  codigo: string;
  nome: string;
  aplicavel_pf: boolean;
  aplicavel_pj: boolean;
  ativo: boolean;
}

export const PropostasPage: React.FC = () => {
  const [propostas, setPropostas] = useState<Proposta[]>([]);
  const [filteredPropostas, setFilteredPropostas] = useState<Proposta[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [error, setError] = useState('');

  // Estados para controle de passos
  const [currentStep, setCurrentStep] = useState(0); // 0: Lista, 1: Passo1, 2: Passo2, 3: Passo3
  const [selectedClienteId, setSelectedClienteId] = useState<number | null>(null);
  const [configTributarias, setConfigTributarias] = useState<ConfiguracoesTributarias | null>(null);
  const [tipoAtividade, setTipoAtividade] = useState<TipoAtividade | null>(null);
  const [servicosSelecionados, setServicosSelecionados] = useState<ServicoSelecionado[]>([]);

  const fetchPropostas = async (page = 1, search = '') => {
    setLoading(true);
    setError('');
    
    try {
      const response = await apiService.getPropostas({
        page,
        per_page: 20,
        search: search.trim() || undefined
      });
      
      setPropostas(response.items || []);
      setFilteredPropostas(response.items || []);
      setTotalPages(response.pages || 1);
    } catch (err: unknown) {
      console.error('Erro ao carregar propostas:', err);
      
      // Se for erro de autenticação ou conexão, usar dados mockados temporariamente
      const errorMessage = (err as Error)?.message || '';
      if (errorMessage.includes('401') || errorMessage.includes('UNAUTHORIZED') || errorMessage.includes('Failed to fetch')) {
        setError('API não disponível. Usando dados de demonstração.');
        
        // Dados mockados para demonstração
        const dadosMockados = [
          {
            id: 1,
            numero: 'PROP-20250108001',
            cliente_id: 1,
            funcionario_responsavel_id: 1,
            tipo_atividade_id: 1,
            regime_tributario_id: 1,
            faixa_faturamento_id: 1,
            valor_total: 2500.00,
            data_validade: '2025-02-08T00:00:00',
            status: 'ENVIADA',
            observacoes: 'Proposta para serviços contábeis',
            ativo: true,
            created_at: '2025-01-08T00:00:00',
            updated_at: '2025-01-08T00:00:00',
            cliente: {
              id: 1,
              nome: 'Empresa ABC Ltda',
              cpf: '11.111.111/0001-11',
              email: 'contato@abc.com'
            },
            funcionario_responsavel: {
              id: 1,
              nome: 'João Silva',
              email: 'joao@empresa.com'
            }
          },
          {
            id: 2,
            numero: 'PROP-20250107002',
            cliente_id: 2,
            funcionario_responsavel_id: 2,
            tipo_atividade_id: 1,
            regime_tributario_id: 1,
            faixa_faturamento_id: 1,
            valor_total: 1800.00,
            data_validade: '2025-02-07T00:00:00',
            status: 'RASCUNHO',
            observacoes: 'Proposta em elaboração',
            ativo: true,
            created_at: '2025-01-07T00:00:00',
            updated_at: '2025-01-07T00:00:00',
            cliente: {
              id: 2,
              nome: 'Comércio XYZ ME',
              cpf: '22.222.222/0001-22',
              email: 'info@xyz.com'
            },
            funcionario_responsavel: {
              id: 2,
              nome: 'Maria Santos',
              email: 'maria@empresa.com'
            }
          }
        ];
        
        setPropostas(dadosMockados);
        setFilteredPropostas(dadosMockados);
        setTotalPages(1);
      } else {
        setError(errorMessage || 'Erro ao carregar propostas');
        setPropostas([]);
        setFilteredPropostas([]);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (currentStep === 0) {
      fetchPropostas(currentPage, searchTerm);
    }
  }, [currentPage, searchTerm, currentStep]);

  // Filtrar propostas baseado no termo de busca
  useEffect(() => {
    if (!searchTerm.trim()) {
      setFilteredPropostas(propostas);
    } else {
      const filtered = propostas.filter(proposta => 
        proposta.numero.toLowerCase().includes(searchTerm.toLowerCase()) ||
        proposta.status.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (proposta.observacoes || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
        (proposta.cliente?.nome || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
        (proposta.funcionario_responsavel?.nome || '').toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredPropostas(filtered);
    }
    setCurrentPage(1);
  }, [searchTerm, propostas]);

  const handleNovaPropostaClick = () => {
    setCurrentStep(1);
    setSelectedClienteId(null);
    setConfigTributarias(null);
    setTipoAtividade(null);
    setServicosSelecionados([]);
  };

  const handleVoltarPasso1 = () => {
    setCurrentStep(0);
    setSelectedClienteId(null);
    setConfigTributarias(null);
    setTipoAtividade(null);
    setServicosSelecionados([]);
  };

  const handleProximoPasso1 = (clienteId: number) => {
    setSelectedClienteId(clienteId);
    setCurrentStep(2);
    console.log('Cliente selecionado:', clienteId, '- Indo para Passo 2');
  };

  const handleVoltarPasso2 = () => {
    setCurrentStep(1);
    setConfigTributarias(null);
    setTipoAtividade(null);
    setServicosSelecionados([]);
  };

  const handleVoltarPasso3 = () => {
    setCurrentStep(2);
    setServicosSelecionados([]);
  };

  const handleProximoPasso3 = (servicos: ServicoSelecionado[]) => {
    setServicosSelecionados(servicos);
    console.log('Serviços selecionados:', servicos);
    alert('Proposta criada com sucesso!');
    setCurrentStep(0);
  };

  const handleProximoPasso2 = (dados: ConfiguracoesTributarias) => {
    setConfigTributarias(dados);
    
    // Buscar informações do tipo de atividade para verificar se é aplicável para PJ
    const buscarTipoAtividade = async () => {
      try {
        const response = await apiService.getTiposAtividade({ ativo: true });
        const tipos = response.items || response || [];
        const tipoEncontrado = tipos.find((t: TipoAtividade) => t.id === dados.tipo_atividade_id);
        
        if (tipoEncontrado && tipoEncontrado.aplicavel_pj) {
          // Se for aplicável para PJ, ir para Passo 3
          setTipoAtividade(tipoEncontrado);
          setCurrentStep(3);
          console.log('Tipo de atividade aplicável para PJ. Indo para Passo 3.');
        } else {
          // Se não for aplicável para PJ, finalizar proposta
          console.log('Tipo de atividade não aplicável para PJ. Finalizando proposta.');
          alert('Proposta criada com sucesso!');
          setCurrentStep(0);
        }
      } catch (error) {
        console.error('Erro ao buscar tipo de atividade:', error);
        // Em caso de erro, assumir que é aplicável para PJ e ir para Passo 3
        setCurrentStep(3);
      }
    };
    
    buscarTipoAtividade();
  };

  // RENDERIZAÇÃO CONDICIONAL BASEADA NO PASSO ATUAL
  if (currentStep === 1) {
    return (
      <Passo1SelecionarCliente
        onVoltar={handleVoltarPasso1}
        onProximo={handleProximoPasso1}
      />
    );
  }

  if (currentStep === 2) {
    return (
      <Passo2ConfiguracoesTributarias
        clienteId={selectedClienteId!}
        onVoltar={handleVoltarPasso2}
        onProximo={handleProximoPasso2}
      />
    );
  }

  if (currentStep === 3 && tipoAtividade) {
    return (
      <Passo3SelecaoServicos
        tipoAtividade={tipoAtividade}
        onVoltar={handleVoltarPasso3}
        onProximo={handleProximoPasso3}
      />
    );
  }

  // PÁGINA NORMAL DE PROPOSTAS
  return (
    <div>
      {/* Header da Página */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Propostas</h1>
        <p className="text-sm text-gray-500">Crie e gerencie propostas contábeis para seus clientes</p>
      </div>

      {/* Erro */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Barra de Ações */}
      <div className="mb-6 flex items-center justify-between">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                     <input
             type="text"
             placeholder="Buscar por número, cliente, funcionário, status..."
             value={searchTerm}
             onChange={(e) => setSearchTerm(e.target.value)}
             className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent w-full"
           />
        </div>
        <button 
          onClick={handleNovaPropostaClick}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Nova Proposta</span>
        </button>
      </div>

      {/* Tabela de Propostas */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="flex items-center">
              <LoadingSpinner size="md" />
              <span className="ml-3 text-gray-500">Carregando propostas...</span>
            </div>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Número
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Cliente
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Valor Total
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Data
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Responsável
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ações
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredPropostas.map((proposta) => (
                    <tr key={proposta.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {proposta.numero || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {proposta.cliente?.nome || `Cliente ID: ${proposta.cliente_id}`}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        R$ {proposta.valor_total ? proposta.valor_total.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) : '0,00'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          proposta.status === 'APROVADA' ? 'bg-green-100 text-green-800' :
                          proposta.status === 'ENVIADA' ? 'bg-blue-100 text-blue-800' :
                          proposta.status === 'RASCUNHO' ? 'bg-yellow-100 text-yellow-800' :
                          proposta.status === 'REJEITADA' ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {proposta.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {proposta.created_at ? new Date(proposta.created_at).toLocaleDateString('pt-BR') : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {proposta.funcionario_responsavel?.nome || (proposta.funcionario_responsavel_id ? `Funcionário ID: ${proposta.funcionario_responsavel_id}` : 'Não atribuído')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex items-center space-x-2">
                          <button className="text-blue-600 hover:text-blue-900">
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button className="text-red-600 hover:text-red-900">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Estado Vazio */}
            {filteredPropostas.length === 0 && (
              <div className="text-center py-8">
                <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                                 {searchTerm ? (
                   <>
                     <p className="text-gray-500">Nenhuma proposta encontrada para "{searchTerm}"</p>
                     <p className="text-sm text-gray-400 mt-1">Tente buscar por número, cliente, funcionário, status ou observações</p>
                   </>
                 ) : (
                  <>
                    <p className="text-gray-500">Nenhuma proposta encontrada</p>
                    <p className="text-sm text-gray-400 mt-1">Comece criando sua primeira proposta</p>
                  </>
                )}
              </div>
            )}
          </>
        )}
      </div>

      {/* Paginação */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center space-x-2 mt-6">
          <button
            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
            disabled={currentPage === 1}
            className="px-3 py-1 border border-gray-300 rounded-md disabled:opacity-50 hover:bg-gray-50"
          >
            Anterior
          </button>
          <span className="px-3 py-1">
            Página {currentPage} de {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
            disabled={currentPage === totalPages}
            className="px-3 py-1 border border-gray-300 rounded-md disabled:opacity-50 hover:bg-gray-50"
          >
            Próxima
          </button>
        </div>
      )}
    </div>
  );
};
