import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { DadosPropostaCompleta, PropostaComDesconto } from '../types/propostas';

// Tipos de ações
type PropostaAction =
  | { type: 'SET_DADOS_PROPOSTA'; payload: DadosPropostaCompleta }
  | { type: 'UPDATE_CLIENTE'; payload: any }
  | { type: 'UPDATE_TIPO_ATIVIDADE'; payload: any }
  | { type: 'UPDATE_REGIME_TRIBUTARIO'; payload: any }
  | { type: 'UPDATE_FAIXA_FATURAMENTO'; payload: any }
  | { type: 'SET_SERVICOS_SELECIONADOS'; payload: any[] }
  | { type: 'ADD_SERVICO'; payload: any }
  | { type: 'REMOVE_SERVICO'; payload: number }
  | { type: 'UPDATE_SERVICO'; payload: { index: number; servico: any } }
  | { type: 'SET_DESCONTO'; payload: number }
  | { type: 'SET_OBSERVACOES'; payload: string }
  | { type: 'RESET_PROPOSTA' }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null };

// Estado inicial
interface PropostaState {
  dadosProposta: DadosPropostaCompleta | null;
  percentualDesconto: number;
  observacoes: string;
  loading: boolean;
  error: string | null;
}

const initialState: PropostaState = {
  dadosProposta: null,
  percentualDesconto: 0,
  observacoes: '',
  loading: false,
  error: null
};

// Reducer
function propostaReducer(state: PropostaState, action: PropostaAction): PropostaState {
  switch (action.type) {
    case 'SET_DADOS_PROPOSTA':
      return {
        ...state,
        dadosProposta: action.payload,
        error: null
      };

    case 'UPDATE_CLIENTE':
      return {
        ...state,
        dadosProposta: state.dadosProposta ? {
          ...state.dadosProposta,
          cliente: action.payload
        } : null,
        error: null
      };

    case 'UPDATE_TIPO_ATIVIDADE':
      return {
        ...state,
        dadosProposta: state.dadosProposta ? {
          ...state.dadosProposta,
          tipoAtividade: action.payload
        } : null,
        error: null
      };

    case 'UPDATE_REGIME_TRIBUTARIO':
      return {
        ...state,
        dadosProposta: state.dadosProposta ? {
          ...state.dadosProposta,
          regimeTributario: action.payload
        } : null,
        error: null
      };

    case 'UPDATE_FAIXA_FATURAMENTO':
      return {
        ...state,
        dadosProposta: state.dadosProposta ? {
          ...state.dadosProposta,
          faixaFaturamento: action.payload
        } : null,
        error: null
      };

    case 'SET_SERVICOS_SELECIONADOS':
      return {
        ...state,
        dadosProposta: state.dadosProposta ? {
          ...state.dadosProposta,
          servicosSelecionados: action.payload
        } : null,
        error: null
      };

    case 'ADD_SERVICO':
      return {
        ...state,
        dadosProposta: state.dadosProposta ? {
          ...state.dadosProposta,
          servicosSelecionados: [...state.dadosProposta.servicosSelecionados, action.payload]
        } : null,
        error: null
      };

    case 'REMOVE_SERVICO':
      return {
        ...state,
        dadosProposta: state.dadosProposta ? {
          ...state.dadosProposta,
          servicosSelecionados: state.dadosProposta.servicosSelecionados.filter(
            (_, index) => index !== action.payload
          )
        } : null,
        error: null
      };

    case 'UPDATE_SERVICO':
      return {
        ...state,
        dadosProposta: state.dadosProposta ? {
          ...state.dadosProposta,
          servicosSelecionados: state.dadosProposta.servicosSelecionados.map(
            (servico, index) => index === action.payload.index ? action.payload.servico : servico
          )
        } : null,
        error: null
      };

    case 'SET_DESCONTO':
      return {
        ...state,
        percentualDesconto: action.payload,
        error: null
      };

    case 'SET_OBSERVACOES':
      return {
        ...state,
        observacoes: action.payload,
        error: null
      };

    case 'RESET_PROPOSTA':
      return initialState;

    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload
      };

    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        loading: false
      };

    default:
      return state;
  }
}

