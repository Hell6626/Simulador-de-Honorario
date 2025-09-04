import React, { useState, useEffect } from 'react';
import {
    Edit, Tag, List, DollarSign, Settings, CheckCircle,
    MessageSquare, Clock, X
} from 'lucide-react';
import { apiService } from '../../services/api';

interface HistoricoLogsProps {
    propostaId: number;
    isOpen: boolean;
    onClose: () => void;
}

interface Log {
    id: number;
    proposta_id: number;
    funcionario_id: number;
    acao: string;
    detalhes: string;
    detalhes_formatados?: any;
    created_at: string;
    funcionario?: {
        id: number;
        nome: string;
        email: string;
    };
}

export const HistoricoLogs: React.FC<HistoricoLogsProps> = ({
    propostaId,
    isOpen,
    onClose
}) => {
    const [logs, setLogs] = useState<Log[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        if (isOpen && propostaId) {
            carregarLogs();
        }
    }, [isOpen, propostaId]);

    const carregarLogs = async () => {
        setLoading(true);
        setError('');

        try {
            const response = await apiService.getLogsPropostas(propostaId);
            setLogs(response.logs || []);
        } catch (error) {
            console.error('Erro ao carregar logs:', error);
            setError('Erro ao carregar histórico de alterações');
        } finally {
            setLoading(false);
        }
    };

    const getIconeAcao = (acao: string) => {
        const icones = {
            'PROPOSTA_EDITADA': <Edit className="w-4 h-4 text-blue-600" />,
            'STATUS_ALTERADO': <Tag className="w-4 h-4 text-purple-600" />,
            'SERVICOS_ALTERADOS': <List className="w-4 h-4 text-green-600" />,
            'DESCONTO_ALTERADO': <DollarSign className="w-4 h-4 text-orange-600" />,
            'CONFIGURACOES_ALTERADAS': <Settings className="w-4 h-4 text-indigo-600" />,
            'PROPOSTA_FINALIZADA': <CheckCircle className="w-4 h-4 text-emerald-600" />,
            'OBSERVACOES_ALTERADAS': <MessageSquare className="w-4 h-4 text-gray-600" />
        };
        return icones[acao as keyof typeof icones] || <Clock className="w-4 h-4 text-gray-500" />;
    };

    const formatarDetalhes = (log: Log) => {
        if (typeof log.detalhes_formatados === 'object') {
            return (
                <pre className="text-xs bg-gray-100 p-2 rounded mt-2 overflow-x-auto">
                    {JSON.stringify(log.detalhes_formatados, null, 2)}
                </pre>
            );
        }
        return <p className="text-sm text-gray-600 mt-1">{log.detalhes_formatados || log.detalhes}</p>;
    };

    const formatarAcao = (acao: string) => {
        return acao.replace('_', ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999]">
            <div className="bg-white shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col mx-4">
                {/* Header */}
                <div className="bg-gradient-to-r from-gray-700 to-gray-800 text-white p-6 flex-shrink-0">
                    <div className="flex items-center justify-between">
                        <div>
                            <h3 className="text-xl font-bold">Histórico de Alterações</h3>
                            <p className="text-gray-300 text-sm">Proposta #{propostaId}</p>
                        </div>
                        <button
                            onClick={onClose}
                            className="text-gray-300 hover:text-white transition-colors"
                        >
                            <X className="w-6 h-6" />
                        </button>
                    </div>
                </div>

                {/* Conteúdo */}
                <div className="flex-1 overflow-y-auto p-6">
                    {loading ? (
                        <div className="text-center py-8">
                            <div className="animate-spin w-8 h-8 border-4 border-gray-300 border-t-blue-600 rounded-full mx-auto mb-4"></div>
                            <p className="text-gray-600">Carregando histórico...</p>
                        </div>
                    ) : error ? (
                        <div className="text-center py-8">
                            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                                <p className="text-red-700">{error}</p>
                                <button
                                    onClick={carregarLogs}
                                    className="mt-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                                >
                                    Tentar Novamente
                                </button>
                            </div>
                        </div>
                    ) : logs.length === 0 ? (
                        <div className="text-center py-8 text-gray-500">
                            <Clock className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                            <p>Nenhuma alteração registrada</p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {logs.map((log, index) => (
                                <div key={log.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                                    <div className="flex items-start space-x-3">
                                        <div className="flex-shrink-0 mt-1">
                                            {getIconeAcao(log.acao)}
                                        </div>

                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center justify-between">
                                                <h4 className="font-medium text-gray-900">
                                                    {formatarAcao(log.acao)}
                                                </h4>
                                                <span className="text-xs text-gray-500">
                                                    {new Date(log.created_at).toLocaleString('pt-BR')}
                                                </span>
                                            </div>

                                            {log.funcionario && (
                                                <p className="text-sm text-gray-600">
                                                    por <span className="font-medium">{log.funcionario.nome}</span>
                                                </p>
                                            )}

                                            {log.detalhes_formatados && formatarDetalhes(log)}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="bg-gray-50 px-6 py-4 border-t flex justify-between items-center flex-shrink-0">
                    <div className="text-sm text-gray-600">
                        Total de {logs.length} registro{logs.length !== 1 ? 's' : ''} encontrado{logs.length !== 1 ? 's' : ''}
                    </div>
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                        Fechar
                    </button>
                </div>
            </div>
        </div>
    );
};
