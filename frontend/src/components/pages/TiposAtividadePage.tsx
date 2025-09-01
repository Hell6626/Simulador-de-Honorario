import React, { useState, useEffect } from 'react';
import { Plus, Search, Trash2, Eye, Edit2, Shield, Building2, Users, AlertTriangle } from 'lucide-react';
import { apiService } from '../../services/api';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { Modal } from '../modals/Modal';
import { ModalVisualizacao } from '../modals/ModalVisualizacao';
import { useAuth } from '../../context/AuthContext';

interface TipoAtividade {
    id: number;
    codigo: string;
    nome: string;
    aplicavel_pf: boolean;
    aplicavel_pj: boolean;
    ativo: boolean;
    created_at?: string;
    updated_at?: string;
}

export const TiposAtividadePage: React.FC = () => {
    const { user } = useAuth();
    const [tiposAtividade, setTiposAtividade] = useState<TipoAtividade[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [searchTerm, setSearchTerm] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isModalEdicaoOpen, setIsModalEdicaoOpen] = useState(false);
    const [isModalVisualizacaoOpen, setIsModalVisualizacaoOpen] = useState(false);
    const [isModalConfirmacaoOpen, setIsModalConfirmacaoOpen] = useState(false);
    const [tipoParaEditar, setTipoParaEditar] = useState<TipoAtividade | null>(null);
    const [tipoParaExcluir, setTipoParaExcluir] = useState<TipoAtividade | null>(null);
    const [formData, setFormData] = useState({
        codigo: '',
        nome: '',
        aplicavel_pf: false,
        aplicavel_pj: false,
        ativo: true,
    });

    // Verificar permissão de admin
    const [isAdmin, setIsAdmin] = useState(false);
    const [verificandoPermissao, setVerificandoPermissao] = useState(true);

    useEffect(() => {
        const isAdminUser = Boolean(user?.gerente);
        setIsAdmin(isAdminUser);
        setVerificandoPermissao(false);

        if (isAdminUser) {
            fetchTiposAtividade();
        }
    }, [user]);

    const fetchTiposAtividade = async () => {
        try {
            setLoading(true);
            const response = await apiService.getTiposAtividade({
                search: searchTerm,
                ativo: true
            });
            setTiposAtividade(response.items || response);
        } catch (error: any) {
            console.error('Erro ao carregar tipos de atividade:', error);
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    const handleSalvar = async () => {
        if (!formData.codigo.trim()) {
            setError('Código é obrigatório');
            return;
        }

        if (!formData.nome.trim()) {
            setError('Nome é obrigatório');
            return;
        }

        if (!formData.aplicavel_pf && !formData.aplicavel_pj) {
            setError('Deve ser aplicável para pelo menos um tipo de pessoa');
            return;
        }

        try {
            setLoading(true);
            const dataToSend = {
                ...formData,
                codigo: formData.codigo.toUpperCase()
            };
            const response = await apiService.createTipoAtividade(dataToSend);
            setTiposAtividade(prev => [response, ...prev]);
            setIsModalOpen(false);
            setFormData({ codigo: '', nome: '', aplicavel_pf: false, aplicavel_pj: false, ativo: true });
            setError('');
        } catch (err: any) {
            setError(err.message || 'Erro ao criar tipo de atividade');
        } finally {
            setLoading(false);
        }
    };

    const handleEditar = async () => {
        if (!tipoParaEditar || !formData.codigo.trim()) {
            setError('Código é obrigatório');
            return;
        }

        if (!formData.nome.trim()) {
            setError('Nome é obrigatório');
            return;
        }

        if (!formData.aplicavel_pf && !formData.aplicavel_pj) {
            setError('Deve ser aplicável para pelo menos um tipo de pessoa');
            return;
        }

        try {
            setLoading(true);
            const dataToSend = {
                ...formData,
                codigo: formData.codigo.toUpperCase()
            };
            const response = await apiService.updateTipoAtividade(tipoParaEditar.id, dataToSend);
            setTiposAtividade(prev => prev.map(t => t.id === tipoParaEditar.id ? response : t));
            setIsModalEdicaoOpen(false);
            setTipoParaEditar(null);
            setFormData({ codigo: '', nome: '', aplicavel_pf: false, aplicavel_pj: false, ativo: true });
            setError('');
        } catch (err: any) {
            setError(err.message || 'Erro ao atualizar tipo de atividade');
        } finally {
            setLoading(false);
        }
    };

    const handleExcluir = async () => {
        if (!tipoParaExcluir) return;

        try {
            setLoading(true);
            await apiService.deleteTipoAtividade(tipoParaExcluir.id);
            setTiposAtividade(prev => prev.filter(t => t.id !== tipoParaExcluir.id));
            setIsModalConfirmacaoOpen(false);
            setTipoParaExcluir(null);
        } catch (err: any) {
            // Verificar se é erro de relacionamento
            if (err.message && err.message.includes('possui regimes associados')) {
                setError('Não é possível excluir este tipo de atividade pois existem regimes tributários vinculados a ele. Remova os vínculos primeiro.');
            } else {
                setError(err.message || 'Erro ao excluir tipo de atividade');
            }
        } finally {
            setLoading(false);
        }
    };

    const confirmarExclusao = (tipo: TipoAtividade) => {
        setTipoParaExcluir(tipo);
        setIsModalConfirmacaoOpen(true);
    };

    const abrirModalEdicao = (tipo: TipoAtividade) => {
        setTipoParaEditar(tipo);
        setFormData({
            codigo: tipo.codigo,
            nome: tipo.nome,
            aplicavel_pf: tipo.aplicavel_pf,
            aplicavel_pj: tipo.aplicavel_pj,
            ativo: tipo.ativo,
        });
        setIsModalEdicaoOpen(true);
    };

    const handleSearch = () => {
        fetchTiposAtividade();
    };

    if (verificandoPermissao) {
        return <LoadingSpinner />;
    }

    if (!isAdmin) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <AlertTriangle className="mx-auto h-12 w-12 text-red-500 mb-4" />
                    <h2 className="text-xl font-semibold text-gray-900 mb-2">Acesso Negado</h2>
                    <p className="text-gray-600">Você não tem permissão para acessar esta página.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Cabeçalho */}
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900">Tipos de Atividade</h1>
                <p className="text-sm text-gray-500">Configure os tipos de atividade contábil disponíveis</p>
            </div>

            {/* Barra de Ações */}
            <div className="flex justify-between items-center">
                <button
                    onClick={() => setIsModalOpen(true)}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                    <Plus className="h-4 w-4 mr-2" />
                    Novo Tipo de Atividade
                </button>
            </div>

            {/* Barra de Busca */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="flex gap-4">
                    <div className="flex-1">
                        <input
                            type="text"
                            placeholder="Buscar tipos de atividade..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                    </div>
                    <button
                        onClick={handleSearch}
                        className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
                    >
                        <Search className="h-4 w-4" />
                    </button>
                </div>
            </div>

            {/* Tabela */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                {loading ? (
                    <div className="p-8 text-center">
                        <LoadingSpinner />
                    </div>
                ) : error ? (
                    <div className="p-8 text-center text-red-600">
                        <p>{error}</p>
                    </div>
                ) : tiposAtividade.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">
                        <Building2 className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                        <p>Nenhum tipo de atividade encontrado</p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50 border-b border-gray-200">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Código
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Nome
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Aplicabilidade
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
                                {tiposAtividade.map((tipo) => (
                                    <tr key={tipo.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                                {tipo.codigo}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                            {tipo.nome}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                            <div className="space-y-1">
                                                {tipo.aplicavel_pf && (
                                                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mr-2">
                                                        PF
                                                    </span>
                                                )}
                                                {tipo.aplicavel_pj && (
                                                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                                                        PJ
                                                    </span>
                                                )}
                                                {!tipo.aplicavel_pf && !tipo.aplicavel_pj && (
                                                    <span className="text-sm text-gray-500">Não especificado</span>
                                                )}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${tipo.ativo
                                                ? 'bg-green-100 text-green-800'
                                                : 'bg-red-100 text-red-800'
                                                }`}>
                                                {tipo.ativo ? 'Ativo' : 'Inativo'}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                            <div className="flex space-x-2">
                                                <button
                                                    onClick={() => {
                                                        setTipoParaEditar(tipo);
                                                        setIsModalVisualizacaoOpen(true);
                                                    }}
                                                    className="text-blue-600 hover:text-blue-900"
                                                    title="Visualizar"
                                                >
                                                    <Eye className="h-4 w-4" />
                                                </button>
                                                <button
                                                    onClick={() => abrirModalEdicao(tipo)}
                                                    className="text-indigo-600 hover:text-indigo-900"
                                                    title="Editar"
                                                >
                                                    <Edit2 className="h-4 w-4" />
                                                </button>
                                                <button
                                                    onClick={() => confirmarExclusao(tipo)}
                                                    className="text-red-600 hover:text-red-900"
                                                    title="Excluir"
                                                >
                                                    <Trash2 className="h-4 w-4" />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Modal de Cadastro */}
            <Modal
                isOpen={isModalOpen}
                onClose={() => {
                    setIsModalOpen(false);
                    setFormData({ codigo: '', nome: '', aplicavel_pf: false, aplicavel_pj: false, ativo: true });
                    setError('');
                }}
                title="Novo Tipo de Atividade"
            >
                <div className="space-y-4">
                    {error && (
                        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                            {error}
                        </div>
                    )}

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Código *
                        </label>
                        <input
                            type="text"
                            value={formData.codigo}
                            onChange={(e) => setFormData(prev => ({ ...prev, codigo: e.target.value }))}
                            placeholder="Ex: COM, IND, SERV"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            maxLength={10}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Nome *
                        </label>
                        <input
                            type="text"
                            value={formData.nome}
                            onChange={(e) => setFormData(prev => ({ ...prev, nome: e.target.value }))}
                            placeholder="Ex: Comércio, Indústria, Serviços"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    <div className="space-y-3">
                        <label className="block text-sm font-medium text-gray-700">
                            Aplicabilidade
                        </label>
                        <div className="flex space-x-4">
                            <label className="flex items-center">
                                <input
                                    type="checkbox"
                                    checked={formData.aplicavel_pf}
                                    onChange={(e) => setFormData(prev => ({ ...prev, aplicavel_pf: e.target.checked }))}
                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                />
                                <span className="ml-2 text-sm text-gray-700">Aplicável para Pessoa Física</span>
                            </label>
                            <label className="flex items-center">
                                <input
                                    type="checkbox"
                                    checked={formData.aplicavel_pj}
                                    onChange={(e) => setFormData(prev => ({ ...prev, aplicavel_pj: e.target.checked }))}
                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                />
                                <span className="ml-2 text-sm text-gray-700">Aplicável para Pessoa Jurídica</span>
                            </label>
                        </div>
                    </div>

                    <div>
                        <label className="flex items-center">
                            <input
                                type="checkbox"
                                checked={formData.ativo}
                                onChange={(e) => setFormData(prev => ({ ...prev, ativo: e.target.checked }))}
                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                            />
                            <span className="ml-2 text-sm text-gray-700">Ativo</span>
                        </label>
                    </div>
                </div>

                <div className="flex justify-end space-x-3 mt-6">
                    <button
                        onClick={() => setIsModalOpen(false)}
                        className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                        Cancelar
                    </button>
                    <button
                        onClick={handleSalvar}
                        disabled={loading}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                    >
                        {loading ? 'Salvando...' : 'Salvar'}
                    </button>
                </div>
            </Modal>

            {/* Modal de Edição */}
            <Modal
                isOpen={isModalEdicaoOpen}
                onClose={() => {
                    setIsModalEdicaoOpen(false);
                    setTipoParaEditar(null);
                    setFormData({ codigo: '', nome: '', aplicavel_pf: false, aplicavel_pj: false, ativo: true });
                    setError('');
                }}
                title="Editar Tipo de Atividade"
            >
                <div className="space-y-4">
                    {error && (
                        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                            {error}
                        </div>
                    )}

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Código *
                        </label>
                        <input
                            type="text"
                            value={formData.codigo}
                            onChange={(e) => setFormData(prev => ({ ...prev, codigo: e.target.value }))}
                            placeholder="Ex: COM, IND, SERV"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            maxLength={10}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Nome *
                        </label>
                        <input
                            type="text"
                            value={formData.nome}
                            onChange={(e) => setFormData(prev => ({ ...prev, nome: e.target.value }))}
                            placeholder="Ex: Comércio, Indústria, Serviços"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    <div className="space-y-3">
                        <label className="block text-sm font-medium text-gray-700">
                            Aplicabilidade
                        </label>
                        <div className="flex space-x-4">
                            <label className="flex items-center">
                                <input
                                    type="checkbox"
                                    checked={formData.aplicavel_pf}
                                    onChange={(e) => setFormData(prev => ({ ...prev, aplicavel_pf: e.target.checked }))}
                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                />
                                <span className="ml-2 text-sm text-gray-700">Aplicável para Pessoa Física</span>
                            </label>
                            <label className="flex items-center">
                                <input
                                    type="checkbox"
                                    checked={formData.aplicavel_pj}
                                    onChange={(e) => setFormData(prev => ({ ...prev, aplicavel_pj: e.target.checked }))}
                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                />
                                <span className="ml-2 text-sm text-gray-700">Aplicável para Pessoa Jurídica</span>
                            </label>
                        </div>
                    </div>

                    <div>
                        <label className="flex items-center">
                            <input
                                type="checkbox"
                                checked={formData.ativo}
                                onChange={(e) => setFormData(prev => ({ ...prev, ativo: e.target.checked }))}
                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                            />
                            <span className="ml-2 text-sm text-gray-700">Ativo</span>
                        </label>
                    </div>
                </div>

                <div className="flex justify-end space-x-3 mt-6">
                    <button
                        onClick={() => setIsModalEdicaoOpen(false)}
                        className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                        Cancelar
                    </button>
                    <button
                        onClick={handleEditar}
                        disabled={loading}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                    >
                        {loading ? 'Salvando...' : 'Salvar'}
                    </button>
                </div>
            </Modal>

            {/* Modal de Visualização */}
            <Modal
                isOpen={isModalVisualizacaoOpen}
                onClose={() => {
                    setIsModalVisualizacaoOpen(false);
                    setTipoParaEditar(null);
                }}
                title="Visualizar Tipo de Atividade"
            >
                {tipoParaEditar && (
                    <div className="space-y-6">
                        {/* Informações Básicas */}
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                            <h3 className="text-lg font-semibold text-blue-900 mb-3 flex items-center">
                                <Building2 className="h-5 w-5 mr-2" />
                                Informações do Tipo de Atividade
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Código</label>
                                    <p className="text-sm text-gray-900 bg-white px-3 py-2 rounded border">
                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                            {tipoParaEditar.codigo}
                                        </span>
                                    </p>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Nome</label>
                                    <p className="text-sm text-gray-900 bg-white px-3 py-2 rounded border">
                                        {tipoParaEditar.nome}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Aplicabilidade */}
                        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                            <h3 className="text-lg font-semibold text-purple-900 mb-3 flex items-center">
                                <Users className="h-5 w-5 mr-2" />
                                Aplicabilidade
                            </h3>
                            <div className="flex flex-wrap gap-2">
                                {tipoParaEditar.aplicavel_pf && (
                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                        Pessoa Física
                                    </span>
                                )}
                                {tipoParaEditar.aplicavel_pj && (
                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                                        Pessoa Jurídica
                                    </span>
                                )}
                                {!tipoParaEditar.aplicavel_pf && !tipoParaEditar.aplicavel_pj && (
                                    <span className="text-sm text-gray-500">Não especificado</span>
                                )}
                            </div>
                        </div>

                        {/* Status */}
                        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                            <h3 className="text-lg font-semibold text-green-900 mb-3 flex items-center">
                                <Shield className="h-5 w-5 mr-2" />
                                Status
                            </h3>
                            <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${tipoParaEditar.ativo
                                ? 'bg-green-100 text-green-800'
                                : 'bg-red-100 text-red-800'
                                }`}>
                                {tipoParaEditar.ativo ? 'Ativo' : 'Inativo'}
                            </span>
                        </div>

                        {/* Datas */}
                        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                            <h3 className="text-lg font-semibold text-gray-900 mb-3">Informações do Sistema</h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Data de Criação</label>
                                    <p className="text-sm text-gray-900 bg-white px-3 py-2 rounded border">
                                        {tipoParaEditar.created_at ? new Date(tipoParaEditar.created_at).toLocaleDateString('pt-BR') : '-'}
                                    </p>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Última Atualização</label>
                                    <p className="text-sm text-gray-900 bg-white px-3 py-2 rounded border">
                                        {tipoParaEditar.updated_at ? new Date(tipoParaEditar.updated_at).toLocaleDateString('pt-BR') : '-'}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                <div className="flex justify-end mt-6">
                    <button
                        onClick={() => setIsModalVisualizacaoOpen(false)}
                        className="px-4 py-2 bg-gray-600 text-white rounded-md text-sm font-medium hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                    >
                        Fechar
                    </button>
                </div>
            </Modal>

            {/* Modal de Confirmação de Exclusão */}
            <Modal
                isOpen={isModalConfirmacaoOpen}
                onClose={() => {
                    setIsModalConfirmacaoOpen(false);
                    setTipoParaExcluir(null);
                    setError(''); // Limpar erro ao fechar
                }}
                title="Confirmar Exclusão"
            >
                <div className="space-y-4">
                    {/* Mostrar erro se houver */}
                    {error && (
                        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                            <div className="flex">
                                <AlertTriangle className="h-5 w-5 text-red-400 mr-2 mt-0.5" />
                                <p className="text-sm">{error}</p>
                            </div>
                        </div>
                    )}

                    <div className="flex items-center">
                        <AlertTriangle className="h-12 w-12 text-red-500 mr-4" />
                        <div>
                            <h3 className="text-lg font-medium text-gray-900">Confirmar exclusão</h3>
                            <p className="text-sm text-gray-500">
                                Tem certeza que deseja excluir o tipo de atividade <strong>"{tipoParaExcluir?.nome}"</strong>?
                            </p>
                        </div>
                    </div>

                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                        <div className="flex">
                            <AlertTriangle className="h-5 w-5 text-yellow-400 mr-2 mt-0.5" />
                            <p className="text-sm text-yellow-800">
                                <strong>Atenção:</strong> Esta ação não pode ser desfeita. O tipo de atividade será removido permanentemente do sistema.
                            </p>
                        </div>
                    </div>

                    {/* Informação sobre restrições */}
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <div className="flex">
                            <Shield className="h-5 w-5 text-blue-400 mr-2 mt-0.5" />
                            <div className="text-sm text-blue-800">
                                <p className="font-medium mb-1">Restrições de Exclusão:</p>
                                <ul className="list-disc list-inside space-y-1 text-xs">
                                    <li>Não é possível excluir se houver <strong>regimes tributários vinculados</strong></li>
                                    <li>Não é possível excluir se houver <strong>propostas associadas</strong></li>
                                    <li>Para excluir, remova primeiro todos os vínculos</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="flex justify-end space-x-3 mt-6">
                    <button
                        onClick={() => {
                            setIsModalConfirmacaoOpen(false);
                            setTipoParaExcluir(null);
                            setError(''); // Limpar erro ao cancelar
                        }}
                        className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                        Cancelar
                    </button>
                    <button
                        onClick={handleExcluir}
                        disabled={loading}
                        className="px-4 py-2 bg-red-600 text-white rounded-md text-sm font-medium hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
                    >
                        {loading ? 'Excluindo...' : 'Sim, Excluir'}
                    </button>
                </div>
            </Modal>
        </div>
    );
};
