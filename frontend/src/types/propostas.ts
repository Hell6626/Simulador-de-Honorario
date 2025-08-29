/**
 * Tipos específicos para propostas
 */

import { Cliente, TipoAtividade, RegimeTributario, FaixaFaturamento } from './index';

export interface ServicoSelecionado {
  servico_id: number;
  quantidade: number;
  valor_unitario: number;
  subtotal: number;
  extras?: Record<string, any>;
}

export interface DadosPropostaCompleta {
  cliente: Cliente;
  tipoAtividade: TipoAtividade;
  regimeTributario: RegimeTributario;
  faixaFaturamento?: FaixaFaturamento;
  servicosSelecionados: ServicoSelecionado[];
}

export interface ResumoFinanceiro {
  subtotalPorCategoria: Map<string, number>;
  subtotalServicos: number;
  taxaAberturaEmpresa: number;
  tipoAbertura: string;
  ehMEI: boolean;
  subtotalGeral: number;
  percentualDesconto: number;
  valorDesconto: number;
  totalFinal: number;
}

export interface PropostaComDesconto {
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
  propostaId?: number;
  propostaNumero?: string;
}

export interface ServicoPorCategoria {
  categoria: string;
  servicos: any[];
  total: number;
}

export interface EstadoSalvamento {
  salvando: boolean;
  ultimoSalvamento?: Date;
  erro?: string;
  tentativas: number;
}
