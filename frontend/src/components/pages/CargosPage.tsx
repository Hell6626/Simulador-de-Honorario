import React, { useState, useEffect } from 'react';
import { Plus, Search, Trash2, UserCheck, Eye, Edit2, Shield, Building2 } from 'lucide-react';
import { apiService } from '../../services/api';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { Modal } from '../modals/Modal';
import { ModalVisualizacao } from '../modals/ModalVisualizacao';
import { useAuth } from '../../context/AuthContext';

interface Cargo {
  id: number;
  codigo: string;
  nome: string;
  descricao?: string;
  nivel?: string;
  empresa_id: number;
  ativo: boolean;
  created_at: string;
  updated_at: string;
  empresa?: {
    nome: string;
    cnpj: string;
  };
}

interface CargosPageProps {
  openModalOnLoad?: boolean;
}

export const CargosPage: React.FC<CargosPageProps> = ({ openModalOnLoad = false }) => {
  const { user } = useAuth();
  const [cargos, setCargos] = useState<Cargo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Estados para os modais
  const [cargoParaVisualizar, setCargoParaVisualizar] = useState<Cargo | null>(null);
  const [cargoParaEditar, setCargoParaEditar] = useState<Cargo | null>(null);
  const [cargoParaDeletar, setCargoParaDeletar] = useState<Cargo | null>(null);
  const [isModalEdicaoOpen, setIsModalEdicaoOpen] = useState(false);

  // Estados do formulário
  const [formData, setFormData] = useState({
    nome: '',
    descricao: '',
    nivel: ''
  });

  // Verificar se o usuário é admin
  const [isAdmin, setIsAdmin] = useState(false);
  const [verificandoPermissao, setVerificandoPermissao] = useState(true);

  // Verificar permissão de admin
  useEffect(() => {
    const isAdminUser = Boolean(user?.gerente);
    setIsAdmin(isAdminUser);
    setVerificandoPermissao(false);

    if (isAdminUser) {
      fetchCargos();
    }
  }, [user]);

  const fetchCargos = async (page = 1, search = '') => {
    try {
      setLoading(true);
      const response = await apiService.getCargos({
        page,
        per_page: 10,
        search: search || undefined
      });
      setCargos(response.cargos || []);
      setTotalPages(response.pages || 1);
      setCurrentPage(page);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };



  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchCargos(1, searchTerm);
  };

  const handlePageChange = (page: number) => {
    fetchCargos(page, searchTerm);
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSalvar = async () => {
    if (!formData.nome.trim()) {
      setError('Nome do cargo é obrigatório');
      return;
    }

    try {
      setLoading(true);
      const response = await apiService.createCargo(formData);
      setCargos(prev => [response, ...prev]);
      setIsModalOpen(false);
      setFormData({ nome: '', descricao: '', nivel: '' });
      setError('');
    } catch (err: any) {
      console.error('Erro ao criar cargo:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleEditar = async () => {
    if (!cargoParaEditar || !formData.nome.trim()) {
      setError('Nome do cargo é obrigatório');
      return;
    }

    try {
      setLoading(true);
      const response = await apiService.updateCargo(cargoParaEditar.id, formData);
      setCargos(prev => prev.map(c => c.id === cargoParaEditar.id ? response : c));
      setIsModalEdicaoOpen(false);
      setCargoParaEditar(null);
      setFormData({ nome: '', descricao: '', nivel: '' });
      setError('');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const confirmarDeletar = async () => {
    if (!cargoParaDeletar) return;

    try {
      await apiService.deleteCargo(cargoParaDeletar.id);
      setCargos(cargos.filter(c => c.id !== cargoParaDeletar.id));
      setCargoParaDeletar(null);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const abrirModalEdicao = (cargo: Cargo) => {
    setCargoParaEditar(cargo);
    setFormData({
      nome: cargo.nome,
      descricao: cargo.descricao || '',
      nivel: cargo.nivel || ''
    });
    setIsModalEdicaoOpen(true);
  };

  // Se não for admin, mostrar mensagem de acesso negado
  if (verificandoPermissao) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  if (!isAdmin) {
    return (
      <div className="space-y-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Cargos</h1>
          <p className="text-sm text-gray-500">Gerencie os cargos do sistema</p>
        </div>

        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center">
            <Shield className="w-8 h-8 text-red-400 mr-3" />
            <div>
              <h3 className="text-lg font-medium text-red-800">Acesso Negado</h3>
              <p className="text-red-700 mt-1">
                Você não tem permissão para acessar esta página. Apenas administradores podem gerenciar cargos.
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
        <h1 className="text-2xl font-bold text-gray-900">Cargos</h1>
        <p className="text-sm text-gray-500">Gerencie os cargos da sua empresa</p>
      </div>

      {/* Search and Actions */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
        <form onSubmit={handleSearch} className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Buscar cargos..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </form>

        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4 mr-2" />
          Novo Cargo
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Jobs List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner />
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cargo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Código
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Nível
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ações
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {cargos.map((cargo) => (
                  <tr key={cargo.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <UserCheck className="w-5 h-5 text-gray-400 mr-3" />
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {cargo.nome}
                          </div>
                          {cargo.descricao && (
                            <div className="text-sm text-gray-500">
                              {cargo.descricao}
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {cargo.codigo}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {cargo.nivel || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${cargo.ativo
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                        }`}>
                        {cargo.ativo ? 'Ativo' : 'Inativo'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => setCargoParaVisualizar(cargo)}
                          className="text-blue-600 hover:text-blue-900 p-1"
                          title="Visualizar"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => abrirModalEdicao(cargo)}
                          className="text-green-600 hover:text-green-900 p-1"
                          title="Editar"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => setCargoParaDeletar(cargo)}
                          className="text-red-600 hover:text-red-900 p-1"
                          title="Excluir"
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

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
              <div className="flex-1 flex justify-between sm:hidden">
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                >
                  Anterior
                </button>
                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                >
                  Próxima
                </button>
              </div>
              <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm text-gray-700">
                    Página <span className="font-medium">{currentPage}</span> de{' '}
                    <span className="font-medium">{totalPages}</span>
                  </p>
                </div>
                <div>
                  <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                    <button
                      onClick={() => handlePageChange(currentPage - 1)}
                      disabled={currentPage === 1}
                      className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                    >
                      Anterior
                    </button>
                    <button
                      onClick={() => handlePageChange(currentPage + 1)}
                      disabled={currentPage === totalPages}
                      className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                    >
                      Próxima
                    </button>
                  </nav>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Modals */}
      {/* Modal de Cadastro */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setFormData({ nome: '', descricao: '', nivel: '' });
          setError('');
        }}
        title="Cadastrar Novo Cargo"
      >
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nome do Cargo *
            </label>
            <input
              type="text"
              value={formData.nome}
              onChange={(e) => handleInputChange('nome', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Ex: Administrador"
            />
            <p className="text-xs text-gray-500 mt-1">
              O código será gerado automaticamente com as 3 primeiras letras + 3 números
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Descrição
            </label>
            <textarea
              value={formData.descricao}
              onChange={(e) => handleInputChange('descricao', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={3}
              placeholder="Descreva as responsabilidades do cargo"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nível
            </label>
            <select
              value={formData.nivel}
              onChange={(e) => handleInputChange('nivel', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Selecione um nível</option>
              <option value="Júnior">Júnior</option>
              <option value="Pleno">Pleno</option>
              <option value="Sênior">Sênior</option>
              <option value="Especialista">Especialista</option>
              <option value="Gerente">Gerente</option>
              <option value="Diretor">Diretor</option>
            </select>
          </div>
        </div>

        <div className="flex justify-end space-x-3 mt-6">
          <button
            onClick={() => {
              setIsModalOpen(false);
              setFormData({ nome: '', descricao: '', nivel: '' });
              setError('');
            }}
            className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={handleSalvar}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {loading ? 'Salvando...' : 'Cadastrar'}
          </button>
        </div>
      </Modal>

      {/* Modal de Edição */}
      <Modal
        isOpen={isModalEdicaoOpen}
        onClose={() => {
          setIsModalEdicaoOpen(false);
          setCargoParaEditar(null);
          setFormData({ nome: '', descricao: '', nivel: '' });
          setError('');
        }}
        title="Editar Cargo"
      >
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nome do Cargo *
            </label>
            <input
              type="text"
              value={formData.nome}
              onChange={(e) => handleInputChange('nome', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Ex: Administrador"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Descrição
            </label>
            <textarea
              value={formData.descricao}
              onChange={(e) => handleInputChange('descricao', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={3}
              placeholder="Descreva as responsabilidades do cargo"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nível
            </label>
            <select
              value={formData.nivel}
              onChange={(e) => handleInputChange('nivel', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Selecione um nível</option>
              <option value="Júnior">Júnior</option>
              <option value="Pleno">Pleno</option>
              <option value="Sênior">Sênior</option>
              <option value="Especialista">Especialista</option>
              <option value="Gerente">Gerente</option>
              <option value="Diretor">Diretor</option>
            </select>
          </div>
        </div>

        <div className="flex justify-end space-x-3 mt-6">
          <button
            onClick={() => {
              setIsModalEdicaoOpen(false);
              setCargoParaEditar(null);
              setFormData({ nome: '', descricao: '', nivel: '' });
              setError('');
            }}
            className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={handleEditar}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {loading ? 'Salvando...' : 'Salvar'}
          </button>
        </div>
      </Modal>

      {/* Modal de Visualização */}
      <ModalVisualizacao
        isOpen={!!cargoParaVisualizar}
        onClose={() => setCargoParaVisualizar(null)}
        type="cargo"
        data={cargoParaVisualizar}
      />

      {/* Modal de Confirmação de Exclusão */}
      {cargoParaDeletar && (
        <Modal
          isOpen={!!cargoParaDeletar}
          onClose={() => setCargoParaDeletar(null)}
          title="Confirmar Exclusão"
        >
          <div className="space-y-4">
            <p className="text-gray-700">
              Tem certeza que deseja excluir o cargo <strong>{cargoParaDeletar.nome}</strong>?
            </p>
            <p className="text-sm text-gray-500">
              Esta ação não pode ser desfeita.
            </p>
          </div>

          <div className="flex justify-end space-x-3 mt-6">
            <button
              onClick={() => setCargoParaDeletar(null)}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancelar
            </button>
            <button
              onClick={confirmarDeletar}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Excluir
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
};
