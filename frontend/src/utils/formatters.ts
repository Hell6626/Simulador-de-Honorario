/**
 * Utilitários para formatação de dados
 */

export const formatarMoeda = (valor: number): string => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(valor);
};

export const formatarTipoCobranca = (tipoCobranca: string): string => {
  const tipos: Record<string, string> = {
    'MENSAL': 'mês',
    'POR_NF': 'NF',
    'VALOR_UNICO': 'serviço'
  };
  return tipos[tipoCobranca] || tipoCobranca;
};

export const formatarMoedaPDF = (valor: number): string => {
  return `R$ ${valor.toFixed(2).replace('.', ',')}`;
};

export const formatarData = (data: string | Date): string => {
  const date = typeof data === 'string' ? new Date(data) : data;
  return date.toLocaleDateString('pt-BR');
};

export const formatarDataHora = (data: string | Date): string => {
  const date = typeof data === 'string' ? new Date(data) : data;
  return date.toLocaleString('pt-BR');
};
