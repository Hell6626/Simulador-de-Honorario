import React from 'react';
import { Cliente } from '../../types';

interface ClienteDisplayProps {
    cliente: Cliente;
    showDetails?: boolean;
    className?: string;
}

const ClienteDisplay: React.FC<ClienteDisplayProps> = ({
    cliente,
    showDetails = true,
    className = ''
}) => {
    // Verificar se é cliente PJ (tem entidades jurídicas)
    const isPessoaJuridica = cliente.entidades_juridicas && cliente.entidades_juridicas.length > 0;

    // Dados da empresa (primeira entidade jurídica)
    const empresa = isPessoaJuridica ? cliente.entidades_juridicas[0] : null;

    // Formatar CPF/CNPJ
    const formatarDocumento = (documento: string, tipo: 'CPF' | 'CNPJ') => {
        if (!documento) return '';

        if (tipo === 'CPF') {
            return documento.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
        } else {
            return documento.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
        }
    };

    return (
        <div className={`cliente-display ${className}`}>
            {isPessoaJuridica && empresa ? (
                // Exibição para Pessoa Jurídica
                <div className="cliente-pj">
                    <div className="cliente-header">
                        <h3 className="cliente-nome-empresa">{empresa.razao_social}</h3>
                        <span className="cliente-tipo-badge">Pessoa Jurídica</span>
                    </div>

                    <div className="cliente-dados-empresa">
                        <div className="cliente-campo">
                            <span className="cliente-label">CNPJ:</span>
                            <span className="cliente-valor">{formatarDocumento(empresa.cnpj, 'CNPJ')}</span>
                        </div>

                        {empresa.nome_fantasia && (
                            <div className="cliente-campo">
                                <span className="cliente-label">Nome Fantasia:</span>
                                <span className="cliente-valor">{empresa.nome_fantasia}</span>
                            </div>
                        )}

                        {empresa.inscricao_estadual && (
                            <div className="cliente-campo">
                                <span className="cliente-label">Inscrição Estadual:</span>
                                <span className="cliente-valor">{empresa.inscricao_estadual}</span>
                            </div>
                        )}
                    </div>

                    {showDetails && (
                        <div className="cliente-dados-responsavel">
                            <h4 className="cliente-subtitulo">Responsável Legal</h4>
                            <div className="cliente-campo">
                                <span className="cliente-label">Nome:</span>
                                <span className="cliente-valor">{cliente.nome}</span>
                            </div>

                            <div className="cliente-campo">
                                <span className="cliente-label">CPF:</span>
                                <span className="cliente-valor">{formatarDocumento(cliente.cpf, 'CPF')}</span>
                            </div>

                            {cliente.email && (
                                <div className="cliente-campo">
                                    <span className="cliente-label">Email:</span>
                                    <span className="cliente-valor">{cliente.email}</span>
                                </div>
                            )}

                            {cliente.telefone && (
                                <div className="cliente-campo">
                                    <span className="cliente-label">Telefone:</span>
                                    <span className="cliente-valor">{cliente.telefone}</span>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            ) : (
                // Exibição para Pessoa Física
                <div className="cliente-pf">
                    <div className="cliente-header">
                        <h3 className="cliente-nome">{cliente.nome}</h3>
                        <span className="cliente-tipo-badge">Pessoa Física</span>
                    </div>

                    <div className="cliente-dados-pessoais">
                        <div className="cliente-campo">
                            <span className="cliente-label">CPF:</span>
                            <span className="cliente-valor">{formatarDocumento(cliente.cpf, 'CPF')}</span>
                        </div>

                        {cliente.email && (
                            <div className="cliente-campo">
                                <span className="cliente-label">Email:</span>
                                <span className="cliente-valor">{cliente.email}</span>
                            </div>
                        )}

                        {cliente.telefone && (
                            <div className="cliente-campo">
                                <span className="cliente-label">Telefone:</span>
                                <span className="cliente-valor">{cliente.telefone}</span>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default ClienteDisplay;
