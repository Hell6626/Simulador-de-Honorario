import React from 'react';
import {
  X, User, Mail, Hash, Calendar, MapPin, Building, Shield,
  Phone, Globe, Fingerprint, Home, FileText, CreditCard,
  UserCheck, TrendingUp, Briefcase
} from 'lucide-react';

interface ModalVisualizacaoProps {
  isOpen: boolean;
  onClose: () => void;
  data: any;
  type: 'cliente' | 'funcionario' | 'cargo';
}

export const ModalVisualizacao: React.FC<ModalVisualizacaoProps> = ({
  isOpen,
  onClose,
  data,
  type
}) => {
  if (!isOpen) return null;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Função para formatar CPF
  const formatCPF = (cpf: string) => {
    const numbers = cpf.replace(/\D/g, '');
    return numbers.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
  };

  // Função para formatar CNPJ
  const formatCNPJ = (cnpj: string) => {
    const numbers = cnpj.replace(/\D/g, '');
    return numbers.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
  };

  // Função genérica que detecta CPF ou CNPJ
  const formatCpfCnpj = (value: string) => {
    if (!value) return '-';
    const numbers = value.replace(/\D/g, '');

    if (numbers.length === 11) {
      return formatCPF(value);
    } else if (numbers.length === 14) {
      return formatCNPJ(value);
    }
    return value; // Retorna sem formatação se não for CPF nem CNPJ
  };

  // Mapeamento de ícones temáticos
  const getIconForField = (fieldType: string) => {
    const iconMap: { [key: string]: any } = {
      'cpf': Fingerprint, // Ícone de digital para CPF/CNPJ
      'cnpj': CreditCard, // Usando CreditCard como substituto para IdCard
      'nome': User,
      'email': Mail,
      'endereco': Home,
      'logradouro': MapPin,
      'cidade': Building,
      'estado': Globe,
      'cep': Hash,
      'empresa': Building,
      'telefone': Phone,
      'data': Calendar,
      'documento': CreditCard,
      'cargo': Briefcase,
      'tipo': Shield,
      'nivel': TrendingUp,
      'codigo': Hash
    };
    return iconMap[fieldType] || FileText;
  };

  const InfoCard = ({ icon: Icon, title, children, color = "blue" }: any) => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow duration-300">
      <div className={`bg-gradient-to-r from-${color}-50 to-${color}-100 px-6 py-4`}>
        <div className="flex items-center space-x-3">
          <div className={`p-2 bg-${color}-500 rounded-lg shadow-md`}>
            <Icon className="w-5 h-5 text-white" />
          </div>
          <h3 className={`text-lg font-semibold text-${color}-800`}>{title}</h3>
        </div>
      </div>
      <div className="p-6">
        {children}
      </div>
    </div>
  );

  const InfoField = ({ iconType, label, value, color = "gray" }: any) => {
    const IconComponent = getIconForField(iconType);

    return (
      <div className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors duration-200">
        <div className={`p-2 bg-${color}-100 rounded-lg`}>
          <IconComponent className={`w-4 h-4 text-${color}-600`} />
        </div>
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-500 mb-1">{label}</p>
          <p className="text-lg font-semibold text-gray-900">{value || '-'}</p>
        </div>
      </div>
    );
  };

  const StatusBadge = ({ active, label }: any) => (
    <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium shadow-sm ${active
      ? 'bg-green-100 text-green-800 border border-green-200'
      : 'bg-red-100 text-red-800 border border-red-200'
      }`}>
      <div className={`w-2 h-2 rounded-full mr-2 ${active ? 'bg-green-500' : 'bg-red-500'
        }`} />
      {label}
    </div>
  );

  const renderCliente = () => (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="bg-gray-50 rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto scrollbar-hide">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-8 py-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-white bg-opacity-20 rounded-xl">
                <User className="w-8 h-8 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">Detalhes do Cliente</h2>
                <p className="text-blue-100">ID: {data.id}</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <StatusBadge active={data.ativo} label={data.ativo ? 'Ativo' : 'Inativo'} />
              <button
                onClick={onClose}
                className="p-2 text-white hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors duration-200"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-8 space-y-6">
          {/* Informações Pessoais */}
          <InfoCard icon={User} title="Informações Pessoais" color="blue">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InfoField iconType="nome" label="Nome Completo" value={data.nome} color="blue" />
              <InfoField iconType="cpf" label="CPF" value={formatCpfCnpj(data.cpf)} color="green" />
              <InfoField iconType="email" label="E-mail" value={data.email} color="purple" />
              <InfoField
                iconType="data"
                label="Data de Cadastro"
                value={data.created_at ? formatDate(data.created_at) : '-'}
                color="orange"
              />
            </div>
          </InfoCard>

          {/* Configurações */}
          <InfoCard icon={Shield} title="Configurações" color="indigo">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-indigo-50 rounded-lg">
                <p className="text-sm font-medium text-indigo-600 mb-2">Tipo de Cliente</p>
                <div className={`inline-flex items-center px-3 py-2 rounded-full text-sm font-medium ${data.abertura_empresa
                  ? 'bg-purple-100 text-purple-800 border border-purple-200'
                  : 'bg-green-100 text-green-800 border border-green-200'
                  }`}>
                  {data.abertura_empresa ? 'Abertura de Empresa' : 'Cliente Existente'}
                </div>
              </div>
              <InfoField
                iconType="data"
                label="Última Atualização"
                value={data.updated_at ? formatDate(data.updated_at) : '-'}
                color="indigo"
              />
            </div>
          </InfoCard>

          {/* Endereço */}
          {data.enderecos && data.enderecos.length > 0 && (
            <InfoCard icon={Home} title="Endereço" color="emerald">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="md:col-span-2">
                  <InfoField
                    iconType="logradouro"
                    label="Logradouro"
                    value={`${data.enderecos[0].rua}, ${data.enderecos[0].numero}`}
                    color="emerald"
                  />
                </div>
                <InfoField
                  iconType="cep"
                  label="CEP"
                  value={data.enderecos[0].cep}
                  color="emerald"
                />
                <InfoField
                  iconType="cidade"
                  label="Cidade"
                  value={data.enderecos[0].cidade}
                  color="emerald"
                />
                <InfoField
                  iconType="estado"
                  label="Estado"
                  value={data.enderecos[0].estado}
                  color="emerald"
                />
              </div>
            </InfoCard>
          )}

          {/* Empresa */}
          {!data.abertura_empresa && data.entidades_juridicas && data.entidades_juridicas.length > 0 && (
            <InfoCard icon={Building} title="Empresa Vinculada" color="violet">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <InfoField
                  iconType="empresa"
                  label="Nome da Empresa"
                  value={data.entidades_juridicas[0].nome}
                  color="violet"
                />
                <InfoField
                  iconType="cnpj"
                  label="CNPJ"
                  value={formatCpfCnpj(data.entidades_juridicas[0].cnpj)}
                  color="violet"
                />
                <InfoField
                  iconType="tipo"
                  label="Tipo"
                  value={data.entidades_juridicas[0].tipo}
                  color="violet"
                />
              </div>
            </InfoCard>
          )}
        </div>

        {/* Footer */}
        <div className="px-8 py-6 bg-gray-100 rounded-b-2xl">
          <div className="flex justify-end">
            <button
              onClick={onClose}
              className="px-6 py-3 bg-gray-600 text-white font-medium rounded-lg hover:bg-gray-700 transition-colors duration-200 shadow-md"
            >
              Fechar
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderFuncionario = () => (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="bg-gray-50 rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto scrollbar-hide">
        {/* Header */}
        <div className="bg-gradient-to-r from-emerald-600 to-emerald-700 px-8 py-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-white bg-opacity-20 rounded-xl">
                <UserCheck className="w-8 h-8 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">Detalhes do Funcionário</h2>
                <p className="text-emerald-100">ID: {data.id}</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <StatusBadge active={data.ativo} label={data.ativo ? 'Ativo' : 'Inativo'} />
              <button
                onClick={onClose}
                className="p-2 text-white hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors duration-200"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-8 space-y-6">
          {/* Informações Profissionais */}
          <InfoCard icon={UserCheck} title="Informações Profissionais" color="emerald">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InfoField iconType="nome" label="Nome Completo" value={data.nome} color="emerald" />
              <InfoField iconType="email" label="E-mail" value={data.email} color="purple" />
              <InfoField iconType="cargo" label="Cargo" value={data.cargo?.nome} color="blue" />
              <InfoField
                iconType="data"
                label="Data de Cadastro"
                value={data.created_at ? formatDate(data.created_at) : '-'}
                color="orange"
              />
            </div>
          </InfoCard>

          {/* Permissões */}
          <InfoCard icon={Shield} title="Permissões" color="indigo">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-indigo-50 rounded-lg">
                <p className="text-sm font-medium text-indigo-600 mb-2">Nível de Acesso</p>
                <div className={`inline-flex items-center px-3 py-2 rounded-full text-sm font-medium ${data.gerente
                  ? 'bg-purple-100 text-purple-800 border border-purple-200'
                  : 'bg-blue-100 text-blue-800 border border-blue-200'
                  }`}>
                  {data.gerente ? 'Gerente' : 'Funcionário'}
                </div>
              </div>
              <InfoField
                iconType="empresa"
                label="Empresa"
                value={data.empresa?.nome}
                color="indigo"
              />
            </div>
          </InfoCard>

          {/* Status */}
          <InfoCard icon={Shield} title="Status" color="blue">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InfoField
                iconType="data"
                label="Última Atualização"
                value={data.updated_at ? formatDate(data.updated_at) : '-'}
                color="blue"
              />
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-sm font-medium text-blue-600 mb-2">Status Atual</p>
                <StatusBadge active={data.ativo} label={data.ativo ? 'Ativo' : 'Inativo'} />
              </div>
            </div>
          </InfoCard>
        </div>

        {/* Footer */}
        <div className="px-8 py-6 bg-gray-100 rounded-b-2xl">
          <div className="flex justify-end">
            <button
              onClick={onClose}
              className="px-6 py-3 bg-gray-600 text-white font-medium rounded-lg hover:bg-gray-700 transition-colors duration-200 shadow-md"
            >
              Fechar
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderCargo = () => (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="bg-gray-50 rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto scrollbar-hide">
        {/* Header */}
        <div className="bg-gradient-to-r from-violet-600 to-violet-700 px-8 py-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-white bg-opacity-20 rounded-xl">
                <Briefcase className="w-8 h-8 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">Detalhes do Cargo</h2>
                <p className="text-violet-100">ID: {data.id}</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <StatusBadge active={data.ativo} label={data.ativo ? 'Ativo' : 'Inativo'} />
              <button
                onClick={onClose}
                className="p-2 text-white hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors duration-200"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-8 space-y-6">
          {/* Identificação */}
          <InfoCard icon={Briefcase} title="Identificação" color="violet">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InfoField iconType="nome" label="Nome do Cargo" value={data.nome} color="violet" />
              <InfoField iconType="codigo" label="Código" value={data.codigo} color="green" />
              <InfoField
                iconType="data"
                label="Data de Cadastro"
                value={data.created_at ? formatDate(data.created_at) : '-'}
                color="orange"
              />
            </div>
          </InfoCard>

          {/* Hierarquia */}
          <InfoCard icon={TrendingUp} title="Hierarquia" color="blue">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-sm font-medium text-blue-600 mb-2">Nível do Cargo</p>
                <div className="inline-flex items-center px-3 py-2 rounded-full text-sm font-medium bg-blue-100 text-blue-800 border border-blue-200">
                  Nível {data.nivel || 'N/A'}
                </div>
              </div>
              <InfoField
                iconType="data"
                label="Última Atualização"
                value={data.updated_at ? formatDate(data.updated_at) : '-'}
                color="blue"
              />
            </div>
          </InfoCard>

          {/* Status */}
          <InfoCard icon={Shield} title="Status" color="indigo">
            <div className="p-4 bg-indigo-50 rounded-lg">
              <p className="text-sm font-medium text-indigo-600 mb-2">Status Atual</p>
              <StatusBadge active={data.ativo} label={data.ativo ? 'Ativo' : 'Inativo'} />
            </div>
          </InfoCard>
        </div>

        {/* Footer */}
        <div className="px-8 py-6 bg-gray-100 rounded-b-2xl">
          <div className="flex justify-end">
            <button
              onClick={onClose}
              className="px-6 py-3 bg-gray-600 text-white font-medium rounded-lg hover:bg-gray-700 transition-colors duration-200 shadow-md"
            >
              Fechar
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  // Renderizar baseado no tipo
  switch (type) {
    case 'cliente':
      return renderCliente();
    case 'funcionario':
      return renderFuncionario();
    case 'cargo':
      return renderCargo();
    default:
      return null;
  }
};
