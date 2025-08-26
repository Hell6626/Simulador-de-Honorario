import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  ArrowLeft,
  ArrowRight,
  FileText,
  List,
  Calculator,
  MessageSquare,
  AlertTriangle,
  CheckCircle,
  User,
  Settings,
  Building,
  Info,
  Percent,
  FileDown,
  Download,
  Save,
  RefreshCw
} from 'lucide-react';
import jsPDF from 'jspdf';
import 'jspdf-autotable';

// Extend jsPDF type para autoTable
declare module 'jspdf' {
  interface jsPDF {
    autoTable: (options: any) => jsPDF;
  }
}
import { apiService } from '../../../services/api';
import { LoadingSpinner } from '../../common/LoadingSpinner';
import { ModalConfirmacaoDesconto } from '../../common/ModalConfirmacaoDesconto';
import { StatusSalvamento } from '../../common/StatusSalvamento';
import { useSalvamentoAutomatico } from '../../../hooks/useSalvamentoAutomatico';
import { Cliente } from '../../../types';

// Interfaces TypeScript

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

interface DadosPropostaCompleta {
  cliente: Cliente;
  tipoAtividade: TipoAtividade;
  regimeTributario: RegimeTributario;
  faixaFaturamento?: FaixaFaturamento;
  servicosSelecionados: ServicoSelecionado[];
}

interface ResumoFinanceiro {
  subtotalPorCategoria: Map<string, number>;
  subtotalServicos: number;
  taxaAberturaEmpresa: number;
  tipoAbertura: string; // ⚠️ NOVO: 'MEI' ou 'Empresa' ou ''
  ehMEI: boolean; // ⚠️ NOVO: Flag para MEI
  subtotalGeral: number;
  percentualDesconto: number;
  valorDesconto: number;
  totalFinal: number;
}

interface PropostaComDesconto {
  cliente: Cliente;
  tipoAtividade: TipoAtividade;
  regimeTributario: RegimeTributario;
  faixaFaturamento?: FaixaFaturamento;
  servicosSelecionados: ServicoSelecionado[];
  percentualDesconto: number;
  valorDesconto: number;
  totalFinal: number;
  requerAprovacao: boolean;
  observacoes?: string;
}

interface Passo4Props {
  dadosProposta: DadosPropostaCompleta;
  onVoltar: () => void;
  onProximo: (dadosComDesconto: PropostaComDesconto) => void;
  // ⚠️ NOVO: Props para salvamento automático
  dadosSalvos?: any;
  onSalvarProgresso?: (dados: any) => void;
}

// Função para formatar moeda
const formatarMoeda = (valor: number): string => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(valor);
};

