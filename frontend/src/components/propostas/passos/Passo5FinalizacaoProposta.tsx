import React, { useState, useEffect, useMemo } from 'react';
import {
    CheckCircle,
    ArrowLeft,
    AlertTriangle,
    User,
    Building,
    Settings,
    List,
    Calculator,
    MessageSquare,
    FileDown,
    FileText,
    Info
} from 'lucide-react';
import jsPDF from 'jspdf';

// Importação do autoTable
import 'jspdf-autotable';
import { apiService } from '../../../services/api';
import { LoadingSpinner } from '../../common/LoadingSpinner';

// Extend jsPDF type para autoTable
declare module 'jspdf' {
    interface jsPDF {
        autoTable: (options: any) => jsPDF;
        lastAutoTable: {
            finalY: number;
        };
    }
}

// Interfaces TypeScript
interface Cliente {
    id: number;
    nome: string;
    cpf: string;
    email: string;
    abertura_empresa: boolean;
    ativo: boolean;
}

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
    aplicavel_pf: boolean;
    aplicavel_pj: boolean;
    requer_definicoes_fiscais: boolean;
    ativo: boolean;
}

interface FaixaFaturamento {
    id: number;
    nome: string;
    valor_inicial: number;
    valor_final?: number;
    aliquota: number;
    regime_tributario_id: number;
    ativo: boolean;
}

interface Servico {
    id: number;
    codigo: string;
    nome: string;
    categoria: string;
    tipo_cobranca: string;
    valor_base: number;
    descricao: string;
    ativo: boolean;
}

interface ServicoSelecionado {
    servico_id: number;
    quantidade: number;
    valor_unitario: number;
    subtotal: number;
    extras?: Record<string, any>;
}

interface PropostaCompleta {
    cliente: Cliente;
    tipoAtividade: TipoAtividade;
    regimeTributario: RegimeTributario;
    faixaFaturamento?: FaixaFaturamento;
    servicosSelecionados: ServicoSelecionado[];
}

interface PropostaComDesconto extends PropostaCompleta {
    id?: number;
    percentualDesconto: number;
    valorDesconto: number;
    totalFinal: number;
    requerAprovacao: boolean;
    observacoes?: string;
}

interface PropostaResponse {
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
}

interface Passo5Props {
    dadosProposta: PropostaComDesconto;
    onVoltar: () => void;
    onFinalizado: (propostaFinalizada: PropostaResponse) => void;
}

// Função para formatar moeda
const formatarMoeda = (valor: number): string => {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
};

