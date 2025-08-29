import { useMemo } from 'react';
import { DadosPropostaCompleta, ResumoFinanceiro } from '../types/propostas';
import { isMEI, calcularTaxaAbertura, getTipoAbertura, calcularDesconto } from '../utils/calculations';

export const usePropostaCalculations = (
  dadosProposta: DadosPropostaCompleta, 
  percentualDesconto: number,
  todosServicos: any[] = []
): ResumoFinanceiro => {
  return useMemo((): ResumoFinanceiro => {


    // Agrupar subtotais por categoria
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

    // Calcular taxa de abertura
    const taxaAberturaEmpresa = calcularTaxaAbertura(dadosProposta.cliente, dadosProposta.regimeTributario);
    const tipoAbertura = getTipoAbertura(dadosProposta.cliente, dadosProposta.regimeTributario);
    const ehMEI = isMEI(dadosProposta.regimeTributario);

    const subtotalGeral = subtotalServicos + taxaAberturaEmpresa;
    const valorDesconto = calcularDesconto(subtotalGeral, percentualDesconto);
    const totalFinal = subtotalGeral - valorDesconto;

    return {
      subtotalPorCategoria,
      subtotalServicos,
      taxaAberturaEmpresa,
      tipoAbertura,
      ehMEI,
      subtotalGeral,
      percentualDesconto,
      valorDesconto,
      totalFinal
    };
  }, [dadosProposta, percentualDesconto, todosServicos]);
};
