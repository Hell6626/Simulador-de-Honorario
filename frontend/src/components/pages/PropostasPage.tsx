import React, { useState, useEffect } from 'react';
import {
  Search,
  Plus,
  Edit2,
  Trash2,
  FileText,
  Clock
} from 'lucide-react';
import { apiService } from '../../services/api';
import { LoadingSpinner, StatusBadge } from '../common';
import { Passo1SelecionarCliente, Passo2ConfiguracoesTributarias, Passo3SelecaoServicos, Passo4RevisaoProposta, Passo5FinalizacaoProposta } from '../propostas/passos';
import { ModalEdicaoProposta } from '../propostas/ModalEdicaoProposta';
import { ModalExclusaoProposta } from '../propostas/ModalExclusaoProposta';
import { ModalEdicaoCompleta } from '../propostas/ModalEdicaoCompleta';
import { HistoricoLogs } from '../propostas/HistoricoLogs';
import { Proposta, PropostaResponse } from '../../types';

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
  extras?: Record<string, any>;
}

// ⚠️ ESTADO PRINCIPAL CORRIGIDO
interface PropostaCompleta {
  // Dados do Cliente (Passo 1)
  cliente: {
    id: number;
    nome: string;
    cpf: string;
    email: string;
    abertura_empresa: boolean;
    ativo: boolean;
    entidades_juridicas?: any[];
  } | null;
  clienteId: number;

  // Configurações Tributárias (Passo 2)
  tipoAtividade: {
    id: number;
    codigo: string;
    nome: string;
    aplicavel_pf: boolean;
    aplicavel_pj: boolean;
    ativo: boolean;
  } | null;
  regimeTributario: {
    id: number;
    codigo: string;
    nome: string;
    aplicavel_pf: boolean;
    aplicavel_pj: boolean;
    requer_definicoes_fiscais: boolean;
    ativo: boolean;
  } | null;
  faixaFaturamento?: {
    id: number;
    nome: string;
    valor_inicial: number;
    valor_final?: number;
    aliquota: number;
    regime_tributario_id: number;
    ativo: boolean;
  } | null;
  tipo_atividade_id: number;
  regime_tributario_id: number;
  faixa_faturamento_id?: number;

  // Serviços (Passo 3)
  servicosSelecionados: ServicoSelecionado[];

  // Desconto e valores (Passo 4)
  percentualDesconto?: number;
  valorDesconto?: number;
  totalFinal?: number;
  requerAprovacao?: boolean;
  observacoes?: string;
}

interface DadosPropostaCompleta {
  cliente: {
    id: number;
    nome: string;
    cpf: string;
    email: string;
    abertura_empresa: boolean;
  };
  tipoAtividade: {
    id: number;
    codigo: string;
    nome: string;
    aplicavel_pf: boolean;
    aplicavel_pj: boolean;
  };
  regimeTributario: {
    id: number;
    codigo: string;
    nome: string;
    aplicavel_pf: boolean;
    aplicavel_pj: boolean;
    requer_definicoes_fiscais: boolean;
  };
  faixaFaturamento?: {
    id: number;
    nome: string;
    valor_inicial: number;
    valor_final?: number;
    aliquota: number;
    regime_tributario_id: number;
  };
  servicosSelecionados: ServicoSelecionado[];
}

interface PropostaComDesconto {
  cliente: {
    id: number;
    nome: string;
    cpf: string;
    email: string;
    abertura_empresa: boolean;
  };
  tipoAtividade: {
    id: number;
    codigo: string;
    nome: string;
    aplicavel_pf: boolean;
    aplicavel_pj: boolean;
  };
  regimeTributario: {
    id: number;
    codigo: string;
    nome: string;
    aplicavel_pf: boolean;
    aplicavel_pj: boolean;
    requer_definicoes_fiscais: boolean;
  };
  faixaFaturamento?: {
    id: number;
    nome: string;
    valor_inicial: number;
    valor_final?: number;
    aliquota: number;
    regime_tributario_id: number;
  };
  servicosSelecionados: ServicoSelecionado[];
  percentualDesconto: number;
  valorDesconto: number;
  totalFinal: number;
  requerAprovacao: boolean;
  observacoes?: string;
}

interface TipoAtividade {
  id: number;
  codigo: string;
  nome: string;
  aplicavel_pf: boolean;
  aplicavel_pj: boolean;
  ativo: boolean;
}

interface PropostasPageProps {
  openModalOnLoad?: boolean;
}