// ⚠️ FUNÇÃO: Sanitizar texto para PDF
const sanitizarTexto = (texto: string): string => {
    if (!texto) return '';

    return texto
        // Remover caracteres de controle e invisíveis
        .replace(/[\u0000-\u001F\u007F-\u009F]/g, '')
        // Remover emojis
        .replace(/[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu, '')
        // Remover caracteres especiais problemáticos
        .replace(/[^\w\s\-\.,:;!?()[\]{}'"@#$%&*+=<>/\\|`~áàâãäéèêëíìîïóòôõöúùûüçñÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑ]/g, '')
        // Normalizar espaços
        .replace(/\s+/g, ' ')
        .trim();
};

// ⚠️ FUNÇÃO: Sanitizar dados da proposta
const sanitizarDadosProposta = (dados: any): any => {
    const sanitizarObjeto = (obj: any): any => {
        if (typeof obj === 'string') {
            return sanitizarTexto(obj);
        }
        if (Array.isArray(obj)) {
            return obj.map(sanitizarObjeto);
        }
        if (obj && typeof obj === 'object') {
            const resultado: any = {};
            for (const [chave, valor] of Object.entries(obj)) {
                resultado[chave] = sanitizarObjeto(valor);
            }
            return resultado;
        }
        return obj;
    };

    return sanitizarObjeto(dados);
};

// ⚠️ FUNÇÃO: Identificar se é MEI
const isMEI = (regimeTributario: RegimeTributario): boolean => {
    if (!regimeTributario) return false;

    // Verificar por código do regime
    if (regimeTributario?.codigo?.toLowerCase().includes('mei')) {
        return true;
    }

    // Verificar por nome do regime
    if (regimeTributario?.nome?.toLowerCase().includes('microempreendedor') ||
        regimeTributario?.nome?.toLowerCase().includes('mei')) {
        return true;
    }

    return false;
};

// ⚠️ FUNÇÃO PARA CALCULAR TAXA DE ABERTURA
const calcularTaxaAbertura = (cliente: Cliente, regimeTributario: RegimeTributario): number => {
    if (!cliente?.abertura_empresa) {
        return 0;
    }

    return isMEI(regimeTributario) ? 300.00 : 1000.00;
};

// ⚠️ FUNÇÃO PARA OBTER TIPO DE ABERTURA
const getTipoAbertura = (cliente: Cliente, regimeTributario: RegimeTributario): string => {
    if (!cliente?.abertura_empresa) {
        return '';
    }

    return isMEI(regimeTributario) ? 'MEI' : 'Empresa';
};

// ⚠️ FUNÇÃO DE DEBUG: Verificar dados antes de gerar PDF
const verificarDadosCompletos = (
    dadosProposta: PropostaComDesconto,
    todosServicos: Servico[]
) => {
    console.group('🔍 VERIFICAÇÃO DE DADOS PARA PDF');

    console.log('1. Dados da Proposta:', {
        id: dadosProposta.id,
        cliente: dadosProposta.cliente?.nome,
        tipoAtividade: dadosProposta.tipoAtividade?.nome,
        regimeTributario: dadosProposta.regimeTributario?.nome,
        servicosSelecionados: dadosProposta.servicosSelecionados?.length
    });

    console.log('2. Serviços Selecionados:', dadosProposta.servicosSelecionados);

    console.log('3. Todos os Serviços Carregados:', {
        total: todosServicos.length,
        servicos: todosServicos.map(s => ({ id: s.id, nome: s.nome, categoria: s.categoria }))
    });

    console.groupEnd();

    // ⚠️ VALIDAÇÕES
    const problemas = [];

    if (!dadosProposta.cliente) problemas.push('Cliente não encontrado');
    if (!dadosProposta.tipoAtividade) problemas.push('Tipo de atividade não encontrado');
    if (!dadosProposta.regimeTributario) problemas.push('Regime tributário não encontrado');
    if (!dadosProposta.servicosSelecionados || dadosProposta.servicosSelecionados.length === 0) {
        problemas.push('Nenhum serviço selecionado');
    }
    if (todosServicos.length === 0) problemas.push('Lista de serviços não carregada');

    if (problemas.length > 0) {
        console.error('❌ PROBLEMAS ENCONTRADOS:', problemas);
        alert(`Erro: ${problemas.join(', ')}. Recarregue a página e tente novamente.`);
        return false;
    }

    return true;
};

// ⚠️ FUNÇÃO CORRIGIDA: PDF com dados completos
const gerarPDFProfissionalCorrigido = (
    dadosProposta: PropostaComDesconto,
    proposta: PropostaResponse,
    todosServicos: Servico[]
) => {
    // ⚠️ VERIFICAR: Dados antes de prosseguir
    if (!verificarDadosCompletos(dadosProposta, todosServicos)) {
        return;
    }

    // ⚠️ VERIFICAR: Se jsPDF está disponível
    if (typeof jsPDF === 'undefined') {
        console.error('❌ jsPDF não está disponível');
        alert('Erro: Biblioteca jsPDF não carregada. Recarregue a página.');
        return;
    }

    const doc = new jsPDF('p', 'mm', 'a4');
    let yPos = 10;

    // 🧡 PALETA LARANJA CORPORATIVA
    const cores = {
        laranjaEscuro: [204, 85, 0] as [number, number, number],      // #CC5500 - Laranja principal escuro
        laranjaMedio: [255, 140, 0] as [number, number, number],      // #FF8C00 - Laranja médio
        laranjaClaro: [255, 218, 185] as [number, number, number],    // #FFDAB9 - Laranja claro
        laranjaDestaque: [255, 165, 0] as [number, number, number],   // #FFA500 - Laranja destaque
        cinzaEscuro: [64, 64, 64] as [number, number, number],        // #404040 - Cinza escuro
        cinzaMedio: [128, 128, 128] as [number, number, number],      // #808080 - Cinza médio
        cinzaClaro: [245, 245, 245] as [number, number, number],      // #F5F5F5 - Cinza claro
        verde: [34, 139, 34] as [number, number, number],             // #228B22 - Verde contábil
        azulApoio: [52, 115, 179] as [number, number, number],        // #3473B3 - Azul apoio
        branco: [255, 255, 255] as [number, number, number]           // #FFFFFF - Branco
    };

    // 🧡 CABEÇALHO CORPORATIVO COM FUNDO LARANJA
    doc.setFillColor(cores.laranjaEscuro[0], cores.laranjaEscuro[1], cores.laranjaEscuro[2]);
    doc.rect(0, 0, 210, 45, 'F');

    // Espaço para logo (pode ser adicionado depois)
    doc.setFillColor(255, 255, 255);
    doc.rect(15, 8, 25, 25, 'F');
    doc.setDrawColor(cores.laranjaMedio[0], cores.laranjaMedio[1], cores.laranjaMedio[2]);
    doc.setLineWidth(1);
    doc.rect(15, 8, 25, 25, 'S');

    // Texto "LOGO" temporário
    doc.setTextColor(cores.laranjaMedio[0], cores.laranjaMedio[1], cores.laranjaMedio[2]);
    doc.setFontSize(8);
    doc.setFont('helvetica', 'bold');
    doc.text('LOGO', 27.5, 22, { align: 'center' });

    // 🎨 TÍTULO PRINCIPAL
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(24);
    doc.setFont('helvetica', 'bold');
    doc.text('PROPOSTA COMERCIAL', 105, 18, { align: 'center' });

    doc.setFontSize(12);
    doc.setFont('helvetica', 'normal');
    doc.text('Serviços Contábeis e Tributários', 105, 25, { align: 'center' });

    // Número da proposta
    if (proposta.numero) {
        doc.setFontSize(10);
        doc.setFont('helvetica', 'bold');
        doc.text(`Proposta Nº ${proposta.numero}`, 105, 32, { align: 'center' });
    }

    // Data
    const dataGeracao = new Date().toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: 'long',
        year: 'numeric'
    });
    doc.setFontSize(9);
    doc.setFont('helvetica', 'italic');
    doc.text(`Brasília, ${dataGeracao}`, 105, 38, { align: 'center' });

    yPos = 55;

    // 🎨 INFORMAÇÕES DA EMPRESA (Rodapé do cabeçalho)
    doc.setFillColor(cores.cinzaClaro[0], cores.cinzaClaro[1], cores.cinzaClaro[2]);
    doc.rect(0, 45, 210, 15, 'F');

    doc.setTextColor(cores.cinzaEscuro[0], cores.cinzaEscuro[1], cores.cinzaEscuro[2]);
    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    doc.text('Sistema Contábil | CNPJ: 00.000.000/0001-00 | (61) 3000-0000 | contato@sistemacontabil.com.br', 105, 53, { align: 'center' });

    yPos = 70;

    // 🧡 SEÇÃO: DADOS DO CLIENTE
    adicionarSecaoLaranja(doc, 'DADOS DO CLIENTE', yPos, cores);
    yPos += 15;

    // Card do cliente
    doc.setFillColor(255, 255, 255);
    doc.setDrawColor(cores.laranjaClaro[0], cores.laranjaClaro[1], cores.laranjaClaro[2]);
    doc.setLineWidth(0.5);
    doc.roundedRect(15, yPos, 180, 25, 3, 3, 'FD');

    doc.setTextColor(cores.cinzaEscuro[0], cores.cinzaEscuro[1], cores.cinzaEscuro[2]);
    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');
    doc.text(sanitizarTexto(dadosProposta.cliente.nome), 20, yPos + 7);

    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    doc.text(`CPF: ${sanitizarTexto(dadosProposta.cliente.cpf)}`, 20, yPos + 13);
    doc.text(`E-mail: ${sanitizarTexto(dadosProposta.cliente.email)}`, 20, yPos + 18);

    // Badge tipo cliente
    const tipoCliente = dadosProposta.cliente.abertura_empresa ? 'ABERTURA DE EMPRESA' : 'CLIENTE EXISTENTE';
    const corBadge = dadosProposta.cliente.abertura_empresa ? cores.laranjaMedio : cores.verde;

    doc.setFillColor(corBadge[0], corBadge[1], corBadge[2]);
    doc.roundedRect(140, yPos + 4, 50, 8, 2, 2, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(7);
    doc.setFont('helvetica', 'bold');
    doc.text(tipoCliente, 165, yPos + 9, { align: 'center' });

    yPos += 35;

    // 🧡 SEÇÃO: CONFIGURAÇÕES TRIBUTÁRIAS
    adicionarSecaoLaranja(doc, 'CONFIGURACOES TRIBUTARIAS', yPos, cores);
    yPos += 15;

    // Grid de configurações
    const configs = [
        { label: 'Tipo de Atividade', valor: sanitizarTexto(dadosProposta.tipoAtividade.nome), codigo: sanitizarTexto(dadosProposta.tipoAtividade.codigo) },
        { label: 'Regime Tributario', valor: sanitizarTexto(dadosProposta.regimeTributario.nome), codigo: sanitizarTexto(dadosProposta.regimeTributario.codigo) }
    ];

    configs.forEach((config, index) => {
        const x = 15 + (index * 90);

        doc.setFillColor(cores.laranjaClaro[0], cores.laranjaClaro[1], cores.laranjaClaro[2]);
        doc.roundedRect(x, yPos, 85, 20, 2, 2, 'F');

        doc.setTextColor(cores.laranjaEscuro[0], cores.laranjaEscuro[1], cores.laranjaEscuro[2]);
        doc.setFontSize(7);
        doc.setFont('helvetica', 'bold');
        doc.text(config.label.toUpperCase(), x + 3, yPos + 5);

        doc.setFontSize(9);
        doc.setFont('helvetica', 'bold');
        doc.text(config.valor, x + 3, yPos + 11);

        doc.setFontSize(7);
        doc.setFont('helvetica', 'normal');
        doc.text(`Codigo: ${config.codigo}`, x + 3, yPos + 16);
    });

    yPos += 30;

    // ⚠️ SEÇÃO: SERVIÇOS SELECIONADOS (CORRIGIDA)
    yPos = adicionarServicosCompletos(doc, dadosProposta, todosServicos, cores, yPos);

    // 🎨 NOVA PÁGINA SE NECESSÁRIO
    if (yPos > 240) {
        doc.addPage();
        yPos = 20;
    }

    // 🧡 RESUMO FINANCEIRO DESTACADO
    doc.setFillColor(cores.laranjaEscuro[0], cores.laranjaEscuro[1], cores.laranjaEscuro[2]);
    doc.roundedRect(15, yPos, 180, 8, 2, 2, 'F');

    doc.setTextColor(255, 255, 255);
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.text('RESUMO FINANCEIRO', 20, yPos + 6);

    yPos += 15;

    // Card resumo
    doc.setFillColor(255, 255, 255);
    doc.setDrawColor(cores.laranjaClaro[0], cores.laranjaClaro[1], cores.laranjaClaro[2]);
    doc.setLineWidth(1);
    doc.roundedRect(15, yPos, 180, 45, 3, 3, 'FD');

    // Grid de valores
    const subtotalServicos = dadosProposta.servicosSelecionados.reduce((sum, item) => sum + item.subtotal, 0);
    const taxaAbertura = calcularTaxaAbertura(dadosProposta.cliente, dadosProposta.regimeTributario);
    const totalGeral = subtotalServicos + taxaAbertura;
    const valorDesconto = dadosProposta.valorDesconto || 0;
    const totalFinal = dadosProposta.totalFinal;

    const resumoItens = [
        {
            label: 'SUBTOTAL',
            valor: formatarMoedaPDF(totalGeral),
            sublabel: 'Valor antes do desconto',
            cor: cores.laranjaMedio
        },
        {
            label: 'TOTAL FINAL',
            valor: formatarMoedaPDF(totalFinal),
            sublabel: 'Valor com desconto aplicado',
            cor: cores.verde
        }
    ];

    resumoItens.forEach((item, index) => {
        const x = 25 + (index * 80);

        doc.setFillColor(item.cor[0], item.cor[1], item.cor[2]);
        doc.roundedRect(x, yPos + 5, 70, 25, 2, 2, 'F');

        doc.setTextColor(255, 255, 255);
        doc.setFontSize(8);
        doc.setFont('helvetica', 'bold');
        doc.text(item.label, x + 35, yPos + 10, { align: 'center' });

        doc.setFontSize(14);
        doc.setFont('helvetica', 'bold');
        doc.text(item.valor, x + 35, yPos + 18, { align: 'center' });

        doc.setFontSize(6);
        doc.setFont('helvetica', 'normal');
        doc.text(item.sublabel, x + 35, yPos + 25, { align: 'center' });
    });

    // Desconto (se houver)
    if (dadosProposta.percentualDesconto > 0) {
        yPos += 35;
        doc.setFillColor(cores.laranjaDestaque[0], cores.laranjaDestaque[1], cores.laranjaDestaque[2]);
        doc.roundedRect(45, yPos, 120, 15, 2, 2, 'F');

        doc.setTextColor(255, 255, 255);
        doc.setFontSize(9);
        doc.setFont('helvetica', 'bold');
        doc.text(`DESCONTO APLICADO: ${dadosProposta.percentualDesconto}%`, 105, yPos + 6, { align: 'center' });
        doc.text(`Economia: ${formatarMoedaPDF(valorDesconto)}`, 105, yPos + 12, { align: 'center' });
    }

    yPos += dadosProposta.percentualDesconto > 0 ? 25 : 50;

    // 🧡 OBSERVAÇÕES (se houver)
    if (dadosProposta.observacoes && dadosProposta.observacoes.trim()) {
        adicionarSecaoLaranja(doc, 'OBSERVACOES ESPECIFICAS', yPos, cores);
        yPos += 15;

        doc.setFillColor(cores.cinzaClaro[0], cores.cinzaClaro[1], cores.cinzaClaro[2]);
        doc.roundedRect(15, yPos, 180, 20, 2, 2, 'F');

        doc.setTextColor(cores.cinzaEscuro[0], cores.cinzaEscuro[1], cores.cinzaEscuro[2]);
        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');

        const observacoesLinhas = doc.splitTextToSize(sanitizarTexto(dadosProposta.observacoes), 170);
        let alturaObservacoes = observacoesLinhas.length * 5 + 6;

        doc.roundedRect(15, yPos, 180, alturaObservacoes, 2, 2, 'F');

        observacoesLinhas.forEach((linha: string, index: number) => {
            doc.text(linha, 20, yPos + 6 + (index * 5));
        });

        yPos += alturaObservacoes + 10;
    }

    // 🧡 RODAPÉ PROFISSIONAL
    const alturaRodape = 35;
    const yRodape = 297 - alturaRodape;

    doc.setFillColor(cores.laranjaEscuro[0], cores.laranjaEscuro[1], cores.laranjaEscuro[2]);
    doc.rect(0, yRodape, 210, alturaRodape, 'F');

    doc.setTextColor(255, 255, 255);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.text('CONDIÇÕES GERAIS', 20, yRodape + 8);

    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    const condicoes = [
        '• Esta proposta é válida por 30 (trinta) dias a partir da data de emissão',
        '• Os valores estão sujeitos a reajuste conforme tabela vigente',
        '• Pagamento conforme condições a serem acordadas no contrato',
        '• Proposta sujeita à análise e aprovação interna'
    ];

    condicoes.forEach((condicao, index) => {
        doc.text(condicao, 20, yRodape + 15 + (index * 4));
    });

    // Status finalizada
    if (proposta.status === 'REALIZADA') {
        doc.setFillColor(cores.verde[0], cores.verde[1], cores.verde[2]);
        doc.roundedRect(140, yRodape + 8, 50, 12, 2, 2, 'F');

        doc.setTextColor(255, 255, 255);
        doc.setFontSize(8);
        doc.setFont('helvetica', 'bold');
        doc.text('PROPOSTA FINALIZADA', 165, yRodape + 15, { align: 'center' });
    }

    // 🎨 SALVAR COM NOME PROFISSIONAL
    const nomeArquivo = `Proposta_Comercial_${proposta.numero}_${dadosProposta.cliente.nome.replace(/\s+/g, '_')}.pdf`;
    doc.save(nomeArquivo);

    console.log('✅ PDF profissional gerado:', nomeArquivo);
};

// 🧡 FUNÇÃO AUXILIAR: Adicionar seção laranja
const adicionarSecaoLaranja = (
    doc: jsPDF,
    titulo: string,
    yPos: number,
    cores: any,
    corCustomizada?: [number, number, number]
) => {
    const cor = corCustomizada || cores.laranjaEscuro;

    doc.setFillColor(cor[0], cor[1], cor[2]);
    doc.roundedRect(15, yPos, 180, 8, 2, 2, 'F');

    doc.setTextColor(255, 255, 255);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.text(sanitizarTexto(titulo), 20, yPos + 6);
};

// 🎨 FUNÇÃO AUXILIAR: Adicionar seção profissional (mantida para compatibilidade)
const adicionarSecaoProfissional = (
    doc: jsPDF,
    titulo: string,
    yPos: number,
    cores: any,
    corCustomizada?: [number, number, number]
) => {
    const cor = corCustomizada || cores.laranjaEscuro;

    doc.setFillColor(cor[0], cor[1], cor[2]);
    doc.roundedRect(15, yPos, 180, 8, 2, 2, 'F');

    doc.setTextColor(255, 255, 255);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.text(sanitizarTexto(titulo), 20, yPos + 6);
};

// 🎨 FUNÇÃO AUXILIAR: Formatar moeda para PDF
const formatarMoedaPDF = (valor: number): string => {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
};

// ⚠️ FUNÇÃO AUXILIAR: Adicionar serviços completos
const adicionarServicosCompletos = (
    doc: jsPDF,
    dadosProposta: PropostaComDesconto,
    todosServicos: Servico[],
    cores: any,
    yPos: number
): number => {

    console.log('📝 Adicionando serviços ao PDF...');

    // ⚠️ SEPARAR: Serviços por tipo de cobrança
    const servicosMensais: any[] = [];
    const servicosUnicos: any[] = [];

    dadosProposta.servicosSelecionados.forEach(item => {
        const servico = todosServicos.find(s => s.id === item.servico_id);
        console.log(`🔍 Buscando serviço ID ${item.servico_id}:`, servico);

        if (servico) {
            if (servico.tipo_cobranca === 'MENSAL') {
                servicosMensais.push({ item, servico });
            } else {
                servicosUnicos.push({ item, servico });
            }
        } else {
            console.warn(`⚠️ Serviço ID ${item.servico_id} não encontrado na lista`);
        }
    });

    // ⚠️ SERVIÇOS MENSAIS
    if (servicosMensais.length > 0) {
        adicionarSecaoLaranja(doc, 'SERVICOS MENSAIS (RECORRENTES)', yPos, cores, cores.laranjaMedio);
        yPos += 15;

        console.log('📝 Serviços mensais encontrados:', servicosMensais);

        const servicosMensaisData: any[] = [];

        // ⚠️ AGRUPAR: Por categoria
        const categoriasMensais = new Map<string, any[]>();

        servicosMensais.forEach(({ item, servico }) => {
            if (!categoriasMensais.has(servico.categoria)) {
                categoriasMensais.set(servico.categoria, []);
            }
            categoriasMensais.get(servico.categoria)!.push({ item, servico });
        });

        // ⚠️ RENDERIZAR: Serviços por categoria
        categoriasMensais.forEach((servicosCategoria, categoria) => {
            // Cabeçalho da categoria
            servicosMensaisData.push([
                {
                    content: sanitizarTexto(categoria.toUpperCase()),
                    colSpan: 4,
                    styles: {
                        fillColor: cores.laranjaMedio,
                        textColor: [255, 255, 255],
                        fontStyle: 'bold',
                        fontSize: 10,
                        halign: 'left'
                    }
                }
            ]);

            // Serviços da categoria
            servicosCategoria.forEach(({ item, servico }) => {
                servicosMensaisData.push([
                    { content: sanitizarTexto(servico.nome), styles: { fontSize: 9 } },
                    { content: `${item.quantidade}x`, styles: { fontSize: 9, halign: 'center' } },
                    { content: formatarMoedaPDF(item.valor_unitario), styles: { fontSize: 9, halign: 'right' } },
                    {
                        content: formatarMoedaPDF(item.subtotal) + '/mes',
                        styles: { fontSize: 9, halign: 'right', fontStyle: 'bold', textColor: cores.laranjaEscuro }
                    }
                ]);
            });
        });

        // ⚠️ VERIFICAR: Se autoTable está disponível antes de usar
        if (typeof doc.autoTable === 'function') {
            doc.autoTable({
                startY: yPos,
                head: [[
                    { content: 'Servico Mensal', styles: { fillColor: cores.laranjaEscuro, textColor: [255, 255, 255], fontSize: 9 } },
                    { content: 'Qtd', styles: { fillColor: cores.laranjaEscuro, textColor: [255, 255, 255], fontSize: 9 } },
                    { content: 'Valor Unit.', styles: { fillColor: cores.laranjaEscuro, textColor: [255, 255, 255], fontSize: 9 } },
                    { content: 'Total Mensal', styles: { fillColor: cores.laranjaEscuro, textColor: [255, 255, 255], fontSize: 9 } }
                ]],
                body: servicosMensaisData,
                theme: 'grid',
                styles: {
                    fontSize: 8,
                    cellPadding: { top: 4, right: 4, bottom: 4, left: 4 },
                    lineColor: cores.cinzaClaro,
                    lineWidth: 0.5
                },
                columnStyles: {
                    0: { cellWidth: 100 },
                    1: { cellWidth: 20, halign: 'center' },
                    2: { cellWidth: 35, halign: 'right' },
                    3: { cellWidth: 35, halign: 'right' }
                },
                alternateRowStyles: { fillColor: [250, 250, 250] }
            });
        } else {
            console.error('❌ autoTable não está disponível, usando fallback');
            // Fallback: adicionar texto simples
            doc.setTextColor(cores.cinzaEscuro[0], cores.cinzaEscuro[1], cores.cinzaEscuro[2]);
            doc.setFontSize(10);
            doc.text('Serviços Mensais:', 20, yPos + 10);
            servicosMensaisData.forEach((row, index) => {
                if (Array.isArray(row) && row.length > 0) {
                    const content = row[0]?.content || row[0] || '';
                    doc.text(content, 20, yPos + 15 + (index * 5));
                }
            });
            yPos += 15 + (servicosMensaisData.length * 5);
        }

        // ⚠️ ATUALIZAR: yPos baseado no resultado do autoTable
        if (typeof doc.autoTable === 'function' && doc.lastAutoTable) {
            yPos = doc.lastAutoTable.finalY + 15;
        }
    }

    // ⚠️ SERVIÇOS ÚNICOS
    if (servicosUnicos.length > 0) {
        adicionarSecaoProfissional(doc, '🎯 VALORES ÚNICOS (INVESTIMENTO INICIAL)', yPos, cores, cores.verde);
        yPos += 15;

        console.log('📝 Serviços únicos encontrados:', servicosUnicos);

        const servicosUnicosData: any[] = [];

        // ⚠️ AGRUPAR: Por categoria
        const categoriasUnicas = new Map<string, any[]>();

        servicosUnicos.forEach(({ item, servico }) => {
            if (!categoriasUnicas.has(servico.categoria)) {
                categoriasUnicas.set(servico.categoria, []);
            }
            categoriasUnicas.get(servico.categoria)!.push({ item, servico });
        });

        // ⚠️ ADICIONAR: Taxa de abertura se houver
        const taxaAbertura = calcularTaxaAbertura(dadosProposta.cliente, dadosProposta.regimeTributario);
        if (taxaAbertura > 0) {
            if (!categoriasUnicas.has('SOCIETARIO')) {
                categoriasUnicas.set('SOCIETARIO', []);
            }

            const tipoAbertura = getTipoAbertura(dadosProposta.cliente, dadosProposta.regimeTributario);
            categoriasUnicas.get('SOCIETARIO')!.push({
                item: {
                    quantidade: 1,
                    valor_unitario: taxaAbertura,
                    subtotal: taxaAbertura
                },
                servico: {
                    nome: `Taxa de Abertura ${tipoAbertura}`,
                    categoria: 'SOCIETARIO'
                }
            });
        }

        // ⚠️ RENDERIZAR: Serviços únicos por categoria
        categoriasUnicas.forEach((servicosCategoria, categoria) => {
            servicosUnicosData.push([
                {
                    content: `🏢 ${categoria.toUpperCase()}`,
                    colSpan: 4,
                    styles: {
                        fillColor: cores.verde,
                        textColor: [255, 255, 255],
                        fontStyle: 'bold',
                        fontSize: 10,
                        halign: 'left'
                    }
                }
            ]);

            servicosCategoria.forEach(({ item, servico }) => {
                servicosUnicosData.push([
                    { content: `• ${servico.nome}`, styles: { fontSize: 9 } },
                    { content: '1x', styles: { fontSize: 9, halign: 'center' } },
                    { content: formatarMoedaPDF(item.valor_unitario), styles: { fontSize: 9, halign: 'right' } },
                    {
                        content: formatarMoedaPDF(item.subtotal),
                        styles: { fontSize: 9, halign: 'right', fontStyle: 'bold', textColor: cores.verde }
                    }
                ]);
            });
        });

        // ⚠️ VERIFICAR: Se autoTable está disponível antes de usar
        if (typeof doc.autoTable === 'function') {
            doc.autoTable({
                startY: yPos,
                head: [[
                    { content: 'Serviço/Taxa Única', styles: { fillColor: cores.verde, textColor: [255, 255, 255], fontSize: 9 } },
                    { content: 'Qtd', styles: { fillColor: cores.verde, textColor: [255, 255, 255], fontSize: 9 } },
                    { content: 'Valor', styles: { fillColor: cores.verde, textColor: [255, 255, 255], fontSize: 9 } },
                    { content: 'Total', styles: { fillColor: cores.verde, textColor: [255, 255, 255], fontSize: 9 } }
                ]],
                body: servicosUnicosData,
                theme: 'grid',
                styles: {
                    fontSize: 8,
                    cellPadding: { top: 4, right: 4, bottom: 4, left: 4 },
                    lineColor: cores.cinzaClaro,
                    lineWidth: 0.5
                },
                columnStyles: {
                    0: { cellWidth: 100 },
                    1: { cellWidth: 20, halign: 'center' },
                    2: { cellWidth: 35, halign: 'right' },
                    3: { cellWidth: 35, halign: 'right' }
                },
                alternateRowStyles: { fillColor: [250, 250, 250] }
            });
        } else {
            console.error('❌ autoTable não está disponível, usando fallback');
            // Fallback: adicionar texto simples
            doc.setTextColor(cores.cinzaEscuro[0], cores.cinzaEscuro[1], cores.cinzaEscuro[2]);
            doc.setFontSize(10);
            doc.text('Serviços Únicos:', 20, yPos + 10);
            servicosUnicosData.forEach((row, index) => {
                if (Array.isArray(row) && row.length > 0) {
                    const content = row[0]?.content || row[0] || '';
                    doc.text(content, 20, yPos + 15 + (index * 5));
                }
            });
            yPos += 15 + (servicosUnicosData.length * 5);
        }

        // ⚠️ ATUALIZAR: yPos baseado no resultado do autoTable
        if (typeof doc.autoTable === 'function' && doc.lastAutoTable) {
            yPos = doc.lastAutoTable.finalY + 15;
        }
    }

    // ⚠️ VERIFICAR: Se não há serviços
    if (servicosMensais.length === 0 && servicosUnicos.length === 0) {
        adicionarSecaoProfissional(doc, 'SERVIÇOS SELECIONADOS', yPos, cores);
        yPos += 15;

        doc.setTextColor(cores.cinzaMedio[0], cores.cinzaMedio[1], cores.cinzaMedio[2]);
        doc.setFontSize(10);
        doc.setFont('helvetica', 'italic');
        doc.text('Nenhum serviço selecionado', 20, yPos + 10);
        yPos += 20;
    }

    return yPos;
};

export const Passo5FinalizacaoProposta: React.FC<Passo5Props> = ({
    dadosProposta,
    onVoltar,
    onFinalizado
}) => {
    const [finalizando, setFinalizando] = useState(false);
    const [finalizada, setFinalizada] = useState(false);
    const [propostaFinalizada, setPropostaFinalizada] = useState<PropostaResponse | null>(null);
    const [todosServicos, setTodosServicos] = useState<Servico[]>([]);
    const [erro, setErro] = useState<string>('');

    // Carregar serviços para exibição
    useEffect(() => {
        const carregarServicos = async () => {
            try {
                const response = await apiService.getServicos();
                setTodosServicos(response || []);
            } catch (error) {
                console.error('Erro ao carregar serviços:', error);
                // Usar dados mockados se necessário
                const servicosMockados: Servico[] = [
                    {
                        id: 1,
                        codigo: 'CONT-MENSAL',
                        nome: 'Contabilidade Mensal',
                        categoria: 'CONTABIL',
                        tipo_cobranca: 'MENSAL',
                        valor_base: 150.00,
                        descricao: 'Serviços de contabilidade mensal incluindo escrituração, DRE e balanço',
                        ativo: true
                    },
                    {
                        id: 2,
                        codigo: 'BALANCETE',
                        nome: 'Balancete Mensal',
                        categoria: 'CONTABIL',
                        tipo_cobranca: 'MENSAL',
                        valor_base: 50.00,
                        descricao: 'Elaboração de balancete mensal',
                        ativo: true
                    },
                    {
                        id: 3,
                        codigo: 'NF-e',
                        nome: 'Nota Fiscal Eletrônica (NF-e)',
                        categoria: 'FISCAL',
                        tipo_cobranca: 'POR_NF',
                        valor_base: 20.00,
                        descricao: 'Emissão de notas fiscais eletrônicas',
                        ativo: true
                    },
                    {
                        id: 4,
                        codigo: 'NFS-e',
                        nome: 'Nota Fiscal de Serviços (NFS-e)',
                        categoria: 'FISCAL',
                        tipo_cobranca: 'POR_NF',
                        valor_base: 10.00,
                        descricao: 'Emissão de notas fiscais de serviços eletrônicas',
                        ativo: true
                    },
                    {
                        id: 5,
                        codigo: 'FOLHA',
                        nome: 'Folha de Pagamento',
                        categoria: 'PESSOAL',
                        tipo_cobranca: 'MENSAL',
                        valor_base: 80.00,
                        descricao: 'Processamento da folha de pagamento mensal',
                        ativo: true
                    },
                    {
                        id: 6,
                        codigo: 'FUNCIONARIO',
                        nome: 'Gestão de Funcionários',
                        categoria: 'PESSOAL',
                        tipo_cobranca: 'MENSAL',
                        valor_base: 50.00,
                        descricao: 'Gestão de funcionários',
                        ativo: true
                    },
                    {
                        id: 7,
                        codigo: 'PRO-LABORE',
                        nome: 'Retirada de Pró-labore',
                        categoria: 'PESSOAL',
                        tipo_cobranca: 'MENSAL',
                        valor_base: 30.00,
                        descricao: 'Retirada de pró-labore',
                        ativo: true
                    },
                    {
                        id: 8,
                        codigo: 'SOCIETARIO',
                        nome: 'Serviços Societários',
                        categoria: 'SOCIETARIO',
                        tipo_cobranca: 'VALOR_UNICO',
                        valor_base: 1000.00,
                        descricao: 'Constituição e alterações societárias',
                        ativo: true
                    },
                    {
                        id: 9,
                        codigo: 'ORGAO-CLASSE',
                        nome: 'Registro de Órgão de Classe',
                        categoria: 'SOCIETARIO',
                        tipo_cobranca: 'VALOR_UNICO',
                        valor_base: 200.00,
                        descricao: 'Registro em órgão de classe profissional',
                        ativo: true
                    }
                ];
                setTodosServicos(servicosMockados);
            }
        };

        carregarServicos();
    }, []);

    // Calcular resumo financeiro final
    const resumoFinal = useMemo(() => {
        const subtotalServicos = dadosProposta.servicosSelecionados.reduce((sum, item) => sum + item.subtotal, 0);
        const taxaAbertura = calcularTaxaAbertura(dadosProposta.cliente, dadosProposta.regimeTributario);
        const subtotalGeral = subtotalServicos + taxaAbertura;

        return {
            subtotalServicos,
            taxaAbertura,
            subtotalGeral,
            valorDesconto: dadosProposta.valorDesconto,
            totalFinal: dadosProposta.totalFinal,
            percentualDesconto: dadosProposta.percentualDesconto
        };
    }, [dadosProposta]);

    // Função para finalizar proposta
    const finalizarProposta = async () => {
        setFinalizando(true);
        setErro('');

        try {
            // Preparar dados finais para API
            const dadosFinalizacao = {
                status: 'REALIZADA',
                valor_total: dadosProposta.totalFinal,
                observacoes: dadosProposta.observacoes
            };

            console.log('Tentando finalizar proposta com dados:', dadosFinalizacao);

            // Atualizar proposta no backend
            const proposta = await apiService.finalizarProposta(dadosProposta.id || 1, dadosFinalizacao);

            console.log('Proposta finalizada com sucesso:', proposta);

            setPropostaFinalizada(proposta);
            setFinalizada(true);

            console.log(`Proposta #${proposta.numero} finalizada com sucesso`);

        } catch (error) {
            console.error('Erro ao finalizar proposta:', error);
            setErro(error instanceof Error ? error.message : 'Erro ao finalizar proposta');
        } finally {
            setFinalizando(false);
        }
    };

    // Renderizar tela de sucesso se finalizada
    if (finalizada && propostaFinalizada) {
        return <TelaFinalizada proposta={propostaFinalizada} dadosCompletos={dadosProposta} />;
    }

    return (
        <div className="min-h-screen pb-32">
            {/* Cabeçalho */}
            <div className="mb-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">Nova Proposta - Passo 5</h1>
                        <p className="text-sm text-gray-500">Finalização da Proposta</p>
                        <p className="text-sm text-gray-600 mt-1">
                            Revise todos os dados e finalize a proposta
                        </p>
                    </div>

                    <div className="flex items-center space-x-3">
                        <button
                            onClick={onVoltar}
                            className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                        >
                            <ArrowLeft className="w-4 h-4" />
                            <span>Voltar</span>
                        </button>
                    </div>
                </div>
            </div>

            {/* Erro de finalização */}
            {erro && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                    <div className="flex items-center space-x-2">
                        <AlertTriangle className="w-5 h-5 text-red-600" />
                        <span className="text-red-800 font-medium">Erro ao finalizar proposta</span>
                    </div>
                    <p className="text-red-700 text-sm mt-1">{erro}</p>
                </div>
            )}

            {/* Resumo Executivo */}
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-6 text-white mb-6">
                <div className="flex justify-between items-center">
                    <div>
                        <h2 className="text-xl font-bold mb-2">Resumo da Proposta</h2>
                        <p className="text-blue-100">Cliente: {dadosProposta.cliente.nome}</p>
                        <p className="text-blue-100">Atividade: {dadosProposta.tipoAtividade.nome}</p>
                    </div>
                    <div className="text-right">
                        <p className="text-blue-100 text-sm">Valor Total</p>
                        <p className="text-3xl font-bold">{formatarMoeda(resumoFinal.totalFinal)}</p>
                        {dadosProposta.percentualDesconto > 0 && (
                            <p className="text-blue-200 text-sm">
                                Desconto de {dadosProposta.percentualDesconto}% aplicado
                            </p>
                        )}
                    </div>
                </div>
            </div>

            {/* Dados Completos */}
            <ResumoCompletoProps
                dadosProposta={dadosProposta}
                resumoFinal={resumoFinal}
                todosServicos={todosServicos}
            />

            {/* Botão de Finalização */}
            <div className="fixed bottom-0 left-64 right-0 bg-white border-t border-gray-200 px-6 py-4 z-10">
                <div className="flex justify-between items-center">
                    <div className="text-sm text-gray-600">
                        <p className="font-medium">Pronto para finalizar?</p>
                        <p>A proposta será marcada como realizada e não poderá mais ser editada.</p>
                    </div>

                    <div className="flex space-x-3">
                        <button
                            onClick={onVoltar}
                            disabled={finalizando}
                            className="px-6 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors"
                        >
                            Anterior
                        </button>

                        <button
                            onClick={finalizarProposta}
                            disabled={finalizando}
                            className={`px-6 py-3 text-sm font-medium text-white rounded-lg transition-colors disabled:opacity-50 flex items-center space-x-2 ${dadosProposta.requerAprovacao
                                ? 'bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600'
                                : 'bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600'
                                }`}
                        >
                            {finalizando ? (
                                <>
                                    <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>
                                    <span>Finalizando...</span>
                                </>
                            ) : (
                                <>
                                    <CheckCircle className="w-4 h-4" />
                                    <span>
                                        {dadosProposta.requerAprovacao ? 'Finalizar e Enviar p/ Aprovação' : 'Finalizar Proposta'}
                                    </span>
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

// Componente de Resumo Completo
const ResumoCompletoProps: React.FC<{
    dadosProposta: PropostaComDesconto;
    resumoFinal: any;
    todosServicos: Servico[];
}> = ({ dadosProposta, resumoFinal, todosServicos }) => {
    return (
        <div className="space-y-6">
            {/* Dados do Cliente */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <User className="w-5 h-5 mr-2 text-blue-600" />
                    Dados do Cliente
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                        <div>
                            <span className="text-sm font-medium text-gray-500">Nome Completo</span>
                            <p className="text-gray-900 font-medium">{dadosProposta.cliente.nome}</p>
                        </div>
                        <div>
                            <span className="text-sm font-medium text-gray-500">CPF</span>
                            <p className="text-gray-900">{dadosProposta.cliente.cpf}</p>
                        </div>
                        <div>
                            <span className="text-sm font-medium text-gray-500">E-mail</span>
                            <p className="text-gray-900">{dadosProposta.cliente.email}</p>
                        </div>
                    </div>
                    <div className="flex items-center justify-center">
                        <span className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium ${dadosProposta.cliente.abertura_empresa
                            ? 'bg-purple-100 text-purple-800 border border-purple-200'
                            : 'bg-green-100 text-green-800 border border-green-200'
                            }`}>
                            {dadosProposta.cliente.abertura_empresa ? (
                                <>
                                    <Building className="w-4 h-4 mr-2" />
                                    Abertura de Empresa
                                </>
                            ) : (
                                <>
                                    <CheckCircle className="w-4 h-4 mr-2" />
                                    Cliente Existente
                                </>
                            )}
                        </span>
                    </div>
                </div>
            </div>

            {/* Configurações Tributárias */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <Settings className="w-5 h-5 mr-2 text-blue-600" />
                    Configurações Tributárias
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-blue-50 rounded-lg p-4">
                        <span className="text-xs font-medium text-blue-600 uppercase tracking-wide">Tipo de Atividade</span>
                        <p className="text-blue-900 font-semibold mt-1">{dadosProposta.tipoAtividade.nome}</p>
                        <p className="text-blue-700 text-sm">Código: {dadosProposta.tipoAtividade.codigo}</p>
                    </div>

                    <div className="bg-green-50 rounded-lg p-4">
                        <span className="text-xs font-medium text-green-600 uppercase tracking-wide">Regime Tributário</span>
                        <p className="text-green-900 font-semibold mt-1">{dadosProposta.regimeTributario.nome}</p>
                        <p className="text-green-700 text-sm">Código: {dadosProposta.regimeTributario.codigo}</p>
                    </div>

                    <div className="bg-purple-50 rounded-lg p-4">
                        <span className="text-xs font-medium text-purple-600 uppercase tracking-wide">Faixa de Faturamento</span>
                        {dadosProposta.faixaFaturamento ? (
                            <>
                                <p className="text-purple-900 font-semibold mt-1">
                                    {formatarMoeda(dadosProposta.faixaFaturamento.valor_inicial)} até{' '}
                                    {dadosProposta.faixaFaturamento.valor_final
                                        ? formatarMoeda(dadosProposta.faixaFaturamento.valor_final)
                                        : 'ilimitado'
                                    }
                                </p>
                                <p className="text-purple-700 text-sm">Alíquota: {dadosProposta.faixaFaturamento.aliquota}%</p>
                            </>
                        ) : (
                            <p className="text-purple-700 text-sm italic mt-1">Não aplicável</p>
                        )}
                    </div>
                </div>
            </div>

            {/* Serviços Detalhados */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <List className="w-5 h-5 mr-2 text-blue-600" />
                    Serviços Selecionados
                </h3>

                <ServicosDetalhados
                    servicosSelecionados={dadosProposta.servicosSelecionados}
                    todosServicos={todosServicos}
                    resumoFinal={resumoFinal}
                    regimeTributario={dadosProposta.regimeTributario}
                />
            </div>

            {/* Resumo Financeiro Final */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <Calculator className="w-5 h-5 mr-2 text-blue-600" />
                    Resumo Financeiro
                </h3>

                <ResumoFinanceiroFinal resumo={resumoFinal} dadosProposta={dadosProposta} />
            </div>

            {/* Observações */}
            {dadosProposta.observacoes && (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                        <MessageSquare className="w-5 h-5 mr-2 text-blue-600" />
                        Observações
                    </h3>

                    <div className="bg-gray-50 rounded-lg p-4">
                        <p className="text-gray-800 whitespace-pre-wrap">{dadosProposta.observacoes}</p>
                    </div>
                </div>
            )}
        </div>
    );
};

// Componente de Serviços Detalhados
const ServicosDetalhados: React.FC<{
    servicosSelecionados: ServicoSelecionado[];
    todosServicos: Servico[];
    resumoFinal: any;
    regimeTributario: RegimeTributario;
}> = ({ servicosSelecionados, todosServicos, resumoFinal, regimeTributario }) => {
    // Agrupar serviços por categoria
    const servicosPorCategoria = new Map<string, { servico: Servico; item: ServicoSelecionado }[]>();

    servicosSelecionados.forEach(item => {
        const servico = todosServicos.find(s => s.id === item.servico_id);
        if (servico) {
            if (!servicosPorCategoria.has(servico.categoria)) {
                servicosPorCategoria.set(servico.categoria, []);
            }
            servicosPorCategoria.get(servico.categoria)!.push({ servico, item });
        }
    });

    return (
        <div className="space-y-6">
            {Array.from(servicosPorCategoria.entries()).map(([categoria, servicos]) => (
                <div key={categoria} className="border-l-4 border-blue-500 pl-4">
                    <div className="flex justify-between items-center mb-3">
                        <h4 className="text-base font-medium text-gray-900 capitalize flex items-center">
                            <span className="w-3 h-3 bg-blue-500 rounded-full mr-2"></span>
                            {categoria.toLowerCase()}
                        </h4>
                        <span className="text-lg font-semibold text-blue-600">
                            {formatarMoeda(servicos.reduce((sum, { item }) => sum + item.subtotal, 0))}
                        </span>
                    </div>

                    <div className="space-y-2 ml-5">
                        {servicos.map(({ servico, item }) => (
                            <div key={item.servico_id} className="flex justify-between items-center text-sm bg-gray-50 rounded-lg p-3">
                                <div className="flex-1">
                                    <span className="text-gray-700 font-medium">• {servico.nome}</span>
                                    {item.quantidade > 1 && (
                                        <span className="text-gray-500">
                                            : {item.quantidade} × {formatarMoeda(item.valor_unitario)}
                                        </span>
                                    )}
                                    {item.extras?.nomeOrgao && (
                                        <span className="text-blue-600"> ({item.extras.nomeOrgao})</span>
                                    )}
                                </div>
                                <span className="font-semibold text-gray-900">
                                    {formatarMoeda(item.subtotal)}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            ))}

            {/* Taxa de Abertura */}
            {resumoFinal.taxaAbertura > 0 && (
                <div className="border-l-4 border-green-500 pl-4">
                    <div className="flex justify-between items-center mb-3">
                        <h4 className="text-base font-medium text-gray-900 capitalize flex items-center">
                            <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                            Abertura de {isMEI(regimeTributario) ? 'MEI' : 'Empresa'}
                        </h4>
                        <span className="text-lg font-semibold text-green-600">
                            {formatarMoeda(resumoFinal.taxaAbertura)}
                        </span>
                    </div>

                    <div className="ml-5">
                        <div className="flex justify-between items-center text-sm bg-green-50 rounded-lg p-3">
                            <div className="flex-1">
                                <span className="text-gray-700 font-medium flex items-center">
                                    {isMEI(regimeTributario) ? (
                                        <>
                                            <User className="w-4 h-4 mr-1 text-green-600" />
                                            • Taxa de Abertura MEI
                                        </>
                                    ) : (
                                        <>
                                            <Building className="w-4 h-4 mr-1 text-green-600" />
                                            • Taxa de Abertura de Empresa
                                        </>
                                    )}
                                </span>
                            </div>
                            <span className="font-semibold text-gray-900">
                                {formatarMoeda(resumoFinal.taxaAbertura)}
                            </span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

// Componente de Resumo Financeiro Final
const ResumoFinanceiroFinal: React.FC<{
    resumo: any;
    dadosProposta: PropostaComDesconto;
}> = ({ resumo, dadosProposta }) => {
    return (
        <div className="space-y-4">
            {/* Breakdown detalhado */}
            <div className="bg-gray-50 rounded-lg p-4">
                <div className="space-y-3">
                    <div className="flex justify-between items-center">
                        <span className="text-gray-700">Subtotal dos serviços:</span>
                        <span className="font-medium text-gray-900">{formatarMoeda(resumo.subtotalServicos)}</span>
                    </div>

                    {resumo.taxaAbertura > 0 && (
                        <div className="flex justify-between items-center">
                            <span className="text-gray-700 flex items-center">
                                {isMEI(dadosProposta.regimeTributario) ? (
                                    <>
                                        <User className="w-4 h-4 mr-1 text-orange-500" />
                                        Taxa abertura MEI:
                                    </>
                                ) : (
                                    <>
                                        <Building className="w-4 h-4 mr-1 text-green-500" />
                                        Taxa abertura empresa:
                                    </>
                                )}
                            </span>
                            <span className="font-medium text-gray-900">{formatarMoeda(resumo.taxaAbertura)}</span>
                        </div>
                    )}

                    <div className="border-t border-gray-300 pt-3">
                        <div className="flex justify-between items-center">
                            <span className="font-semibold text-gray-800">Subtotal geral:</span>
                            <span className="font-bold text-gray-900">{formatarMoeda(resumo.subtotalGeral)}</span>
                        </div>
                    </div>

                    {dadosProposta.percentualDesconto > 0 && (
                        <>
                            <div className="flex justify-between items-center">
                                <span className="text-gray-700">Desconto ({dadosProposta.percentualDesconto}%):</span>
                                <span className="font-medium text-red-600">-{formatarMoeda(resumo.valorDesconto)}</span>
                            </div>

                            {dadosProposta.requerAprovacao && (
                                <div className="bg-orange-100 border border-orange-200 rounded-lg p-3">
                                    <div className="flex items-center space-x-2">
                                        <AlertTriangle className="w-4 h-4 text-orange-600" />
                                        <span className="text-orange-800 text-sm font-medium">
                                            Desconto de {dadosProposta.percentualDesconto}% requer aprovação administrativa
                                        </span>
                                    </div>
                                </div>
                            )}
                        </>
                    )}
                </div>
            </div>

            {/* Total final destacado */}
            <div className="bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg p-6 text-white">
                <div className="flex justify-between items-center">
                    <div>
                        <span className="text-green-100 text-sm font-medium">VALOR FINAL DA PROPOSTA</span>
                        <p className="text-3xl font-bold mt-1">{formatarMoeda(resumo.totalFinal)}</p>
                        {dadosProposta.percentualDesconto > 0 && (
                            <p className="text-green-200 text-sm mt-1">
                                Economia total: {formatarMoeda(resumo.valorDesconto)} ({dadosProposta.percentualDesconto}%)
                            </p>
                        )}
                    </div>

                    <div className="text-right">
                        <CheckCircle className="w-12 h-12 text-green-200 mx-auto mb-2" />
                        <span className="text-green-100 text-sm">Pronto para finalizar</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

// Tela de Sucesso após Finalização
const TelaFinalizada: React.FC<{
    proposta: PropostaResponse;
    dadosCompletos: PropostaComDesconto;
}> = ({ proposta, dadosCompletos }) => {
    const [gerandoPDF, setGerandoPDF] = useState(false);
    const [todosServicos, setTodosServicos] = useState<Servico[]>([]);

    // Carregar serviços para o PDF
    useEffect(() => {
        const carregarServicos = async () => {
            try {
                const response = await apiService.getServicos();
                setTodosServicos(response || []);
            } catch (error) {
                console.error('Erro ao carregar serviços:', error);
                // Usar dados mockados se necessário
                const servicosMockados: Servico[] = [
                    {
                        id: 1,
                        codigo: 'CONT-MENSAL',
                        nome: 'Contabilidade Mensal',
                        categoria: 'CONTABIL',
                        tipo_cobranca: 'MENSAL',
                        valor_base: 150.00,
                        descricao: 'Serviços de contabilidade mensal incluindo escrituração, DRE e balanço',
                        ativo: true
                    },
                    {
                        id: 2,
                        codigo: 'BALANCETE',
                        nome: 'Balancete Mensal',
                        categoria: 'CONTABIL',
                        tipo_cobranca: 'MENSAL',
                        valor_base: 50.00,
                        descricao: 'Elaboração de balancete mensal',
                        ativo: true
                    },
                    {
                        id: 3,
                        codigo: 'NF-e',
                        nome: 'Nota Fiscal Eletrônica (NF-e)',
                        categoria: 'FISCAL',
                        tipo_cobranca: 'POR_NF',
                        valor_base: 20.00,
                        descricao: 'Emissão de notas fiscais eletrônicas',
                        ativo: true
                    },
                    {
                        id: 4,
                        codigo: 'NFS-e',
                        nome: 'Nota Fiscal de Serviços (NFS-e)',
                        categoria: 'FISCAL',
                        tipo_cobranca: 'POR_NF',
                        valor_base: 10.00,
                        descricao: 'Emissão de notas fiscais de serviços eletrônicas',
                        ativo: true
                    },
                    {
                        id: 5,
                        codigo: 'FOLHA',
                        nome: 'Folha de Pagamento',
                        categoria: 'PESSOAL',
                        tipo_cobranca: 'MENSAL',
                        valor_base: 80.00,
                        descricao: 'Processamento da folha de pagamento mensal',
                        ativo: true
                    },
                    {
                        id: 6,
                        codigo: 'FUNCIONARIO',
                        nome: 'Gestão de Funcionários',
                        categoria: 'PESSOAL',
                        tipo_cobranca: 'MENSAL',
                        valor_base: 50.00,
                        descricao: 'Gestão de funcionários',
                        ativo: true
                    },
                    {
                        id: 7,
                        codigo: 'PRO-LABORE',
                        nome: 'Retirada de Pró-labore',
                        categoria: 'PESSOAL',
                        tipo_cobranca: 'MENSAL',
                        valor_base: 30.00,
                        descricao: 'Retirada de pró-labore',
                        ativo: true
                    },
                    {
                        id: 8,
                        codigo: 'SOCIETARIO',
                        nome: 'Serviços Societários',
                        categoria: 'SOCIETARIO',
                        tipo_cobranca: 'VALOR_UNICO',
                        valor_base: 1000.00,
                        descricao: 'Constituição e alterações societárias',
                        ativo: true
                    },
                    {
                        id: 9,
                        codigo: 'ORGAO-CLASSE',
                        nome: 'Registro de Órgão de Classe',
                        categoria: 'SOCIETARIO',
                        tipo_cobranca: 'VALOR_UNICO',
                        valor_base: 200.00,
                        descricao: 'Registro em órgão de classe profissional',
                        ativo: true
                    }
                ];
                setTodosServicos(servicosMockados);
            }
        };

        carregarServicos();
    }, []);

    const gerarPDFProposta = async () => {
        setGerandoPDF(true);
        try {
            console.log('🚀 Gerando PDF da proposta finalizada...');

            // ⚠️ GARANTIR: Serviços carregados
            if (todosServicos.length === 0) {
                console.log('📥 Carregando serviços...');
                const response = await apiService.getServicos();
                setTodosServicos(response || []);
            }

            // ⚠️ AGUARDAR: Estado atualizado
            setTimeout(() => {
                gerarPDFProfissionalCorrigido(dadosCompletos, proposta, todosServicos);
            }, 200);

        } catch (error) {
            console.error('❌ Erro ao gerar PDF:', error);
            alert('Erro ao gerar PDF. Tente novamente.');
        } finally {
            setGerandoPDF(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto p-6 text-center">
            {/* Ícone de sucesso */}
            <div className="mx-auto mb-6 w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                <CheckCircle className="w-10 h-10 text-green-600" />
            </div>

            {/* Título */}
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Proposta Finalizada com Sucesso!
            </h1>

            {/* Subtítulo */}
            <p className="text-gray-600 mb-8">
                A proposta foi salva e está pronta para ser enviada ao cliente.
            </p>

            {/* Informações da proposta */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
                <div className="space-y-3">
                    <div className="flex justify-between">
                        <span className="text-gray-600">Número da proposta:</span>
                        <span className="font-medium text-gray-900">#{proposta.numero}</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-600">Cliente:</span>
                        <span className="font-medium text-gray-900">{dadosCompletos.cliente.nome}</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-600">Valor total:</span>
                        <span className="font-bold text-green-600 text-lg">{formatarMoeda(dadosCompletos.totalFinal)}</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-600">Status:</span>
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            {proposta.status}
                        </span>
                    </div>
                    {dadosCompletos.requerAprovacao && (
                        <div className="bg-orange-50 border border-orange-200 rounded-lg p-3 mt-4">
                            <div className="flex items-center justify-center space-x-2">
                                <AlertTriangle className="w-4 h-4 text-orange-600" />
                                <span className="text-orange-800 text-sm">
                                    Esta proposta requer aprovação administrativa devido ao desconto aplicado
                                </span>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Debug visual no desenvolvimento */}
            {typeof window !== 'undefined' && window.location.hostname === 'localhost' && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
                    <details>
                        <summary className="text-sm font-medium text-yellow-800 cursor-pointer">
                            🔍 Debug: Dados para PDF
                        </summary>
                        <div className="text-xs text-yellow-700 mt-2 space-y-2">
                            <div><strong>Serviços selecionados:</strong> {dadosCompletos.servicosSelecionados?.length || 0}</div>
                            <div><strong>Todos os serviços carregados:</strong> {todosServicos.length}</div>
                            <div><strong>Cliente:</strong> {dadosCompletos.cliente?.nome || 'N/A'}</div>
                            <div><strong>Tipo de atividade:</strong> {dadosCompletos.tipoAtividade?.nome || 'N/A'}</div>
                            <div><strong>Regime tributário:</strong> {dadosCompletos.regimeTributario?.nome || 'N/A'}</div>
                            <div><strong>Valor total:</strong> {formatarMoeda(dadosCompletos.totalFinal)}</div>
                        </div>
                    </details>
                </div>
            )}

            {/* Ações */}
            <div className="space-y-4">
                <button
                    onClick={gerarPDFProposta}
                    disabled={gerandoPDF}
                    className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center justify-center space-x-2"
                >
                    {gerandoPDF ? (
                        <>
                            <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>
                            <span>Gerando PDF...</span>
                        </>
                    ) : (
                        <>
                            <FileDown className="w-4 h-4" />
                            <span>Gerar PDF da Proposta Finalizada</span>
                        </>
                    )}
                </button>

                <button
                    onClick={() => window.location.href = '/propostas'}
                    className="w-full bg-gray-100 text-gray-700 py-3 px-6 rounded-lg hover:bg-gray-200 transition-colors"
                >
                    Ver Todas as Propostas
                </button>
            </div>
        </div>
    );
};

// Função de PDF Profissional com Design Corporativo
const gerarPDFProfissional = (
    dados: PropostaComDesconto,
    proposta: PropostaResponse,
    todosServicos: Servico[]
) => {
    const doc = new jsPDF('p', 'mm', 'a4');
    let yPos = 10;

    // 🎨 CORES CORPORATIVAS
    const cores = {
        azulEscuro: [25, 55, 109] as [number, number, number],     // #19376D - Azul corporativo
        azulMedio: [52, 115, 179] as [number, number, number],     // #3473B3 - Azul médio
        azulClaro: [176, 216, 230] as [number, number, number],    // #B0D8E6 - Azul claro
        cinzaEscuro: [64, 64, 64] as [number, number, number],     // #404040 - Cinza escuro
        cinzaMedio: [128, 128, 128] as [number, number, number],   // #808080 - Cinza médio
        cinzaClaro: [245, 245, 245] as [number, number, number],   // #F5F5F5 - Cinza claro
        verde: [34, 139, 34] as [number, number, number],          // #228B22 - Verde contábil
        laranja: [255, 140, 0] as [number, number, number]         // #FF8C00 - Laranja destaque
    };

    // 🎨 CABEÇALHO CORPORATIVO COM FUNDO
    doc.setFillColor(cores.azulEscuro[0], cores.azulEscuro[1], cores.azulEscuro[2]);
    doc.rect(0, 0, 210, 45, 'F');

    // Espaço para logo (pode ser adicionado depois)
    doc.setFillColor(255, 255, 255);
    doc.rect(15, 8, 25, 25, 'F');
    doc.setDrawColor(...cores.azulMedio);
    doc.setLineWidth(1);
    doc.rect(15, 8, 25, 25, 'S');

    // Texto "LOGO" temporário
    doc.setTextColor(...cores.azulMedio);
    doc.setFontSize(8);
    doc.setFont('helvetica', 'bold');
    doc.text('LOGO', 27.5, 22, { align: 'center' });

    // 🎨 TÍTULO PRINCIPAL
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(24);
    doc.setFont('helvetica', 'bold');
    doc.text('PROPOSTA COMERCIAL', 105, 18, { align: 'center' });

    doc.setFontSize(12);
    doc.setFont('helvetica', 'normal');
    doc.text('Serviços Contábeis e Tributários', 105, 25, { align: 'center' });

    // Número da proposta
    if (proposta.numero) {
        doc.setFontSize(10);
        doc.setFont('helvetica', 'bold');
        doc.text(`Proposta Nº ${proposta.numero}`, 105, 32, { align: 'center' });
    }

    // Data
    const dataGeracao = new Date().toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: 'long',
        year: 'numeric'
    });
    doc.setFontSize(9);
    doc.setFont('helvetica', 'italic');
    doc.text(`Brasília, ${dataGeracao}`, 105, 38, { align: 'center' });

    yPos = 55;

    // 🎨 INFORMAÇÕES DA EMPRESA (Rodapé do cabeçalho)
    doc.setFillColor(...cores.cinzaClaro);
    doc.rect(0, 45, 210, 15, 'F');

    doc.setTextColor(...cores.cinzaEscuro);
    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    doc.text('Sistema Contábil | CNPJ: 00.000.000/0001-00 | (61) 3000-0000 | contato@sistemacontabil.com.br', 105, 53, { align: 'center' });

    yPos = 70;

    // 🎨 SEÇÃO: DADOS DO CLIENTE
    adicionarSecaoProfissional(doc, 'DADOS DO CLIENTE', yPos, cores);
    yPos += 15;

    // Card do cliente
    doc.setFillColor(255, 255, 255);
    doc.setDrawColor(...cores.azulClaro);
    doc.setLineWidth(0.5);
    doc.roundedRect(15, yPos, 180, 25, 3, 3, 'FD');

    doc.setTextColor(...cores.cinzaEscuro);
    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');
    doc.text(dados.cliente.nome, 20, yPos + 7);

    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    doc.text(`CPF: ${dados.cliente.cpf}`, 20, yPos + 13);
    doc.text(`E-mail: ${dados.cliente.email}`, 20, yPos + 18);

    // Badge tipo cliente
    const tipoCliente = dados.cliente.abertura_empresa ? 'ABERTURA DE EMPRESA' : 'CLIENTE EXISTENTE';
    const corBadge = dados.cliente.abertura_empresa ? cores.laranja : cores.verde;

    doc.setFillColor(...corBadge);
    doc.roundedRect(140, yPos + 4, 50, 8, 2, 2, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(7);
    doc.setFont('helvetica', 'bold');
    doc.text(tipoCliente, 165, yPos + 9, { align: 'center' });

    yPos += 35;

    // 🎨 SEÇÃO: CONFIGURAÇÕES TRIBUTÁRIAS
    adicionarSecaoProfissional(doc, 'CONFIGURAÇÕES TRIBUTÁRIAS', yPos, cores);
    yPos += 15;

    // Grid de configurações
    const configs = [
        { label: 'Tipo de Atividade', valor: dados.tipoAtividade.nome, codigo: dados.tipoAtividade.codigo },
        { label: 'Regime Tributário', valor: dados.regimeTributario.nome, codigo: dados.regimeTributario.codigo }
    ];

    configs.forEach((config, index) => {
        const x = 15 + (index * 90);

        doc.setFillColor(...cores.azulClaro);
        doc.roundedRect(x, yPos, 85, 20, 2, 2, 'F');

        doc.setTextColor(...cores.azulEscuro);
        doc.setFontSize(7);
        doc.setFont('helvetica', 'bold');
        doc.text(config.label.toUpperCase(), x + 3, yPos + 5);

        doc.setFontSize(9);
        doc.setFont('helvetica', 'bold');
        doc.text(config.valor, x + 3, yPos + 11);

        doc.setFontSize(7);
        doc.setFont('helvetica', 'normal');
        doc.text(`Código: ${config.codigo}`, x + 3, yPos + 16);
    });

    yPos += 30;

    // 🎨 SERVIÇOS SELECIONADOS
    adicionarSecaoProfissional(doc, 'SERVIÇOS SELECIONADOS', yPos, cores);
    yPos += 15;

    // Agrupar serviços por categoria
    const servicosPorCategoria = new Map<string, any[]>();
    let subtotalServicos = 0;

    dados.servicosSelecionados.forEach(item => {
        const servico = todosServicos.find(s => s.id === item.servico_id);
        if (servico) {
            if (!servicosPorCategoria.has(servico.categoria)) {
                servicosPorCategoria.set(servico.categoria, []);
            }
            servicosPorCategoria.get(servico.categoria)!.push({
                nome: servico.nome,
                quantidade: item.quantidade,
                valorUnitario: item.valor_unitario,
                subtotal: item.subtotal
            });
            subtotalServicos += item.subtotal;
        }
    });

    // Criar tabela de serviços
    const servicosData: any[] = [];
    servicosPorCategoria.forEach((servicos, categoria) => {
        // Linha de categoria
        servicosData.push([
            {
                content: categoria.toUpperCase(),
                colSpan: 4,
                styles: {
                    fillColor: cores.azulMedio,
                    textColor: [255, 255, 255],
                    fontStyle: 'bold',
                    fontSize: 9,
                    halign: 'left'
                }
            }
        ]);

        // Serviços da categoria
        servicos.forEach(servico => {
            servicosData.push([
                { content: `• ${servico.nome}`, styles: { fontSize: 8 } },
                { content: `${servico.quantidade}x`, styles: { fontSize: 8, halign: 'center' } },
                { content: formatarMoedaPDF(servico.valorUnitario), styles: { fontSize: 8, halign: 'right' } },
                { content: formatarMoedaPDF(servico.subtotal), styles: { fontSize: 8, halign: 'right', fontStyle: 'bold', textColor: cores.azulEscuro } }
            ]);
        });
    });

    // Taxa de abertura (se aplicável)
    const taxaAbertura = calcularTaxaAbertura(dados.cliente, dados.regimeTributario);
    if (taxaAbertura > 0) {
        const tipoAbertura = getTipoAbertura(dados.cliente, dados.regimeTributario);
        servicosData.push([
            {
                content: 'ABERTURA DE EMPRESA',
                colSpan: 4,
                styles: {
                    fillColor: cores.verde,
                    textColor: [255, 255, 255],
                    fontStyle: 'bold',
                    fontSize: 9,
                    halign: 'left'
                }
            }
        ]);
        servicosData.push([
            { content: `• Taxa de Abertura ${tipoAbertura}`, styles: { fontSize: 8, fontStyle: 'bold' } },
            { content: '1x', styles: { fontSize: 8, halign: 'center' } },
            { content: formatarMoedaPDF(taxaAbertura), styles: { fontSize: 8, halign: 'right' } },
            { content: formatarMoedaPDF(taxaAbertura), styles: { fontSize: 8, halign: 'right', fontStyle: 'bold', textColor: cores.verde } }
        ]);
    }

    // ⚠️ VERIFICAR: Se autoTable está disponível antes de usar
    if (typeof doc.autoTable === 'function') {
        try {
            doc.autoTable({
                startY: yPos,
                head: [[
                    { content: 'Serviço', styles: { fillColor: cores.azulEscuro, textColor: [255, 255, 255] } },
                    { content: 'Qtd', styles: { fillColor: cores.azulEscuro, textColor: [255, 255, 255] } },
                    { content: 'Valor Unit.', styles: { fillColor: cores.azulEscuro, textColor: [255, 255, 255] } },
                    { content: 'Subtotal', styles: { fillColor: cores.azulEscuro, textColor: [255, 255, 255] } }
                ]],
                body: servicosData,
                theme: 'grid',
                styles: {
                    fontSize: 8,
                    cellPadding: { top: 3, right: 4, bottom: 3, left: 4 },
                    lineColor: cores.cinzaClaro,
                    lineWidth: 0.5
                },
                columnStyles: {
                    0: { cellWidth: 100 },
                    1: { cellWidth: 20, halign: 'center' },
                    2: { cellWidth: 35, halign: 'right' },
                    3: { cellWidth: 35, halign: 'right' }
                },
                alternateRowStyles: { fillColor: [250, 250, 250] }
            });
            if (doc.lastAutoTable) {
                yPos = doc.lastAutoTable.finalY + 10;
            }
        } catch (error) {
            console.error('Erro ao gerar tabela de serviços:', error);
            yPos += 50; // Fallback
        }
    } else {
        console.error('❌ autoTable não está disponível, usando fallback');
        // Fallback: adicionar texto simples
        doc.setTextColor(cores.cinzaEscuro[0], cores.cinzaEscuro[1], cores.cinzaEscuro[2]);
        doc.setFontSize(10);
        doc.text('Serviços Selecionados:', 20, yPos + 10);
        servicosData.forEach((row, index) => {
            if (Array.isArray(row) && row.length > 0) {
                const content = row[0]?.content || row[0] || '';
                doc.text(content, 20, yPos + 15 + (index * 5));
            }
        });
        yPos += 15 + (servicosData.length * 5);
    }

    // 🎨 NOVA PÁGINA SE NECESSÁRIO
    if (yPos > 240) {
        doc.addPage();
        yPos = 20;
    }

    // 🎨 RESUMO FINANCEIRO DESTACADO
    doc.setFillColor(...cores.azulEscuro);
    doc.roundedRect(15, yPos, 180, 8, 2, 2, 'F');

    doc.setTextColor(255, 255, 255);
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.text('RESUMO FINANCEIRO', 20, yPos + 6);

    yPos += 15;

    // Card resumo
    doc.setFillColor(255, 255, 255);
    doc.setDrawColor(...cores.azulClaro);
    doc.setLineWidth(1);
    doc.roundedRect(15, yPos, 180, 45, 3, 3, 'FD');

    // Grid de valores
    const totalGeral = subtotalServicos + taxaAbertura;
    const valorDesconto = dados.valorDesconto || 0;
    const totalFinal = dados.totalFinal;

    const resumoItens = [
        {
            label: 'SUBTOTAL',
            valor: formatarMoedaPDF(totalGeral),
            sublabel: 'Valor antes do desconto',
            cor: cores.azulMedio
        },
        {
            label: 'TOTAL FINAL',
            valor: formatarMoedaPDF(totalFinal),
            sublabel: 'Valor com desconto aplicado',
            cor: cores.verde
        }
    ];

    resumoItens.forEach((item, index) => {
        const x = 25 + (index * 80);

        doc.setFillColor(...item.cor);
        doc.roundedRect(x, yPos + 5, 70, 25, 2, 2, 'F');

        doc.setTextColor(255, 255, 255);
        doc.setFontSize(8);
        doc.setFont('helvetica', 'bold');
        doc.text(item.label, x + 35, yPos + 10, { align: 'center' });

        doc.setFontSize(14);
        doc.setFont('helvetica', 'bold');
        doc.text(item.valor, x + 35, yPos + 18, { align: 'center' });

        doc.setFontSize(6);
        doc.setFont('helvetica', 'normal');
        doc.text(item.sublabel, x + 35, yPos + 25, { align: 'center' });
    });

    // Desconto (se houver)
    if (dados.percentualDesconto > 0) {
        yPos += 35;
        doc.setFillColor(...cores.laranja);
        doc.roundedRect(45, yPos, 120, 15, 2, 2, 'F');

        doc.setTextColor(255, 255, 255);
        doc.setFontSize(9);
        doc.setFont('helvetica', 'bold');
        doc.text(`DESCONTO APLICADO: ${dados.percentualDesconto}%`, 105, yPos + 6, { align: 'center' });
        doc.text(`Economia: ${formatarMoedaPDF(valorDesconto)}`, 105, yPos + 12, { align: 'center' });
    }

    yPos += dados.percentualDesconto > 0 ? 25 : 50;

    // 🎨 OBSERVAÇÕES (se houver)
    if (dados.observacoes && dados.observacoes.trim()) {
        adicionarSecaoProfissional(doc, 'OBSERVAÇÕES ESPECÍFICAS', yPos, cores);
        yPos += 15;

        doc.setFillColor(cores.cinzaClaro[0], cores.cinzaClaro[1], cores.cinzaClaro[2]);
        doc.roundedRect(15, yPos, 180, 20, 2, 2, 'F');

        doc.setTextColor(cores.cinzaEscuro[0], cores.cinzaEscuro[1], cores.cinzaEscuro[2]);
        doc.setFontSize(9);
        doc.setFont('helvetica', 'normal');

        const observacoesLinhas = doc.splitTextToSize(dados.observacoes, 170);
        let alturaObservacoes = observacoesLinhas.length * 5 + 6;

        doc.roundedRect(15, yPos, 180, alturaObservacoes, 2, 2, 'F');

        observacoesLinhas.forEach((linha: string, index: number) => {
            doc.text(linha, 20, yPos + 6 + (index * 5));
        });

        yPos += alturaObservacoes + 10;
    }

    // 🎨 RODAPÉ PROFISSIONAL
    const alturaRodape = 35;
    const yRodape = 297 - alturaRodape;

    doc.setFillColor(cores.azulEscuro[0], cores.azulEscuro[1], cores.azulEscuro[2]);
    doc.rect(0, yRodape, 210, alturaRodape, 'F');

    doc.setTextColor(255, 255, 255);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.text('CONDIÇÕES GERAIS', 20, yRodape + 8);

    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    const condicoes = [
        '• Esta proposta é válida por 30 (trinta) dias a partir da data de emissão',
        '• Os valores estão sujeitos a reajuste conforme tabela vigente',
        '• Pagamento conforme condições a serem acordadas no contrato',
        '• Proposta sujeita à análise e aprovação interna'
    ];

    condicoes.forEach((condicao, index) => {
        doc.text(condicao, 20, yRodape + 15 + (index * 4));
    });

    // Status finalizada
    if (proposta.status === 'REALIZADA') {
        doc.setFillColor(cores.verde[0], cores.verde[1], cores.verde[2]);
        doc.roundedRect(140, yRodape + 8, 50, 12, 2, 2, 'F');

        doc.setTextColor(255, 255, 255);
        doc.setFontSize(8);
        doc.setFont('helvetica', 'bold');
        doc.text('PROPOSTA FINALIZADA', 165, yRodape + 15, { align: 'center' });
    }

    // 🎨 SALVAR COM NOME PROFISSIONAL
    const nomeArquivo = `Proposta_Comercial_${proposta.numero}_${dados.cliente.nome.replace(/\s+/g, '_')}.pdf`;
    doc.save(nomeArquivo);

    console.log('✅ PDF profissional gerado:', nomeArquivo);
};

// Função de PDF Finalizada (mantida para compatibilidade)
const gerarPDFPropostaFinalizada = (dados: PropostaComDesconto, proposta: PropostaResponse, todosServicos: Servico[]) => {
    gerarPDFProfissional(dados, proposta, todosServicos);
};
