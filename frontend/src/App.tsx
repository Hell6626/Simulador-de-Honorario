import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LoginPage } from './components/pages/LoginPage';
import { DashboardPage } from './components/pages/DashboardPage';
import { ClientesPage } from './components/pages/ClientesPage';
import { ChatPage } from './components/pages/ChatPage';
import { Sidebar } from './components/layout/Sidebar';
import { LoadingSpinner } from './components/common/LoadingSpinner';
import { PropostasPage } from './components/pages/PropostasPage';
import { AgendaPage } from './components/pages/AgendaPage';

// Placeholder components for other pages
import { FuncionariosPage } from './components/pages/FuncionariosPage';
import { CargosPage } from './components/pages/CargosPage';
import { ServicosPage } from './components/pages/ServicosPage';

const TiposAtividadePage = () => (
  <div className="space-y-6">
    <div className="mb-6">
      <h1 className="text-2xl font-bold text-gray-900">Tipos de Atividade</h1>
      <p className="text-sm text-gray-500">Configure os tipos de atividade contábil disponíveis</p>
    </div>
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
      <h2 className="text-xl font-bold mb-4">Tipos de Atividade</h2>
      <p>Página em desenvolvimento...</p>
    </div>
  </div>
);

const RegimesTributariosPage = () => (
  <div className="space-y-6">
    <div className="mb-6">
      <h1 className="text-2xl font-bold text-gray-900">Regimes Tributários</h1>
      <p className="text-sm text-gray-500">Gerencie os regimes tributários e suas configurações</p>
    </div>
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
      <h2 className="text-xl font-bold mb-4">Regimes Tributários</h2>
      <p>Página em desenvolvimento...</p>
    </div>
  </div>
);



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
    setCurrentPage(page);
    setNavigationOptions(options || {});

    // Limpar as opções após um breve delay para evitar que o modal abra novamente
    setTimeout(() => {
      setNavigationOptions({});
    }, 100);
  };

  const handleNavigateToProposta = (propostaId: number) => {
    setCurrentPage('propostas');
    setNavigationOptions({ propostaId });
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
        <div className="h-full overflow-y-auto p-6">
          {renderPage()}
        </div>
      </main>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;