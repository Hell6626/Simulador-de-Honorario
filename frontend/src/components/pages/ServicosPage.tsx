import React, { useState, useEffect } from 'react';
import { Plus, Search, Trash2, Eye, Edit2, Shield, Package, DollarSign, AlertTriangle } from 'lucide-react';
import { apiService } from '../../services/api';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { Modal } from '../modals/Modal';
import { ModalVisualizacao } from '../modals/ModalVisualizacao';
import { useAuth } from '../../context/AuthContext';
import { Servico } from '../../types';

export const ServicosPage: React.FC = () => {
    const { user } = useAuth();
    const [servicos, setServicos] = useState<Servico[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [searchTerm, setSearchTerm] = useState('');
    const [categoriaFiltro, setCategoriaFiltro] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);

    // Estados para os modais
    const [servicoParaVisualizar, setServicoParaVisualizar] = useState<Servico | null>(null);
    const [servicoParaEditar, setServicoParaEditar] = useState<Servico | null>(null);
    const [isModalEdicaoOpen, setIsModalEdicaoOpen] = useState(false);

    // Estados para exclusão com impacto
    const [modalExclusaoOpen, setModalExclusaoOpen] = useState(false);
    const [dadosExclusao, setDadosExclusao] = useState<{
        servico: Servico;
        propostas_afetadas: any[];
        total_propostas: number;
    } | null>(null);
    const [verificandoImpacto, setVerificandoImpacto] = useState(false);

    // Estados do formulário
    const [formData, setFormData] = useState({
        nome: '',
        categoria: '',
        valor_base: '',
        descricao: '',
        tipo_atividade_id: null as number | null,
        regimes_tributarios: [] as number[]
    });

    // Estados para nova categoria
    const [modalNovaCategoria, setModalNovaCategoria] = useState(false);
    const [novaCategoria, setNovaCategoria] = useState('');
    const [categorias, setCategorias] = useState(['FISCAL', 'PESSOAL', 'SOCIETARIO', 'CONSULTORIA']);

    // Estados para regimes tributários
    const [regimesTributarios, setRegimesTributarios] = useState<Array<{ id: number, codigo: string, nome: string }>>([]);
    const [tiposAtividade, setTiposAtividade] = useState<Array<{ id: number, codigo: string, nome: string }>>([]);

    // Verificar se o usuário é admin
    const [isAdmin, setIsAdmin] = useState(false);
    const [verificandoPermissao, setVerificandoPermissao] = useState(true);

    // Verificar permissão de admin
    useEffect(() => {
        console.log('🔍 DEBUG: useEffect inicial executado');
        const isAdminUser = Boolean(user?.gerente);
        console.log('🔍 DEBUG: isAdminUser:', isAdminUser);
        setIsAdmin(isAdminUser);
        setVerificandoPermissao(false);

        if (isAdminUser) {
            console.log('🔍 DEBUG: Usuário é admin, carregando dados...');
            fetchServicos();
            fetchTiposAtividade();
            // Removido fetchRegimesTributarios() para evitar carregar todos os regimes no início
            console.log('🔍 DEBUG: fetchServicos e fetchTiposAtividade chamados');
        }
    }, [user]);

    // useEffect para pré-carregar dados quando o modal de edição abrir
    useEffect(() => {
        if (servicoParaEditar && isModalEdicaoOpen) {
            console.log('🔍 DEBUG: Modal de edição aberto, pré-carregando dados para:', servicoParaEditar.nome);

            // Garantir que os dados do formulário estejam corretos
            if (servicoParaEditar.tipo_atividade_id && regimesTributarios.length === 0) {
                console.log('🔍 DEBUG: Modal aberto mas regimes não carregados, carregando agora...');
                fetchRegimesTributarios(servicoParaEditar.tipo_atividade_id);
            }
        }
    }, [servicoParaEditar, isModalEdicaoOpen, regimesTributarios.length]);

    const fetchTiposAtividade = async () => {
        try {
            console.log('🔍 DEBUG: fetchTiposAtividade iniciado');
            const response = await apiService.getTiposAtividade();
            console.log('🔍 DEBUG: Tipos de atividade recebidos:', response);
            setTiposAtividade(response);
            console.log('🔍 DEBUG: tiposAtividade atualizado com', response.length, 'tipos');
        } catch (err: any) {
            console.error('❌ Erro ao carregar tipos de atividade:', err);
        }
    };

    const fetchRegimesTributarios = async (tipoAtividadeId?: number) => {
        try {
            console.log('🔍 DEBUG: fetchRegimesTributarios iniciado com tipoAtividadeId:', tipoAtividadeId);

            // Se não houver tipoAtividadeId, não buscar regimes
            if (!tipoAtividadeId) {
                console.log('🔍 DEBUG: Sem tipoAtividadeId, limpando regimes');
                setRegimesTributarios([]);
                return;
            }

            console.log('🔍 DEBUG: Chamando apiService.getRegimesTributarios...');

            const response = await apiService.getRegimesTributarios(tipoAtividadeId);

            console.log('🔍 DEBUG: Resposta da API:', response);
            console.log('🔍 DEBUG: Tipo da resposta:', typeof response);
            console.log('🔍 DEBUG: É array?', Array.isArray(response));
            console.log('🔍 DEBUG: Quantidade de regimes recebidos:', response.length);

            if (Array.isArray(response)) {
                setRegimesTributarios(response);
                console.log('🔍 DEBUG: regimesTributarios atualizado com', response.length, 'regimes');
                console.log('🔍 DEBUG: Regimes recebidos:', response.map(r => r.codigo));

                // Se estivermos editando um serviço, verificar se o regime atual ainda está disponível
                if (servicoParaEditar && servicoParaEditar.regimes_tributarios && servicoParaEditar.regimes_tributarios.length > 0) {
                    const regimeAtual = servicoParaEditar.regimes_tributarios[0];
                    const regimeAindaDisponivel = response.find(r => r.id === regimeAtual.id);

                    if (!regimeAindaDisponivel) {
                        console.log('🔍 DEBUG: Regime atual não está mais disponível, limpando seleção');
                        setFormData(prev => ({
                            ...prev,
                            regimes_tributarios: []
                        }));
                    }
                }
            } else {
                console.error('❌ Resposta não é um array:', response);
                setRegimesTributarios([]);
            }
        } catch (err: any) {
            console.error('❌ Erro ao carregar regimes tributários:', err);
            console.error('❌ Detalhes do erro:', err.message);
            setRegimesTributarios([]);
        }
    };

    const fetchServicos = async (page = 1, search = '', categoria = '') => {
        try {
            setLoading(true);
            const response = await apiService.getServicos({
                page,
                per_page: 10,
                search: search || undefined,
                categoria: categoria || undefined,
                ativo: true
            });
            setServicos(response.servicos || response.items || response || []);
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
        fetchServicos(1, searchTerm, categoriaFiltro);
    };

    const handlePageChange = (page: number) => {
        fetchServicos(page, searchTerm, categoriaFiltro);
    };

    const handleInputChange = (field: string, value: string) => {
        setFormData(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const handleTipoAtividadeChange = async (tipoAtividadeId: number | null) => {
        console.log('🔍 DEBUG: handleTipoAtividadeChange chamado com:', tipoAtividadeId);

        // Primeiro, limpar os regimes para evitar mostrar dados antigos
        setRegimesTributarios([]);
        console.log('🔍 DEBUG: regimesTributarios limpo');

        setFormData(prev => ({
            ...prev,
            tipo_atividade_id: tipoAtividadeId,
            regimes_tributarios: [] // Limpar regimes quando mudar o tipo de atividade
        }));
        console.log('🔍 DEBUG: formData atualizado');

        // Buscar regimes tributários filtrados pelo tipo de atividade
        if (tipoAtividadeId) {
            console.log('🔍 DEBUG: Chamando fetchRegimesTributarios com tipoAtividadeId:', tipoAtividadeId);
            try {
                await fetchRegimesTributarios(tipoAtividadeId);
                console.log('🔍 DEBUG: Regimes carregados com sucesso');
            } catch (error) {
                console.error('❌ Erro ao carregar regimes:', error);
                setRegimesTributarios([]);
            }
        } else {
            console.log('🔍 DEBUG: Sem tipoAtividadeId, regimes permanecerão vazios');
            // Não chamar fetchRegimesTributarios() - deixar regimes vazios
        }
    };

    const handleSalvar = async () => {
        if (!formData.nome.trim()) {
            setError('Nome do serviço é obrigatório');
            return;
        }

        if (!formData.categoria) {
            setError('Categoria é obrigatória');
            return;
        }

        if (!formData.tipo_atividade_id) {
            setError('Tipo de atividade é obrigatório');
            return;
        }

        if (!formData.regimes_tributarios || formData.regimes_tributarios.length === 0) {
            setError('Regime tributário é obrigatório');
            return;
        }

        if (!formData.valor_base || isNaN(Number(formData.valor_base))) {
            setError('Valor base é obrigatório e deve ser um número válido');
            return;
        }

        try {
            setLoading(true);
            const dataToSend = {
                ...formData,
                valor_base: Number(formData.valor_base),
                tipo_cobranca: 'MENSAL' // Valor padrão
            };
            const response = await apiService.createServico(dataToSend);
            setServicos(prev => [response, ...prev]);
            setIsModalOpen(false);
            setFormData({ nome: '', categoria: '', valor_base: '', descricao: '', tipo_atividade_id: null, regimes_tributarios: [] });
            setError('');
        } catch (err: any) {
            console.error('Erro ao criar serviço:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleEditar = async () => {
        if (!servicoParaEditar || !formData.nome.trim()) {
            setError('Nome do serviço é obrigatório');
            return;
        }

        if (!formData.categoria) {
            setError('Categoria é obrigatória');
            return;
        }

        if (!formData.tipo_atividade_id) {
            setError('Tipo de atividade é obrigatório');
            return;
        }

        if (!formData.regimes_tributarios || formData.regimes_tributarios.length === 0) {
            setError('Regime tributário é obrigatório');
            return;
        }

        if (!formData.valor_base || isNaN(Number(formData.valor_base))) {
            setError('Valor base é obrigatório e deve ser um número válido');
            return;
        }

        try {
            setLoading(true);
            const dataToSend = {
                ...formData,
                valor_base: Number(formData.valor_base)
            };
            const response = await apiService.updateServico(servicoParaEditar.id, dataToSend);
            setServicos(prev => prev.map(s => s.id === servicoParaEditar.id ? response : s));
            setIsModalEdicaoOpen(false);
            setServicoParaEditar(null);
            setFormData({ nome: '', categoria: '', valor_base: '', descricao: '', tipo_atividade_id: null, regimes_tributarios: [] });
            setError('');
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const verificarImpactoExclusao = async (servico: Servico) => {
        try {
            setVerificandoImpacto(true);
            const response = await apiService.verificarImpactoExclusaoServico(servico.id);

            setDadosExclusao({
                servico: servico,
                propostas_afetadas: response.propostas_afetadas || [],
                total_propostas: response.total_propostas || 0
            });
            setModalExclusaoOpen(true);
        } catch (err: any) {
            setError(`Erro ao verificar impacto: ${err.message}`);
        } finally {
            setVerificandoImpacto(false);
        }
    };

    const confirmarExclusaoComImpacto = async () => {
        if (!dadosExclusao) return;

        try {
            setLoading(true);
            const response = await apiService.deleteServico(dadosExclusao.servico.id) as any;

            // Atualizar lista de serviços
            setServicos(servicos.filter(s => s.id !== dadosExclusao.servico.id));

            // Mostrar mensagem de sucesso
            setError(''); // Limpar erro anterior
            // Aqui poderia mostrar uma notificação de sucesso
            console.log(response.message);

            // Fechar modal
            setModalExclusaoOpen(false);
            setDadosExclusao(null);
        } catch (err: any) {
            setError(`Erro ao excluir serviço: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    const cancelarExclusao = () => {
        setModalExclusaoOpen(false);
        setDadosExclusao(null);
    };



    const abrirModalEdicao = async (servico: Servico) => {
        console.log('🔍 DEBUG: Abrindo modal de edição para serviço:', servico);

        setServicoParaEditar(servico);

        // Primeiro, definir os dados básicos
        const dadosIniciais = {
            nome: servico.nome,
            categoria: servico.categoria,
            valor_base: servico.valor_base.toString(),
            descricao: servico.descricao || '',
            tipo_atividade_id: servico.tipo_atividade_id || null,
            regimes_tributarios: servico.regimes_tributarios?.map(r => r.id) || []
        };

        console.log('🔍 DEBUG: Dados iniciais do formulário:', dadosIniciais);
        setFormData(dadosIniciais);

        // Carregar regimes tributários filtrados baseado no tipo de atividade do serviço
        if (servico.tipo_atividade_id) {
            console.log('🔍 DEBUG: Editando serviço - carregando regimes para tipo_atividade_id:', servico.tipo_atividade_id);
            try {
                await fetchRegimesTributarios(servico.tipo_atividade_id);
                console.log('🔍 DEBUG: Regimes carregados com sucesso para edição');
            } catch (error) {
                console.error('❌ Erro ao carregar regimes para edição:', error);
                setRegimesTributarios([]);
            }
        } else {
            console.log('🔍 DEBUG: Editando serviço - serviço sem tipo_atividade_id, regimes permanecerão vazios');
            setRegimesTributarios([]);
        }

        setIsModalEdicaoOpen(true);
    };

    const handleSubmitNovaCategoria = (e: React.FormEvent) => {
        e.preventDefault();
        if (novaCategoria.trim()) {
            const novaCategoriaNormalizada = novaCategoria.toUpperCase().trim();
            if (!categorias.includes(novaCategoriaNormalizada)) {
                setCategorias([...categorias, novaCategoriaNormalizada]);
                setFormData(prev => ({ ...prev, categoria: novaCategoriaNormalizada }));
            }
            setNovaCategoria('');
            setModalNovaCategoria(false);
        }
    };

    // Formatação de valor monetário
    const formatarValor = (valor: number) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(valor);
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
                    <h1 className="text-2xl font-bold text-gray-900">Serviços</h1>
                    <p className="text-sm text-gray-500">Gerencie os serviços oferecidos pela empresa</p>
                </div>

                <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                    <div className="flex items-center">
                        <Shield className="w-8 h-8 text-red-400 mr-3" />
                        <div>
                            <h3 className="text-lg font-medium text-red-800">Acesso Negado</h3>
                            <p className="text-red-700 mt-1">
                                Você não tem permissão para acessar esta página. Apenas administradores podem gerenciar serviços.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Debug Info */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h3 className="font-medium text-yellow-800">Debug Info:</h3>
                <p className="text-sm text-yellow-700">
                    Tipos de Atividade: {tiposAtividade.length} |
                    Regimes Tributários: {regimesTributarios.length} |
                    Tipo Selecionado: {formData.tipo_atividade_id || 'Nenhum'}
                </p>
                <p className="text-sm text-yellow-700">
                    Regimes disponíveis: {regimesTributarios.map(r => r.codigo).join(', ') || 'Nenhum'}
                </p>
            </div>
            {/* Page Title */}
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900">Serviços</h1>
                <p className="text-sm text-gray-500">Gerencie os serviços oferecidos pela empresa</p>
            </div>

            {/* Search and Actions */}
            <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
                <div className="flex flex-col sm:flex-row gap-4 flex-1">
                    <form onSubmit={handleSearch} className="flex-1 max-w-md">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                            <input
                                type="text"
                                placeholder="Buscar serviços..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                        </div>
                    </form>

                    <select
                        value={categoriaFiltro}
                        onChange={(e) => {
                            setCategoriaFiltro(e.target.value);
                            fetchServicos(1, searchTerm, e.target.value);
                        }}
                        className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                        <option value="">Todas as categorias</option>
                        {categorias.map(cat => (
                            <option key={cat} value={cat}>{cat}</option>
                        ))}
                    </select>
                </div>

                <button
                    onClick={() => setIsModalOpen(true)}
                    className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                    <Plus className="w-4 h-4 mr-2" />
                    Novo Serviço
                </button>
            </div>

            {/* Error Message */}
            {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-700">{error}</p>
                </div>
            )}

            {/* Services List */}
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
                                        Serviço
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Categoria
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Tipo Atividade
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Regime Tributário
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Valor Base
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Descrição
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
                                {servicos.map((servico) => (
                                    <tr key={servico.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center">
                                                <Package className="w-5 h-5 text-gray-400 mr-3" />
                                                <div>
                                                    <div className="text-sm font-medium text-gray-900">
                                                        {servico.nome}
                                                    </div>
                                                    <div className="text-sm text-gray-500">
                                                        {servico.codigo}
                                                    </div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${servico.categoria === 'FISCAL' ? 'bg-blue-100 text-blue-800' :
                                                servico.categoria === 'PESSOAL' ? 'bg-green-100 text-green-800' :
                                                    servico.categoria === 'SOCIETARIO' ? 'bg-purple-100 text-purple-800' :
                                                        'bg-yellow-100 text-yellow-800'
                                                }`}>
                                                {servico.categoria}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                            {servico.tipo_atividade_id ? (
                                                tiposAtividade.find(t => t.id === servico.tipo_atividade_id)?.nome || 'N/A'
                                            ) : '-'}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                            {servico.regimes_tributarios && servico.regimes_tributarios.length > 0 ? (
                                                <div className="space-y-1">
                                                    {servico.regimes_tributarios.map((regime: any, index: number) => (
                                                        <span key={index} className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mr-1">
                                                            {regime.codigo}
                                                        </span>
                                                    ))}
                                                </div>
                                            ) : '-'}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center text-sm text-gray-900">
                                                <DollarSign className="w-4 h-4 mr-1 text-gray-400" />
                                                {formatarValor(servico.valor_base)}
                                            </div>
                                        </td>

                                        <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                                            {servico.descricao || '-'}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${servico.ativo
                                                ? 'bg-green-100 text-green-800'
                                                : 'bg-red-100 text-red-800'
                                                }`}>
                                                {servico.ativo ? 'Ativo' : 'Inativo'}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                            <div className="flex items-center justify-end space-x-2">
                                                <button
                                                    onClick={() => setServicoParaVisualizar(servico)}
                                                    className="text-blue-600 hover:text-blue-900 p-1"
                                                    title="Visualizar"
                                                >
                                                    <Eye className="w-4 h-4" />
                                                </button>
                                                <button
                                                    onClick={() => abrirModalEdicao(servico)}
                                                    className="text-green-600 hover:text-green-900 p-1"
                                                    title="Editar"
                                                >
                                                    <Edit2 className="w-4 h-4" />
                                                </button>
                                                <button
                                                    onClick={() => verificarImpactoExclusao(servico)}
                                                    className="text-red-600 hover:text-red-900 p-1"
                                                    title="Excluir"
                                                    disabled={verificandoImpacto}
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
                    setFormData({ nome: '', categoria: '', valor_base: '', descricao: '', tipo_atividade_id: null, regimes_tributarios: [] });
                    setError('');
                }}
                title="Cadastrar Novo Serviço"
            >
                <div className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Nome do Serviço *
                        </label>
                        <input
                            type="text"
                            value={formData.nome}
                            onChange={(e) => handleInputChange('nome', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="Ex: Contabilidade Mensal"
                        />
                    </div>

                    <div className="flex items-center gap-2">
                        <div className="flex-1">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Categoria *
                            </label>
                            <select
                                value={formData.categoria}
                                onChange={(e) => handleInputChange('categoria', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            >
                                <option value="">Selecione uma categoria</option>
                                {categorias.map(cat => (
                                    <option key={cat} value={cat}>{cat}</option>
                                ))}
                            </select>
                        </div>

                        <button
                            type="button"
                            onClick={() => setModalNovaCategoria(true)}
                            className="mt-6 p-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                            title="Criar nova categoria"
                        >
                            <Plus className="w-4 h-4" />
                        </button>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Tipo de Atividade
                        </label>
                        <select
                            value={formData.tipo_atividade_id || ''}
                            onChange={(e) => handleTipoAtividadeChange(e.target.value ? parseInt(e.target.value) : null)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                            <option value="">Selecione um tipo de atividade</option>
                            {tiposAtividade.map((tipo) => (
                                <option key={tipo.id} value={tipo.id}>
                                    {tipo.codigo} - {tipo.nome}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Valor Base *
                        </label>
                        <input
                            type="number"
                            step="0.01"
                            value={formData.valor_base}
                            onChange={(e) => handleInputChange('valor_base', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="0,00"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Regime Tributário
                        </label>
                        <select
                            value={formData.regimes_tributarios[0] || ''}
                            onChange={(e) => {
                                const selectedValue = e.target.value ? parseInt(e.target.value) : null;
                                setFormData(prev => ({
                                    ...prev,
                                    regimes_tributarios: selectedValue ? [selectedValue] : []
                                }));
                            }}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            disabled={regimesTributarios.length === 0}
                        >
                            <option value="">
                                {regimesTributarios.length === 0
                                    ? (formData.tipo_atividade_id
                                        ? "Nenhum regime tributário disponível para este tipo de atividade"
                                        : "Selecione um tipo de atividade primeiro")
                                    : "Selecione um regime tributário"
                                }
                            </option>
                            {regimesTributarios.map((regime) => (
                                <option key={regime.id} value={regime.id}>
                                    {regime.codigo} - {regime.nome}
                                </option>
                            ))}
                        </select>
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
                            placeholder="Descreva o serviço oferecido"
                        />
                    </div>
                </div>

                <div className="flex justify-end space-x-3 mt-6">
                    <button
                        onClick={() => {
                            setIsModalOpen(false);
                            setFormData({ nome: '', categoria: '', valor_base: '', descricao: '', tipo_atividade_id: null, regimes_tributarios: [] });
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
                    setServicoParaEditar(null);
                    setFormData({ nome: '', categoria: '', valor_base: '', descricao: '', tipo_atividade_id: null, regimes_tributarios: [] });
                    setError('');
                }}
                title="Editar Serviço"
            >
                {/* Debug Info */}
                {servicoParaEditar && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                        <h4 className="font-medium text-blue-800 text-sm">Debug Info:</h4>
                        <p className="text-xs text-blue-700">
                            Serviço: {servicoParaEditar.nome} |
                            Tipo Atividade ID: {servicoParaEditar.tipo_atividade_id || 'N/A'} |
                            Regimes: {servicoParaEditar.regimes_tributarios?.length || 0} |
                            Regimes Disponíveis: {regimesTributarios.length}
                        </p>
                    </div>
                )}
                <div className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Nome do Serviço *
                        </label>
                        <input
                            type="text"
                            value={formData.nome}
                            onChange={(e) => handleInputChange('nome', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="Ex: Contabilidade Mensal"
                        />
                    </div>

                    <div className="flex items-center gap-2">
                        <div className="flex-1">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Categoria *
                            </label>
                            <select
                                value={formData.categoria}
                                onChange={(e) => handleInputChange('categoria', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            >
                                <option value="">Selecione uma categoria</option>
                                {categorias.map(cat => (
                                    <option key={cat} value={cat}>{cat}</option>
                                ))}
                            </select>
                        </div>

                        <button
                            type="button"
                            onClick={() => setModalNovaCategoria(true)}
                            className="mt-6 p-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                            title="Criar nova categoria"
                        >
                            <Plus className="w-4 h-4" />
                        </button>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Tipo de Atividade
                        </label>
                        <select
                            value={formData.tipo_atividade_id || ''}
                            onChange={(e) => handleTipoAtividadeChange(e.target.value ? parseInt(e.target.value) : null)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                            <option value="">Selecione um tipo de atividade</option>
                            {tiposAtividade.map((tipo) => (
                                <option key={tipo.id} value={tipo.id}>
                                    {tipo.codigo} - {tipo.nome}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Valor Base *
                        </label>
                        <input
                            type="number"
                            step="0.01"
                            value={formData.valor_base}
                            onChange={(e) => handleInputChange('valor_base', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="0,00"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Regime Tributário
                        </label>
                        <select
                            value={formData.regimes_tributarios[0] || ''}
                            onChange={(e) => {
                                const selectedValue = e.target.value ? parseInt(e.target.value) : null;
                                setFormData(prev => ({
                                    ...prev,
                                    regimes_tributarios: selectedValue ? [selectedValue] : []
                                }));
                            }}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            disabled={regimesTributarios.length === 0}
                        >
                            <option value="">
                                {regimesTributarios.length === 0
                                    ? (formData.tipo_atividade_id
                                        ? "Nenhum regime tributário disponível para este tipo de atividade"
                                        : "Selecione um tipo de atividade primeiro")
                                    : "Selecione um regime tributário"
                                }
                            </option>
                            {regimesTributarios.map((regime) => (
                                <option key={regime.id} value={regime.id}>
                                    {regime.codigo} - {regime.nome}
                                </option>
                            ))}
                        </select>
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
                            placeholder="Descreva o serviço oferecido"
                        />
                    </div>
                </div>

                <div className="flex justify-end space-x-3 mt-6">
                    <button
                        onClick={() => {
                            setIsModalEdicaoOpen(false);
                            setServicoParaEditar(null);
                            setFormData({ nome: '', categoria: '', valor_base: '', descricao: '', tipo_atividade_id: null, regimes_tributarios: [] });
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
                isOpen={!!servicoParaVisualizar}
                onClose={() => setServicoParaVisualizar(null)}
                type="servico"
                data={servicoParaVisualizar}
            />

            {/* Modal Nova Categoria */}
            <Modal
                isOpen={modalNovaCategoria}
                onClose={() => {
                    setModalNovaCategoria(false);
                    setNovaCategoria('');
                }}
                title="Criar Nova Categoria"
                size="sm"
            >
                <form onSubmit={handleSubmitNovaCategoria}>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Nome da Categoria *
                            </label>
                            <input
                                type="text"
                                value={novaCategoria}
                                onChange={(e) => setNovaCategoria(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="Ex: CONSULTORIA"
                                required
                            />
                        </div>

                        <div className="flex justify-end gap-3">
                            <button
                                type="button"
                                onClick={() => {
                                    setModalNovaCategoria(false);
                                    setNovaCategoria('');
                                }}
                                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                            >
                                Cancelar
                            </button>
                            <button
                                type="submit"
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                            >
                                Criar Categoria
                            </button>
                        </div>
                    </div>
                </form>
            </Modal>

            {/* Modal de Confirmação de Exclusão com Impacto */}
            {modalExclusaoOpen && dadosExclusao && (
                <Modal
                    isOpen={modalExclusaoOpen}
                    onClose={cancelarExclusao}
                    title="Confirmar Exclusão"
                    size="md"
                >
                    <div className="space-y-4">
                        <div className="flex items-center text-red-600">
                            <AlertTriangle className="w-6 h-6 mr-2" />
                            <h3 className="font-medium">Atenção: Ação Irreversível</h3>
                        </div>

                        <p className="text-gray-700">Tem certeza que deseja excluir o serviço:</p>
                        <div className="bg-gray-100 p-3 rounded-lg">
                            <strong>{dadosExclusao.servico.nome}</strong>
                            <div className="text-sm text-gray-600 mt-1">
                                Categoria: {dadosExclusao.servico.categoria} |
                                Valor: {formatarValor(dadosExclusao.servico.valor_base)}
                            </div>
                        </div>

                        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
                            <h4 className="font-medium text-yellow-800">Impactos desta ação:</h4>
                            <ul className="mt-2 text-sm text-yellow-700 list-disc list-inside space-y-1">
                                <li>O serviço será removido de <strong>{dadosExclusao.total_propostas} proposta(s)</strong></li>
                                <li>Os valores das propostas serão recalculados automaticamente</li>
                                <li>Um registro será criado no histórico de cada proposta</li>
                                <li>Esta ação não pode ser desfeita</li>
                            </ul>
                        </div>

                        {dadosExclusao.propostas_afetadas.length > 0 && (
                            <div>
                                <h4 className="font-medium text-gray-800 mb-2">Propostas que serão afetadas:</h4>
                                <div className="max-h-32 overflow-y-auto bg-gray-50 rounded-lg p-3 space-y-2">
                                    {dadosExclusao.propostas_afetadas.map(prop => (
                                        <div key={prop.id} className="text-sm">
                                            <div className="font-medium text-gray-900">
                                                • {prop.numero} - {prop.cliente_nome}
                                            </div>
                                            <div className="text-gray-600 ml-3">
                                                Valor do serviço: {formatarValor(prop.valor_servico)}
                                                ({prop.quantidade_itens} item{prop.quantidade_itens !== 1 ? 's' : ''})
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        <div className="flex justify-end gap-3 pt-4">
                            <button
                                onClick={cancelarExclusao}
                                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                                disabled={loading}
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={confirmarExclusaoComImpacto}
                                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
                                disabled={loading}
                            >
                                {loading ? 'Excluindo...' : 'Confirmar Exclusão'}
                            </button>
                        </div>
                    </div>
                </Modal>
            )}
        </div>
    );
};