export const PropostasPage: React.FC<PropostasPageProps> = ({ openModalOnLoad = false }) => {
  const [propostas, setPropostas] = useState<Proposta[]>([]);
  const [filteredPropostas, setFilteredPropostas] = useState<Proposta[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [error, setError] = useState('');

  // ⚠️ ESTADO PRINCIPAL CORRIGIDO
  const [dadosProposta, setDadosProposta] = useState<PropostaCompleta>({
    cliente: null,
    clienteId: 0,
    tipoAtividade: null,
    regimeTributario: null,
    faixaFaturamento: null,
    tipo_atividade_id: 0,
    regime_tributario_id: 0,
    faixa_faturamento_id: undefined,
    servicosSelecionados: []
  });

  // Estados para controle de passos
  const [currentStep, setCurrentStep] = useState(0); // 0: Lista, 1: Passo1, 2: Passo2, 3: Passo3, 4: Passo4
  const [selectedClienteId, setSelectedClienteId] = useState<number | null>(null);
  const [configTributarias, setConfigTributarias] = useState<ConfiguracoesTributarias | null>(null);
  const [tipoAtividade, setTipoAtividade] = useState<TipoAtividade | null>(null);
  const [servicosSelecionados, setServicosSelecionados] = useState<ServicoSelecionado[]>([]);
  const [dadosPropostaCompleta, setDadosPropostaCompleta] = useState<DadosPropostaCompleta | null>(null);

  // Estados para modais de edição e exclusão
  const [modalEdicaoOpen, setModalEdicaoOpen] = useState(false);
  const [modalExclusaoOpen, setModalExclusaoOpen] = useState(false);
  const [modalEdicaoCompletaOpen, setModalEdicaoCompletaOpen] = useState(false);
  const [propostaSelecionada, setPropostaSelecionada] = useState<Proposta | null>(null);

  // Estado para modal de histórico
  const [modalHistorico, setModalHistorico] = useState({
    isOpen: false,
    propostaId: 0
  });

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

  // Abrir modal de nova proposta automaticamente se openModalOnLoad for true
  useEffect(() => {
    if (openModalOnLoad) {
      handleNovaPropostaClick();
    }
  }, [openModalOnLoad]);

  const handleNovaPropostaClick = () => {
    setCurrentStep(1);
    // ⚠️ RESETAR: Estado principal da proposta
    setDadosProposta({
      cliente: null,
      clienteId: 0,
      tipoAtividade: null,
      regimeTributario: null,
      faixaFaturamento: null,
      tipo_atividade_id: 0,
      regime_tributario_id: 0,
      faixa_faturamento_id: undefined,
      servicosSelecionados: []
    });
    setSelectedClienteId(null);
    setConfigTributarias(null);
    setTipoAtividade(null);
    setServicosSelecionados([]);
    setDadosPropostaCompleta(null);
  };

  const handleVoltarPasso1 = () => {
    setCurrentStep(0);
    setSelectedClienteId(null);
    setConfigTributarias(null);
    setTipoAtividade(null);
    setServicosSelecionados([]);
    setDadosPropostaCompleta(null);
  };

  // ⚠️ CORRIGIDO: Função onProximo do Passo 1
  const handleProximoPasso1 = (clienteId: number) => {
    // ⚠️ CAPTURAR: Dados completos do cliente, não apenas ID
    const buscarClienteCompleto = async () => {
      try {
        const response = await apiService.getClientes({ id: clienteId });
        const cliente = response.items?.[0] || response?.[0];

        if (cliente) {
          setDadosProposta(prev => ({
            ...prev,
            cliente: cliente,
            clienteId: clienteId
          }));
          setSelectedClienteId(clienteId);
          setCurrentStep(2);
          console.log('Cliente selecionado:', cliente, '- Indo para Passo 2');
        } else {
          console.error('Cliente não encontrado');
          alert('Erro: Cliente não encontrado');
        }
      } catch (error) {
        console.error('Erro ao buscar cliente:', error);
        // Fallback: usar dados básicos
        setDadosProposta(prev => ({
          ...prev,
          cliente: {
            id: clienteId,
            nome: 'Cliente ID: ' + clienteId,
            cpf: '000.000.000-00',
            email: 'cliente@exemplo.com',
            abertura_empresa: false,
            ativo: true
          },
          clienteId: clienteId
        }));
        setSelectedClienteId(clienteId);
        setCurrentStep(2);
      }
    };

    buscarClienteCompleto();
  };

  const handleVoltarPasso2 = () => {
    setCurrentStep(1);
    setConfigTributarias(null);
    setTipoAtividade(null);
    setServicosSelecionados([]);
    setDadosPropostaCompleta(null);
  };

  const handleVoltarPasso3 = () => {
    setCurrentStep(2);
    setServicosSelecionados([]);
    setDadosPropostaCompleta(null);
  };

  // ⚠️ CORRIGIDO: Função onProximo do Passo 3
  const handleProximoPasso3 = (servicos: ServicoSelecionado[]) => {
    setServicosSelecionados(servicos);

    // ⚠️ ATUALIZAR: Estado principal com serviços selecionados
    setDadosProposta(prev => ({
      ...prev,
      servicosSelecionados: servicos
    }));

    // Preparar dados completos para o Passo 4 usando dados reais
    if (dadosProposta.cliente && dadosProposta.tipoAtividade && dadosProposta.regimeTributario) {
      const dadosCompletos: DadosPropostaCompleta = {
        cliente: {
          id: dadosProposta.cliente.id,
          nome: dadosProposta.cliente.nome,
          cpf: dadosProposta.cliente.cpf,
          email: dadosProposta.cliente.email,
          abertura_empresa: dadosProposta.cliente.abertura_empresa
        },
        tipoAtividade: {
          id: dadosProposta.tipoAtividade.id,
          codigo: dadosProposta.tipoAtividade.codigo,
          nome: dadosProposta.tipoAtividade.nome,
          aplicavel_pf: dadosProposta.tipoAtividade.aplicavel_pf,
          aplicavel_pj: dadosProposta.tipoAtividade.aplicavel_pj
        },
        regimeTributario: {
          id: dadosProposta.regimeTributario.id,
          codigo: dadosProposta.regimeTributario.codigo,
          nome: dadosProposta.regimeTributario.nome,
          aplicavel_pf: dadosProposta.regimeTributario.aplicavel_pf,
          aplicavel_pj: dadosProposta.regimeTributario.aplicavel_pj,
          requer_definicoes_fiscais: dadosProposta.regimeTributario.requer_definicoes_fiscais
        },
        faixaFaturamento: dadosProposta.faixaFaturamento ? {
          id: dadosProposta.faixaFaturamento.id,
          nome: dadosProposta.faixaFaturamento.nome,
          valor_inicial: dadosProposta.faixaFaturamento.valor_inicial,
          valor_final: dadosProposta.faixaFaturamento.valor_final,
          aliquota: dadosProposta.faixaFaturamento.aliquota,
          regime_tributario_id: dadosProposta.faixaFaturamento.regime_tributario_id
        } : undefined,
        servicosSelecionados: servicos
      };

      setDadosPropostaCompleta(dadosCompletos);
      setCurrentStep(4);
      console.log('Indo para Passo 4 - Revisão da Proposta com dados reais');
    } else {
      console.error('Dados incompletos para Passo 4:', dadosProposta);
      alert('Erro: Dados incompletos para prosseguir');
    }
  };

  // ⚠️ CORRIGIDO: Função onProximo do Passo 2
  const handleProximoPasso2 = (dados: ConfiguracoesTributarias) => {
    setConfigTributarias(dados);

    // ⚠️ BUSCAR: Dados completos dos objetos selecionados
    const buscarDadosCompletos = async () => {
      try {
        // Buscar tipo de atividade completo
        const responseTipos = await apiService.getTiposAtividade({ ativo: true });
        const tipos = responseTipos.items || responseTipos || [];
        const tipoEncontrado = tipos.find((t: TipoAtividade) => t.id === dados.tipo_atividade_id);

        // Buscar regime tributário completo
        const responseRegimes = await apiService.getRegimesTributarios({ ativo: true });
        const regimes = responseRegimes.items || responseRegimes || [];
        const regimeEncontrado = regimes.find((r: any) => r.id === dados.regime_tributario_id);

        // Buscar faixa de faturamento se houver
        let faixaEncontrada = null;
        if (dados.faixa_faturamento_id) {
          const responseFaixas = await apiService.getFaixasFaturamento({ id: dados.faixa_faturamento_id });
          const faixas = responseFaixas.items || responseFaixas || [];
          faixaEncontrada = faixas.find((f: any) => f.id === dados.faixa_faturamento_id);
        }

        if (tipoEncontrado && regimeEncontrado) {
          // ⚠️ ATUALIZAR: Estado principal com dados completos
          setDadosProposta(prev => ({
            ...prev,
            tipoAtividade: tipoEncontrado,
            regimeTributario: regimeEncontrado,
            faixaFaturamento: faixaEncontrada,
            tipo_atividade_id: dados.tipo_atividade_id,
            regime_tributario_id: dados.regime_tributario_id,
            faixa_faturamento_id: dados.faixa_faturamento_id
          }));

          // ⚠️ CORREÇÃO: Todos os tipos de atividade vão para Passo 3 (seleção de serviços)
          setTipoAtividade(tipoEncontrado);
          setCurrentStep(3);
          console.log('Indo para Passo 3 - Seleção de Serviços');
        } else {
          console.error('Dados não encontrados');
          alert('Erro: Dados não encontrados');
        }
      } catch (error) {
        console.error('Erro ao buscar dados completos:', error);
        // Em caso de erro, assumir que é aplicável para PJ e ir para Passo 3
        setCurrentStep(3);
      }
    };

    buscarDadosCompletos();
  };

  const handleVoltarPasso4 = () => {
    setCurrentStep(3);
    setDadosPropostaCompleta(null);
  };

  const handleProximoPasso4 = (dadosComDesconto: PropostaComDesconto) => {
    console.log('Dados da proposta com desconto:', dadosComDesconto);
    // ⚠️ ATUALIZAR: Estado principal com dados completos incluindo desconto
    setDadosProposta(prev => ({
      ...prev,
      percentualDesconto: dadosComDesconto.percentualDesconto,
      valorDesconto: dadosComDesconto.valorDesconto,
      totalFinal: dadosComDesconto.totalFinal,
      requerAprovacao: dadosComDesconto.requerAprovacao,
      observacoes: dadosComDesconto.observacoes
    }));
    console.log('Estado atualizado para Passo 5:', {
      ...dadosProposta,
      percentualDesconto: dadosComDesconto.percentualDesconto,
      valorDesconto: dadosComDesconto.valorDesconto,
      totalFinal: dadosComDesconto.totalFinal,
      requerAprovacao: dadosComDesconto.requerAprovacao,
      observacoes: dadosComDesconto.observacoes
    });
    setCurrentStep(5);
  };

  const handleVoltarPasso5 = () => {
    setCurrentStep(4);
  };

  const handleFinalizadoPasso5 = (propostaFinalizada: any) => {
    console.log('Proposta finalizada:', propostaFinalizada);
    alert('Proposta finalizada com sucesso!');
    setCurrentStep(0);
    setSelectedClienteId(null);
    setConfigTributarias(null);
    setTipoAtividade(null);
    setServicosSelecionados([]);
    setDadosPropostaCompleta(null);
    // ⚠️ RESETAR: Estado principal da proposta
    setDadosProposta({
      cliente: null,
      clienteId: 0,
      tipoAtividade: null,
      regimeTributario: null,
      faixaFaturamento: null,
      tipo_atividade_id: 0,
      regime_tributario_id: 0,
      faixa_faturamento_id: undefined,
      servicosSelecionados: []
    });
  };

  // Funções para manipulação de edição e exclusão
  const handleEditarProposta = (proposta: Proposta) => {
    setPropostaSelecionada(proposta);
    setModalEdicaoOpen(true);
  };

  const handleEditarPropostaCompleta = (proposta: Proposta) => {
    setPropostaSelecionada(proposta);
    setModalEdicaoCompletaOpen(true);
  };

  const handleExcluirProposta = (proposta: Proposta) => {
    setPropostaSelecionada(proposta);
    setModalExclusaoOpen(true);
  };

  const handleVerHistorico = (proposta: Proposta) => {
    setModalHistorico({ isOpen: true, propostaId: proposta.id });
  };

  const handleSalvarEdicao = async (propostaId: number, dados: Partial<Proposta>) => {
    try {
      await apiService.updateProposta(propostaId, dados);
      await fetchPropostas(currentPage, searchTerm);
      alert('Proposta atualizada com sucesso!');
    } catch (error) {
      console.error('Erro ao atualizar proposta:', error);
      throw error;
    }
  };

  const handleSalvarEdicaoCompleta = async () => {
    try {
      await fetchPropostas(currentPage, searchTerm);
      alert('Proposta atualizada com sucesso!');
    } catch (error) {
      console.error('Erro ao atualizar proposta:', error);
    }
  };

  const handleConfirmarExclusao = async (propostaId: number) => {
    try {
      await apiService.deleteProposta(propostaId);
      await fetchPropostas(currentPage, searchTerm);
      alert('Proposta excluída com sucesso!');
    } catch (error) {
      console.error('Erro ao excluir proposta:', error);
      throw error;
    }
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

  if (currentStep === 3 && tipoAtividade && dadosProposta.regimeTributario) {
    return (
      <Passo3SelecaoServicos
        tipoAtividade={tipoAtividade}
        regimeTributario={dadosProposta.regimeTributario}
        onVoltar={handleVoltarPasso3}
        onProximo={handleProximoPasso3}
      />
    );
  }

  if (currentStep === 4 && dadosPropostaCompleta) {
    return (
      <Passo4RevisaoProposta
        dadosProposta={dadosPropostaCompleta}
        onVoltar={handleVoltarPasso4}
        onProximo={handleProximoPasso4}
      />
    );
  }

  if (currentStep === 5 && dadosProposta.cliente && dadosProposta.tipoAtividade) {
    // ⚠️ PREPARAR: Dados completos para o Passo 5
    const dadosCompletosPasso5: PropostaComDesconto = {
      cliente: dadosProposta.cliente,
      tipoAtividade: dadosProposta.tipoAtividade,
      regimeTributario: dadosProposta.regimeTributario!,
      faixaFaturamento: dadosProposta.faixaFaturamento,
      servicosSelecionados: dadosProposta.servicosSelecionados,
      percentualDesconto: dadosProposta.percentualDesconto || 0,
      valorDesconto: dadosProposta.valorDesconto || 0,
      totalFinal: dadosProposta.totalFinal || 0,
      requerAprovacao: dadosProposta.requerAprovacao || false,
      observacoes: dadosProposta.observacoes
    };

    console.log('Dados completos para Passo 5:', dadosCompletosPasso5);

    return (
      <Passo5FinalizacaoProposta
        dadosProposta={dadosCompletosPasso5}
        dadosSalvos={dadosCompletosPasso5}
        onSalvarProgresso={(dados) => {
          console.log('Salvando progresso do Passo 5:', dados);
          // Atualizar estado principal com dados salvos
          setDadosProposta(prev => {
            const novoEstado = {
              ...prev,
              ...dados
            };
            console.log('Estado atualizado após salvamento:', novoEstado);
            return novoEstado;
          });
        }}
        onVoltar={handleVoltarPasso5}
        onFinalizado={handleFinalizadoPasso5}
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
                        <StatusBadge status={proposta.status} />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {proposta.created_at ? new Date(proposta.created_at).toLocaleDateString('pt-BR') : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {proposta.funcionario_responsavel?.nome || (proposta.funcionario_responsavel_id ? `Funcionário ID: ${proposta.funcionario_responsavel_id}` : 'Não atribuído')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleEditarPropostaCompleta(proposta)}
                            className="text-blue-600 hover:text-blue-900 transition-colors"
                            title="Editar proposta completa"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>

                          {/* Botão de histórico */}
                          <button
                            onClick={() => handleVerHistorico(proposta)}
                            className="text-purple-600 hover:text-purple-900 transition-colors"
                            title="Ver histórico de alterações"
                          >
                            <Clock className="w-4 h-4" />
                          </button>

                          <button
                            onClick={() => handleExcluirProposta(proposta)}
                            className="text-red-600 hover:text-red-900 transition-colors"
                            title="Excluir proposta"
                          >
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

      {/* Modais de Edição e Exclusão */}
      <ModalEdicaoProposta
        proposta={propostaSelecionada}
        isOpen={modalEdicaoOpen}
        onClose={() => setModalEdicaoOpen(false)}
        onSave={handleSalvarEdicao}
      />

      <ModalEdicaoCompleta
        proposta={propostaSelecionada as PropostaResponse}
        isOpen={modalEdicaoCompletaOpen}
        onClose={() => setModalEdicaoCompletaOpen(false)}
        onSaved={handleSalvarEdicaoCompleta}
      />

      <ModalExclusaoProposta
        proposta={propostaSelecionada}
        isOpen={modalExclusaoOpen}
        onClose={() => setModalExclusaoOpen(false)}
        onDelete={handleConfirmarExclusao}
      />

      {/* Modal de Histórico */}
      <HistoricoLogs
        propostaId={modalHistorico.propostaId}
        isOpen={modalHistorico.isOpen}
        onClose={() => setModalHistorico({ isOpen: false, propostaId: 0 })}
      />
    </div>
  );
};
