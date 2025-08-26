import React, { useState, useEffect } from 'react';
import { X, User, MapPin, Building, Check, AlertCircle } from 'lucide-react';
import { apiService } from '../../../services/api';
import { Cliente } from '../../../types';

interface ClienteForm {
  nome: string;
  cpf: string;
  email?: string;
  abertura_empresa: boolean;
}

interface EnderecoForm {
  rua: string;
  numero: string;
  cidade: string;
  estado: string;
  cep: string;
}

interface EntidadeJuridicaForm {
  nome: string;
  cnpj: string;
  tipo: string;
}

interface ClienteCompleto {
  cliente: ClienteForm;
  endereco: EnderecoForm | null;
  empresa: EntidadeJuridicaForm | null;
}

interface FormErrors {
  cliente?: Partial<ClienteForm>;
  endereco?: Partial<EnderecoForm>;
  empresa?: Partial<EntidadeJuridicaForm>;
}



interface ModalCadastroClienteProps {
  isOpen: boolean;
  onClose: () => void;
  onClienteCadastrado: (cliente: Cliente) => void;
  clienteParaEditar?: Cliente | null;
}

const ESTADOS_BRASIL = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
  'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
  'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
];

const TIPOS_EMPRESA = ['LTDA', 'ME', 'EIRELI', 'S/A', 'EPP', 'OSCIP', 'ONG'];

// Funções de validação
const validarCPF = (cpf: string): boolean => {
  const cpfLimpo = cpf.replace(/\D/g, '');
  if (cpfLimpo.length !== 11) return false;

  // Verifica se todos os dígitos são iguais
  if (/^(\d)\1{10}$/.test(cpfLimpo)) return false;

  // Validação do primeiro dígito verificador
  let soma = 0;
  for (let i = 0; i < 9; i++) {
    soma += parseInt(cpfLimpo.charAt(i)) * (10 - i);
  }
  let resto = 11 - (soma % 11);
  if (resto === 10 || resto === 11) resto = 0;
  if (resto !== parseInt(cpfLimpo.charAt(9))) return false;

  // Validação do segundo dígito verificador
  soma = 0;
  for (let i = 0; i < 10; i++) {
    soma += parseInt(cpfLimpo.charAt(i)) * (11 - i);
  }
  resto = 11 - (soma % 11);
  if (resto === 10 || resto === 11) resto = 0;
  if (resto !== parseInt(cpfLimpo.charAt(10))) return false;

  return true;
};

const validarCNPJ = (cnpj: string): boolean => {
  const cnpjLimpo = cnpj.replace(/\D/g, '');
  if (cnpjLimpo.length !== 14) return false;

  // Verifica se todos os dígitos são iguais
  if (/^(\d)\1{13}$/.test(cnpjLimpo)) return false;

  // Validação do primeiro dígito verificador
  let soma = 0;
  let peso = 2;
  for (let i = 11; i >= 0; i--) {
    soma += parseInt(cnpjLimpo.charAt(i)) * peso;
    peso = peso === 9 ? 2 : peso + 1;
  }
  let resto = soma % 11;
  let digito1 = resto < 2 ? 0 : 11 - resto;
  if (parseInt(cnpjLimpo.charAt(12)) !== digito1) return false;

  // Validação do segundo dígito verificador
  soma = 0;
  peso = 2;
  for (let i = 12; i >= 0; i--) {
    soma += parseInt(cnpjLimpo.charAt(i)) * peso;
    peso = peso === 9 ? 2 : peso + 1;
  }
  resto = soma % 11;
  let digito2 = resto < 2 ? 0 : 11 - resto;
  if (parseInt(cnpjLimpo.charAt(13)) !== digito2) return false;

  return true;
};

const validarEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Funções de máscara
const aplicarMascaraCPF = (valor: string): string => {
  const cpfLimpo = valor.replace(/\D/g, '');
  return cpfLimpo.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
};

const aplicarMascaraCNPJ = (valor: string): string => {
  const cnpjLimpo = valor.replace(/\D/g, '');
  return cnpjLimpo.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
};

const aplicarMascaraCEP = (valor: string): string => {
  const cepLimpo = valor.replace(/\D/g, '');
  return cepLimpo.replace(/(\d{5})(\d{3})/, '$1-$2');
};

