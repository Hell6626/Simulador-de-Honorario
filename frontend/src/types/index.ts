export interface User {
  id: number;
  nome: string;
  email: string;
  cargo_id: number;
  empresa_id: number;
  gerente: boolean;
  ativo: boolean;
  created_at: string;
  updated_at: string;
}

export interface Cliente {
  id: number;
  nome: string;
  cpf: string;
  email: string;
  abertura_empresa: boolean;
  ativo: boolean;
  created_at: string;
  updated_at: string;
}

export interface TipoAtividade {
  id: number;
  nome: string;
  codigo: string;
  descricao: string;
  aplicavel_pf: boolean;
  aplicavel_pj: boolean;
  ativo: boolean;
}

export interface RegimeTributario {
  id: number;
  nome: string;
  codigo: string;
  descricao: string;
  aplicavel_pf: boolean;
  aplicavel_pj: boolean;
  requer_definicoes_fiscais: boolean;
  ativo: boolean;
}

export interface FaixaFaturamento {
  id: number;
  nome: string;
  valor_minimo: number;
  valor_maximo: number;
  regime_tributario_id: number;
}

export interface Servico {
  id: number;
  nome: string;
  categoria: string;
  descricao: string;
  valor_base: number;
  ativo: boolean;
}

export interface Proposta {
  id: number;
  numero: string;
  cliente_id: number;
  funcionario_id: number;
  tipo_atividade_id: number;
  regime_tributario_id: number;
  faixa_faturamento_id: number;
  valor_total: number;
  data_validade: string;
  status: 'RASCUNHO' | 'ENVIADA' | 'APROVADA' | 'REJEITADA' | 'CANCELADA';
  observacoes?: string;
  created_at: string;
  updated_at: string;
  cliente?: Cliente;
  funcionario?: User;
  tipo_atividade?: TipoAtividade;
  regime_tributario?: RegimeTributario;
  faixa_faturamento?: FaixaFaturamento;
  itens?: ItemProposta[];
}

// ⚠️ NOVO: Interface para criação de proposta
export interface PropostaParaCriacao {
  cliente_id: number;
  tipo_atividade_id: number;
  regime_tributario_id: number;
  faixa_faturamento_id?: number;
  valor_total: number;
  data_validade?: string;
  status?: 'RASCUNHO' | 'PENDENTE' | 'APROVADA' | 'REJEITADA' | 'ENVIADA';
  observacoes?: string;
  // ⚠️ NOVO: Itens da proposta separados
  itens: {
    servico_id: number;
    quantidade: number;
    valor_unitario: number;
    valor_total: number;
    descricao_personalizada?: string;
  }[];
  // ⚠️ NOVO: Dados de desconto nas observações ou campo customizado
  percentual_desconto?: number;
  valor_desconto?: number;
  requer_aprovacao?: boolean;
}

// ⚠️ NOVO: Interface para resposta da API
export interface PropostaResponse {
  id: number;
  numero: string;
  cliente_id: number;
  funcionario_responsavel_id: number;
  tipo_atividade_id: number;
  regime_tributario_id: number;
  faixa_faturamento_id?: number;
  valor_total: number;
  data_validade?: string;
  status: string;
  observacoes?: string;
  ativo: boolean;
  created_at: string;
  updated_at: string;
  itens: ItemProposta[];
  cliente?: {
    id: number;
    nome: string;
    cpf: string;
    email: string;
  };
  funcionario_responsavel?: {
    id: number;
    nome: string;
    email: string;
  };
}

// ⚠️ NOVO: Interface para item de proposta
export interface ItemProposta {
  id: number;
  proposta_id: number;
  servico_id: number;
  quantidade: number;
  valor_unitario: number;
  valor_total: number;
  descricao_personalizada?: string;
  ativo: boolean;
  created_at: string;
  updated_at: string;
}

// ⚠️ NOVO: Interface para estado de salvamento
export interface EstadoSalvamento {
  salvando: boolean;
  ultimoSalvamento?: Date;
  propostaSalva: boolean;
  erro?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  pages: number;
  current_page: number;
  per_page: number;
}

export interface ApiError {
  error: string;
  message: string;
}

export interface LoginRequest {
  email: string;
  senha: string;
}

export interface LoginResponse {
  token: string;
}