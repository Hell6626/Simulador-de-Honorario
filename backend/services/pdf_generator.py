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
import weasyprint
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
        
        # Configurações da empresa
        self.empresa = {
            'nome': 'Christino Consultoria Contábil LTDA',
            'cnpj': '49.666.494/0001-37',
            'endereco': 'Rua Dr. Ataliba Leonel, 847 - Centro',
            'cidade': 'Taquarituba - SP',
            'cep': '18740-019',
            'telefone': '(14) 3762-1991',
            'email': 'contato@christinoconsultoria.com.br',
            'site': 'www.christino.com.br'
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
                return self.gerar_pdf_proposta_temp()
            
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
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                nome_arquivo = f"proposta_{proposta.numero}_{timestamp}.pdf"
                caminho_arquivo = os.path.join(self.upload_dir, nome_arquivo)
                
                # Usar weasyprint para gerar PDF
                self._gerar_pdf_from_html(html_content, caminho_arquivo)
                
                return caminho_arquivo
                
        except Exception as e:
            print(f"Erro ao gerar PDF: {e}")
            import traceback
            traceback.print_exc()
            return self.gerar_pdf_proposta_temp()

    def gerar_pdf_proposta_temp(self) -> str:
        """Gera PDF temporário com logo acessível"""
        # Garantir que logo esteja acessível
        logo_path = self._ensure_logo_accessibility()
        
        template_data = {
            'data_atual': datetime.now().strftime('%d/%m/%Y'),
            'cliente': {'nome': 'Associação Desportiva Futsal Itai'},
            'empresa': self.empresa,
            'itens': [
                {
                    'servico': {
                        'nome': 'Pré-requisito, Certificado Digital',
                        'descricao': 'Emissão do certificado digital (e-CNPJ A1 da empresa): conferência de documentos, agendamento/validação e emissão.\nUtilização do certificado para assinar e transmitir DCTF e EFD-Contribuições e para outorgar procuração eletrônica no e-CAC.'
                    },
                    'quantidade': 1,
                    'valor_unitario': 230.00,
                    'valor_total': 230.00
                },
                {
                    'servico': {
                        'nome': 'Regularização de CNPJ, o serviço compreende:',
                        'descricao': 'Elaboração e transmissão da DCTF (Declaração de Débitos e Créditos Tributários Federais) dos exercícios de 2020 a 2024.\nElaboração e transmissão da EFD-Contribuições (PIS/COFINS e CPRB) dos exercícios de 2020 a 2025.\nAtendimento às exigências da Receita Federal.\nAdoção das medidas necessárias para voltar o CNPJ à condição de ativo, permitindo o pleno funcionamento da empresa.\nGarantia de que a empresa esteja em situação regular, sem pendências impeditivas.\nPrevenção de multas e restrições futuras.'
                    },
                    'quantidade': 1,
                    'valor_unitario': 1000.00,
                    'valor_total': 1000.00
                }
            ],
            'subtotal': 1230.00,
            'proposta': {'valor_total': 1230.00},
            'valor_vista': 1100.00,
            'logo_path': logo_path  # Usar logo acessível
        }
        
        # Renderizar template com contexto Flask
        try:
            from flask import Flask
            app = Flask(__name__, static_folder=self.upload_dir)
            app.config['SERVER_NAME'] = 'localhost:5000'
            
            with app.app_context():
                template = self.jinja_env.get_template('modelo_pdf.html')
                html_content = template.render(**template_data)
        except Exception as e:
            print(f"⚠️ Erro ao renderizar com Flask context: {e}")
            print("🔄 Tentando renderização sem Flask context...")
            template = self.jinja_env.get_template('modelo_pdf.html')
            html_content = template.render(**template_data)
        
        # Salvar HTML para debug
        debug_path = os.path.join(self.upload_dir, 'debug.html')
        with open(debug_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Gerar PDF
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f"proposta_PROP-{timestamp}_{timestamp}.pdf"
        caminho_arquivo = os.path.join(self.upload_dir, nome_arquivo)
        
        # Usar weasyprint para gerar PDF
        self._gerar_pdf_from_html(html_content, caminho_arquivo)
        
        return caminho_arquivo
    
    def _preparar_dados_template(self, proposta):
        """Prepara dados com debug melhorado"""
        
        # ✅ CORREÇÃO: Calcular subtotal incluindo mensalidade
        subtotal_servicos = sum(float(item.valor_total) for item in proposta.itens if item.ativo)
        valor_mensalidade = float(proposta.valor_mensalidade) if proposta.valor_mensalidade else 0.0
        subtotal = subtotal_servicos + valor_mensalidade
        
        print(f"💰 PDF Generator - Cálculo do subtotal:")
        print(f"   Serviços: R$ {subtotal_servicos:.2f}")
        print(f"   Mensalidade: R$ {valor_mensalidade:.2f}")
        print(f"   Subtotal: R$ {subtotal:.2f}")
        
        # Encontrar logo
        logo_path = self._find_logo_path()
        
        # Carregar serviços para cada item
        itens_com_servicos = []
        for item in proposta.itens:
            if not item.ativo:
                continue
            servico = Servico.query.get(item.servico_id) if MODELS_AVAILABLE else None
            
            
            item_data = {
                'servico': servico or {'nome': f'Serviço {item.id}', 'descricao': None},
                'quantidade': item.quantidade,
                'valor_unitario': float(item.valor_unitario),
                'valor_total': float(item.valor_total)
            }
            itens_com_servicos.append(item_data)
        
        # ✅ CORREÇÃO: Preparar dados do cliente para PDF
        cliente_data = self._preparar_dados_cliente(proposta.cliente)
        
        template_data = {
            'data_atual': datetime.now().strftime('%d/%m/%Y'),
            'cliente': cliente_data,
            'proposta': proposta,
            'empresa': self.empresa,
            'itens': itens_com_servicos,
            'subtotal': subtotal,
            'subtotal_servicos': subtotal_servicos,
            'valor_mensalidade': valor_mensalidade,
            'valor_vista': float(proposta.valor_total) * 0.9,
            'logo_path': logo_path
        }
        
        
        return template_data
    
    def _preparar_dados_cliente(self, cliente):
        """Prepara dados do cliente para o PDF - se for empresa, usa nome da empresa"""
        try:
            # ✅ CORREÇÃO: Se for Pessoa Jurídica, usar nome da empresa
            if hasattr(cliente, 'entidades_juridicas') and cliente.entidades_juridicas:
                # Verificar se tem entidades jurídicas ativas
                entidades_ativas = [ej for ej in cliente.entidades_juridicas if ej.ativo]
                if entidades_ativas:
                    # Usar nome da primeira entidade jurídica (empresa)
                    nome_empresa = entidades_ativas[0].nome
                    print(f"🏢 PDF Generator - Cliente PJ detectado: {cliente.nome} -> Empresa: {nome_empresa}")
                    
                    # Retornar dados do cliente com nome da empresa
                    return {
                        'id': cliente.id,
                        'nome': nome_empresa,  # ✅ Nome da empresa
                        'cpf': cliente.cpf,
                        'email': cliente.email,
                        'abertura_empresa': cliente.abertura_empresa,
                        'ativo': cliente.ativo,
                        'created_at': cliente.created_at,
                        'updated_at': cliente.updated_at,
                        'tipo_cliente': 'PJ',
                        'is_pessoa_juridica': True,
                        'entidades_juridicas': cliente.entidades_juridicas,
                        'enderecos': cliente.enderecos
                    }
            
            # ✅ Se for Pessoa Física, usar nome do cliente
            print(f"👤 PDF Generator - Cliente PF: {cliente.nome}")
            return {
                'id': cliente.id,
                'nome': cliente.nome,  # ✅ Nome do cliente
                'cpf': cliente.cpf,
                'email': cliente.email,
                'abertura_empresa': cliente.abertura_empresa,
                'ativo': cliente.ativo,
                'created_at': cliente.created_at,
                'updated_at': cliente.updated_at,
                'tipo_cliente': 'PF',
                'is_pessoa_juridica': False,
                'entidades_juridicas': cliente.entidades_juridicas or [],
                'enderecos': cliente.enderecos or []
            }
            
        except Exception as e:
            print(f"❌ Erro ao preparar dados do cliente: {e}")
            # Fallback: retornar dados originais
            return cliente
    
    def _gerar_pdf_from_html(self, html_content: str, output_path: str):
        """Gera PDF usando APENAS o CSS do HTML"""
        try:
            
            # Criar documento HTML
            html_doc = weasyprint.HTML(
                string=html_content,
                base_url=os.path.abspath(self.upload_dir),  # Para encontrar assets como logo
                encoding='utf-8'
            )
            
            # Gerar PDF sem qualquer CSS adicional
            html_doc.write_pdf(output_path)
            
            
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

# Função de teste para verificar a geração do PDF
def test_pdf_generation():
    """Testa a geração do PDF com o novo template"""
    try:
        pdf_path = pdf_generator.gerar_pdf_proposta_temp()
        
        if pdf_path and os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Executar teste se o arquivo for executado diretamente
    test_pdf_generation()