export const ModalCadastroCliente: React.FC<ModalCadastroClienteProps> = ({
  isOpen,
  onClose,
  onClienteCadastrado,
  clienteParaEditar
}) => {
  const [abaAtiva, setAbaAtiva] = useState(0); // 0: Cliente, 1: Endereço, 2: Empresa
  const [formData, setFormData] = useState<ClienteCompleto>({
    cliente: { nome: '', cpf: '', email: '', abertura_empresa: false },
    endereco: null,
    empresa: null
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});

  // Resetar formulário quando modal fechar
  useEffect(() => {
    if (!isOpen) {
      setFormData({
        cliente: { nome: '', cpf: '', email: '', abertura_empresa: false },
        endereco: null,
        empresa: null
      });
      setErrors({});
      setAbaAtiva(0);
    }
  }, [isOpen]);

  // Carregar dados do cliente para edição
  useEffect(() => {
    if (clienteParaEditar && isOpen) {
      // Buscar dados completos do cliente se necessário
      const carregarDadosCompletos = async () => {
        try {
          console.log('Carregando dados completos do cliente ID:', clienteParaEditar.id);
          const clienteCompleto = await apiService.getCliente(clienteParaEditar.id);
          console.log('Dados completos carregados:', clienteCompleto);

          const formDataToSet = {
            cliente: {
              nome: clienteCompleto.nome,
              cpf: aplicarMascaraCPF(clienteCompleto.cpf),
              email: clienteCompleto.email || '',
              abertura_empresa: clienteCompleto.abertura_empresa
            },
            endereco: clienteCompleto.enderecos && clienteCompleto.enderecos.length > 0 ? {
              rua: clienteCompleto.enderecos[0].rua,
              numero: clienteCompleto.enderecos[0].numero,
              cidade: clienteCompleto.enderecos[0].cidade,
              estado: clienteCompleto.enderecos[0].estado,
              cep: aplicarMascaraCEP(clienteCompleto.enderecos[0].cep)
            } : null,
            empresa: clienteCompleto.entidades_juridicas && clienteCompleto.entidades_juridicas.length > 0 ? {
              nome: clienteCompleto.entidades_juridicas[0].nome,
              cnpj: aplicarMascaraCNPJ(clienteCompleto.entidades_juridicas[0].cnpj),
              tipo: clienteCompleto.entidades_juridicas[0].tipo
            } : null
          };

          console.log('FormData a ser definido:', formDataToSet);
          setFormData(formDataToSet);
        } catch (error) {
          console.error('Erro ao carregar dados completos do cliente:', error);
          // Fallback para dados básicos
          const fallbackData = {
            cliente: {
              nome: clienteParaEditar.nome,
              cpf: aplicarMascaraCPF(clienteParaEditar.cpf),
              email: clienteParaEditar.email || '',
              abertura_empresa: clienteParaEditar.abertura_empresa
            },
            endereco: null,
            empresa: null
          };
          console.log('Usando dados fallback:', fallbackData);
          setFormData(fallbackData);
        }
      };

      carregarDadosCompletos();
    } else if (isOpen) {
      // Reset form para novo cliente
      setFormData({
        cliente: { nome: '', cpf: '', email: '', abertura_empresa: false },
        endereco: null,
        empresa: null
      });
    }
  }, [clienteParaEditar, isOpen]);


  // Validações
  const validacoes = {
    cliente: {
      nome: (valor: string) => valor.trim().length >= 3,
      cpf: (valor: string) => validarCPF(valor.replace(/\D/g, '')),
      email: (valor: string) => !valor || validarEmail(valor)
    },
    endereco: {
      rua: (valor: string) => valor.trim().length >= 3,
      numero: (valor: string) => valor.trim().length >= 1,
      cidade: (valor: string) => valor.trim().length >= 2,
      estado: (valor: string) => valor.length === 2,
      cep: (valor: string) => /^\d{5}-?\d{3}$/.test(valor.replace(/\D/g, ''))
    },
    empresa: {
      nome: (valor: string) => valor.trim().length >= 3,
      cnpj: (valor: string) => validarCNPJ(valor.replace(/\D/g, '')),
      tipo: (valor: string) => TIPOS_EMPRESA.includes(valor)
    }
  };

  const validarFormulario = (): boolean => {
    const novosErrors: FormErrors = {};

    // Validar dados do cliente (sempre obrigatórios)
    if (!validacoes.cliente.nome(formData.cliente.nome)) {
      novosErrors.cliente = { ...novosErrors.cliente, nome: 'Nome deve ter pelo menos 3 caracteres' };
    }
    if (!validacoes.cliente.cpf(formData.cliente.cpf)) {
      novosErrors.cliente = { ...novosErrors.cliente, cpf: 'CPF inválido' };
    }
    if (formData.cliente.email && !validacoes.cliente.email(formData.cliente.email)) {
      novosErrors.cliente = { ...novosErrors.cliente, email: 'E-mail inválido' };
    }

    // Validar endereço se pelo menos um campo estiver preenchido
    if (formData.endereco && (
      formData.endereco.rua ||
      formData.endereco.numero ||
      formData.endereco.cidade ||
      formData.endereco.estado ||
      formData.endereco.cep
    )) {
      if (!validacoes.endereco.rua(formData.endereco.rua)) {
        novosErrors.endereco = { ...novosErrors.endereco, rua: 'Rua deve ter pelo menos 3 caracteres' };
      }
      if (!validacoes.endereco.numero(formData.endereco.numero)) {
        novosErrors.endereco = { ...novosErrors.endereco, numero: 'Número é obrigatório' };
      }
      if (!validacoes.endereco.cidade(formData.endereco.cidade)) {
        novosErrors.endereco = { ...novosErrors.endereco, cidade: 'Cidade deve ter pelo menos 2 caracteres' };
      }
      if (!validacoes.endereco.estado(formData.endereco.estado)) {
        novosErrors.endereco = { ...novosErrors.endereco, estado: 'Estado deve ter 2 caracteres' };
      }
      if (!validacoes.endereco.cep(formData.endereco.cep)) {
        novosErrors.endereco = { ...novosErrors.endereco, cep: 'CEP inválido' };
      }
    }

    // Validar empresa se pelo menos um campo estiver preenchido
    if (formData.empresa && (
      formData.empresa.nome ||
      formData.empresa.cnpj ||
      formData.empresa.tipo
    )) {
      // Só validar se o campo estiver preenchido
      if (formData.empresa.nome && !validacoes.empresa.nome(formData.empresa.nome)) {
        novosErrors.empresa = { ...novosErrors.empresa, nome: 'Nome da empresa deve ter pelo menos 3 caracteres' };
      }
      if (formData.empresa.cnpj && !validacoes.empresa.cnpj(formData.empresa.cnpj)) {
        novosErrors.empresa = { ...novosErrors.empresa, cnpj: 'CNPJ inválido' };
      }
      if (formData.empresa.tipo && !validacoes.empresa.tipo(formData.empresa.tipo)) {
        novosErrors.empresa = { ...novosErrors.empresa, tipo: 'Tipo de empresa inválido' };
      }
    }

    setErrors(novosErrors);
    return Object.keys(novosErrors).length === 0;
  };

  const handleInputChange = (secao: keyof ClienteCompleto, campo: string, valor: string | boolean) => {
    setFormData(prev => {
      if (secao === 'endereco' && !prev.endereco) {
        return {
          ...prev,
          endereco: { rua: '', numero: '', cidade: '', estado: '', cep: '', [campo]: valor }
        };
      }
      if (secao === 'empresa' && !prev.empresa) {
        return {
          ...prev,
          empresa: { nome: '', cnpj: '', tipo: '', [campo]: valor }
        };
      }
      return {
        ...prev,
        [secao]: {
          ...prev[secao],
          [campo]: valor
        }
      };
    });

    // Limpar erro do campo quando usuário começar a digitar
    if (errors[secao] && (errors[secao] as any)[campo]) {
      setErrors(prev => ({
        ...prev,
        [secao]: {
          ...prev[secao],
          [campo]: undefined
        }
      }));
    }
  };

  const handleSalvar = async () => {
    if (!validarFormulario()) {
      return;
    }

    setLoading(true);
    try {
      const dadosParaEnviar = {
        nome: formData.cliente.nome,
        cpf: formData.cliente.cpf.replace(/\D/g, ''),
        email: formData.cliente.email || null,
        abertura_empresa: formData.cliente.abertura_empresa,
        endereco: formData.endereco && formData.endereco.rua ? {
          rua: formData.endereco.rua,
          numero: formData.endereco.numero,
          cidade: formData.endereco.cidade,
          estado: formData.endereco.estado,
          cep: formData.endereco.cep.replace(/\D/g, '')
        } : null,
        entidade_juridica: !formData.cliente.abertura_empresa && formData.empresa && (formData.empresa.nome || formData.empresa.cnpj || formData.empresa.tipo) ? {
          nome: formData.empresa.nome || '',
          cnpj: formData.empresa.cnpj ? formData.empresa.cnpj.replace(/\D/g, '') : '',
          tipo: formData.empresa.tipo || ''
        } : null
      };

      console.log('Dados para enviar:', dadosParaEnviar);
      console.log('Cliente para editar:', clienteParaEditar);

      let response: Cliente;

      if (clienteParaEditar) {
        // Atualizar cliente existente
        console.log('Atualizando cliente ID:', clienteParaEditar.id);
        response = await apiService.updateCliente(clienteParaEditar.id, dadosParaEnviar);
      } else {
        // Criar novo cliente
        console.log('Criando novo cliente');
        response = await apiService.createCliente(dadosParaEnviar);
      }

      console.log('Resposta do servidor:', response);
      onClienteCadastrado(response);
      onClose();
    } catch (error: any) {
      console.error('Erro ao salvar cliente:', error);
      console.error('Detalhes do erro:', {
        message: error.message,
        stack: error.stack,
        name: error.name
      });

      // Mostrar mensagem de erro mais específica
      const mensagemErro = error.message || 'Erro desconhecido';
      alert(`Erro ao ${clienteParaEditar ? 'atualizar' : 'cadastrar'} cliente: ${mensagemErro}`);
    } finally {
      setLoading(false);
    }
  };

  const podeIrParaEmpresa = !formData.cliente.abertura_empresa; // Aba empresa só disponível se não for abertura de empresa

  const podeSalvar = (): boolean => {
    // Dados do cliente sempre obrigatórios
    if (!formData.cliente.nome.trim() || !formData.cliente.cpf.trim()) {
      return false;
    }

    // Se endereço estiver parcialmente preenchido, deve estar completo
    if (formData.endereco && (
      formData.endereco.rua ||
      formData.endereco.numero ||
      formData.endereco.cidade ||
      formData.endereco.estado ||
      formData.endereco.cep
    )) {
      if (!formData.endereco.rua || !formData.endereco.numero || !formData.endereco.cidade || !formData.endereco.estado || !formData.endereco.cep) {
        return false;
      }
    }

    // Se empresa estiver parcialmente preenchida, deve estar completa
    if (formData.empresa && (
      formData.empresa.nome ||
      formData.empresa.cnpj ||
      formData.empresa.tipo
    )) {
      if (!formData.empresa.nome || !formData.empresa.cnpj || !formData.empresa.tipo) {
        return false;
      }
    }

    return true;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[9999] overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <div
          className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75"
          onClick={onClose}
        />

        <div className="inline-block w-full max-w-2xl p-0 my-8 text-left align-middle transition-all transform bg-white shadow-xl rounded-lg max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                {clienteParaEditar ? 'Editar Cliente' : 'Cadastrar Novo Cliente'}
              </h2>
              <p className="text-sm text-gray-500">
                {clienteParaEditar ? 'Atualize os dados do cliente' : 'Preencha os dados do novo cliente'}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Abas */}
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setAbaAtiva(0)}
              className={`flex items-center space-x-2 px-6 py-3 text-sm font-medium transition-colors ${abaAtiva === 0
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
                }`}
            >
              <User className="w-4 h-4" />
              <span>Dados do Cliente</span>
            </button>
            <button
              onClick={() => setAbaAtiva(1)}
              className={`flex items-center space-x-2 px-6 py-3 text-sm font-medium transition-colors ${abaAtiva === 1
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
                }`}
            >
              <MapPin className="w-4 h-4" />
              <span>Endereço</span>
            </button>
            <button
              onClick={() => setAbaAtiva(2)}
              disabled={!podeIrParaEmpresa}
              className={`flex items-center space-x-2 px-6 py-3 text-sm font-medium transition-colors ${!podeIrParaEmpresa
                  ? 'text-gray-400 cursor-not-allowed'
                  : abaAtiva === 2
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
            >
              <Building className="w-4 h-4" />
              <span>Empresa</span>
            </button>
          </div>

          {/* Conteúdo das Abas */}
          <div className="p-6">
            {/* Aba Dados do Cliente */}
            {abaAtiva === 0 && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nome Completo <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.cliente.nome}
                    onChange={(e) => handleInputChange('cliente', 'nome', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.cliente?.nome ? 'border-red-500' : 'border-gray-300'
                      }`}
                    placeholder="Digite o nome completo"
                  />
                  {errors.cliente?.nome && (
                    <p className="mt-1 text-sm text-red-600 flex items-center">
                      <AlertCircle className="w-4 h-4 mr-1" />
                      {errors.cliente.nome}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    CPF <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.cliente.cpf}
                    onChange={(e) => {
                      const valor = e.target.value;
                      const mascara = aplicarMascaraCPF(valor);
                      if (mascara.length <= 14) {
                        handleInputChange('cliente', 'cpf', mascara);
                      }
                    }}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.cliente?.cpf ? 'border-red-500' : 'border-gray-300'
                      }`}
                    placeholder="000.000.000-00"
                    maxLength={14}
                  />
                  {errors.cliente?.cpf && (
                    <p className="mt-1 text-sm text-red-600 flex items-center">
                      <AlertCircle className="w-4 h-4 mr-1" />
                      {errors.cliente.cpf}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    E-mail
                  </label>
                  <input
                    type="email"
                    value={formData.cliente.email || ''}
                    onChange={(e) => handleInputChange('cliente', 'email', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.cliente?.email ? 'border-red-500' : 'border-gray-300'
                      }`}
                    placeholder="exemplo@email.com"
                  />
                  {errors.cliente?.email && (
                    <p className="mt-1 text-sm text-red-600 flex items-center">
                      <AlertCircle className="w-4 h-4 mr-1" />
                      {errors.cliente.email}
                    </p>
                  )}
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="abertura_empresa"
                    checked={formData.cliente.abertura_empresa}
                    onChange={(e) => {
                      const isAberturaEmpresa = e.target.checked;
                      handleInputChange('cliente', 'abertura_empresa', isAberturaEmpresa);

                      // Se marcar como abertura de empresa, limpar dados de empresa
                      if (isAberturaEmpresa) {
                        setFormData(prev => ({
                          ...prev,
                          empresa: null
                        }));
                        // Voltar para a primeira aba se estiver na aba empresa
                        if (abaAtiva === 2 as number) {
                          setAbaAtiva(0);
                        }
                      }
                    }}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="abertura_empresa" className="ml-2 text-sm text-gray-700">
                    Este cliente é para abertura de empresa
                  </label>
                </div>
              </div>
            )}

            {/* Aba Endereço */}
            {abaAtiva === 1 && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Rua <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.endereco?.rua || ''}
                      onChange={(e) => {
                        handleInputChange('endereco', 'rua', e.target.value);
                      }}
                      className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.endereco?.rua ? 'border-red-500' : 'border-gray-300'
                        }`}
                      placeholder="Nome da rua"
                    />
                    {errors.endereco?.rua && (
                      <p className="mt-1 text-sm text-red-600 flex items-center">
                        <AlertCircle className="w-4 h-4 mr-1" />
                        {errors.endereco.rua}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Número <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.endereco?.numero || ''}
                      onChange={(e) => {
                        handleInputChange('endereco', 'numero', e.target.value);
                      }}
                      className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.endereco?.numero ? 'border-red-500' : 'border-gray-300'
                        }`}
                      placeholder="123"
                    />
                    {errors.endereco?.numero && (
                      <p className="mt-1 text-sm text-red-600 flex items-center">
                        <AlertCircle className="w-4 h-4 mr-1" />
                        {errors.endereco.numero}
                      </p>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Cidade <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.endereco?.cidade || ''}
                      onChange={(e) => {
                        handleInputChange('endereco', 'cidade', e.target.value);
                      }}
                      className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.endereco?.cidade ? 'border-red-500' : 'border-gray-300'
                        }`}
                      placeholder="Nome da cidade"
                    />
                    {errors.endereco?.cidade && (
                      <p className="mt-1 text-sm text-red-600 flex items-center">
                        <AlertCircle className="w-4 h-4 mr-1" />
                        {errors.endereco.cidade}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Estado <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={formData.endereco?.estado || ''}
                      onChange={(e) => {
                        handleInputChange('endereco', 'estado', e.target.value);
                      }}
                      className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.endereco?.estado ? 'border-red-500' : 'border-gray-300'
                        }`}
                    >
                      <option value="">Selecione o estado</option>
                      {ESTADOS_BRASIL.map(estado => (
                        <option key={estado} value={estado}>{estado}</option>
                      ))}
                    </select>
                    {errors.endereco?.estado && (
                      <p className="mt-1 text-sm text-red-600 flex items-center">
                        <AlertCircle className="w-4 h-4 mr-1" />
                        {errors.endereco.estado}
                      </p>
                    )}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    CEP <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.endereco?.cep || ''}
                    onChange={(e) => {
                      const valor = e.target.value;
                      const mascara = aplicarMascaraCEP(valor);
                      if (mascara.length <= 9) {
                        handleInputChange('endereco', 'cep', mascara);
                      }
                    }}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.endereco?.cep ? 'border-red-500' : 'border-gray-300'
                      }`}
                    placeholder="00000-000"
                    maxLength={9}
                  />
                  {errors.endereco?.cep && (
                    <p className="mt-1 text-sm text-red-600 flex items-center">
                      <AlertCircle className="w-4 h-4 mr-1" />
                      {errors.endereco.cep}
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Aba Empresa */}
            {abaAtiva === 2 && (
              <div className="space-y-4">
                {formData.cliente.abertura_empresa ? (
                  <div className="text-center py-8">
                    <Building className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Cliente para Abertura de Empresa</h3>
                    <p className="text-gray-500">
                      Este cliente é para abertura de empresa, portanto não possui dados de empresa cadastrados.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Nome da Empresa <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        value={formData.empresa?.nome || ''}
                        onChange={(e) => {
                          handleInputChange('empresa', 'nome', e.target.value);
                        }}
                        className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.empresa?.nome ? 'border-red-500' : 'border-gray-300'
                          }`}
                        placeholder="Nome da empresa"
                      />
                      {errors.empresa?.nome && (
                        <p className="mt-1 text-sm text-red-600 flex items-center">
                          <AlertCircle className="w-4 h-4 mr-1" />
                          {errors.empresa.nome}
                        </p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        CNPJ <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        value={formData.empresa?.cnpj || ''}
                        onChange={(e) => {
                          const valor = e.target.value;
                          const mascara = aplicarMascaraCNPJ(valor);
                          if (mascara.length <= 18) {
                            handleInputChange('empresa', 'cnpj', mascara);
                          }
                        }}
                        className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.empresa?.cnpj ? 'border-red-500' : 'border-gray-300'
                          }`}
                        placeholder="00.000.000/0000-00"
                        maxLength={18}
                      />
                      {errors.empresa?.cnpj && (
                        <p className="mt-1 text-sm text-red-600 flex items-center">
                          <AlertCircle className="w-4 h-4 mr-1" />
                          {errors.empresa.cnpj}
                        </p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Tipo de Empresa <span className="text-red-500">*</span>
                      </label>
                      <select
                        value={formData.empresa?.tipo || ''}
                        onChange={(e) => {
                          handleInputChange('empresa', 'tipo', e.target.value);
                        }}
                        className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.empresa?.tipo ? 'border-red-500' : 'border-gray-300'
                          }`}
                      >
                        <option value="">Selecione o tipo</option>
                        {TIPOS_EMPRESA.map(tipo => (
                          <option key={tipo} value={tipo}>{tipo}</option>
                        ))}
                      </select>
                      {errors.empresa?.tipo && (
                        <p className="mt-1 text-sm text-red-600 flex items-center">
                          <AlertCircle className="w-4 h-4 mr-1" />
                          {errors.empresa.tipo}
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Botões */}
          <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancelar
            </button>
            <button
              onClick={handleSalvar}
              disabled={loading || !podeSalvar()}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Salvando...</span>
                </>
              ) : (
                <>
                  <Check className="w-4 h-4" />
                  <span>{clienteParaEditar ? 'Atualizar Cliente' : 'Salvar Cliente'}</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
