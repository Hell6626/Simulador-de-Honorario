import Cookies from 'js-cookie';

const BASE_URL = 'http://localhost:5000/api';
const TOKEN_KEY = 'propostas_token';

class ApiService {
  private getAuthHeaders() {
    const token = Cookies.get(TOKEN_KEY);
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${BASE_URL}${endpoint}`;
    const config: RequestInit = {
      headers: this.getAuthHeaders(),
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || error.error || 'Erro na requisição');
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }

      return response.text() as unknown as T;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Erro desconhecido');
    }
  }

  // Auth
  async login(email: string, senha: string) {
    const response = await this.request<{ token: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, senha }),
    });

    Cookies.set(TOKEN_KEY, response.token, { expires: 7 });
    return response;
  }

  async logout() {
    try {
      await this.request('/auth/logout', { method: 'POST' });
    } finally {
      Cookies.remove(TOKEN_KEY);
    }
  }

  getToken() {
    return Cookies.get(TOKEN_KEY);
  }

  // Health
  async healthCheck() {
    return this.request<{ status: string; message: string }>('/health/health');
  }

  // Funcionários
  async getFuncionarios(params?: {
    page?: number;
    per_page?: number;
    ativo?: boolean;
    search?: string;
  }) {
    const query = new URLSearchParams();
    if (params?.page) query.append('page', params.page.toString());
    if (params?.per_page) query.append('per_page', params.per_page.toString());
    if (params?.ativo !== undefined) query.append('ativo', params.ativo.toString());
    if (params?.search) query.append('search', params.search);

    return this.request<any>(`/funcionarios?${query}`);
  }

  async getFuncionario(id: number) {
    return this.request<any>(`/funcionarios/${id}`);
  }

  async createFuncionario(data: any) {
    return this.request<any>('/funcionarios', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateFuncionario(id: number, data: any) {
    return this.request<any>(`/funcionarios/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteFuncionario(id: number) {
    return this.request(`/funcionarios/${id}`, { method: 'DELETE' });
  }

  // Clientes
  async getClientes(params?: {
    page?: number;
    per_page?: number;
    ativo?: boolean;
    search?: string;
  }) {
    const query = new URLSearchParams();
    if (params?.page) query.append('page', params.page.toString());
    if (params?.per_page) query.append('per_page', params.per_page.toString());
    if (params?.ativo !== undefined) query.append('ativo', params.ativo.toString());
    if (params?.search) query.append('search', params.search);

    return this.request<any>(`/clientes?${query}`);
  }

  async getCliente(id: number) {
    return this.request<any>(`/clientes/${id}`);
  }

  async createCliente(data: any) {
    return this.request<any>('/clientes', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateCliente(id: number, data: any) {
    return this.request<any>(`/clientes/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteCliente(id: number) {
    return this.request(`/clientes/${id}`, { method: 'DELETE' });
  }

  // Tipos de Atividade
  async getTiposAtividade(params?: {
    ativo?: boolean;
    aplicavel_pf?: boolean;
    aplicavel_pj?: boolean;
    search?: string;
  }) {
    const query = new URLSearchParams();
    if (params?.ativo !== undefined) query.append('ativo', params.ativo.toString());
    if (params?.aplicavel_pf !== undefined) query.append('aplicavel_pf', params.aplicavel_pf.toString());
    if (params?.aplicavel_pj !== undefined) query.append('aplicavel_pj', params.aplicavel_pj.toString());
    if (params?.search) query.append('search', params.search);

    return this.request<any>(`/tipos-atividade?${query}`);
  }

  async getTipoAtividade(id: number) {
    return this.request<any>(`/tipos-atividade/${id}`);
  }

  async createTipoAtividade(data: any) {
    return this.request<any>('/tipos-atividade', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateTipoAtividade(id: number, data: any) {
    return this.request<any>(`/tipos-atividade/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteTipoAtividade(id: number) {
    return this.request(`/tipos-atividade/${id}`, { method: 'DELETE' });
  }

  // Regimes Tributários
  async getRegimesTributarios(params?: {
    ativo?: boolean;
    aplicavel_pf?: boolean;
    aplicavel_pj?: boolean;
    atividades_ids?: number[];
    search?: string;
  }) {
    const query = new URLSearchParams();
    if (params?.ativo !== undefined) query.append('ativo', params.ativo.toString());
    if (params?.aplicavel_pf !== undefined) query.append('aplicavel_pf', params.aplicavel_pf.toString());
    if (params?.aplicavel_pj !== undefined) query.append('aplicavel_pj', params.aplicavel_pj.toString());
    if (params?.atividades_ids) query.append('atividades_ids', params.atividades_ids.join(','));
    if (params?.search) query.append('search', params.search);

    return this.request<any>(`/regimes-tributarios?${query}`);
  }

  async getRegimeTributario(id: number) {
    return this.request<any>(`/regimes-tributarios/${id}`);
  }

  async createRegimeTributario(data: any) {
    return this.request<any>('/regimes-tributarios', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateRegimeTributario(id: number, data: any) {
    return this.request<any>(`/regimes-tributarios/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteRegimeTributario(id: number) {
    return this.request(`/regimes-tributarios/${id}`, { method: 'DELETE' });
  }

  // Faixas de Faturamento
  async getFaixasFaturamento(params?: { regime_tributario_id?: number }) {
    const query = new URLSearchParams();
    if (params?.regime_tributario_id) query.append('regime_tributario_id', params.regime_tributario_id.toString());

    return this.request<any>(`/faixas-faturamento?${query}`);
  }

  async getFaixaFaturamento(id: number) {
    return this.request<any>(`/faixas-faturamento/${id}`);
  }

  // Serviços
  async getServicos(params?: { categoria?: string }) {
    const query = new URLSearchParams();
    if (params?.categoria) query.append('categoria', params.categoria);

    return this.request<any>(`/servicos?${query}`);
  }

  async getServicosFiscais() {
    return this.request<any>('/servicos/fiscais');
  }

  async getServico(id: number) {
    return this.request<any>(`/servicos/${id}`);
  }

  // ⚠️ NOVO: Serviços filtrados por regime tributário
  async getServicosPorRegime(regimeId: number) {
    return this.request<any>(`/servicos/por-regime/${regimeId}`);
  }

  async getServicosParaProposta(tipoAtividadeId: number, regimeTributarioId: number) {
    return this.request<any>('/servicos/para-proposta', {
      method: 'POST',
      body: JSON.stringify({
        tipo_atividade_id: tipoAtividadeId,
        regime_tributario_id: regimeTributarioId
      }),
    });
  }

  // Propostas
  async getPropostas(params?: {
    page?: number;
    per_page?: number;
    status?: string;
    cliente_id?: number;
    funcionario_id?: number;
    search?: string;
  }) {
    const query = new URLSearchParams();
    if (params?.page) query.append('page', params.page.toString());
    if (params?.per_page) query.append('per_page', params.per_page.toString());
    if (params?.status) query.append('status', params.status);
    if (params?.cliente_id) query.append('cliente_id', params.cliente_id.toString());
    if (params?.funcionario_id) query.append('funcionario_id', params.funcionario_id.toString());
    if (params?.search) query.append('search', params.search);

    // Endpoint de propostas não requer autenticação
    const url = `${BASE_URL}/propostas?${query}`;
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || error.error || 'Erro na requisição');
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }

      return response.text() as unknown as any;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Erro desconhecido');
    }
  }

  async getProposta(id: number) {
    // Endpoint de proposta individual não requer autenticação
    const url = `${BASE_URL}/propostas/${id}`;
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || error.error || 'Erro na requisição');
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }

      return response.text() as unknown as any;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Erro desconhecido');
    }
  }

  async createProposta(data: any) {
    return this.request<any>('/propostas', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateProposta(id: number, data: any) {
    return this.request<any>(`/propostas/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteProposta(id: number) {
    return this.request(`/propostas/${id}`, { method: 'DELETE' });
  }

  async calcularServicosProposta(id: number) {
    return this.request<any>(`/propostas/${id}/calcular-servicos`, {
      method: 'POST',
    });
  }

  async finalizarProposta(id: number, data: any) {
    // Endpoint de finalização não requer autenticação
    const url = `${BASE_URL}/propostas/${id}/finalizar`;
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
      },
      method: 'POST',
      body: JSON.stringify(data),
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        let errorMessage = 'Erro na requisição';
        try {
          const errorData = await response.json();
          errorMessage = errorData.error || errorData.message || `Erro ${response.status}`;
        } catch {
          errorMessage = `Erro ${response.status}: ${response.statusText}`;
        }

        // Incluir código de status na mensagem de erro
        const error = new Error(`${response.status} - ${errorMessage}`);
        (error as any).status = response.status;
        throw error;
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }

      return response.text() as unknown as any;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Erro desconhecido');
    }
  }

  async getLogsPropostas(propostaId: number) {
    return this.request<any>(`/propostas/${propostaId}/logs`);
  }

  // Chat
  async sendChatMessage(message: string, sessionId: string = 'default') {
    return this.request<any>('/chat/send-message', {
      method: 'POST',
      body: JSON.stringify({ message, session_id: sessionId }),
    });
  }

  async getChatMessages(sessionId: string = 'default', limit: number = 50) {
    const query = new URLSearchParams();
    query.append('session_id', sessionId);
    query.append('limit', limit.toString());

    return this.request<any>(`/chat/messages?${query}`);
  }

  async getChatSessions() {
    return this.request<any>('/chat/sessions');
  }

  async clearChatSession(sessionId: string = 'default') {
    return this.request<any>('/chat/clear-session', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId }),
    });
  }
}

export const apiService = new ApiService();