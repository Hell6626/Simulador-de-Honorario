"""
Serviço para geração de PDFs das propostas.
Baseado no template da Christino Consultoria Contábil LTDA.
"""

import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.units import inch, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
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
    print("⚠️ Modelos não disponíveis - usando dados mock")


class PropostaPDFGenerator:
    """Gerador de PDF para propostas"""
    
    def __init__(self):
        self.upload_dir = os.path.join(os.getcwd(), 'uploads', 'pdfs')
        os.makedirs(self.upload_dir, exist_ok=True)
        
        # Configurações da empresa
        self.empresa = {
            'nome': 'Christino Consultoria Contábil LTDA',
            'cnpj': '00.000.000/0001-00',
            'endereco': 'Rua das Flores, 123 - Centro',
            'cidade': 'São Paulo - SP',
            'cep': '01234-567',
            'telefone': '(11) 99999-9999',
            'email': 'contato@christino.com.br',
            'site': 'www.christino.com.br'
        }
        
        # Cores - apenas preto, branco e laranja para logo
        self.cores = {
            'preto': colors.black,
            'branco': colors.white,
            'laranja': colors.Color(1.0, 0.4, 0.0)  # Para logo apenas
        }
    
    def gerar_pdf_proposta(self, proposta_id: int) -> str:
        """
        Gera PDF da proposta e retorna o caminho do arquivo
        """
        try:
            if not MODELS_AVAILABLE:
                # Se modelos não estão disponíveis, usar dados mock
                return self.gerar_pdf_proposta_temp()
            
            # Buscar proposta com todos os relacionamentos
            from flask import current_app
            with current_app.app_context():
                proposta = Proposta.query.filter_by(id=proposta_id, ativo=True).first()
                if not proposta:
                    raise ValueError(f"Proposta {proposta_id} não encontrada")
                
                # Gerar nome do arquivo
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                nome_arquivo = f"proposta_{proposta.numero}_{timestamp}.pdf"
                caminho_arquivo = os.path.join(self.upload_dir, nome_arquivo)
                
                # Criar documento PDF
                doc = SimpleDocTemplate(
                    caminho_arquivo,
                    pagesize=A4,
                    rightMargin=25*mm,
                    leftMargin=25*mm,
                    topMargin=25*mm,
                    bottomMargin=25*mm
                )
                
                # Estilos
                styles = getSampleStyleSheet()
                self._configurar_estilos(styles)
                
                # Conteúdo do PDF
                story = []
                
                # PÁGINA 1
                # Cabeçalho com data e logo
                story.extend(self._criar_cabecalho(proposta, styles))
                
                # Box "Preparado para" com borda preta
                story.extend(self._criar_box_cliente(proposta.cliente, styles))
                
                # Texto introdutório (3 parágrafos específicos)
                story.extend(self._criar_introducao(styles))
                
                # Seção "Sobre Nós"
                story.extend(self._criar_sobre_nos(styles))
                
                # Seção "Serviços" com lista numerada
                story.extend(self._criar_servicos(proposta.itens, styles))
                
                # Quebra de página
                story.append(PageBreak())
                
                # PÁGINA 2
                # Seção "Orçamento" com tabela de 4 colunas
                story.extend(self._criar_orcamento(proposta, styles))
                
                # Detalhes adicionais com sub-seções
                story.extend(self._criar_detalhes_adicionais(proposta, styles))
                
                # Rodapé simples
                story.extend(self._criar_rodape(styles))
                
                # Gerar PDF
                doc.build(story)
                
                return caminho_arquivo
                
        except Exception as e:
            print(f"Erro ao gerar PDF com dados reais: {e}")
            import traceback
            traceback.print_exc()
            # Fallback para PDF temporário
            return self.gerar_pdf_proposta_temp()

    def gerar_pdf_proposta_temp(self) -> str:
        """
        Gera PDF temporário para proposta nova (ainda não salva no banco)
        """
        # Gerar nome do arquivo temporário
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f"proposta_temp_{timestamp}.pdf"
        caminho_arquivo = os.path.join(self.upload_dir, nome_arquivo)
        
        # Criar documento PDF
        doc = SimpleDocTemplate(
            caminho_arquivo,
            pagesize=A4,
            rightMargin=25*mm,
            leftMargin=25*mm,
            topMargin=25*mm,
            bottomMargin=25*mm
        )
        
        # Estilos
        styles = getSampleStyleSheet()
        self._configurar_estilos(styles)
        
        # Conteúdo do PDF temporário
        story = []
        
        # PÁGINA 1
        # Cabeçalho com data e logo
        story.extend(self._criar_cabecalho_temp(styles))
        
        # Box "Preparado para" com borda preta (dados mock)
        story.extend(self._criar_box_cliente_temp(styles))
        
        # Texto introdutório (3 parágrafos específicos)
        story.extend(self._criar_introducao(styles))
        
        # Seção "Sobre Nós"
        story.extend(self._criar_sobre_nos(styles))
        
        # Seção "Serviços" com lista numerada (dados mock)
        story.extend(self._criar_servicos_temp(styles))
        
        # Quebra de página
        story.append(PageBreak())
        
        # PÁGINA 2
        # Seção "Orçamento" com tabela de 4 colunas (dados mock)
        story.extend(self._criar_orcamento_temp(styles))
        
        # Detalhes adicionais com sub-seções (dados mock)
        story.extend(self._criar_detalhes_adicionais_temp(styles))
        
        # Rodapé simples
        story.extend(self._criar_rodape(styles))
        
        # Gerar PDF
        doc.build(story)
        
        return caminho_arquivo
    
    def _configurar_estilos(self, styles):
        """Configura estilos personalizados - layout limpo e minimalista"""
        # Título principal
        styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=styles['Heading1'],
            fontSize=28,
            spaceAfter=30,
            textColor=self.cores['preto'],
            alignment=1,  # Centralizado
            fontName='Helvetica-Bold'
        ))
        
        # Título de seção
        styles.add(ParagraphStyle(
            name='TituloSecao',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=15,
            spaceBefore=20,
            textColor=self.cores['preto'],
            alignment=0,  # Esquerda
            fontName='Helvetica-Bold'
        ))
        
        # Texto normal
        styles.add(ParagraphStyle(
            name='TextoNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            textColor=self.cores['preto'],
            fontName='Helvetica'
        ))
        
        # Texto pequeno
        styles.add(ParagraphStyle(
            name='TextoPequeno',
            parent=styles['Normal'],
            fontSize=9,
            spaceAfter=4,
            textColor=self.cores['preto'],
            fontName='Helvetica'
        ))
        
        # Data
        styles.add(ParagraphStyle(
            name='Data',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=20,
            textColor=self.cores['preto'],
            fontName='Helvetica'
        ))
    
    def _criar_cabecalho(self, proposta, styles):
        """Cria o cabeçalho com data e logo circular"""
        story = []
        
        # Criar tabela simples: [Data] [Logo]
        if self._logo_exists():
            logo_img = self._get_logo_image()
            if logo_img:
                # Tabela com data à esquerda e logo à direita
                header_data = [
                    [
                        Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y')}", styles['Data']),
                        logo_img
                    ]
                ]
                
                header_table = Table(header_data, colWidths=[100*mm, 70*mm])
                header_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),   # Data à esquerda
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),  # Logo à direita
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                
                story.append(header_table)
            else:
                # Fallback: apenas data
                data_atual = datetime.now().strftime('%d/%m/%Y')
                story.append(Paragraph(f"Data: {data_atual}", styles['Data']))
        else:
            # Fallback: apenas data
            data_atual = datetime.now().strftime('%d/%m/%Y')
            story.append(Paragraph(f"Data: {data_atual}", styles['Data']))
        
        story.append(Spacer(1, 20))
        
        # Título centralizado
        story.append(Paragraph("Proposta de Orçamento", styles['TituloPrincipal']))
        story.append(Spacer(1, 40))  # Mais espaço
        
        return story

    def _criar_cabecalho_temp(self, styles):
        """Cria o cabeçalho temporário com data e logo circular"""
        return self._criar_cabecalho(None, styles)
    
    def _criar_box_cliente(self, cliente, styles):
        """Cria box oval com borda preta para informações do cliente"""
        story = []
        
        # CORRIGIR: Adicionar CPF e email
        cliente_info = f"""Preparado para: {cliente.nome}
CPF/CNPJ: {cliente.cpf}
Email: {cliente.email}"""
        
        # Box com cantos arredondados (oval) e borda preta
        cliente_data = [[cliente_info]]
        
        cliente_table = Table(cliente_data, colWidths=[120*mm])
        cliente_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1.5, self.cores['preto']),
            ('ROUNDEDCORNERS', (0, 0), (-1, -1), 15),  # Cantos arredondados
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ]))
        
        story.append(cliente_table)
        story.append(Spacer(1, 30))
        return story

    def _criar_box_cliente_temp(self, styles):
        """Cria box oval com borda preta para informações do cliente (temporário)"""
        story = []
        
        # Dados mock do cliente
        cliente_info = """Preparado para: Cliente Exemplo
CPF/CNPJ: 123.456.789-00
Email: cliente@exemplo.com"""
        
        # Box com cantos arredondados (oval) e borda preta
        cliente_data = [[cliente_info]]
        
        cliente_table = Table(cliente_data, colWidths=[120*mm])
        cliente_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1.5, self.cores['preto']),
            ('ROUNDEDCORNERS', (0, 0), (-1, -1), 15),  # Cantos arredondados
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ]))
        
        story.append(cliente_table)
        story.append(Spacer(1, 30))
        return story
    
    def _criar_introducao(self, styles):
        """Cria o texto introdutório específico do modelo"""
        story = []
        
        introducao_texto = """
        Agradecemos o seu interesse em nossos serviços. É um prazer apresentar esta <b>proposta de orçamento</b>, onde reunimos informações sobre nossa empresa, os serviços oferecidos e as formas de colaboração possíveis.<br/><br/>
        
        Nosso objetivo é construir uma <b>parceria sólida e estratégica</b>, entregando soluções que atendam plenamente às suas necessidades. Estamos à disposição para esclarecer quaisquer dúvidas e esperamos colaborar em breve!
        """
        
        story.append(Paragraph(introducao_texto, styles['TextoNormal']))
        story.append(Spacer(1, 25))  # Padronizar
        
        return story
    
    def _criar_sobre_nos(self, styles):
        """Cria a seção 'Sobre Nós' específica"""
        story = []
        
        # Título da seção
        story.append(Paragraph("Sobre Nós", styles['TituloSecao']))
        
        sobre_texto = """
        A Christino Consultoria Contábil LTDA, fundada em 1995, é especializada no atendimento a pequenos e médios empresários.<br/><br/>
        
        Atuamos com ética, qualidade e inovação, oferecendo serviços contábeis e consultoria empresarial que agregam valor, promovem segurança e fortalecem os negócios de nossos clientes.
        """
        
        story.append(Paragraph(sobre_texto, styles['TextoNormal']))
        story.append(Spacer(1, 25))  # Padronizar
        
        return story
    
    def _criar_servicos(self, itens, styles):
        """Cria a seção de serviços com lista numerada específica"""
        story = []
        
        # Título da seção
        story.append(Paragraph("Serviços", styles['TituloSecao']))
        
        # USAR serviços REAIS da proposta, não texto fixo
        for i, item in enumerate(itens, 1):
            if not item.ativo:
                continue
                
            servico = Servico.query.get(item.servico_id)
            if not servico:
                continue
            
            servico_texto = f"""
            <b>{i}. {servico.nome}</b><br/>
            • Quantidade: {item.quantidade}<br/>
            • Valor unitário: R$ {float(item.valor_unitario):.2f}<br/>
            • Categoria: {servico.categoria}<br/>
            • Descrição: {servico.descricao}<br/><br/>
            """
            story.append(Paragraph(servico_texto, styles['TextoNormal']))
        
        return story
    
    def _criar_orcamento(self, proposta, styles):
        """Cria a seção de orçamento com tabela de 4 colunas"""
        story = []
        
        # Título da seção
        story.append(Paragraph("Orçamento", styles['TituloSecao']))
        story.append(Spacer(1, 20))  # Padronizar
        
        # Dados da tabela com 4 colunas
        table_data = [['Serviço ou Produto', 'Quantidade', 'Preço Unitário', 'Total']]
        
        for item in proposta.itens:
            if not item.ativo:
                continue
                
            servico = Servico.query.get(item.servico_id)
            if not servico:
                continue
            
            table_data.append([
                servico.nome,
                str(float(item.quantidade)),
                f"R$ {float(item.valor_unitario):,.2f}",
                f"R$ {float(item.valor_total):,.2f}"
            ])
        
        # Subtotal
        subtotal = sum(float(item.valor_total) for item in proposta.itens if item.ativo)
        table_data.append(['Subtotal', '', '', f"R$ {subtotal:,.2f}"])
        
        # Impostos (zero por padrão)
        table_data.append(['Impostos', '', '', 'R$ 0,00'])
        
        # CORRIGIR cálculo do total final
        # Verificar se valor_total está calculado certo no backend
        total_calculado = sum(float(item.valor_total) for item in proposta.itens if item.ativo)
        
        # Usar o valor correto da proposta
        table_data.append(['Total', '', '', f"R$ {float(proposta.valor_total):.2f}"])
        
        # Criar tabela com bordas pretas simples
        table = Table(table_data, colWidths=[80*mm, 25*mm, 30*mm, 35*mm])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, self.cores['preto']),  # Bordas pretas simples
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),     # Cabeçalho em negrito
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),         # Dados normais
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),                # Cabeçalho centralizado
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),                # Valores à direita
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 25))
        
        return story
    
    def _criar_detalhes_adicionais(self, proposta, styles):
        """Cria a seção de detalhes adicionais com sub-seções"""
        story = []
        
        # Título da seção
        story.append(Paragraph("Detalhes Adicionais", styles['TituloSecao']))
        story.append(Spacer(1, 20))  # Padronizar
        
        # Sub-seção: Previsão de Entrega
        story.append(Paragraph("<b>Previsão de Entrega</b>", styles['TextoNormal']))
        story.append(Paragraph("O serviço será concluído em até <b>10 dias úteis</b>, contados a partir da disponibilização completa da documentação e do certificado digital necessários.", styles['TextoNormal']))
        story.append(Spacer(1, 20))  # Padronizar
        
        # Sub-seção: Opções de Pagamento
        story.append(Paragraph("<b>Opções de Pagamento</b>", styles['TextoNormal']))
        
        # CALCULAR valores baseados na proposta real
        valor_total = float(proposta.valor_total)
        valor_vista = valor_total * 0.95  # 5% desconto
        
        pagamento_texto = f"""
        • À vista: R$ {valor_vista:.2f} (pagamento via PIX, transferência ou boleto).<br/>
        • Parcelado: R$ {valor_total:.2f} em até 3x no cartão de crédito.
        """
        story.append(Paragraph(pagamento_texto, styles['TextoNormal']))
        
        return story

    def _get_logo_image(self):
        """Retorna a imagem da logo"""
        logo_path = self._find_logo_path()
        if logo_path:
            try:
                # Carregar imagem com dimensões específicas
                img = Image(logo_path, width=60, height=60)
                img.hAlign = 'RIGHT'  # Alinhar à direita
                return img
            except Exception as e:
                print(f"Erro ao carregar logo: {e}")
                return ""
        return ""

    def _find_logo_path(self):
        """Encontra o caminho da logo"""
        possible_paths = [
            'assets/images/Logo_Contabilidade.png',
            '../frontend/src/assets/images/Logo_Contabilidade.png',
            'frontend/src/assets/images/Logo_Contabilidade.png'
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    def _logo_exists(self):
        """Verifica se a logo existe"""
        return self._find_logo_path() is not None

    def _criar_rodape(self, styles):
        """Cria rodapé simples (sem caixa colorida)"""
        story = []
        story.append(Spacer(1, 30))
        
        # Manter formatação simples do modelo original
        rodape_texto = f"""
        Christino Consultoria Contábil LTDA<br/>
        CNPJ: 00.000.000/0001-00<br/>
        Rua das Flores, 123 - Centro<br/>
        São Paulo - SP<br/>
        Tel: (11) 99999-9999 | Email: contato@christino.com.br<br/>
        Site: www.christino.com.br
        """
        
        story.append(Paragraph(rodape_texto, styles['TextoPequeno']))
        return story

    def _criar_servicos_temp(self, styles):
        """Cria a seção de serviços temporária com dados mock"""
        story = []
        
        # Título da seção
        story.append(Paragraph("Serviços", styles['TituloSecao']))
        
        # Dados mock de serviços
        servicos_mock = [
            {
                'nome': 'Serviço Contábil Básico',
                'quantidade': 1,
                'valor_unitario': 150.00,
                'categoria': 'Contabilidade',
                'descricao': 'Serviços contábeis básicos mensais'
            },
            {
                'nome': 'Declaração de Impostos',
                'quantidade': 1,
                'valor_unitario': 80.00,
                'categoria': 'Fiscal',
                'descricao': 'Elaboração e entrega de declarações'
            }
        ]
        
        for i, servico in enumerate(servicos_mock, 1):
            servico_texto = f"""
            <b>{i}. {servico['nome']}</b><br/>
            • Quantidade: {servico['quantidade']}<br/>
            • Valor unitário: R$ {servico['valor_unitario']:.2f}<br/>
            • Categoria: {servico['categoria']}<br/>
            • Descrição: {servico['descricao']}<br/><br/>
            """
            story.append(Paragraph(servico_texto, styles['TextoNormal']))
        
        return story

    def _criar_orcamento_temp(self, styles):
        """Cria a seção de orçamento temporária com dados mock"""
        story = []
        
        # Título da seção
        story.append(Paragraph("Orçamento", styles['TituloSecao']))
        story.append(Spacer(1, 20))
        
        # Dados mock da tabela
        table_data = [['Serviço ou Produto', 'Quantidade', 'Preço Unitário', 'Total']]
        table_data.append(['Serviço Contábil Básico', '1', 'R$ 150,00', 'R$ 150,00'])
        table_data.append(['Declaração de Impostos', '1', 'R$ 80,00', 'R$ 80,00'])
        table_data.append(['Subtotal', '', '', 'R$ 230,00'])
        table_data.append(['Impostos', '', '', 'R$ 0,00'])
        table_data.append(['Total', '', '', 'R$ 230,00'])
        
        # Criar tabela com bordas pretas simples
        table = Table(table_data, colWidths=[80*mm, 25*mm, 30*mm, 35*mm])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, self.cores['preto']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 25))
        
        return story

    def _criar_detalhes_adicionais_temp(self, styles):
        """Cria a seção de detalhes adicionais temporária"""
        story = []
        
        # Título da seção
        story.append(Paragraph("Detalhes Adicionais", styles['TituloSecao']))
        story.append(Spacer(1, 20))
        
        # Sub-seção: Previsão de Entrega
        story.append(Paragraph("<b>Previsão de Entrega</b>", styles['TextoNormal']))
        story.append(Paragraph("O serviço será concluído em até <b>10 dias úteis</b>, contados a partir da disponibilização completa da documentação e do certificado digital necessários.", styles['TextoNormal']))
        story.append(Spacer(1, 20))
        
        # Sub-seção: Opções de Pagamento
        story.append(Paragraph("<b>Opções de Pagamento</b>", styles['TextoNormal']))
        
        # Valores mock
        valor_total = 230.00
        valor_vista = valor_total * 0.95  # 5% desconto
        
        pagamento_texto = f"""
        • À vista: R$ {valor_vista:.2f} (pagamento via PIX, transferência ou boleto).<br/>
        • Parcelado: R$ {valor_total:.2f} em até 3x no cartão de crédito.
        """
        story.append(Paragraph(pagamento_texto, styles['TextoNormal']))
        
        return story


# Instância global do gerador
pdf_generator = PropostaPDFGenerator()