// Context
interface PropostaContextType {
  state: PropostaState;
  dispatch: React.Dispatch<PropostaAction>;
  // Actions helpers
  setDadosProposta: (dados: DadosPropostaCompleta) => void;
  updateCliente: (cliente: any) => void;
  updateTipoAtividade: (tipoAtividade: any) => void;
  updateRegimeTributario: (regimeTributario: any) => void;
  updateFaixaFaturamento: (faixaFaturamento: any) => void;
  setServicosSelecionados: (servicos: any[]) => void;
  addServico: (servico: any) => void;
  removeServico: (index: number) => void;
  updateServico: (index: number, servico: any) => void;
  setDesconto: (percentual: number) => void;
  setObservacoes: (observacoes: string) => void;
  resetProposta: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

const PropostaContext = createContext<PropostaContextType | undefined>(undefined);

// Provider
interface PropostaProviderProps {
  children: ReactNode;
}

export const PropostaProvider: React.FC<PropostaProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(propostaReducer, initialState);

  // Action helpers
  const setDadosProposta = (dados: DadosPropostaCompleta) => {
    dispatch({ type: 'SET_DADOS_PROPOSTA', payload: dados });
  };

  const updateCliente = (cliente: any) => {
    dispatch({ type: 'UPDATE_CLIENTE', payload: cliente });
  };

  const updateTipoAtividade = (tipoAtividade: any) => {
    dispatch({ type: 'UPDATE_TIPO_ATIVIDADE', payload: tipoAtividade });
  };

  const updateRegimeTributario = (regimeTributario: any) => {
    dispatch({ type: 'UPDATE_REGIME_TRIBUTARIO', payload: regimeTributario });
  };

  const updateFaixaFaturamento = (faixaFaturamento: any) => {
    dispatch({ type: 'UPDATE_FAIXA_FATURAMENTO', payload: faixaFaturamento });
  };

  const setServicosSelecionados = (servicos: any[]) => {
    dispatch({ type: 'SET_SERVICOS_SELECIONADOS', payload: servicos });
  };

  const addServico = (servico: any) => {
    dispatch({ type: 'ADD_SERVICO', payload: servico });
  };

  const removeServico = (index: number) => {
    dispatch({ type: 'REMOVE_SERVICO', payload: index });
  };

  const updateServico = (index: number, servico: any) => {
    dispatch({ type: 'UPDATE_SERVICO', payload: { index, servico } });
  };

  const setDesconto = (percentual: number) => {
    dispatch({ type: 'SET_DESCONTO', payload: percentual });
  };

  const setObservacoes = (observacoes: string) => {
    dispatch({ type: 'SET_OBSERVACOES', payload: observacoes });
  };

  const resetProposta = () => {
    dispatch({ type: 'RESET_PROPOSTA' });
  };

  const setLoading = (loading: boolean) => {
    dispatch({ type: 'SET_LOADING', payload: loading });
  };

  const setError = (error: string | null) => {
    dispatch({ type: 'SET_ERROR', payload: error });
  };

  const value: PropostaContextType = {
    state,
    dispatch,
    setDadosProposta,
    updateCliente,
    updateTipoAtividade,
    updateRegimeTributario,
    updateFaixaFaturamento,
    setServicosSelecionados,
    addServico,
    removeServico,
    updateServico,
    setDesconto,
    setObservacoes,
    resetProposta,
    setLoading,
    setError
  };

  return (
    <PropostaContext.Provider value={value}>
      {children}
    </PropostaContext.Provider>
  );
};

// Hook
export const usePropostaStore = () => {
  const context = useContext(PropostaContext);
  if (context === undefined) {
    throw new Error('usePropostaStore deve ser usado dentro de um PropostaProvider');
  }
  return context;
};
