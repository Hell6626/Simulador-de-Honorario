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

  async getUserInfo() {
    return this.request<any>('/auth/me');
  }

  async testAuth() {
    return this.request<any>('/auth/test');
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

  // Cargos
  async getCargos(params?: {
    page?: number;
    per_page?: number;
    ativo?: boolean;
    search?: string;
    empresa_id?: number;
  }) {
    const query = new URLSearchParams();
    if (params?.page) query.append('page', params.page.toString());
    if (params?.per_page) query.append('per_page', params.per_page.toString());
    if (params?.ativo !== undefined) query.append('ativo', params.ativo.toString());
    if (params?.search) query.append('search', params.search);
    if (params?.empresa_id) query.append('empresa_id', params.empresa_id.toString());

    return this.request<any>(`/cargos?${query}`);
  }

  async getCargo(id: number) {
    return this.request<any>(`/cargos/${id}`);
  }

  async createCargo(data: any) {
    return this.request<any>('/cargos', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async updateCargo(id: number, data: any) {
    return this.request<any>(`/cargos/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  async deleteCargo(id: number) {
    return this.request(`/cargos/${id}`, { method: 'DELETE' });
  }

  // Empresas
  async getEmpresas(params?: {
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

    return this.request<any>(`/empresas?${query}`);
  }

  async getEmpresa(id: number) {
    return this.request<any>(`/empresas/${id}`);
  }

  async createEmpresa(data: any) {
    return this.request<any>('/empresas', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async updateEmpresa(id: number, data: any) {
    return this.request<any>(`/empresas/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  async deleteEmpresa(id: number) {
    return this.request(`/empresas/${id}`, { method: 'DELETE' });
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
    if (params?.atividades_ids) {
      console.log('🔍 DEBUG API: Enviando atividades_ids:', params.atividades_ids);
      params.atividades_ids.forEach(id => query.append('atividades_ids', id.toString()));
    }
    if (params?.search) query.append('search', params.search);

    const url = `/regimes-tributarios?${query}`;
    console.log('🔍 DEBUG API: URL final:', url);
    console.log('🔍 DEBUG API: Query string:', query.toString());
    
    return this.request<any>(url);
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

  // Métodos para a página de Regimes Tributários (mesmo padrão de clientes)
  async getRegimes(params: { page?: number; per_page?: number; search?: string; ativo?: boolean }) {
    const query = new URLSearchParams();
    if (params?.page) query.append('page', String(params.page));
    if (params?.per_page) query.append('per_page', String(params.per_page));
    if (params?.search) query.append('search', params.search);
    if (params?.ativo !== undefined) query.append('ativo', String(params.ativo));
    return this.request<any>(`/regimes-tributarios?${query.toString()}`);
  }

  async getRegime(id: number) {
    return this.request<any>(`/regimes-tributarios/${id}`);
  }

  async createRegime(data: any) {
    return this.request<any>('/regimes-tributarios', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateRegime(id: number, data: any) {
    return this.request<any>(`/regimes-tributarios/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteRegime(id: number) {
    return this.request<any>(`/regimes-tributarios/${id}`, { method: 'DELETE' });
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
  async getServicos(params?: {
    categoria?: string;
    page?: number;
    per_page?: number;
    search?: string;
    ativo?: boolean;
  }) {
    const query = new URLSearchParams();
    if (params?.categoria) query.append('categoria', params.categoria);
    if (params?.page) query.append('page', params.page.toString());
    if (params?.per_page) query.append('per_page', params.per_page.toString());
    if (params?.search) query.append('search', params.search);
    if (params?.ativo !== undefined) query.append('ativo', params.ativo.toString());

    return this.request<any>(`/servicos?${query}`);
  }

  async getServicosFiscais() {
    return this.request<any>('/servicos/fiscais');
  }

  async getServico(id: number) {
    return this.request<any>(`/servicos/${id}`);
  }

  async createServico(data: any) {
    return this.request<any>('/servicos', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateServico(id: number, data: any) {
    return this.request<any>(`/servicos/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteServico(id: number) {
    return this.request(`/servicos/${id}`, { method: 'DELETE' });
  }

  async verificarImpactoExclusaoServico(id: number) {
    return this.request<any>(`/servicos/${id}/impacto-exclusao`);
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

  async getRegimesTributarios(tipoAtividadeId?: number) {
    if (tipoAtividadeId) {
      return this.request<any>(`/servicos/regimes-tributarios?tipo_atividade_id=${tipoAtividadeId}`);
    }
    return this.request<any>('/servicos/regimes-tributarios');
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

    // ⚠️ CORRIGIDO: Endpoint de propostas agora requer autenticação
    return this.request<any>(`/propostas?${query}`);
  }

  async getProposta(id: number) {
    // ⚠️ CORRIGIDO: Endpoint de proposta individual agora requer autenticação
    return this.request<any>(`/propostas/${id}`);
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

  async aprovarProposta(propostaId: number): Promise<{ message: string; proposta: Proposta }> {
    const response = await this.request<any>(`/propostas/${propostaId}/aprovar`, {
      method: 'POST',
    });
    return response;
  }

  async rejeitarProposta(propostaId: number, motivo: string): Promise<{ message: string; proposta: Proposta }> {
    const response = await this.request<any>(`/propostas/${propostaId}/rejeitar`, {
      method: 'POST',
      body: JSON.stringify({ motivo }),
    });
    return response;
  }

  // Notificações
  async getNotificacoes(params?: {
    page?: number;
    per_page?: number;
    lida?: boolean;
    tipo?: string;
  }): Promise<PaginatedResponse<Notificacao>> {
    const query = new URLSearchParams();
    if (params?.page) query.append('page', params.page.toString());
    if (params?.per_page) query.append('per_page', params.per_page.toString());
    if (params?.lida !== undefined) query.append('lida', params.lida.toString());
    if (params?.tipo) query.append('tipo', params.tipo);

    const response = await this.request<any>(`/notificacoes?${query}`);
    return response;
  }

  async marcarNotificacaoComoLida(notificacaoId: number): Promise<{ message: string; notificacao: Notificacao }> {
    const response = await this.request<any>(`/notificacoes/${notificacaoId}/ler`, {
      method: 'POST',
    });
    return response;
  }

  async marcarTodasNotificacoesComoLidas(): Promise<{ message: string }> {
    const response = await this.request<any>('/notificacoes/ler-todas', {
      method: 'POST',
    });
    return response;
  }

  async getContadorNotificacoes(): Promise<{ total_nao_lidas: number; aprovacao_nao_lidas: number }> {
    const response = await this.request<any>('/notificacoes/contador');
    return response;
  }

  async deleteNotificacao(notificacaoId: number): Promise<{ message: string }> {
    const response = await this.request<any>(`/notificacoes/${notificacaoId}`, {
      method: 'DELETE',
    });
    return response;
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

  // PDF Endpoints
  async gerarPDFProposta(propostaId: number) {
    return this.request<any>(`/propostas/${propostaId}/gerar-pdf`, {
      method: 'POST',
    });
  }

  async visualizarPDFProposta(propostaId: number) {
    const token = this.getToken();
    const url = `${BASE_URL}/propostas/${propostaId}/pdf`;

    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Erro ao visualizar PDF');
    }

    // Retornar blob para download
    const blob = await response.blob();
    return blob;
  }

  async excluirPDFProposta(propostaId: number) {
    return this.request<any>(`/propostas/${propostaId}/pdf`, {
      method: 'DELETE',
    });
  }
}

export const apiService = new ApiService();