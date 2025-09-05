import React, { useState, useEffect } from 'react';
import { Plus, Search, Trash2, Mail, User, Building, Eye, Edit2, Shield, UserCheck } from 'lucide-react';
import { apiService } from '../../services/api';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { Modal } from '../modals/Modal';
import { ModalCadastroFuncionario } from '../modals/ModalCadastroFuncionario';
import { ModalVisualizacao } from '../modals/ModalVisualizacao';
import { useAuth } from '../../context/AuthContext';
import { Funcionario } from '../../types';

interface FuncionariosPageProps {
  openModalOnLoad?: boolean;
}

export const FuncionariosPage: React.FC<FuncionariosPageProps> = ({ openModalOnLoad = false }) => {
  const { user } = useAuth();
  const [funcionarios, setFuncionarios] = useState<Funcionario[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Estados para os modais
  const [funcionarioParaVisualizar, setFuncionarioParaVisualizar] = useState<Funcionario | null>(null);
  const [funcionarioParaEditar, setFuncionarioParaEditar] = useState<Funcionario | null>(null);
  const [funcionarioParaDeletar, setFuncionarioParaDeletar] = useState<Funcionario | null>(null);
  const [isModalEdicaoOpen, setIsModalEdicaoOpen] = useState(false);

  // Verificar se o usuário é gerente
  const [isGerente, setIsGerente] = useState(false);
  const [verificandoPermissao, setVerificandoPermissao] = useState(true);

  // Verificar permissão de gerente
  useEffect(() => {
    const verificarPermissao = async () => {
      try {
        // Por enquanto, vou assumir que o usuário é gerente
        // Em uma implementação real, você verificaria isso na API
        setIsGerente(true);
      } catch (error) {
        console.error('Erro ao verificar permissão:', error);
        setIsGerente(false);
      } finally {
        setVerificandoPermissao(false);
      }
    };

    verificarPermissao();
  }, []);

  const fetchFuncionarios = async (page = 1, search = '') => {
    setLoading(true);
    try {
      const response = await apiService.getFuncionarios({
        page,
        per_page: 10,
        search,
        ativo: true
      });

      setFuncionarios(response.funcionarios || []);
      setTotalPages(response.pages || 1);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isGerente && !verificandoPermissao) {
      fetchFuncionarios(currentPage, searchTerm);
    }
  }, [currentPage, searchTerm, isGerente, verificandoPermissao]);

  // Abrir modal automaticamente se openModalOnLoad for true
  useEffect(() => {
    if (openModalOnLoad && isGerente) {
      setIsModalOpen(true);
    }
  }, [openModalOnLoad, isGerente]);

  const handleSearch = (term: string) => {
    setSearchTerm(term);
    setCurrentPage(1);
  };

  const openModal = () => {
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  const handleFuncionarioCadastrado = (funcionario: Funcionario) => {
    fetchFuncionarios(currentPage, searchTerm);
    closeModal();
  };

  // Funções para os botões de ação
  const handleVisualizar = (funcionario: Funcionario) => {
    setFuncionarioParaVisualizar(funcionario);
  };

  const handleEditar = (funcionario: Funcionario) => {
    setFuncionarioParaEditar(funcionario);
    setIsModalEdicaoOpen(true);
  };

  const handleDeletar = (funcionario: Funcionario) => {
    setFuncionarioParaDeletar(funcionario);
  };

  const confirmarDeletar = async () => {
    if (!funcionarioParaDeletar) return;

    try {
      await apiService.deleteFuncionario(funcionarioParaDeletar.id);
      fetchFuncionarios(currentPage, searchTerm);
      setFuncionarioParaDeletar(null);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleFuncionarioEditado = (funcionario: Funcionario) => {
    fetchFuncionarios(currentPage, searchTerm);
    setIsModalEdicaoOpen(false);
    setFuncionarioParaEditar(null);
  };

  // Se não for gerente, mostrar mensagem de acesso negado
  if (verificandoPermissao) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  if (!isGerente) {
    return (
      <div className="space-y-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Funcionários</h1>
          <p className="text-sm text-gray-500">Gerencie a equipe e colaboradores da empresa</p>
        </div>

        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center">
            <Shield className="w-8 h-8 text-red-400 mr-3" />
            <div>
              <h3 className="text-lg font-medium text-red-800">Acesso Negado</h3>
              <p className="text-red-700 mt-1">
                Você não tem permissão para acessar esta página. Apenas gerentes podem gerenciar funcionários.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Title */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Funcionários</h1>
        <p className="text-sm text-gray-500">Gerencie a equipe e colaboradores da empresa</p>
      </div>

      {/* Header Actions */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar funcionários..."
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
        <button
          onClick={() => openModal()}
          className="bg-custom-blue text-white px-4 py-2 rounded-lg hover:bg-custom-blue-light transition-colors flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Novo Funcionário</span>
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Content */}
      {loading ? (
        <div className="flex justify-center py-8">
          <LoadingSpinner />
        </div>
      ) : (
        <>
          {/* Funcionários List */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Funcionário
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      E-mail
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Cargo
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Empresa
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Tipo
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ações
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {funcionarios.map((funcionario) => (
                    <tr key={funcionario.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-8 h-8 bg-blue-50 rounded-full flex items-center justify-center mr-3">
                            <User className="w-4 h-4 text-blue-600" />
                          </div>
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {funcionario.nome}
                            </div>
                            <div className="text-sm text-gray-500">
                              ID: {funcionario.id}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center text-sm text-gray-900">
                          <Mail className="w-4 h-4 mr-2 text-gray-400" />
                          {funcionario.email}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {funcionario.cargo?.nome || `Cargo ID: ${funcionario.cargo_id}`}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {funcionario.empresa?.nome || `Empresa ID: ${funcionario.empresa_id}`}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${funcionario.gerente
                          ? 'bg-purple-100 text-purple-800'
                          : 'bg-green-100 text-green-800'
                          }`}>
                          {funcionario.gerente ? 'Gerente' : 'Funcionário'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${funcionario.ativo
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                          }`}>
                          {funcionario.ativo ? 'Ativo' : 'Inativo'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleVisualizar(funcionario)}
                            className="text-blue-600 hover:text-blue-600-light p-1 rounded-full hover:bg-custom-blue-light"
                            title="Visualizar funcionário"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleEditar(funcionario)}
                            className="text-green-600 hover:text-green-900 p-1 rounded-full hover:bg-green-50"
                            title="Editar funcionário"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDeletar(funcionario)}
                            className="text-red-600 hover:text-red-900 p-1 rounded-full hover:bg-red-50"
                            title="Excluir funcionário"
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

            {funcionarios.length === 0 && (
              <div className="text-center py-8">
                <UserCheck className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">Nenhum funcionário encontrado</p>
              </div>
            )}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center space-x-2">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="px-3 py-1 border border-gray-300 rounded-md disabled:opacity-50"
              >
                Anterior
              </button>
              <span className="px-3 py-1">
                Página {currentPage} de {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                className="px-3 py-1 border border-gray-300 rounded-md disabled:opacity-50"
              >
                Próxima
              </button>
            </div>
          )}
        </>
      )}

      {/* Modal de Cadastro de Funcionário */}
      <ModalCadastroFuncionario
        isOpen={isModalOpen}
        onClose={closeModal}
        onFuncionarioCadastrado={handleFuncionarioCadastrado}
      />

      {/* Modal de Edição de Funcionário */}
      <ModalCadastroFuncionario
        isOpen={isModalEdicaoOpen}
        onClose={() => setIsModalEdicaoOpen(false)}
        onFuncionarioCadastrado={handleFuncionarioEditado}
        funcionarioParaEditar={funcionarioParaEditar}
      />

      {/* Modal de Visualização */}
      <ModalVisualizacao
        isOpen={!!funcionarioParaVisualizar}
        onClose={() => setFuncionarioParaVisualizar(null)}
        type="funcionario"
        data={funcionarioParaVisualizar}
      />



      {/* Modal de Confirmação para Deletar */}
      <Modal
        isOpen={!!funcionarioParaDeletar}
        onClose={() => setFuncionarioParaDeletar(null)}
        title="Confirmar Exclusão"
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-gray-700">
            Tem certeza que deseja excluir o funcionário <strong>{funcionarioParaDeletar?.nome}</strong>?
          </p>
          <p className="text-sm text-red-600">
            Esta ação não pode ser desfeita.
          </p>
          <div className="flex justify-end space-x-3">
            <button
              onClick={() => setFuncionarioParaDeletar(null)}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              onClick={confirmarDeletar}
              className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700"
            >
              Excluir
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
