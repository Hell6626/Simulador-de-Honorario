import { createContext, useContext, useReducer, ReactNode } from 'react';
import { DadosPropostaCompleta, PropostaComDesconto } from '../types/propostas';

// Tipos de ações
type PropostaAction =
  | { type: 'SET_DADOS_PROPOSTA'; payload: DadosPropostaCompleta }
  | { type: 'UPDATE_CLIENTE'; payload: any }
  | { type: 'UPDATE_TIPO_ATIVIDADE'; payload: any }
  | { type: 'UPDATE_REGIME_TRIBUTARIO'; payload: any }
  | { type: 'UPDATE_FAIXA_FATURAMENTO'; payload: any }
  | { type: 'UPDATE_SERVICOS'; payload: any[] }
  | { type: 'UPDATE_DESCONTO'; payload: { tipo: string; valor: number } }
  | { type: 'UPDATE_OBSERVACOES'; payload: string }
  | { type: 'RESET_PROPOSTA' }
  | { type: 'LOAD_PROPOSTA'; payload: DadosPropostaCompleta };

// Estado inicial
const initialState: DadosPropostaCompleta = {
  cliente: null,
  tipo_atividade: null,
  regime_tributario: null,
  faixa_faturamento: null,
  servicos: [],
  desconto: { tipo: 'percentual', valor: 0 },
  observacoes: '',
  valor_total: 0,
  valor_com_desconto: 0,
  valor_mensalidade: 0,
};

// Reducer
const propostaReducer = (state: DadosPropostaCompleta, action: PropostaAction): DadosPropostaCompleta => {
  switch (action.type) {
    case 'SET_DADOS_PROPOSTA':
      return action.payload;

    case 'UPDATE_CLIENTE':
      return { ...state, cliente: action.payload };

    case 'UPDATE_TIPO_ATIVIDADE':
      return { ...state, tipo_atividade: action.payload };

    case 'UPDATE_REGIME_TRIBUTARIO':
      return { ...state, regime_tributario: action.payload };

    case 'UPDATE_FAIXA_FATURAMENTO':
      return { ...state, faixa_faturamento: action.payload };

    case 'UPDATE_SERVICOS':
      return { ...state, servicos: action.payload };

    case 'UPDATE_DESCONTO':
      return { ...state, desconto: action.payload };

    case 'UPDATE_OBSERVACOES':
      return { ...state, observacoes: action.payload };

    case 'RESET_PROPOSTA':
      return initialState;

    case 'LOAD_PROPOSTA':
      return action.payload;

    default:
      return state;
  }
};

// Context
const PropostaContext = createContext<{
  state: DadosPropostaCompleta;
  dispatch: React.Dispatch<PropostaAction>;
} | undefined>(undefined);

// Provider
export const PropostaProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(propostaReducer, initialState);

  return (
    <PropostaContext.Provider value={{ state, dispatch }}>
      {children}
    </PropostaContext.Provider>
  );
};

// Hook
export const useProposta = () => {
  const context = useContext(PropostaContext);
  if (context === undefined) {
    throw new Error('useProposta must be used within a PropostaProvider');
  }
  return context;
};
