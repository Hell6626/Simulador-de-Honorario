import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiService } from '../services/api';

interface User {
  id: number;
  nome: string;
  email: string;
  gerente: boolean;
  ativo: boolean;
  empresa_id: number;
  cargo_id?: number;
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  login: (email: string, senha: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const loadUserInfo = async () => {
    try {
      const userInfo = await apiService.getUserInfo();
      setUser(userInfo);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Erro ao carregar informações do usuário:', error);
      setIsAuthenticated(false);
      setUser(null);
    }
  };

  useEffect(() => {
    const token = apiService.getToken();
    if (token) {
      loadUserInfo();
    }
    setLoading(false);
  }, []);

  const login = async (email: string, senha: string): Promise<void> => {
    try {
      await apiService.login(email, senha);
      await loadUserInfo();
    } catch (error) {
      console.error('Erro no login:', error);
      throw error;
    }
  };

  const logout = () => {
    apiService.logout();
    setIsAuthenticated(false);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};