import { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './contexts/ToastContext';
import { LoginPage } from './components/pages/LoginPage';
import { DashboardPage } from './components/pages/DashboardPage';
import { ClientesPage } from './components/pages/ClientesPage';
import { ChatPage } from './components/pages/ChatPage';
import { Sidebar } from './components/layout/Sidebar';
import { LoadingSpinner } from './components/common/LoadingSpinner';
import { PropostasPage } from './components/pages/PropostasPage';
import { AgendaPage } from './components/pages/AgendaPage';
import { usePropostaDataReset } from './hooks/usePropostaDataReset';

// Placeholder components for other pages
import { FuncionariosPage } from './components/pages/FuncionariosPage';
import { CargosPage } from './components/pages/CargosPage';
import { ServicosPage } from './components/pages/ServicosPage';
import { TiposAtividadePage } from './components/pages/TiposAtividadePage';

import { RegimesTributariosPage } from './components/pages/RegimesTributariosPage';



const RelatoriosPage = () => (
  <div className="space-y-6">
    <div className="mb-6">
      <h1 className="text-2xl font-bold text-gray-900">Relatórios</h1>
      <p className="text-sm text-gray-500">Visualize relatórios e análises do sistema</p>
    </div>
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
      <h2 className="text-xl font-bold mb-4">Relatórios</h2>
      <p>Página em desenvolvimento...</p>
    </div>
  </div>
);

const ConfiguracoesPage = () => (
  <div className="space-y-6">
    <div className="mb-6">
      <h1 className="text-2xl font-bold text-gray-900">Configurações</h1>
      <p className="text-sm text-gray-500">Configure parâmetros e preferências do sistema</p>
    </div>
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
      <h2 className="text-xl font-bold mb-4">Configurações</h2>
      <p>Página em desenvolvimento...</p>
    </div>
  </div>
);

const AppContent: React.FC = () => {
  const { isAuthenticated, loading } = useAuth();
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [navigationOptions, setNavigationOptions] = useState<{ openModal?: boolean; propostaId?: number }>({});

  // ✅ NOVO: Hook para reset automático de dados
  const { limparTodosDadosProposta, verificarDadosExistentes } = usePropostaDataReset();

  // ✅ CORREÇÃO: Reset automático quando navega para outras páginas (exceto propostas)
  // Movido para antes dos returns condicionais para evitar violação das Rules of Hooks
  useEffect(() => {
    // Só executa se estiver autenticado e não estiver carregando
    if (isAuthenticated && !loading && currentPage !== 'propostas') {
      console.log(`🔄 [App] Navegou para ${currentPage} - verificando dados salvos...`);

      const temDadosSalvos = verificarDadosExistentes();
      if (temDadosSalvos) {
        console.log('🧹 [App] Dados encontrados - iniciando limpeza automática...');
        const itensRemovidos = limparTodosDadosProposta();

        if (itensRemovidos > 0) {
          console.log(`✅ [App] Reset automático concluído! ${itensRemovidos} itens removidos.`);
        } else {
          console.log('ℹ️ [App] Nenhum dado para limpar.');
        }
      } else {
        console.log('ℹ️ [App] Nenhum dado salvo encontrado.');
      }
    }
  }, [currentPage, limparTodosDadosProposta, verificarDadosExistentes, isAuthenticated, loading]);

  // ✅ CORREÇÃO: Returns condicionais após todos os hooks
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <LoadingSpinner />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  const handleNavigate = (page: string, options?: { openModal?: boolean }) => {
    // ✅ NOVO: Limpeza automática quando navega para outras páginas (exceto propostas)
    if (page !== 'propostas') {
      setNavigationOptions({});
    }

    setCurrentPage(page);
    setNavigationOptions(options || {});

    // ✅ CORREÇÃO: Limpar as opções após um delay maior para garantir que modal abra corretamente
    setTimeout(() => {
      setNavigationOptions({});
    }, 500); // Aumentado de 100ms para 500ms
  };

  const handleNavigateToProposta = (propostaId: number) => {
    setCurrentPage('propostas');
    setNavigationOptions({ propostaId });

    // ✅ NOVO: Limpeza automática após navegação para proposta
    setTimeout(() => {
      setNavigationOptions({});
    }, 1000); // Delay maior para garantir que modal abra
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <DashboardPage onNavigate={handleNavigate} />;
      case 'propostas':
        return <PropostasPage openModalOnLoad={navigationOptions.openModal} propostaId={navigationOptions.propostaId} />;
      case 'clientes':
        return <ClientesPage openModalOnLoad={navigationOptions.openModal} />;
      case 'funcionarios':
        return <FuncionariosPage openModalOnLoad={navigationOptions.openModal} />;
      case 'cargos':
        return <CargosPage openModalOnLoad={navigationOptions.openModal} />;
      case 'tipos-atividade':
        return <TiposAtividadePage />;
      case 'regimes-tributarios':
        return <RegimesTributariosPage />;
      case 'servicos':
        return <ServicosPage />;
      case 'relatorios':
        return <RelatoriosPage />;
      case 'agenda':
        return <AgendaPage />;
      case 'chat':
        return <ChatPage />;
      case 'configuracoes':
        return <ConfiguracoesPage />;
      default:
        return <DashboardPage onNavigate={handleNavigate} />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        onNavigateToProposta={handleNavigateToProposta}
      />

      <main className="flex-1 overflow-hidden">
        <div className="h-full overflow-y-auto p-6 relative">
          {renderPage()}
        </div>
      </main>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <AppContent />
      </ToastProvider>
    </AuthProvider>
  );
}

export default App;
