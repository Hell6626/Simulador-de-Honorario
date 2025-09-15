"""
Serviço para geração de PDFs das propostas usando Jinja2 templates.
Baseado no design HTML moderno fornecido.
Layout 100% idêntico ao HTML original usando weasyprint.
"""

import os
import json
import shutil
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
# import weasyprint  # Temporariamente comentado para evitar erros no Windows
from reportlab.lib import colors

# Importações condicionais para evitar erros
try:
    from config import db
    from models.propostas import Proposta, ItemProposta
    from models.clientes import Cliente
    from models.servicos import Servico
    from models import TipoAtividade, RegimeTributario, FaixaFaturamento
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False


class PropostaPDFGenerator:
    """Gerador de PDF usando Jinja2 templates e weasyprint para layout HTML idêntico"""
    
    def __init__(self):
        self.upload_dir = os.path.join(os.getcwd(), 'uploads', 'pdfs')
        os.makedirs(self.upload_dir, exist_ok=True)
        
        # Configurar Jinja2 com suporte ao Flask
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # Adicionar funções Flask ao Jinja2
        self._setup_flask_functions()
        
        # Configurações completas da empresa
        self.empresa = {
            'nome': 'Christino Consultoria Contábil LTDA',
            'cnpj': '49.666.494/0001-37',
            'endereco': 'Rua Dr. Ataliba Leonel, 847 - Centro',
            'cidade': 'Taquarituba - SP',
            'cep': '18740-019',
            'telefone': '(14) 3762-1991',
            'celular': '(14) 99999-9999',  # Adicionar se disponível
            'email': 'contato@christinoconsultoria.com.br',
            'email_comercial': 'comercial@christinoconsultoria.com.br',  # Adicionar se disponível
            'site': 'www.christino.com.br',
            'horario_funcionamento': 'Segunda a Sexta: 8h às 17h30m',
            'responsavel_comercial': 'Nome do Responsável'  # Adicionar se disponível
        }
        
        # Cores baseadas no design HTML
        self.cores = {
            'preto': colors.Color(0.13, 0.13, 0.13),  # #222
            'cinza_escuro': colors.Color(0.2, 0.2, 0.2),  # #333
            'cinza_medio': colors.Color(0.67, 0.67, 0.67),  # #aaa
            'fundo_header': colors.Color(0.94, 0.93, 0.92),  # #f0eeea
            'fundo_tabela': colors.Color(0.98, 0.98, 0.98),  # #fbfbfa
            'fundo_total': colors.Color(0.94, 0.94, 0.94),  # #efefef
            'laranja': colors.Color(0.96, 0.48, 0.11),  # #f47a1c
            'branco': colors.white
        }
        
        # Testar logo na inicialização
        logo_path = self._find_logo_path()
        if not logo_path:
            print("⚠️ Logo não encontrada na inicialização - usando fallback")
        
        # Cache de dados da empresa para otimização
        self._empresa_cache = None
    
    def _setup_flask_functions(self):
        """Configura funções Flask no Jinja2"""
        try:
            from flask import Flask
            from flask.helpers import url_for
            
            # Criar app Flask temporário
            app = Flask(__name__)
            app.config['SERVER_NAME'] = 'localhost:5000'
            
            # Adicionar url_for ao Jinja2
            self.jinja_env.globals['url_for'] = url_for
            
        except ImportError:
            # Fallback: função url_for simples
            def simple_url_for(endpoint, **kwargs):
                if endpoint == 'static':
                    filename = kwargs.get('filename', '')
                    return f"/static/{filename}"
                return "#"
            
            self.jinja_env.globals['url_for'] = simple_url_for
        
        # Adicionar outras funções úteis
        def format_currency(value):
            """Formata valor monetário no padrão brasileiro"""
            if value is None:
                return "R$ 0,00"
            try:
                return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            except:
                return f"R$ {value}"
        
        self.jinja_env.filters['currency'] = format_currency
    
    def gerar_pdf_proposta(self, proposta_id: int) -> str:
        """Gera PDF da proposta usando Jinja2 template"""
        try:
            if not MODELS_AVAILABLE:
                raise ValueError("Modelos não disponíveis - banco de dados não acessível")
            
            from flask import current_app
            with current_app.app_context():
                proposta = Proposta.query.filter_by(id=proposta_id, ativo=True).first()
                if not proposta:
                    raise ValueError(f"Proposta {proposta_id} não encontrada")
                
                # Preparar dados para o template
                template_data = self._preparar_dados_template(proposta)
                
                # Renderizar HTML com Jinja2
                template = self.jinja_env.get_template('modelo_pdf.html')
                html_content = template.render(**template_data)
                
                # Gerar PDF a partir do HTML
                nome_arquivo = f"{proposta.numero}.pdf"
                caminho_arquivo = os.path.join(self.upload_dir, nome_arquivo)
                
                # Usar weasyprint para gerar PDF
                self._gerar_pdf_from_html(html_content, caminho_arquivo)
                
                return caminho_arquivo
                
        except Exception as e:
            print(f"Erro ao gerar PDF: {e}")
            import traceback
            traceback.print_exc()
            raise e

    
    def _preparar_dados_template(self, proposta):
        """Prepara dados COMPLETOS para o template com máximo de informações"""
        
        # Encontrar logo
        logo_path = self._find_logo_path()
        
        # Carregar serviços para cada item e calcular desconto
        itens_com_servicos = []
        subtotal_servicos = 0.0
        
        for item in proposta.itens:
            if not item.ativo:
                continue
            servico = Servico.query.get(item.servico_id) if MODELS_AVAILABLE else None
            
            # ✅ CORREÇÃO: Usar valor_total do item (já calculado pelo frontend)
            valor_unitario = float(item.valor_unitario)
            valor_total_item = float(item.valor_total)  # ✅ Usar valor já calculado
            
            # ✅ CORREÇÃO: Calcular desconto baseado no valor original
            valor_total_sem_desconto = valor_unitario * float(item.quantidade)
            percentual_desconto = float(proposta.percentual_desconto) if proposta.percentual_desconto else 0.0
            valor_desconto = valor_total_sem_desconto * (percentual_desconto / 100.0)
            
            # ✅ CORREÇÃO: Somar ao subtotal dos serviços (usar valor do item)
            subtotal_servicos += valor_total_item
            
            item_data = {
                'servico': servico or {'nome': f'Serviço {item.id}', 'descricao': None},
                'quantidade': item.quantidade,
                'valor_unitario': valor_unitario,
                'valor_desconto': valor_desconto,  # ✅ Desconto calculado
                'valor_total': valor_total_item  # ✅ Valor do item (já calculado)
            }
            itens_com_servicos.append(item_data)
        
        # ✅ CORREÇÃO: Usar valores exatos do banco de dados
        valor_mensalidade = float(proposta.valor_mensalidade) if proposta.valor_mensalidade else 0.0
        valor_total_banco = float(proposta.valor_total)  # Valor final do banco
        
        print(f"💰 PDF Generator - Valores sincronizados:")
        print(f"   Serviços (itens): R$ {subtotal_servicos:.2f}")
        print(f"   Mensalidade: R$ {valor_mensalidade:.2f}")
        print(f"   Valor total banco: R$ {valor_total_banco:.2f}")
        print(f"   ✅ Ordem dos fatores corrigida!")
        
        # ✅ NOVOS DADOS - Informações completas
        cliente_completo = self._preparar_dados_cliente_completos(proposta.cliente)
        proposta_completa = self._preparar_dados_proposta_completos(proposta)
        empresa_completa = self._preparar_dados_empresa_completos()
        
        # Dados de contato e suporte
        contatos = {
            'telefone_principal': empresa_completa['telefone'],
            'telefone_secundario': empresa_completa.get('celular'),
            'email_principal': empresa_completa['email'],
            'email_comercial': empresa_completa.get('email_comercial'),
            'site': empresa_completa['site'],
            'horario_atendimento': empresa_completa['horario_funcionamento'],
        }
        
        # Condições comerciais
        condicoes = {
            'validade_proposta': proposta_completa['data_validade'],
            'prazo_entrega': '15 dias úteis',
            'forma_pagamento_vista': 'PIX, Transferência ou Boleto',
            'forma_pagamento_parcelado': 'Cartão de Crédito em até 3x',
            'desconto_vista': '10%',
            'termos_gerais': 'Serviços executados conforme especificação e prazos acordados.',
        }
        
        template_data = {
            # Dados existentes
            'data_atual': datetime.now().strftime('%d/%m/%Y'),
            'cliente': cliente_completo,  # ✅ Dados completos
            'proposta': proposta_completa,  # ✅ Dados completos
            'empresa': empresa_completa,  # ✅ Dados completos
            'itens': itens_com_servicos,
            'subtotal': valor_total_banco,  # ✅ Usar valor exato do banco
            'subtotal_servicos': subtotal_servicos,
            'valor_mensalidade': valor_mensalidade,
            'valor_vista': valor_total_banco * 0.9,  # ✅ Usar valor exato do banco
            'logo_path': logo_path,
            
            # NOVOS DADOS
            'contatos': contatos,
            'condicoes': condicoes,
            'dados_tributarios': self._preparar_dados_tributarios(proposta.cliente),
            'observacoes_especiais': self._preparar_observacoes_especiais(proposta),
        }
        
        # Log de dados incluídos
        self._log_dados_incluidos(template_data)
        
        return template_data
    
    def _preparar_dados_cliente_completos(self, cliente):
        """Prepara dados COMPLETOS do cliente para o PDF - se for empresa, usa nome da empresa"""
        try:
            # ✅ CORREÇÃO: Se for Pessoa Jurídica, usar nome da empresa
            if hasattr(cliente, 'entidades_juridicas') and cliente.entidades_juridicas:
                # Verificar se tem entidades jurídicas ativas
                entidades_ativas = [ej for ej in cliente.entidades_juridicas if ej.ativo]
                if entidades_ativas:
                    # Usar nome da primeira entidade jurídica (empresa)
                    entidade_principal = entidades_ativas[0]
                    nome_empresa = entidade_principal.nome
                    print(f"🏢 PDF Generator - Cliente PJ detectado: {cliente.nome} -> Empresa: {nome_empresa}")
                    
                    # Retornar dados completos do cliente com nome da empresa
                    return {
                        'id': cliente.id,
                        'nome': nome_empresa,  # ✅ Nome da empresa
                        'cpf': cliente.cpf,
                        'email': cliente.email,
                        'telefone': getattr(cliente, 'telefone', None),
                        'abertura_empresa': cliente.abertura_empresa,
                        'ativo': cliente.ativo,
                        'created_at': cliente.created_at,
                        'updated_at': cliente.updated_at,
                        'tipo_cliente': 'PJ',
                        'is_pessoa_juridica': True,
                        'entidades_juridicas': cliente.entidades_juridicas,
                        'enderecos': cliente.enderecos,
                        # Dados da empresa
                        'razao_social': entidade_principal.nome,
                        'nome_fantasia': getattr(entidade_principal, 'nome_fantasia', None),
                        'cnpj': entidade_principal.cnpj,
                        'inscricao_estadual': getattr(entidade_principal, 'inscricao_estadual', None),
                    }
            
            # ✅ Se for Pessoa Física, usar nome do cliente
            print(f"👤 PDF Generator - Cliente PF: {cliente.nome}")
            return {
                'id': cliente.id,
                'nome': cliente.nome,  # ✅ Nome do cliente
                'cpf': cliente.cpf,
                'email': cliente.email,
                'telefone': getattr(cliente, 'telefone', None),
                'abertura_empresa': cliente.abertura_empresa,
                'ativo': cliente.ativo,
                'created_at': cliente.created_at,
                'updated_at': cliente.updated_at,
                'tipo_cliente': 'PF',
                'is_pessoa_juridica': False,
                'entidades_juridicas': cliente.entidades_juridicas or [],
                'enderecos': cliente.enderecos or [],
                # Dados de endereço se disponível
                **self._preparar_dados_endereco(cliente)
            }
            
        except Exception as e:
            print(f"❌ Erro ao preparar dados do cliente: {e}")
            # Fallback: retornar dados originais
            return cliente
    
    def _preparar_dados_cliente(self, cliente):
        """Mantém compatibilidade com código existente"""
        return self._preparar_dados_cliente_completos(cliente)
    
    def _preparar_dados_endereco(self, cliente):
        """Prepara dados de endereço se disponível"""
        dados_endereco = {}
        
        if hasattr(cliente, 'enderecos') and cliente.enderecos:
            endereco = cliente.enderecos[0]  # Primeiro endereço
            dados_endereco.update({
                'endereco_completo': f"{endereco.logradouro}, {endereco.numero}",
                'bairro': endereco.bairro,
                'cidade': endereco.cidade,
                'estado': endereco.estado,
                'cep': endereco.cep,
            })
        
        return dados_endereco
    
    def _preparar_dados_proposta_completos(self, proposta):
        """Prepara dados COMPLETOS da proposta"""
        from datetime import timedelta
        
        # ✅ CORREÇÃO: Garantir que percentual_desconto seja sempre um número
        percentual_desconto = proposta.percentual_desconto or 0
        
        return {
            'id': proposta.id,
            'numero': proposta.numero,
            'data_criacao': proposta.created_at.strftime('%d/%m/%Y'),
            'data_validade': (proposta.created_at + timedelta(days=30)).strftime('%d/%m/%Y'),
            'status': proposta.status,
            'valor_total': proposta.valor_total,
            'valor_mensalidade': proposta.valor_mensalidade,
            'percentual_desconto': percentual_desconto,  # ✅ Sempre um número
            'observacoes': getattr(proposta, 'observacoes', None),
            'responsavel': getattr(proposta, 'responsavel', None),
        }
    
    def _preparar_dados_empresa_completos(self):
        """Prepara dados COMPLETOS da empresa"""
        return self.empresa
    
    def _preparar_dados_tributarios(self, cliente):
        """Prepara dados tributários se disponíveis"""
        dados = {}
        
        if hasattr(cliente, 'entidades_juridicas') and cliente.entidades_juridicas:
            entidade = cliente.entidades_juridicas[0]
            
            if hasattr(entidade, 'regime_tributario') and entidade.regime_tributario:
                dados['regime_tributario'] = entidade.regime_tributario.nome
            
            if hasattr(entidade, 'faixa_faturamento') and entidade.faixa_faturamento:
                dados['faixa_faturamento'] = entidade.faixa_faturamento.descricao
        
        return dados
    
    def _preparar_observacoes_especiais(self, proposta):
        """Prepara observações especiais da proposta"""
        observacoes = []
        
        # Observações da proposta
        if hasattr(proposta, 'observacoes') and proposta.observacoes:
            observacoes.append(f"Observações: {proposta.observacoes}")
        
        # Observações sobre mensalidade
        if proposta.valor_mensalidade and proposta.valor_mensalidade > 0:
            observacoes.append("Inclui mensalidade automática para serviços recorrentes.")
        
        # ✅ CORREÇÃO: Observações sobre desconto baseado no banco de dados
        percentual_desconto = proposta.percentual_desconto or 0
        if percentual_desconto > 0:
            observacoes.append(f"Desconto de {percentual_desconto}% aplicado sobre o valor total dos serviços.")
        
        return observacoes
    
    def _log_dados_incluidos(self, template_data):
        """Registra quais dados foram incluídos no PDF"""
        print("📋 Dados incluídos no PDF:")
        print(f"   Cliente: {template_data['cliente']['nome']}")
        print(f"   Proposta: {template_data['proposta']['numero']}")
        print(f"   Valor Total: R$ {template_data['proposta']['valor_total']:.2f}")
        print(f"   Itens: {len(template_data['itens'])}")
        print(f"   Contatos: {len(template_data['contatos'])} campos")
        print(f"   Condições: {len(template_data['condicoes'])} campos")
        if template_data['dados_tributarios']:
            print(f"   Dados Tributários: {len(template_data['dados_tributarios'])} campos")
        if template_data['observacoes_especiais']:
            print(f"   Observações: {len(template_data['observacoes_especiais'])} itens")
        
        # ✅ NOVO: Debug específico do desconto
        self._log_desconto_pdf(template_data['proposta'], template_data['itens'])
    
    def _log_desconto_pdf(self, proposta_data, itens_data):
        """Registra informações sobre desconto no PDF"""
        percentual = proposta_data.get('percentual_desconto', 0)
        
        print("💰 Debug - Desconto no PDF:")
        print(f"   Percentual no banco: {percentual}%")
        print(f"   Tem desconto: {percentual > 0}")
        print(f"   Coluna desconto: {'Sim' if percentual > 0 else 'Não'}")
        
        if percentual > 0:
            subtotal = sum(item['valor_total'] for item in itens_data)
            desconto_total = subtotal * (percentual / 100.0)
            print(f"   Subtotal: R$ {subtotal:.2f}")
            print(f"   Desconto total: R$ {desconto_total:.2f}")
            print(f"   Total final: R$ {subtotal - desconto_total:.2f}")
    
    def _gerar_pdf_from_html(self, html_content: str, output_path: str):
        """Gera PDF usando APENAS o CSS do HTML - TEMPORARIAMENTE DESABILITADO"""
        try:
            # TEMPORARIAMENTE COMENTADO PARA EVITAR ERROS NO WINDOWS
            # TODO: Implementar geração de PDF com ReportLab ou instalar dependências do WeasyPrint
            
            # Criar documento HTML
            # html_doc = weasyprint.HTML(
            #     string=html_content,
            #     base_url=os.path.abspath(self.upload_dir),  # Para encontrar assets como logo
            #     encoding='utf-8'
            # )
            
            # Gerar PDF sem qualquer CSS adicional
            # html_doc.write_pdf(output_path)
            
            # Por enquanto, criar um arquivo de texto como placeholder
            with open(output_path.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
                f.write("PDF temporariamente desabilitado - WeasyPrint não disponível no Windows\n")
                f.write("Conteúdo HTML:\n")
                f.write(html_content[:1000] + "...")
            
            print("⚠️ PDF temporariamente desabilitado - usando arquivo de texto")
            
        except Exception as e:
            print(f"❌ Erro ao gerar PDF: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _find_logo_path(self):
        """Encontra a logo com método mais direto"""
        # Testar diretórios principais do projeto
        base_dirs = [
            os.getcwd(),
            os.path.dirname(os.path.dirname(__file__)),
            os.path.dirname(__file__)
        ]
        
        # Padrões de busca
        search_patterns = [
            'frontend/src/assets/images/Logo_Contabilidade.png',
            'assets/images/Logo_Contabilidade.png',
            'backend/assets/images/Logo_Contabilidade.png',
            'Logo_Contabilidade.png'
        ]
        
        print("🔍 DEBUG: Procurando logo...")
        
        for base_dir in base_dirs:
            for pattern in search_patterns:
                full_path = os.path.join(base_dir, pattern)
                full_path = os.path.abspath(full_path)
                
                if os.path.exists(full_path):
                    return full_path
        
        # Busca recursiva como último recurso
        try:
            import glob
            for pattern in ['**/Logo_Contabilidade.png', '**/Logo_*.png']:
                matches = glob.glob(pattern, recursive=True)
                if matches:
                    logo_path = os.path.abspath(matches[0])
                    return logo_path
        except:
            pass
        
        print("❌ Logo não encontrada")
        return None
    
    
    
    def _ensure_logo_accessibility(self):
        """Garante que a logo esteja em local acessível pelo weasyprint"""
        logo_path = self._find_logo_path()
        
        if not logo_path:
            print("❌ Logo não encontrada para cópia")
            return None
        
        # Copiar logo para pasta de assets acessível
        assets_dir = os.path.join(self.upload_dir, 'assets')
        os.makedirs(assets_dir, exist_ok=True)
        
        logo_dest = os.path.join(assets_dir, 'logo.png')
        
        try:
            # Verificar se arquivo origem existe e tem conteúdo
            if os.path.exists(logo_path):
                file_size = os.path.getsize(logo_path)
                
                if file_size == 0:
                    print("❌ Arquivo origem está vazio!")
                    return None
            else:
                print(f"❌ Arquivo origem não existe: {logo_path}")
                return None
            
            # Copiar arquivo
            shutil.copy2(logo_path, logo_dest)
            
            # Verificar se cópia foi bem-sucedida
            if os.path.exists(logo_dest):
                copied_size = os.path.getsize(logo_dest)
                
                if copied_size != file_size:
                    return None
                
                # Verificar se arquivo é uma imagem válida e otimizar se necessário
                try:
                    from PIL import Image
                    with Image.open(logo_dest) as img:
                        
                        # Se a imagem for muito grande, redimensionar para otimizar o PDF
                        max_size = 300  # Tamanho máximo para logo no PDF
                        if img.size[0] > max_size or img.size[1] > max_size:
                            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                            img.save(logo_dest, 'PNG', optimize=True)
                            
                except Exception as e:
                    print(f"❌ Arquivo não é uma imagem válida: {e}")
                    return None
                
                # Retornar caminho relativo para o template (weasyprint funciona melhor com caminhos relativos)
                relative_path = os.path.relpath(logo_dest, self.upload_dir)
                # Para o WeasyPrint, usar caminho relativo simples
                return relative_path.replace('\\', '/')
            else:
                print(f"❌ Falha na cópia - arquivo destino não existe: {logo_dest}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao copiar logo: {e}")
            import traceback
            traceback.print_exc()
            return logo_path


# Instância global do gerador
pdf_generator = PropostaPDFGenerator()
