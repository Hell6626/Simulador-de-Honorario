"""
Serviço para geração de PDFs das propostas.
Baseado no design HTML moderno fornecido.
Layout atualizado com header estilizado, cores suaves e tipografia moderna.
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
from reportlab.platypus.flowables import Flowable

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


class HeaderBox(Flowable):
    """Box customizado para o cabeçalho com fundo colorido e bordas arredondadas"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
    def draw(self):
        # Fundo cinza claro (#f0eeea)
        self.canv.setFillColor(colors.Color(0.94, 0.93, 0.92))
        self.canv.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=0)


class CircleLogo(Flowable):
    """Logo quadrado com imagem real"""
    
    def __init__(self, size=80):
        self.size = size
        self.width = size
        self.height = size
        
    def draw(self):
        # Tentar carregar a imagem real da logo
        logo_path = self._find_logo_path()
        if logo_path and os.path.exists(logo_path):
            try:
                # Carregar e redimensionar a imagem
                from reportlab.platypus import Image
                img = Image(logo_path, width=self.size, height=self.size)
                img.drawOn(self.canv, 0, 0)
                return
            except Exception as e:
                print(f"Erro ao carregar logo: {e}")
        
        # Fallback: criar um quadrado laranja com letra C
        # Quadrado laranja (#f47a1c)
        self.canv.setFillColor(colors.Color(0.96, 0.48, 0.11))
        self.canv.rect(0, 0, self.size, self.size, fill=1, stroke=0)
        
        # Letra C branca no centro
        self.canv.setFillColor(colors.white)
        self.canv.setFont('Helvetica-Bold', self.size//3)
        self.canv.drawCentredText(self.size/2, self.size/2-8, 'C')
    
    def _find_logo_path(self):
        """Encontra o caminho da logo"""
        possible_paths = [
            'assets/images/Logo_Contabilidade.png',
            'backend/assets/images/Logo_Contabilidade.png',
            '../assets/images/Logo_Contabilidade.png',
            os.path.join(os.path.dirname(__file__), '..', 'assets', 'images', 'Logo_Contabilidade.png')
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None


class DescriptionBox(Flowable):
    """Box de descrição com fundo colorido"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
    def draw(self):
        # Fundo cinza claro (#f0eeea)
        self.canv.setFillColor(colors.Color(0.94, 0.93, 0.92))
        self.canv.roundRect(0, 0, self.width, self.height, 4, fill=1, stroke=0)


class PropostaPDFGenerator:
    """Gerador de PDF para propostas baseado no design HTML moderno"""
    
    def __init__(self):
        self.upload_dir = os.path.join(os.getcwd(), 'uploads', 'pdfs')
        os.makedirs(self.upload_dir, exist_ok=True)
        
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
    
    def gerar_pdf_proposta(self, proposta_id: int) -> str:
        """Gera PDF da proposta e retorna o caminho do arquivo"""
        try:
            if not MODELS_AVAILABLE:
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
                    topMargin=20*mm,
                    bottomMargin=20*mm
                )
                
                # Estilos
                styles = getSampleStyleSheet()
                self._configurar_estilos(styles)
                
                # Conteúdo do PDF
                story = []
                
                # Cabeçalho moderno
                story.extend(self._criar_header_moderno(proposta, styles))
                
                # Box de descrição
                story.extend(self._criar_desc_box(styles))
                
                # Seção "Sobre Nós"
                story.extend(self._criar_sobre_nos(styles))
                
                # Seção "Serviços"
                story.extend(self._criar_servicos(proposta.itens, styles))
                
                # Seção "Orçamento"
                story.extend(self._criar_orcamento(proposta, styles))
                
                # Detalhes Adicionais
                story.extend(self._criar_detalhes_adicionais(proposta, styles))
                
                # Gerar PDF
                doc.build(story)
                
                return caminho_arquivo
                
        except Exception as e:
            print(f"Erro ao gerar PDF com dados reais: {e}")
            import traceback
            traceback.print_exc()
            return self.gerar_pdf_proposta_temp()

    def gerar_pdf_proposta_temp(self) -> str:
        """Gera PDF temporário para proposta nova"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f"proposta_temp_{timestamp}.pdf"
        caminho_arquivo = os.path.join(self.upload_dir, nome_arquivo)
        
        # Criar documento PDF
        doc = SimpleDocTemplate(
            caminho_arquivo,
            pagesize=A4,
            rightMargin=25*mm,
            leftMargin=25*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        # Estilos
        styles = getSampleStyleSheet()
        self._configurar_estilos(styles)
        
        # Conteúdo do PDF temporário
        story = []
        
        story.extend(self._criar_header_moderno_temp(styles))
        story.extend(self._criar_desc_box(styles))
        story.extend(self._criar_sobre_nos(styles))
        story.extend(self._criar_servicos_temp(styles))
        story.extend(self._criar_orcamento_temp(styles))
        story.extend(self._criar_detalhes_adicionais_temp(styles))
        
        # Gerar PDF
        doc.build(story)
        
        return caminho_arquivo
    
    def _configurar_estilos(self, styles):
        """Configura estilos baseados no design HTML moderno"""
        
        # Data no header
        styles.add(ParagraphStyle(
            name='HeaderData',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.cores['preto'],
            fontName='Helvetica',
            spaceAfter=8
        ))
        
        # Título principal grande (baseado em 2.6rem)
        styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=styles['Heading1'],
            fontSize=36,
            spaceAfter=12,
            spaceBefore=8,
            textColor=self.cores['preto'],
            alignment=0,
            fontName='Helvetica-Bold',
            leading=38
        ))
        
        # Box "Preparado para"
        styles.add(ParagraphStyle(
            name='PreparedFor',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.cores['preto'],
            fontName='Helvetica',
            alignment=0
        ))
        
        # Título de seção (baseado em 2.1rem)
        styles.add(ParagraphStyle(
            name='TituloSecao',
            parent=styles['Heading2'],
            fontSize=24,
            spaceAfter=16,
            spaceBefore=28,
            textColor=self.cores['preto'],
            alignment=0,
            fontName='Helvetica-Bold',
            leading=26
        ))
        
        # Texto normal da descrição
        styles.add(ParagraphStyle(
            name='TextoDescricao',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=8,
            leading=18,
            textColor=self.cores['cinza_escuro'],
            fontName='Helvetica',
            alignment=4  # Justificado
        ))
        
        # Texto normal
        styles.add(ParagraphStyle(
            name='TextoNormal',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=8,
            leading=18,
            textColor=self.cores['preto'],
            fontName='Helvetica',
            alignment=4  # Justificado
        ))
        
        # Lista numerada
        styles.add(ParagraphStyle(
            name='ListaNumero',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            spaceBefore=6,
            leftIndent=0,
            textColor=self.cores['preto'],
            fontName='Helvetica',
            alignment=0,
            leading=16
        ))
        
        # Sub-item de lista
        styles.add(ParagraphStyle(
            name='SubItem',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=4,
            spaceBefore=2,
            leftIndent=20,
            textColor=self.cores['preto'],
            fontName='Helvetica',
            alignment=0,
            leading=16
        ))
        
        # Título do orçamento
        styles.add(ParagraphStyle(
            name='TituloOrcamento',
            parent=styles['Heading2'],
            fontSize=22,
            spaceAfter=20,
            spaceBefore=24,
            textColor=self.cores['preto'],
            alignment=0,
            fontName='Helvetica-Bold',
            leading=24
        ))
        
        # Título detalhes adicionais
        styles.add(ParagraphStyle(
            name='TituloDetalhes',
            parent=styles['Heading2'],
            fontSize=22,
            spaceAfter=16,
            spaceBefore=30,
            textColor=self.cores['preto'],
            alignment=0,
            fontName='Helvetica-Bold',
            leading=24
        ))
        
        # Subtítulo em detalhes
        styles.add(ParagraphStyle(
            name='SubtituloDetalhes',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            spaceBefore=12,
            textColor=self.cores['preto'],
            fontName='Helvetica-Bold',
            alignment=0
        ))
    
    def _criar_header_moderno(self, proposta, styles):
        """Cria o cabeçalho moderno para propostas com dados reais"""
        story = []

        # Data atual
        data_atual = datetime.now().strftime('%d/%m/%Y')

        # Bloco da esquerda (textos)
        left_elements = []

        # Data – topo
        left_elements.append(Paragraph(data_atual, styles['HeaderData']))
        # Título grande
        left_elements.append(Paragraph("Proposta de<br/>Orçamento", styles['TituloPrincipal']))
        # Box "Preparado para"
        box_data = [[Paragraph(f'Preparado para: <b>{proposta.cliente.nome}</b>', styles['PreparedFor'])]]
        box_table = Table(box_data, colWidths=[110*mm])
        box_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 1, colors.Color(0.73, 0.78, 0.89)),  # azul claro
            ('INNERGRID', (0, 0), (-1, -1), 0, colors.white),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('ROUNDRECT', (0, 0), (0, 0), 10, colors.white)  # cantos arredondados
        ]))
        left_elements.append(box_table)
        left_table = Table([[le] for le in left_elements], colWidths=[110*mm])
        left_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))

        # Bloco da direita (logo sobre fundo laranja)
        logo_box = Table(
            [[CircleLogo(80)]], colWidths=[80], rowHeights=[80]
        )
        logo_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.96, 0.48, 0.11)),  # laranja #f47a1c
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0)
        ]))

        # Cabeçalho principal dividido em duas colunas
        header_main = Table(
            [[left_table, logo_box]],
            colWidths=[120*mm, 60*mm],  # ajuste largura conforme visual desejado
            rowHeights=[90*mm]
        )
        header_main.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.Color(0.96, 0.96, 0.96)),  # cinza claro #f5f5f5
            ('BACKGROUND', (1, 0), (1, 0), colors.Color(0.96, 0.48, 0.11)),  # laranja
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 24),
            ('RIGHTPADDING', (0, 0), (-1, -1), 18),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ]))

        story.append(header_main)
        story.append(Spacer(1, 24))

        return story

    def _criar_header_moderno_temp(self, styles):
        """Cria o cabeçalho moderno temporário"""
        story = []
        
        data_atual = datetime.now().strftime('%d/%m/%Y')
        
        # Informações do lado esquerdo
        left_content = [
            [Paragraph(data_atual, styles['HeaderData'])],
            [Paragraph("Proposta de<br/>Orçamento", styles['TituloPrincipal'])],
            [self._criar_prepared_box("Associação Desportiva Futsal Itai", styles)]
        ]
        
        left_table = Table(left_content, colWidths=[120*mm])
        left_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        # Logo circular à direita
        logo_circle = CircleLogo(80)
        
        # Header principal com fundo
        header_data = [[left_table, logo_circle]]
        header_table = Table(header_data, colWidths=[120*mm, 40*mm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
            ('LEFTPADDING', (0, 0), (-1, -1), 25),
            ('RIGHTPADDING', (0, 0), (-1, -1), 25),
            ('BACKGROUND', (0, 0), (-1, -1), self.cores['fundo_header']),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 25))
        
        return story
    
    def _criar_prepared_box(self, cliente_nome, styles):
        """Cria o box 'Preparado para' com fundo branco e bordas arredondadas"""
        texto = f"Preparado para: <b>{cliente_nome}</b>"
        
        # Criar tabela para simular o box com fundo branco
        box_data = [[Paragraph(texto, styles['PreparedFor'])]]
        box_table = Table(box_data, colWidths=[100*mm])
        box_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 1, colors.Color(0.9, 0.9, 0.9)),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        return box_table
    
    def _criar_desc_box(self, styles):
        """Cria o box de descrição com fundo colorido"""
        story = []
        
        desc_texto = """Agradecemos o seu interesse em nossos serviços. <b>É um prazer apresentar esta proposta de orçamento</b>, onde reunimos informações sobre nossa empresa, os serviços oferecidos e as formas de colaboração possíveis.<br/><br/>

Nosso objetivo é <b>construir uma parceria sólida e estratégica</b>, entregando soluções que atendam plenamente às suas necessidades. Estamos à disposição para esclarecer quaisquer dúvidas e esperamos colaborar em breve!"""
        
        # Criar tabela para o box de descrição
        desc_data = [[Paragraph(desc_texto, styles['TextoDescricao'])]]
        desc_table = Table(desc_data, colWidths=[160*mm])
        desc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.cores['fundo_header']),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
            ('LEFTPADDING', (0, 0), (-1, -1), 25),
            ('RIGHTPADDING', (0, 0), (-1, -1), 25),
        ]))
        
        story.append(desc_table)
        story.append(Spacer(1, 24))
        
        return story
    
    def _criar_sobre_nos(self, styles):
        """Cria a seção 'Sobre Nós'"""
        story = []
        
        story.append(Paragraph("Sobre Nós", styles['TituloSecao']))
        
        sobre_texto = """A <b>Christino Consultoria Contábil LTDA</b>, fundada em 1995, é especializada no atendimento a pequenos e médios empresários.<br/><br/>

Atuamos com ética, qualidade e inovação, oferecendo serviços contábeis e consultoria empresarial que agregam valor, promovem segurança e fortalecem os negócios de nossos clientes."""
        
        story.append(Paragraph(sobre_texto, styles['TextoNormal']))
        story.append(Spacer(1, 20))
        
        return story
    
    def _criar_servicos(self, itens, styles):
        """Cria a seção de serviços com lista numerada"""
        story = []
        
        story.append(Paragraph("Serviços", styles['TituloSecao']))
        
        contador = 1
        for item in itens:
            if not item.ativo:
                continue
                
            servico = Servico.query.get(item.servico_id)
            if not servico:
                continue
            
            # Título do serviço
            titulo_servico = f"{contador}. <b>{servico.nome}</b>"
            story.append(Paragraph(titulo_servico, styles['ListaNumero']))
            
            # Descrição do serviço
            descricao_texto = servico.descricao.replace('\n', '<br/>')
            story.append(Paragraph(descricao_texto, styles['SubItem']))
            
            contador += 1
        
        return story

    def _criar_servicos_temp(self, styles):
        """Cria a seção de serviços temporária"""
        story = []
        
        story.append(Paragraph("Serviços", styles['TituloSecao']))
        
        # Serviço 1
        story.append(Paragraph("1. <b>Pré-requisito, Certificado Digital</b>", styles['ListaNumero']))
        story.append(Paragraph("• Emissão do certificado digital (e-CNPJ A1 da empresa): conferência de documentos, agendamento/validação e emissão.", styles['SubItem']))
        story.append(Paragraph("• Utilização do certificado para assinar e transmitir DCTF e EFD-Contribuições e para outorgar procuração eletrônica no e-CAC.", styles['SubItem']))
        
        story.append(Spacer(1, 8))
        
        # Serviço 2
        story.append(Paragraph("2. <b>Regularização de CNPJ, o serviço compreende:</b>", styles['ListaNumero']))
        story.append(Paragraph("1. <b>Entrega das Obrigações Acessórias</b>", styles['SubItem']))
        story.append(Paragraph("• Elaboração e transmissão da DCTF (Declaração de Débitos e Créditos Tributários Federais) dos exercícios de 2020 a 2024.", styles['SubItem']))
        story.append(Paragraph("• Elaboração e transmissão da EFD-Contribuições (PIS/COFINS e CPRB) dos exercícios de 2020 a 2025.", styles['SubItem']))
        
        story.append(Paragraph("2. <b>Reativação do CNPJ</b>", styles['SubItem']))
        story.append(Paragraph("• Atendimento às exigências da Receita Federal.", styles['SubItem']))
        story.append(Paragraph("• Adoção das medidas necessárias para voltar o CNPJ à condição de ativo, permitindo o pleno funcionamento da empresa.", styles['SubItem']))
        
        story.append(Paragraph("3. <b>Conformidade Fiscal e Tributária</b>", styles['SubItem']))
        story.append(Paragraph("• Garantia de que a empresa esteja em situação regular, sem pendências impeditivas.", styles['SubItem']))
        story.append(Paragraph("• Prevenção de multas e restrições futuras.", styles['SubItem']))
        
        return story
    
    def _criar_orcamento(self, proposta, styles):
        """Cria a seção de orçamento com tabela estilizada"""
        story = []
        
        story.append(Paragraph("Orçamento", styles['TituloOrcamento']))
        
        # Dados da tabela
        table_data = [['Serviço ou Produto', 'Quantidade', 'Preço Unitário', 'Total']]
        
        subtotal = 0
        for item in proposta.itens:
            if not item.ativo:
                continue
                
            servico = Servico.query.get(item.servico_id)
            if not servico:
                continue
            
            valor_total_item = float(item.valor_total)
            subtotal += valor_total_item
            
            table_data.append([
                servico.nome,
                str(int(item.quantidade)),
                f"R$ {float(item.valor_unitario):,.2f}",
                f"R$ {valor_total_item:,.2f}"
            ])
        
        # Linhas de totais
        table_data.append(['Subtotal', '', '', f'R$ {subtotal:,.2f}'])
        table_data.append(['Impostos', '', '', 'R$ 0'])
        table_data.append(['Total', '', '', f'R$ {float(proposta.valor_total):,.2f}'])
        
        # Criar tabela
        table = Table(table_data, colWidths=[70*mm, 25*mm, 35*mm, 30*mm])
        table.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), self.cores['fundo_tabela']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.cores['preto']),
            ('LINEBELOW', (0, 0), (-1, 0), 2, self.cores['preto']),
            
            # Dados normais
            ('FONTNAME', (0, 1), (-1, -4), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -4), 12),
            ('LINEBELOW', (0, 1), (-1, -4), 1, self.cores['cinza_medio']),
            
            # Subtotal
            ('FONTNAME', (0, -3), (-1, -3), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -3), (-1, -3), 12),
            ('LINEBELOW', (0, -3), (-1, -3), 1, self.cores['cinza_medio']),
            
            # Impostos
            ('FONTNAME', (0, -2), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, -2), (-1, -2), 12),
            ('LINEBELOW', (0, -2), (-1, -2), 1, self.cores['cinza_medio']),
            
            # Total
            ('BACKGROUND', (0, -1), (-1, -1), self.cores['fundo_total']),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            
            # Alinhamentos
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 25))
        
        return story

    def _criar_orcamento_temp(self, styles):
        """Cria a seção de orçamento temporária"""
        story = []
        
        story.append(Paragraph("Orçamento", styles['TituloOrcamento']))
        
        # Dados da tabela
        table_data = [
            ['Serviço ou Produto', 'Quantidade', 'Preço Unitário', 'Total'],
            ['Regularização de CNPJ', '1', 'R$ 1.000,00', 'R$ 1.000,00'],
            ['Certificado Digital', '1', 'R$ 230,00', 'R$ 230,00'],
            ['Subtotal', '', '', 'R$ 1.230,00'],
            ['Impostos', '', '', 'R$ 0'],
            ['Total', '', '', 'R$ 1.230,00']
        ]
        
        # Criar tabela
        table = Table(table_data, colWidths=[70*mm, 25*mm, 35*mm, 30*mm])
        table.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), self.cores['fundo_tabela']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.cores['preto']),
            ('LINEBELOW', (0, 0), (-1, 0), 2, self.cores['preto']),
            
            # Dados normais
            ('FONTNAME', (0, 1), (-1, 2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, 2), 12),
            ('LINEBELOW', (0, 1), (-1, 2), 1, self.cores['cinza_medio']),
            
            # Subtotal
            ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 3), (-1, 3), 12),
            ('LINEBELOW', (0, 3), (-1, 3), 1, self.cores['cinza_medio']),
            
            # Impostos
            ('FONTNAME', (0, 4), (-1, 4), 'Helvetica'),
            ('FONTSIZE', (0, 4), (-1, 4), 12),
            ('LINEBELOW', (0, 4), (-1, 4), 1, self.cores['cinza_medio']),
            
            # Total
            ('BACKGROUND', (0, 5), (-1, 5), self.cores['fundo_total']),
            ('FONTNAME', (0, 5), (-1, 5), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 5), (-1, 5), 12),
            
            # Alinhamentos
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 25))
        
        return story
    
    def _criar_detalhes_adicionais(self, proposta, styles):
        """Cria a seção de detalhes adicionais"""
        story = []
        
        story.append(Paragraph("Detalhes Adicionais", styles['TituloDetalhes']))
        
        # Previsão de Entrega
        story.append(Paragraph("<b>Previsão de Entrega</b>", styles['SubtituloDetalhes']))
        entrega_texto = "O serviço será concluído em até <b>10 dias úteis</b>, contados a partir da disponibilização completa da documentação e do certificado digital necessários."
        story.append(Paragraph(entrega_texto, styles['TextoNormal']))
        
        story.append(Spacer(1, 15))
        
        # Opções de Pagamento
        story.append(Paragraph("<b>Opções de Pagamento</b>", styles['SubtituloDetalhes']))
        
        valor_total = float(proposta.valor_total)
        valor_vista = valor_total * 0.9  # 10% desconto
        
        pagamento_texto = f"""• <b>À vista:</b> R$ {valor_vista:,.2f} (pagamento via PIX, transferência ou boleto).<br/>
• <b>Parcelado:</b> R$ {valor_total:,.2f} em até <b>3x no cartão de crédito</b>."""
        
        story.append(Paragraph(pagamento_texto, styles['TextoNormal']))
        
        return story

    def _criar_detalhes_adicionais_temp(self, styles):
        """Cria a seção de detalhes adicionais temporária"""
        story = []
        
        story.append(Paragraph("Detalhes Adicionais", styles['TituloDetalhes']))
        
        # Previsão de Entrega
        story.append(Paragraph("<b>Previsão de Entrega</b>", styles['SubtituloDetalhes']))
        entrega_texto = "O serviço será concluído em até <b>10 dias úteis</b>, contados a partir da disponibilização completa da documentação e do certificado digital necessários."
        story.append(Paragraph(entrega_texto, styles['TextoNormal']))
        
        story.append(Spacer(1, 15))
        
        # Opções de Pagamento
        story.append(Paragraph("<b>Opções de Pagamento</b>", styles['SubtituloDetalhes']))
        
        pagamento_texto = """• <b>À vista:</b> R$ 1.100,00 (pagamento via PIX, transferência ou boleto).<br/>
• <b>Parcelado:</b> R$ 1.230,00 em até <b>3x no cartão de crédito</b>."""
        
        story.append(Paragraph(pagamento_texto, styles['TextoNormal']))
        
        return story


# Instância global do gerador
pdf_generator = PropostaPDFGenerator()