// ⚠️ NOVA FUNÇÃO: Identificar se é MEI
const isMEI = (regimeTributario: RegimeTributario): boolean => {
  // Verificar por código do regime
  if (regimeTributario?.codigo?.toLowerCase().includes('mei')) {
    return true;
  }

  // Verificar por nome do regime
  if (regimeTributario?.nome?.toLowerCase().includes('microempreendedor') ||
    regimeTributario?.nome?.toLowerCase().includes('mei')) {
    return true;
  }

  // Adicionar outros critérios se necessário
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

export const Passo4RevisaoProposta: React.FC<Passo4Props> = ({
  dadosProposta,
  onVoltar,
  onProximo,
  dadosSalvos,
  onSalvarProgresso
}) => {
  const [percentualDesconto, setPercentualDesconto] = useState<number>(0);
  const [observacoes, setObservacoes] = useState<string>('');
  const [todosServicos, setTodosServicos] = useState<Servico[]>([]);
  const [loading, setLoading] = useState(false);

  // ⚠️ NOVO: Estado do modal de confirmação
  const [showModalConfirmacao, setShowModalConfirmacao] = useState(false);

  // ⚠️ NOVO: Estado para geração de PDF
  const [gerandoPDF, setGerandoPDF] = useState(false);

  // ⚠️ NOVO: Estados para salvamento automático aprimorado
  const [salvando, setSalvando] = useState(false);
  const [ultimoSalvamento, setUltimoSalvamento] = useState<Date | null>(null);
  const [erroSalvamento, setErroSalvamento] = useState<string | null>(null);
  const [tentativasSalvamento, setTentativasSalvamento] = useState(0);

  // ⚠️ NOVO: Hook de salvamento automático com retry
  const dadosCompletos = useMemo(() => ({
    ...dadosProposta,
    percentualDesconto,
    observacoes,
    requerAprovacao: percentualDesconto > 20
  }), [dadosProposta, percentualDesconto, observacoes]);

  // ⚠️ NOVO: Recuperar dados salvos ao montar componente
  useEffect(() => {
    if (dadosSalvos) {
      if (dadosSalvos.percentualDesconto !== undefined) {
        setPercentualDesconto(dadosSalvos.percentualDesconto);
      }
      if (dadosSalvos.observacoes !== undefined) {
        setObservacoes(dadosSalvos.observacoes);
      }
    }

    // Recuperar do localStorage como fallback
    const dadosBackup = localStorage.getItem('proposta_passo4_backup');
    if (dadosBackup && !dadosSalvos) {
      try {
        const dados = JSON.parse(dadosBackup);
        if (dados.percentualDesconto !== undefined) {
          setPercentualDesconto(dados.percentualDesconto);
        }
        if (dados.observacoes !== undefined) {
          setObservacoes(dados.observacoes);
        }
      } catch (error) {
        console.warn('Erro ao recuperar backup do Passo 4:', error);
      }
    }
  }, [dadosSalvos]);

  // ⚠️ NOVO: Função de salvamento automático com retry
  const salvarProgresso = useCallback(async (forcarSalvamento = false) => {
    if (!forcarSalvamento && !percentualDesconto && !observacoes.trim()) return;

    setSalvando(true);
    setErroSalvamento(null);

    try {
      const dadosParaSalvar = {
        passo: 4,
        percentualDesconto,
        observacoes,
        requerAprovacao: percentualDesconto > 20,
        timestamp: new Date().toISOString(),
        dadosCompletos: {
          ...dadosProposta,
          percentualDesconto,
          observacoes,
          requerAprovacao: percentualDesconto > 20
        }
      };

      // Salvar no localStorage como backup
      localStorage.setItem('proposta_passo4_backup', JSON.stringify(dadosParaSalvar));

      // Chamar callback de salvamento se fornecido
      if (onSalvarProgresso) {
        await onSalvarProgresso(dadosParaSalvar);
      }

      setUltimoSalvamento(new Date());
      setTentativasSalvamento(0);
      console.log('Progresso do Passo 4 salvo com sucesso');

    } catch (error) {
      console.error('Erro ao salvar progresso:', error);
      setErroSalvamento(error instanceof Error ? error.message : 'Erro desconhecido');

      // ⚠️ NOVO: Retry automático em caso de erro
      if (tentativasSalvamento < 3) {
        setTentativasSalvamento(prev => prev + 1);
        setTimeout(() => salvarProgresso(true), 2000 * (tentativasSalvamento + 1));
      }
    } finally {
      setSalvando(false);
    }
  }, [percentualDesconto, observacoes, dadosProposta, onSalvarProgresso, tentativasSalvamento]);

  // ⚠️ NOVO: Salvamento automático quando dados mudam
  useEffect(() => {
    const timeoutId = setTimeout(() => salvarProgresso(), 1500); // Debounce de 1.5 segundos
    return () => clearTimeout(timeoutId);
  }, [percentualDesconto, observacoes, salvarProgresso]);

  // ⚠️ NOVO: Limpar backup ao sair
  useEffect(() => {
    return () => {
      // Manter backup por 24 horas para recuperação
      const dadosBackup = localStorage.getItem('proposta_passo4_backup');
      if (dadosBackup) {
        try {
          const dados = JSON.parse(dadosBackup);
          const timestamp = new Date(dados.timestamp);
          const agora = new Date();
          const diffHoras = (agora.getTime() - timestamp.getTime()) / (1000 * 60 * 60);

          if (diffHoras > 24) {
            localStorage.removeItem('proposta_passo4_backup');
          }
        } catch (error) {
          localStorage.removeItem('proposta_passo4_backup');
        }
      }
    };
  }, []);

  // ⚠️ ADICIONAR: Função para diagnosticar problemas de dados
  const diagnosticarDadosProposta = (dados: any) => {
    const problemas: string[] = [];

    if (!dados.cliente) {
      problemas.push('Cliente não encontrado - verificar Passo 1');
    }

    if (!dados.tipoAtividade) {
      problemas.push('Tipo de Atividade não encontrado - verificar Passo 2');
    }

    if (!dados.regimeTributario) {
      problemas.push('Regime Tributário não encontrado - verificar Passo 2');
    }

    if (!dados.servicosSelecionados || dados.servicosSelecionados.length === 0) {
      problemas.push('Nenhum serviço selecionado - verificar Passo 3');
    }

    if (problemas.length > 0) {
      console.error('Problemas encontrados nos dados da proposta:', problemas);
      console.log('Dados atuais:', dados);
    }

    return problemas;
  };

  // ⚠️ ADICIONAR: Verificação de dados obrigatórios
  useEffect(() => {
    // Debug para verificar se os dados estão chegando corretamente
    console.log('Dados da proposta recebidos:', dadosProposta);

    const problemas = diagnosticarDadosProposta(dadosProposta);
    if (problemas.length > 0) {
      console.warn('Dados incompletos recebidos no Passo 4:', {
        cliente: !!dadosProposta.cliente,
        tipoAtividade: !!dadosProposta.tipoAtividade,
        regimeTributario: !!dadosProposta.regimeTributario,
        servicosSelecionados: dadosProposta.servicosSelecionados?.length || 0
      });
    }
  }, [dadosProposta]);

  // Carregar dados dos serviços para exibição completa
  useEffect(() => {
    const carregarServicos = async () => {
      setLoading(true);
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
      } finally {
        setLoading(false);
      }
    };

    carregarServicos();
  }, []);

  // ⚠️ ATUALIZADO: Calcular resumo financeiro com taxa diferenciada
  const resumoFinanceiro = useMemo((): ResumoFinanceiro => {
    // Agrupar subtotais por categoria (lógica existente)
    const subtotalPorCategoria = new Map<string, number>();

    dadosProposta.servicosSelecionados.forEach(item => {
      const servico = todosServicos.find(s => s.id === item.servico_id);
      if (servico) {
        const atual = subtotalPorCategoria.get(servico.categoria) || 0;
        subtotalPorCategoria.set(servico.categoria, atual + item.subtotal);
      }
    });

    const subtotalServicos = Array.from(subtotalPorCategoria.values())
      .reduce((sum, valor) => sum + valor, 0);

    // ⚠️ NOVA LÓGICA: Taxa diferenciada para MEI vs Empresa
    const taxaAberturaEmpresa = calcularTaxaAbertura(dadosProposta.cliente, dadosProposta.regimeTributario);
    const tipoAbertura = getTipoAbertura(dadosProposta.cliente, dadosProposta.regimeTributario);
    const ehMEI = isMEI(dadosProposta.regimeTributario);

    const subtotalGeral = subtotalServicos + taxaAberturaEmpresa;
    const valorDesconto = (subtotalGeral * percentualDesconto) / 100;
    const totalFinal = subtotalGeral - valorDesconto;

    return {
      subtotalPorCategoria,
      subtotalServicos,
      taxaAberturaEmpresa,
      tipoAbertura, // ⚠️ NOVO: Tipo específico (MEI/Empresa)
      ehMEI, // ⚠️ NOVO: Flag para identificação
      subtotalGeral,
      percentualDesconto,
      valorDesconto,
      totalFinal
    };
  }, [dadosProposta.servicosSelecionados, dadosProposta.cliente, dadosProposta.regimeTributario, todosServicos, percentualDesconto]);

  // Verificar se precisa de aprovação
  const requerAprovacao = percentualDesconto > 20;

  // Validações de Desconto
  const handleDescontoChange = (novoDesconto: number) => {
    // Limitar desconto entre 0 e 100%
    const descontoLimitado = Math.max(0, Math.min(100, novoDesconto));
    setPercentualDesconto(descontoLimitado);
  };

  const getStatusDesconto = (desconto: number) => {
    if (desconto === 0) return {
      tipo: 'neutro',
      mensagem: 'Nenhum desconto aplicado',
      cor: 'text-gray-600'
    };
    if (desconto <= 20) return {
      tipo: 'sucesso',
      mensagem: 'Desconto dentro do limite permitido',
      cor: 'text-green-600'
    };
    return {
      tipo: 'aviso',
      mensagem: 'Desconto requer aprovação do administrador',
      cor: 'text-orange-600'
    };
  };

  // Preparar Dados para Passo 5
  const prepararDadosParaPasso5 = (): PropostaComDesconto => {
    return {
      ...dadosProposta,
      percentualDesconto,
      valorDesconto: resumoFinanceiro.valorDesconto,
      totalFinal: resumoFinanceiro.totalFinal,
      requerAprovacao,
      observacoes: observacoes.trim() || undefined
    };
  };

  // ⚠️ NOVA FUNÇÃO: Verificar se precisa de confirmação
  const handleProximoClick = () => {
    if (requerAprovacao) {
      // Mostrar modal de confirmação
      setShowModalConfirmacao(true);
    } else {
      // Prosseguir normalmente
      prosseguirParaPasso5();
    }
  };

  // ⚠️ NOVA FUNÇÃO: Confirmar desconto alto
  const handleConfirmarDesconto = () => {
    setShowModalConfirmacao(false);
    prosseguirParaPasso5();
  };

  // ⚠️ NOVA FUNÇÃO: Cancelar confirmação
  const handleCancelarConfirmacao = () => {
    setShowModalConfirmacao(false);
    // Usuário pode ajustar o desconto
  };

  // ⚠️ FUNÇÃO HELPER: Formatar moeda para PDF
  const formatarMoedaPDF = (valor: number): string => {
    return `R$ ${valor.toFixed(2).replace('.', ',')}`;
  };

  // ⚠️ FUNÇÃO HELPER: Quebrar texto longo
  const quebrarTexto = (doc: jsPDF, texto: string, maxWidth: number): string[] => {
    return doc.splitTextToSize(texto, maxWidth);
  };

  // ⚠️ FUNÇÃO PARA GERAR PDF
  const gerarPDFProposta = () => {
    const doc = new jsPDF();
    let yPos = 20;

    // ⚠️ CABEÇALHO DA EMPRESA
    doc.setFontSize(20);
    doc.setFont('helvetica', 'bold');
    doc.text('PROPOSTA COMERCIAL', 105, yPos, { align: 'center' });

    yPos += 10;
    doc.setFontSize(12);
    doc.setFont('helvetica', 'normal');
    doc.text('Sistema Contábil - Propostas', 105, yPos, { align: 'center' });

    yPos += 15;
    doc.setLineWidth(0.5);
    doc.line(20, yPos, 190, yPos);
    yPos += 10;

    // ⚠️ DADOS DO CLIENTE
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('DADOS DO CLIENTE', 20, yPos);
    yPos += 8;

    doc.setFontSize(11);
    doc.setFont('helvetica', 'normal');

    const dadosCliente = [
      ['Nome:', dadosProposta.cliente?.nome || 'N/A'],
      ['CPF:', dadosProposta.cliente?.cpf || 'N/A'],
      ['E-mail:', dadosProposta.cliente?.email || 'N/A'],
      ['Tipo:', dadosProposta.cliente?.abertura_empresa ? 'Abertura de Empresa' : 'Cliente Existente']
    ];

    dadosCliente.forEach(([label, value]) => {
      doc.setFont('helvetica', 'bold');
      doc.text(label, 25, yPos);
      doc.setFont('helvetica', 'normal');
      doc.text(value, 60, yPos);
      yPos += 6;
    });

    yPos += 5;

    // ⚠️ CONFIGURAÇÕES TRIBUTÁRIAS
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('CONFIGURAÇÕES TRIBUTÁRIAS', 20, yPos);
    yPos += 8;

    doc.setFontSize(11);
    doc.setFont('helvetica', 'normal');

    const configTributarias = [
      ['Atividade:', dadosProposta.tipoAtividade?.nome || 'N/A'],
      ['Código Atividade:', dadosProposta.tipoAtividade?.codigo || 'N/A'],
      ['Regime Tributário:', dadosProposta.regimeTributario?.nome || 'N/A'],
      ['Código Regime:', dadosProposta.regimeTributario?.codigo || 'N/A']
    ];

    if (dadosProposta.faixaFaturamento) {
      const faixa = dadosProposta.faixaFaturamento;
      const faixaTexto = `R$ ${faixa.valor_inicial.toFixed(2).replace('.', ',')} até ${faixa.valor_final ? `R$ ${faixa.valor_final.toFixed(2).replace('.', ',')}` : 'ilimitado'
        } (${faixa.aliquota}%)`;
      configTributarias.push(['Faixa Faturamento:', faixaTexto]);
    }

    configTributarias.forEach(([label, value]) => {
      doc.setFont('helvetica', 'bold');
      doc.text(label, 25, yPos);
      doc.setFont('helvetica', 'normal');
      doc.text(value, 80, yPos);
      yPos += 6;
    });

    yPos += 10;

    // ⚠️ SERVIÇOS SELECIONADOS
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('SERVIÇOS SELECIONADOS', 20, yPos);
    yPos += 10;

    // Agrupar serviços por categoria
    const servicosPorCategoria = new Map<string, any[]>();
    let subtotalServicos = 0;

    dadosProposta.servicosSelecionados.forEach(item => {
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
        { content: categoria.toUpperCase(), colSpan: 4, styles: { fillColor: [240, 240, 240], fontStyle: 'bold' } }
      ]);

      // Serviços da categoria
      servicos.forEach(servico => {
        servicosData.push([
          servico.nome,
          servico.quantidade.toString(),
          formatarMoedaPDF(servico.valorUnitario),
          formatarMoedaPDF(servico.subtotal)
        ]);
      });
    });

    // ⚠️ TAXA DE ABERTURA (se aplicável)
    const taxaAbertura = calcularTaxaAbertura(dadosProposta.cliente, dadosProposta.regimeTributario);
    if (taxaAbertura > 0) {
      const tipoAbertura = getTipoAbertura(dadosProposta.cliente, dadosProposta.regimeTributario);
      servicosData.push([
        { content: 'ABERTURA DE EMPRESA', colSpan: 4, styles: { fillColor: [240, 240, 240], fontStyle: 'bold' } }
      ]);
      servicosData.push([
        `Taxa de Abertura ${tipoAbertura}`,
        '1',
        formatarMoedaPDF(taxaAbertura),
        formatarMoedaPDF(taxaAbertura)
      ]);
    }

    try {
      (doc as any).autoTable({
        startY: yPos,
        head: [['Serviço', 'Qtd', 'Valor Unit.', 'Subtotal']],
        body: servicosData,
        theme: 'grid',
        styles: {
          fontSize: 9,
          cellPadding: 3
        },
        headStyles: {
          fillColor: [41, 128, 185],
          textColor: 255,
          fontStyle: 'bold'
        },
        columnStyles: {
          1: { halign: 'center', cellWidth: 20 },
          2: { halign: 'right', cellWidth: 30 },
          3: { halign: 'right', cellWidth: 30 }
        }
      });

      yPos = (doc as any).lastAutoTable.finalY + 10;
    } catch (error) {
      console.warn('autoTable não disponível, usando texto simples:', error);
      // Fallback: usar texto simples
      servicosData.forEach((row, index) => {
        if (index === 0) return; // Pular cabeçalho
        const servico = row[0];
        const qtd = row[1];
        const valor = row[2];
        const subtotal = row[3];

        doc.setFontSize(10);
        doc.text(`${servico} - Qtd: ${qtd} - ${valor} - ${subtotal}`, 25, yPos);
        yPos += 5;
      });
      yPos += 10;
    }

    // ⚠️ RESUMO FINANCEIRO (SEM DESCONTO)
    const totalGeral = subtotalServicos + taxaAbertura;

    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.text('RESUMO FINANCEIRO', 20, yPos);
    yPos += 8;

    const resumoData = [
      ['Subtotal dos Serviços', formatarMoedaPDF(subtotalServicos)]
    ];

    if (taxaAbertura > 0) {
      const tipoAbertura = getTipoAbertura(dadosProposta.cliente, dadosProposta.regimeTributario);
      resumoData.push([`Taxa Abertura ${tipoAbertura}`, formatarMoedaPDF(taxaAbertura)]);
    }

    resumoData.push([
      'TOTAL GERAL',
      formatarMoedaPDF(totalGeral)
    ]);

    try {
      (doc as any).autoTable({
        startY: yPos,
        body: resumoData,
        theme: 'plain',
        styles: {
          fontSize: 11,
          cellPadding: 4
        },
        columnStyles: {
          0: { cellWidth: 140 },
          1: { halign: 'right', cellWidth: 50 }
        }
      });

      yPos = (doc as any).lastAutoTable.finalY + 15;
    } catch (error) {
      console.warn('autoTable não disponível para resumo, usando texto simples:', error);
      // Fallback: usar texto simples
      resumoData.forEach(([label, value]) => {
        doc.setFontSize(11);
        doc.setFont('helvetica', 'bold');
        doc.text(label, 25, yPos);
        doc.setFont('helvetica', 'normal');
        doc.text(value, 120, yPos);
        yPos += 6;
      });
      yPos += 10;
    }

    // ⚠️ RODAPÉ
    doc.setFontSize(10);
    doc.setFont('helvetica', 'italic');
    doc.text('Esta proposta é válida por 30 dias a partir da data de emissão.', 105, yPos, { align: 'center' });

    yPos += 5;
    const dataAtual = new Date().toLocaleDateString('pt-BR');
    doc.text(`Proposta gerada em: ${dataAtual}`, 105, yPos, { align: 'center' });

    // ⚠️ GERAR E BAIXAR PDF
    const nomeArquivo = `Proposta_${dadosProposta.cliente?.nome?.replace(/\s+/g, '_') || 'Cliente'}_${new Date().toISOString().slice(0, 10)}.pdf`;
    doc.save(nomeArquivo);
  };

  // ⚠️ FUNÇÃO COM FEEDBACK VISUAL
  const gerarPDFComFeedback = async () => {
    setGerandoPDF(true);

    try {
      // Pequeno delay para mostrar loading
      await new Promise(resolve => setTimeout(resolve, 500));

      gerarPDFProposta();

      // Feedback de sucesso (opcional)
      console.log('PDF gerado com sucesso!');
    } catch (error) {
      console.error('Erro ao gerar PDF:', error);
      alert('Erro ao gerar PDF. Tente novamente.');
    } finally {
      setGerandoPDF(false);
    }
  };

  // Função para prosseguir para o passo 5
  const prosseguirParaPasso5 = () => {
    const dadosCompletos = prepararDadosParaPasso5();
    onProximo(dadosCompletos);
  };

  const handleProximo = () => {
    // ⚠️ NOVO: Salvar antes de prosseguir
    salvarProgresso(true);

    const dadosCompletos = prepararDadosParaPasso5();
    onProximo(dadosCompletos);
  };

  // Validação para habilitar botão próximo
  const podeProximo = useMemo(() => {
    return observacoes.length <= 500; // Apenas validar tamanho das observações
  }, [observacoes]);

  // ⚠️ ADICIONAR: Loading state se dados não estiverem completos
  if (!dadosProposta.cliente || !dadosProposta.tipoAtividade || !dadosProposta.regimeTributario) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando dados da proposta...</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="flex items-center">
          <LoadingSpinner size="md" />
          <span className="ml-3 text-gray-500">Carregando dados...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-32">
      {/* ⚠️ VERIFICAÇÃO: Debug dos dados recebidos */}
      {import.meta.env.DEV && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
          <details>
            <summary className="text-sm font-medium text-yellow-800 cursor-pointer">
              Debug: Dados recebidos no Passo 4
            </summary>
            <pre className="text-xs text-yellow-700 mt-2 overflow-auto">
              {JSON.stringify(dadosProposta, null, 2)}
            </pre>
          </details>
        </div>
      )}

      {/* ⚠️ NOVO: Aviso de recuperação se aplicável */}
      {dadosSalvos && (dadosSalvos.percentualDesconto > 0 || dadosSalvos.observacoes) && (
        <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-5 h-5 text-blue-600" />
            <span className="text-blue-800 text-sm">
              Revisão recuperada - Desconto e observações restaurados automaticamente
            </span>
          </div>
        </div>
      )}

      {/* ⚠️ ATUALIZADO: Cabeçalho com botão PDF e status de salvamento */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Nova Proposta - Passo 4</h1>
            <p className="text-sm text-gray-500">Revisão da Proposta</p>
            <p className="text-sm text-gray-600 mt-1">
              Confira os dados e aplique desconto se necessário
            </p>

            {/* ⚠️ NOVO: Status de salvamento automático aprimorado */}
            <div className="flex items-center space-x-2 mt-2">
              {salvando && (
                <div className="flex items-center text-blue-600 text-sm">
                  <div className="animate-spin w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full mr-2"></div>
                  <span>Salvando revisão...</span>
                  {tentativasSalvamento > 0 && (
                    <span className="text-orange-600 ml-2">(Tentativa {tentativasSalvamento}/3)</span>
                  )}
                </div>
              )}

              {ultimoSalvamento && !salvando && (
                <div className="flex items-center text-green-600 text-sm">
                  <CheckCircle className="w-4 h-4 mr-1" />
                  <span>Salvo {ultimoSalvamento.toLocaleTimeString()}</span>
                </div>
              )}

              {erroSalvamento && !salvando && (
                <div className="flex items-center text-red-600 text-sm">
                  <AlertTriangle className="w-4 h-4 mr-1" />
                  <span>Erro no salvamento</span>
                  <button
                    onClick={tentarSalvarNovamente}
                    className="ml-2 text-blue-600 hover:text-blue-700 flex items-center space-x-1"
                  >
                    <RefreshCw className="w-3 h-3" />
                    <span>Tentar novamente</span>
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* ⚠️ NOVO: Botões de ação no cabeçalho */}
          <div className="flex items-center space-x-3">
            <button
              onClick={gerarPDFComFeedback}
              disabled={gerandoPDF}
              className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-blue-700 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {gerandoPDF ? (
                <>
                  <div className="animate-spin w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full"></div>
                  <span>Gerando...</span>
                </>
              ) : (
                <>
                  <FileDown className="w-4 h-4" />
                  <span>Gerar PDF</span>
                </>
              )}
            </button>

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

      {/* ⚠️ INDICADOR ESPECIAL PARA TIPO DE ABERTURA */}
      {dadosProposta.cliente?.abertura_empresa && (
        <div className={`border rounded-lg p-4 mb-6 ${resumoFinanceiro.ehMEI
          ? 'bg-gradient-to-r from-orange-50 to-yellow-50 border-orange-200'
          : 'bg-gradient-to-r from-purple-50 to-pink-50 border-purple-200'
          }`}>
          <div className="flex items-center space-x-3">
            {resumoFinanceiro.ehMEI ? (
              <User className="w-6 h-6 text-orange-600" />
            ) : (
              <Building className="w-6 h-6 text-purple-600" />
            )}
            <div>
              <h3 className={`text-base font-semibold ${resumoFinanceiro.ehMEI ? 'text-orange-900' : 'text-purple-900'
                }`}>
                Proposta para Abertura de {resumoFinanceiro.tipoAbertura}
              </h3>
              <p className={`text-sm ${resumoFinanceiro.ehMEI ? 'text-orange-700' : 'text-purple-700'
                }`}>
                {resumoFinanceiro.ehMEI
                  ? `Inclui taxa de ${formatarMoeda(resumoFinanceiro.taxaAberturaEmpresa)} para registro como Microempreendedor Individual`
                  : `Inclui taxa de ${formatarMoeda(resumoFinanceiro.taxaAberturaEmpresa)} para todo o processo de abertura empresarial`
                }
              </p>

              {/* ⚠️ NOVO: Badge com regime tributário */}
              <div className="mt-2">
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${resumoFinanceiro.ehMEI
                  ? 'bg-orange-100 text-orange-800'
                  : 'bg-purple-100 text-purple-800'
                  }`}>
                  Regime: {dadosProposta.regimeTributario?.nome}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ⚠️ CORRIGIDO: Dados da Proposta com dados reais */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <FileText className="w-5 h-5 mr-2 text-blue-600" />
          Dados da Proposta
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
              <User className="w-4 h-4 mr-1" />
              Cliente
            </h3>
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
              {/* ⚠️ USAR DADOS REAIS DA PROP */}
              <p className="font-semibold text-gray-900 text-lg">{dadosProposta.cliente.nome}</p>
              <div className="mt-2 space-y-1">
                <p className="text-sm text-gray-600 flex items-center">
                  <span className="font-medium">CPF:</span>
                  <span className="ml-2">{dadosProposta.cliente.cpf}</span>
                </p>
                <p className="text-sm text-gray-600 flex items-center">
                  <span className="font-medium">Email:</span>
                  <span className="ml-2">{dadosProposta.cliente.email}</span>
                </p>
              </div>
              <div className="mt-3">
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${dadosProposta.cliente.abertura_empresa
                  ? 'bg-purple-100 text-purple-800 border border-purple-200'
                  : 'bg-green-100 text-green-800 border border-green-200'
                  }`}>
                  {dadosProposta.cliente.abertura_empresa ? (
                    <>
                      <Building className="w-3 h-3 mr-1" />
                      Abertura de Empresa
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-3 h-3 mr-1" />
                      Cliente Existente
                    </>
                  )}
                </span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
              <Settings className="w-4 h-4 mr-1" />
              Configurações Tributárias
            </h3>
            <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4 border border-green-200">
              {/* ⚠️ USAR DADOS REAIS DAS CONFIGURAÇÕES */}
              <div className="space-y-2">
                <div>
                  <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Atividade</span>
                  <p className="font-semibold text-gray-900">{dadosProposta.tipoAtividade.nome}</p>
                  <p className="text-xs text-gray-600">Código: {dadosProposta.tipoAtividade.codigo}</p>
                </div>

                <div className="border-t border-green-100 pt-2">
                  <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Regime Tributário</span>
                  <p className="font-medium text-gray-900">{dadosProposta.regimeTributario.nome}</p>
                  <p className="text-xs text-gray-600">Código: {dadosProposta.regimeTributario.codigo}</p>
                </div>

                {dadosProposta.faixaFaturamento ? (
                  <div className="border-t border-green-100 pt-2">
                    <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Faixa de Faturamento</span>
                    <p className="text-sm text-gray-900">
                      {formatarMoeda(dadosProposta.faixaFaturamento.valor_inicial)} até{' '}
                      {dadosProposta.faixaFaturamento.valor_final
                        ? formatarMoeda(dadosProposta.faixaFaturamento.valor_final)
                        : 'ilimitado'
                      }
                    </p>
                    <p className="text-xs text-gray-600">
                      Alíquota: {dadosProposta.faixaFaturamento.aliquota}%
                    </p>
                  </div>
                ) : (
                  <div className="border-t border-green-100 pt-2">
                    <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Faixa de Faturamento</span>
                    <p className="text-sm text-gray-500 italic">Não aplicável para este regime</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Serviços Selecionados */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <List className="w-5 h-5 mr-2 text-blue-600" />
          Serviços Selecionados
        </h2>

        <div className="space-y-6">
          {Array.from(resumoFinanceiro.subtotalPorCategoria.entries()).map(([categoria, totalCategoria]) => {
            const servicosCategoria = dadosProposta.servicosSelecionados.filter(item => {
              const servico = todosServicos.find(s => s.id === item.servico_id);
              return servico?.categoria === categoria;
            });

            if (servicosCategoria.length === 0) return null;

            return (
              <div key={categoria} className="border-l-4 border-blue-500 pl-4">
                <div className="flex justify-between items-center mb-3">
                  <h3 className="text-base font-medium text-gray-900 capitalize flex items-center">
                    <span className="w-3 h-3 bg-blue-500 rounded-full mr-2"></span>
                    {categoria.toLowerCase()}
                  </h3>
                  <span className="text-lg font-semibold text-blue-600">
                    {formatarMoeda(totalCategoria)}
                  </span>
                </div>

                <div className="space-y-2 ml-5">
                  {servicosCategoria.map(item => {
                    const servico = todosServicos.find(s => s.id === item.servico_id);
                    if (!servico) return null;

                    return (
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
                    );
                  })}
                </div>
              </div>
            );
          })}

          {/* ⚠️ ATUALIZADO: Taxa de Abertura com tipo específico */}
          {dadosProposta.cliente?.abertura_empresa && (
            <div className={`border-l-4 pl-4 ${resumoFinanceiro.ehMEI ? 'border-orange-500' : 'border-green-500'}`}>
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-base font-medium text-gray-900 capitalize flex items-center">
                  <span className={`w-3 h-3 rounded-full mr-2 ${resumoFinanceiro.ehMEI ? 'bg-orange-500' : 'bg-green-500'}`}></span>
                  Abertura de {resumoFinanceiro.tipoAbertura}
                </h3>
                <span className={`text-lg font-semibold ${resumoFinanceiro.ehMEI ? 'text-orange-600' : 'text-green-600'}`}>
                  {formatarMoeda(resumoFinanceiro.taxaAberturaEmpresa)}
                </span>
              </div>

              <div className="ml-5">
                <div className={`flex justify-between items-center text-sm rounded-lg p-3 ${resumoFinanceiro.ehMEI ? 'bg-orange-50' : 'bg-green-50'
                  }`}>
                  <div className="flex-1">
                    <span className="text-gray-700 font-medium flex items-center">
                      {resumoFinanceiro.ehMEI ? (
                        <>
                          <User className="w-4 h-4 mr-1 text-orange-600" />
                          • Taxa de Abertura MEI
                        </>
                      ) : (
                        <>
                          <Building className="w-4 h-4 mr-1 text-green-600" />
                          • Taxa de Abertura de Empresa
                        </>
                      )}
                    </span>
                    <span className="text-gray-500 block text-xs mt-1">
                      {resumoFinanceiro.ehMEI
                        ? 'Inclui registro como Microempreendedor Individual'
                        : 'Inclui todo o processo de abertura e documentação necessária'
                      }
                    </span>
                  </div>
                  <span className="font-semibold text-gray-900">
                    {formatarMoeda(resumoFinanceiro.taxaAberturaEmpresa)}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ⚠️ NOVO DESIGN: Valores e Desconto Melhorado */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
          <Calculator className="w-5 h-5 mr-2 text-blue-600" />
          Valores e Desconto
        </h2>

        <div className="space-y-6">
          {/* ⚠️ ATUALIZADO: Breakdown com tipo específico */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-medium text-gray-800 mb-3">Composição do Valor:</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Serviços selecionados:</span>
                <span className="font-medium">{formatarMoeda(resumoFinanceiro.subtotalServicos)}</span>
              </div>

              {dadosProposta.cliente?.abertura_empresa && (
                <div className="flex justify-between">
                  <span className="text-gray-600 flex items-center">
                    {resumoFinanceiro.ehMEI ? (
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
                  <span className={`font-medium ${resumoFinanceiro.ehMEI ? 'text-orange-600' : 'text-green-600'}`}>
                    + {formatarMoeda(resumoFinanceiro.taxaAberturaEmpresa)}
                  </span>
                </div>
              )}

              <div className="border-t border-gray-300 pt-2">
                <div className="flex justify-between">
                  <span className="font-semibold text-gray-800">Subtotal:</span>
                  <span className="text-xl font-bold text-gray-900">
                    {formatarMoeda(resumoFinanceiro.subtotalGeral)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* ⚠️ NOVA SEÇÃO: Controle de Desconto Melhorado */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <Percent className="w-5 h-5 mr-2 text-blue-600" />
                Aplicar Desconto
              </h3>

              {/* Controle de input melhorado */}
              <div className="flex items-center space-x-3">
                <div className="relative">
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="0.1"
                    value={percentualDesconto || ''}
                    onChange={(e) => handleDescontoChange(parseFloat(e.target.value) || 0)}
                    className="w-24 h-12 text-center text-lg font-bold border-2 border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                    placeholder="0"
                  />
                  <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-blue-600 font-bold">%</span>
                </div>

                <div className="flex items-center text-gray-400">
                  <ArrowRight className="w-5 h-5" />
                </div>

                <div className="bg-white rounded-lg px-4 py-3 border-2 border-red-200 min-w-[120px]">
                  <div className="text-center">
                    <p className="text-xs text-gray-500 mb-1">Desconto</p>
                    <p className="text-lg font-bold text-red-600">
                      -{formatarMoeda(resumoFinanceiro.valorDesconto)}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* ⚠️ NOVA: Barra de progresso visual melhorada */}
            <div className="space-y-3">
              <div className="flex items-center justify-between text-sm text-gray-600">
                <span>0%</span>
                <span className="flex items-center">
                  <AlertTriangle className="w-4 h-4 mr-1" />
                  Limite 20%
                </span>
                <span>100%</span>
              </div>

              <div className="relative">
                <div className="w-full bg-gray-200 rounded-full h-3">
                  {/* Faixa permitida (0-20%) */}
                  <div className="absolute left-0 top-0 h-3 bg-green-400 rounded-l-full" style={{ width: '20%' }}></div>
                  {/* Faixa de atenção (20-100%) */}
                  <div className="absolute left-[20%] top-0 h-3 bg-orange-200 rounded-r-full" style={{ width: '80%' }}></div>
                  {/* Indicador atual */}
                  <div
                    className={`absolute top-0 h-3 rounded-full transition-all duration-300 ${percentualDesconto <= 20 ? 'bg-green-600' : 'bg-orange-600'
                      }`}
                    style={{ width: `${Math.min(percentualDesconto, 100)}%` }}
                  ></div>
                </div>

                {/* Marcador de 20% */}
                <div className="absolute top-0 left-[20%] transform -translate-x-1/2">
                  <div className="w-1 h-3 bg-yellow-500"></div>
                  <div className="w-3 h-3 bg-yellow-500 rounded-full -mt-1 transform -translate-x-1/2"></div>
                </div>
              </div>

              {/* Indicador atual com posição dinâmica */}
              {percentualDesconto > 0 && (
                <div
                  className="absolute transform -translate-x-1/2 mt-1"
                  style={{ left: `${Math.min(percentualDesconto, 100)}%` }}
                >
                  <div className="bg-white border-2 border-blue-600 rounded-lg px-2 py-1 shadow-lg">
                    <span className="text-xs font-bold text-blue-600">{percentualDesconto.toFixed(1)}%</span>
                  </div>
                </div>
              )}
            </div>

            {/* ⚠️ NOVA: Status visual melhorado */}
            <div className="mt-4">
              {percentualDesconto === 0 && (
                <div className="flex items-center space-x-2 text-gray-600">
                  <Info className="w-4 h-4" />
                  <span className="text-sm">Nenhum desconto aplicado</span>
                </div>
              )}

              {percentualDesconto > 0 && percentualDesconto <= 20 && (
                <div className="flex items-center space-x-2 text-green-700 bg-green-100 rounded-lg px-3 py-2">
                  <CheckCircle className="w-5 h-5" />
                  <span className="text-sm font-medium">Desconto aprovado automaticamente</span>
                </div>
              )}

              {percentualDesconto > 20 && (
                <div className="flex items-center space-x-2 text-orange-700 bg-orange-100 rounded-lg px-3 py-2">
                  <AlertTriangle className="w-5 h-5" />
                  <span className="text-sm font-medium">Requer aprovação do administrador</span>
                </div>
              )}
            </div>
          </div>

          {/* ⚠️ AVISO EXPANDIDO para desconto alto */}
          {requerAprovacao && (
            <div className="bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200 rounded-xl p-5">
              <div className="flex items-start space-x-4">
                <div className="bg-orange-100 rounded-full p-2">
                  <AlertTriangle className="w-6 h-6 text-orange-600" />
                </div>
                <div className="flex-1">
                  <h4 className="text-base font-semibold text-orange-800 mb-2">
                    Atenção: Desconto Excepcional Aplicado
                  </h4>
                  <div className="text-sm text-orange-700 space-y-1">
                    <p>• Este desconto de <strong>{percentualDesconto}%</strong> excede o limite padrão de 20%</p>
                    <p>• A proposta será enviada para análise e aprovação do administrador</p>
                    <p>• O cliente receberá a proposta somente após aprovação administrativa</p>
                    <p>• Tempo estimado de aprovação: 1-2 dias úteis</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* ⚠️ ATUALIZADO: Total Final com breakdown específico */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-6 text-white">
            <div className="flex justify-between items-center">
              <div>
                <span className="text-blue-100 text-sm font-medium">VALOR TOTAL DA PROPOSTA</span>
                <div className="flex items-baseline space-x-2 mt-1">
                  <span className="text-3xl font-bold">
                    {formatarMoeda(resumoFinanceiro.totalFinal)}
                  </span>
                  {percentualDesconto > 0 && (
                    <span className="text-blue-200 text-sm">
                      (economia de {formatarMoeda(resumoFinanceiro.valorDesconto)})
                    </span>
                  )}
                </div>

                {/* ⚠️ ATUALIZADO: Breakdown no total com tipo específico */}
                <div className="text-blue-200 text-xs mt-2 space-y-1">
                  <div>Serviços: {formatarMoeda(resumoFinanceiro.subtotalServicos)}</div>
                  {dadosProposta.cliente?.abertura_empresa && (
                    <div>
                      {resumoFinanceiro.ehMEI ? 'Abertura MEI' : 'Abertura Empresa'}: {formatarMoeda(resumoFinanceiro.taxaAberturaEmpresa)}
                    </div>
                  )}
                  {percentualDesconto > 0 && (
                    <div>Desconto: -{formatarMoeda(resumoFinanceiro.valorDesconto)}</div>
                  )}
                </div>
              </div>

              {percentualDesconto > 0 && (
                <div className="text-right">
                  <div className="bg-white bg-opacity-20 rounded-lg px-3 py-2">
                    <span className="text-blue-100 text-xs">Desconto aplicado</span>
                    <p className="text-xl font-bold text-white">-{percentualDesconto}%</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Observações */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <MessageSquare className="w-5 h-5 mr-2 text-blue-600" />
          Observações
        </h2>

        <div className="space-y-3">
          <textarea
            value={observacoes}
            onChange={(e) => setObservacoes(e.target.value.slice(0, 500))}
            placeholder="Adicione observações adicionais sobre esta proposta (opcional)..."
            rows={4}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          />
          <div className="flex justify-between items-center text-xs">
            <span className="text-gray-500">
              Use este espaço para informações específicas do cliente ou observações sobre os serviços
            </span>
            <span className={`${observacoes.length > 450 ? 'text-orange-600' : 'text-gray-500'}`}>
              {observacoes.length}/500 caracteres
            </span>
          </div>
        </div>
      </div>

      {/* ⚠️ BOTÕES ATUALIZADOS */}
      <div className="fixed bottom-0 left-64 right-0 bg-white border-t border-gray-200 px-6 py-4 z-10">
        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            <div>Passo 4 de 5 - Próximo: Finalização da Proposta</div>
            {requerAprovacao && (
              <div className="text-orange-600 font-medium">
                ⚠️ Desconto requer confirmação
              </div>
            )}

            {/* ⚠️ NOVO: Status de salvamento na barra inferior */}
            <div className="mt-1 flex items-center space-x-2">
              {salvando && (
                <div className="flex items-center text-blue-600 text-xs">
                  <div className="animate-spin w-3 h-3 border-2 border-blue-600 border-t-transparent rounded-full mr-1"></div>
                  <span>Salvando...</span>
                </div>
              )}

              {ultimoSalvamento && !salvando && (
                <div className="flex items-center text-green-600 text-xs">
                  <CheckCircle className="w-3 h-3 mr-1" />
                  <span>Último salvamento: {ultimoSalvamento.toLocaleTimeString()}</span>
                </div>
              )}

              {/* ⚠️ NOVO: Botão de salvamento manual */}
              <button
                onClick={() => salvarProgresso(true)}
                disabled={salvando}
                className="flex items-center space-x-1 px-2 py-1 text-xs text-blue-600 bg-blue-50 rounded hover:bg-blue-100 disabled:opacity-50 transition-colors"
              >
                <Save className="w-3 h-3" />
                <span>Salvar Agora</span>
              </button>
            </div>
          </div>

          <div className="flex space-x-3">
            <button
              onClick={onVoltar}
              className="px-6 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Anterior
            </button>

            <button
              onClick={handleProximoClick} // ⚠️ MUDANÇA: Nova função
              disabled={!podeProximo}
              className={`px-6 py-2 text-sm font-medium text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 ${requerAprovacao
                ? 'bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600'
                : 'bg-blue-600 hover:bg-blue-700'
                }`}
            >
              {requerAprovacao ? (
                <>
                  <AlertTriangle className="w-4 h-4 mr-2" />
                  Confirmar Desconto
                </>
              ) : (
                <>
                  <span>Próximo</span>
                  <ArrowRight className="w-4 h-4 ml-2" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* ⚠️ MODAL DE CONFIRMAÇÃO */}
      <ModalConfirmacaoDesconto
        isOpen={showModalConfirmacao}
        percentualDesconto={percentualDesconto}
        valorDesconto={resumoFinanceiro.valorDesconto}
        totalOriginal={resumoFinanceiro.subtotalGeral}
        totalFinal={resumoFinanceiro.totalFinal}
        onConfirmar={handleConfirmarDesconto}
        onCancelar={handleCancelarConfirmacao}
      />
    </div>
  );
};
