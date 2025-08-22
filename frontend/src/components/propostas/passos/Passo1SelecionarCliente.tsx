import React, { useState, useEffect, useCallback } from 'react';
import {
  Search,
  Plus,
  Users,
  ArrowLeft,
  Save,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { apiService } from '../../../services/api';
import { LoadingSpinner } from '../../common/LoadingSpinner';
import { ModalCadastroCliente } from './ModalCadastroCliente';

interface EntidadeJuridica {
  id: number;
  nome: string;
  cnpj: string;
  tipo: string;
  cliente_id: number;
}

interface Cliente {
  id: number;
  nome: string;
  cpf: string;
  email: string;
  abertura_empresa: boolean;
  ativo: boolean;
  entidades_juridicas?: EntidadeJuridica[];
}

interface Passo1Props {
  onVoltar: () => void;
  onProximo: (clienteId: number) => void;
  // ⚠️ NOVO: Props para salvamento automático
  dadosSalvos?: any;
  onSalvarProgresso?: (dados: any) => void;
}

export const Passo1SelecionarCliente: React.FC<Passo1Props> = ({
  onVoltar,
  onProximo,
  dadosSalvos,
  onSalvarProgresso
}) => {
  const [selectedClienteId, setSelectedClienteId] = useState<number | null>(null);
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [modalCadastroAberto, setModalCadastroAberto] = useState(false);

  // ⚠️ NOVO: Estados para salvamento automático
  const [salvando, setSalvando] = useState(false);
  const [ultimoSalvamento, setUltimoSalvamento] = useState<Date | null>(null);
  const [erroSalvamento, setErroSalvamento] = useState<string | null>(null);

  // ⚠️ NOVO: Recuperar dados salvos ao montar componente
  useEffect(() => {
    if (dadosSalvos?.clienteId) {
      setSelectedClienteId(dadosSalvos.clienteId);
    }

    // Recuperar do localStorage como fallback
    const dadosBackup = localStorage.getItem('proposta_passo1_backup');
    if (dadosBackup && !dadosSalvos?.clienteId) {
      try {
        const dados = JSON.parse(dadosBackup);
        if (dados.clienteId) {
          setSelectedClienteId(dados.clienteId);
        }
      } catch (error) {
        console.warn('Erro ao recuperar backup do Passo 1:', error);
      }
    }
  }, [dadosSalvos]);

  // ⚠️ NOVO: Função de salvamento automático
  const salvarProgresso = useCallback(async () => {
    if (!selectedClienteId) return;

    setSalvando(true);
    setErroSalvamento(null);

    try {
      const dadosParaSalvar = {
        passo: 1,
        clienteId: selectedClienteId,
        timestamp: new Date().toISOString(),
        dadosCompletos: {
          cliente: clientes.find(c => c.id === selectedClienteId)
        }
      };

      // Salvar no localStorage como backup
      localStorage.setItem('proposta_passo1_backup', JSON.stringify(dadosParaSalvar));

      // Chamar callback de salvamento se fornecido
      if (onSalvarProgresso) {
        await onSalvarProgresso(dadosParaSalvar);
      }

      setUltimoSalvamento(new Date());
      console.log('Progresso do Passo 1 salvo com sucesso');

    } catch (error) {
      console.error('Erro ao salvar progresso:', error);
      setErroSalvamento(error instanceof Error ? error.message : 'Erro desconhecido');
    } finally {
      setSalvando(false);
    }
  }, [selectedClienteId, clientes, onSalvarProgresso]);

  // ⚠️ NOVO: Salvamento automático quando cliente é selecionado
  useEffect(() => {
    if (selectedClienteId) {
      const timeoutId = setTimeout(salvarProgresso, 1000); // Debounce de 1 segundo
      return () => clearTimeout(timeoutId);
    }
  }, [selectedClienteId, salvarProgresso]);

  // ⚠️ NOVO: Limpar backup ao sair
  useEffect(() => {
    return () => {
      // Manter backup por 24 horas para recuperação
      const dadosBackup = localStorage.getItem('proposta_passo1_backup');
      if (dadosBackup) {
        try {
          const dados = JSON.parse(dadosBackup);
          const timestamp = new Date(dados.timestamp);
          const agora = new Date();
          const diffHoras = (agora.getTime() - timestamp.getTime()) / (1000 * 60 * 60);

          if (diffHoras > 24) {
            localStorage.removeItem('proposta_passo1_backup');
          }
        } catch (error) {
          localStorage.removeItem('proposta_passo1_backup');
        }
      }
    };
  }, []);

  const fetchClientes = async (page = 1, search = '') => {
    setLoading(true);
    setError('');

    try {
      const response = await apiService.getClientes({
        page,
        per_page: 5,
        search: search.trim() || undefined,
        ativo: true
      });

      setClientes(response.items || []);
      setTotalPages(response.pages || 1);
    } catch (err: any) {
      console.error('Erro ao carregar clientes:', err);

      // Se for erro de autenticação ou conexão, usar dados mockados temporariamente
      if (err.message?.includes('401') || err.message?.includes('UNAUTHORIZED') || err.message?.includes('Failed to fetch')) {
        setError('API não disponível. Usando dados de demonstração.');

        // Dados mockados para demonstração com entidades jurídicas
        const clientesMockados: Cliente[] = [
          {
            id: 1,
            nome: 'João Silva Santos',
            cpf: '123.456.789-01',
            email: 'joao@email.com',
            abertura_empresa: false,
            ativo: true,
            entidades_juridicas: []
          },
          {
            id: 2,
            nome: 'Maria Empresária',
            cpf: '987.654.321-02',
            email: 'maria@email.com',
            abertura_empresa: true,
            ativo: true,
            entidades_juridicas: [
              { id: 1, nome: 'Empresa ABC Ltda', cnpj: '12.345.678/0001-90', tipo: 'LTDA', cliente_id: 2 },
              { id: 2, nome: 'Comércio XYZ ME', cnpj: '98.765.432/0001-10', tipo: 'ME', cliente_id: 2 }
            ]
          },
          {
            id: 3,
            nome: 'Pedro Comerciante',
            cpf: '456.789.123-03',
            email: 'pedro@comercio.com',
            abertura_empresa: false,
            ativo: true,
            entidades_juridicas: [
              { id: 3, nome: 'Comércio Pedro EIRELI', cnpj: '11.222.333/0001-44', tipo: 'EIRELI', cliente_id: 3 }
            ]
          },
          {
            id: 4,
            nome: 'Ana Consultora',
            cpf: '789.123.456-04',
            email: 'ana@consultoria.com',
            abertura_empresa: true,
            ativo: true,
            entidades_juridicas: []
          },
          {
            id: 5,
            nome: 'Carlos Industrial',
            cpf: '321.654.987-05',
            email: 'carlos@industria.com',
            abertura_empresa: false,
            ativo: true,
            entidades_juridicas: [
              { id: 4, nome: 'Indústria Beta S/A', cnpj: '33.333.333/0001-33', tipo: 'S/A', cliente_id: 5 },
              { id: 5, nome: 'Tecnologia Zeta S/A', cnpj: '77.777.777/0001-77', tipo: 'S/A', cliente_id: 5 }
            ]
          }
        ];

        setClientes(clientesMockados);
        setTotalPages(1);
      } else {
        setError(err.message || 'Erro ao carregar clientes');
        setClientes([]);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClientes(currentPage, searchTerm);
  }, [currentPage, searchTerm]);

  const handleSearchChange = (term: string) => {
    setSearchTerm(term);
    setCurrentPage(1);
  };

  const handleProximo = () => {
    if (selectedClienteId) {
      // ⚠️ NOVO: Salvar antes de prosseguir
      salvarProgresso();
      onProximo(selectedClienteId);
    }
  };

  const handleClienteCadastrado = (novoCliente: Cliente) => {
    // Adicionar à lista e selecionar automaticamente
    setClientes(prev => [novoCliente, ...prev]);
    setSelectedClienteId(novoCliente.id);
    setModalCadastroAberto(false);

    // Mostrar mensagem de sucesso
    alert('Cliente cadastrado com sucesso!');
  };

  return (
    <div>
      {/* Header da Página */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Nova Proposta - Passo 1</h1>
            <p className="text-sm text-gray-500">Selecione um cliente para criar a proposta</p>

            {/* ⚠️ NOVO: Indicador de salvamento */}
            <div className="flex items-center space-x-2 mt-2">
              {salvando && (
                <div className="flex items-center text-blue-600 text-sm">
                  <div className="animate-spin w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full mr-2"></div>
                  <span>Salvando progresso...</span>
                </div>
              )}

              {ultimoSalvamento && !salvando && (
                <div className="flex items-center text-green-600 text-sm">
                  <CheckCircle className="w-4 h-4 mr-1" />
                  <span>Salvo {ultimoSalvamento.toLocaleTimeString()}</span>
                </div>
              )}

              {erroSalvamento && (
                <div className="flex items-center text-red-600 text-sm">
                  <AlertCircle className="w-4 h-4 mr-1" />
                  <span>Erro no salvamento</span>
                </div>
              )}
            </div>
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

      {/* ⚠️ NOVO: Aviso de recuperação se aplicável */}
      {selectedClienteId && dadosSalvos?.clienteId === selectedClienteId && (
        <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-5 h-5 text-blue-600" />
            <span className="text-blue-800 text-sm">
              Progresso recuperado - Cliente selecionado anteriormente
            </span>
          </div>
        </div>
      )}

      {/* Barra de Ações */}
      <div className="mb-6 flex items-center justify-between">
        <button
          onClick={() => setModalCadastroAberto(true)}
          className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Cadastrar Cliente</span>
        </button>

        <div className="relative flex-1 max-w-md ml-4">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar cliente..."
            value={searchTerm}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent w-full"
          />
        </div>
      </div>

      {/* Lista de Clientes */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="flex items-center">
              <LoadingSpinner size="md" />
              <span className="ml-3 text-gray-500">Carregando clientes...</span>
            </div>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {clientes.map((cliente) => (
              <div key={cliente.id} className="p-6 hover:bg-gray-50 transition-colors">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    name="cliente"
                    value={cliente.id}
                    checked={selectedClienteId === cliente.id}
                    onChange={() => setSelectedClienteId(cliente.id)}
                    className="h-5 w-5 text-blue-600 focus:ring-blue-500 border-gray-300"
                  />
                  <div className="ml-4 flex-1">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-lg font-medium text-gray-900">
                          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${cliente.ativo ? 'bg-green-100 text-green-500' : 'bg-red-100 text-red-500'}`}>
                            {cliente.ativo ? 'Ativo' : 'Inativo'}
                          </span> {cliente.nome}
                        </p>

                        {/* CPF - sempre mostrar */}
                        <p className="text-sm text-gray-500 mt-1">CPF: {cliente.cpf}</p>

                        {/* CNPJs - só mostrar se existirem */}
                        {cliente.entidades_juridicas && cliente.entidades_juridicas.length > 0 && (
                          <div className="mt-1">
                            {cliente.entidades_juridicas.map((entidade) => (
                              <p key={entidade.id} className="text-sm text-gray-500">
                                CNPJ: {entidade.cnpj} ({entidade.nome})
                              </p>
                            ))}
                          </div>
                        )}

                        {/* Email */}
                        <p className="text-sm text-gray-500 mt-1">Email: {cliente.email}</p>
                      </div>

                      {/* Selo de status */}
                      <div className="text-right">
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${cliente.abertura_empresa
                            ? 'bg-purple-100 text-purple-800'
                            : 'bg-green-100 text-green-800'
                          }`}>
                          {cliente.abertura_empresa ? 'Abertura de Empresa' : 'Cliente Existente'}
                        </span>
                      </div>
                    </div>
                  </div>
                </label>
              </div>
            ))}
          </div>
        )}

        {clientes.length === 0 && !loading && (
          <div className="text-center py-16">
            <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-lg text-gray-500 mb-2">
              {searchTerm ? `Nenhum cliente encontrado para "${searchTerm}"` : 'Nenhum cliente encontrado'}
            </p>
            <p className="text-sm text-gray-400">
              {searchTerm ? 'Tente buscar por nome, CPF ou email' : 'Cadastre um cliente para continuar'}
            </p>
          </div>
        )}
      </div>

      {/* Paginação */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center space-x-2 mb-6">
          <button
            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
            disabled={currentPage === 1}
            className="px-4 py-2 border border-gray-300 rounded-md disabled:opacity-50 hover:bg-gray-50 transition-colors"
          >
            Anterior
          </button>
          <span className="px-4 py-2 text-sm text-gray-700">
            Página {currentPage} de {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
            disabled={currentPage === totalPages}
            className="px-4 py-2 border border-gray-300 rounded-md disabled:opacity-50 hover:bg-gray-50 transition-colors"
          >
            Próxima
          </button>
        </div>
      )}

      {/* Botões de Ação Fixos */}
      <div className="fixed bottom-0 left-64 right-0 bg-white border-t border-gray-200 px-6 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4">
            {selectedClienteId && (
              <span className="text-sm text-gray-600">
                Cliente selecionado: {clientes.find(c => c.id === selectedClienteId)?.nome}
              </span>
            )}

            {/* ⚠️ NOVO: Botão de salvamento manual */}
            <button
              onClick={salvarProgresso}
              disabled={!selectedClienteId || salvando}
              className="flex items-center space-x-2 px-3 py-1 text-sm text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 disabled:opacity-50 transition-colors"
            >
              <Save className="w-4 h-4" />
              <span>{salvando ? 'Salvando...' : 'Salvar Progresso'}</span>
            </button>
          </div>

          <div className="flex justify-end space-x-3">
            <button
              onClick={onVoltar}
              className="px-6 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancelar
            </button>
            <button
              onClick={handleProximo}
              disabled={!selectedClienteId}
              className="px-6 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Próximo
            </button>
          </div>
        </div>
      </div>

      {/* Modal de Cadastro de Cliente */}
      <ModalCadastroCliente
        isOpen={modalCadastroAberto}
        onClose={() => setModalCadastroAberto(false)}
        onClienteCadastrado={handleClienteCadastrado}
      />
    </div>
  );
};
