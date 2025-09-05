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

// ✅ NOVO: Funções de formatação para documentos
export const formatarCPF = (cpf: string): string => {
  const cpfLimpo = removerFormatacao(cpf);
  if (cpfLimpo.length !== 11) return cpf;

  return cpfLimpo.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
};

export const formatarCNPJ = (cnpj: string): string => {
  const cnpjLimpo = removerFormatacao(cnpj);
  if (cnpjLimpo.length !== 14) return cnpj;

  return cnpjLimpo.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
};

export const removerFormatacao = (valor: string): string => {
  return valor.replace(/\D/g, '');
};

export const validarCPF = (cpf: string): boolean => {
  const cpfLimpo = removerFormatacao(cpf);

  if (cpfLimpo.length !== 11) return false;
  if (/^(\d)\1{10}$/.test(cpfLimpo)) return false; // CPFs com todos os dígitos iguais

  let soma = 0;
  for (let i = 0; i < 9; i++) {
    soma += parseInt(cpfLimpo.charAt(i)) * (10 - i);
  }
  let resto = 11 - (soma % 11);
  if (resto === 10 || resto === 11) resto = 0;
  if (resto !== parseInt(cpfLimpo.charAt(9))) return false;

  soma = 0;
  for (let i = 0; i < 10; i++) {
    soma += parseInt(cpfLimpo.charAt(i)) * (11 - i);
  }
  resto = 11 - (soma % 11);
  if (resto === 10 || resto === 11) resto = 0;
  if (resto !== parseInt(cpfLimpo.charAt(10))) return false;

  return true;
};

export const validarCNPJ = (cnpj: string): boolean => {
  const cnpjLimpo = removerFormatacao(cnpj);

  if (cnpjLimpo.length !== 14) return false;
  if (/^(\d)\1{13}$/.test(cnpjLimpo)) return false; // CNPJs com todos os dígitos iguais

  let tamanho = cnpjLimpo.length - 2;
  let numeros = cnpjLimpo.substring(0, tamanho);
  let digitos = cnpjLimpo.substring(tamanho);
  let soma = 0;
  let pos = tamanho - 7;

  for (let i = tamanho; i >= 1; i--) {
    soma += parseInt(numeros.charAt(tamanho - i)) * pos--;
    if (pos < 2) pos = 9;
  }

  let resultado = soma % 11 < 2 ? 0 : 11 - (soma % 11);
  if (resultado !== parseInt(digitos.charAt(0))) return false;

  tamanho = tamanho + 1;
  numeros = cnpjLimpo.substring(0, tamanho);
  soma = 0;
  pos = tamanho - 7;

  for (let i = tamanho; i >= 1; i--) {
    soma += parseInt(numeros.charAt(tamanho - i)) * pos--;
    if (pos < 2) pos = 9;
  }

  resultado = soma % 11 < 2 ? 0 : 11 - (soma % 11);
  if (resultado !== parseInt(digitos.charAt(1))) return false;

  return true;
};

export const formatarDocumento = (documento: string): string => {
  const documentoLimpo = removerFormatacao(documento);

  if (documentoLimpo.length === 11) {
    return formatarCPF(documentoLimpo);
  } else if (documentoLimpo.length === 14) {
    return formatarCNPJ(documentoLimpo);
  }

  return documento;
};

export const detectarTipoDocumento = (documento: string): 'CPF' | 'CNPJ' | 'INVALIDO' => {
  const documentoLimpo = removerFormatacao(documento);

  if (documentoLimpo.length === 11) return 'CPF';
  if (documentoLimpo.length === 14) return 'CNPJ';
  return 'INVALIDO';
};