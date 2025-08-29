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
        """Configura estilos personalizados - layout moderno baseado no modelo"""
        # Título principal - mais moderno
        styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=styles['Heading1'],
            fontSize=32,
            spaceAfter=25,
            spaceBefore=15,
            textColor=self.cores['preto'],
            alignment=1,  # Centralizado
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo principal
        styles.add(ParagraphStyle(
            name='SubtituloPrincipal',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.Color(0.3, 0.3, 0.3),  # Cinza escuro
            alignment=1,  # Centralizado
            fontName='Helvetica'
        ))
        
        # Título de seção - mais proeminente
        styles.add(ParagraphStyle(
            name='TituloSecao',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=12,
            spaceBefore=25,
            textColor=self.cores['preto'],
            alignment=0,  # Esquerda
            fontName='Helvetica-Bold'
        ))
        
        # Texto normal - melhor legibilidade
        styles.add(ParagraphStyle(
            name='TextoNormal',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            leading=18,  # Espaçamento entre linhas
            textColor=self.cores['preto'],
            fontName='Helvetica',
            alignment=4  # Justificado
        ))
        
        # Texto pequeno
        styles.add(ParagraphStyle(
            name='TextoPequeno',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            textColor=colors.Color(0.4, 0.4, 0.4),  # Cinza médio
            fontName='Helvetica'
        ))
        
        # Data - mais elegante
        styles.add(ParagraphStyle(
            name='Data',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=15,
            textColor=colors.Color(0.3, 0.3, 0.3),
            fontName='Helvetica',
            alignment=2  # Direita
        ))
        
        # Estilo para box/destaque
        styles.add(ParagraphStyle(
            name='BoxDestaque',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            textColor=self.cores['preto'],
            fontName='Helvetica-Bold',
            alignment=1,  # Centralizado
            backColor=colors.Color(0.95, 0.95, 0.95)  # Fundo cinza claro
        ))
        
        # Lista de serviços
        styles.add(ParagraphStyle(
            name='ListaServicos',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            leftIndent=20,
            textColor=self.cores['preto'],
            fontName='Helvetica'
        ))
    
    def _criar_cabecalho(self, proposta, styles):
        """Cria o cabeçalho moderno baseado no modelo"""
        story = []
        
        # Header superior com logo e data
        if self._logo_exists():
            logo_img = self._get_logo_image()
            if logo_img:
                header_data = [
                    [
                        logo_img,
                        Paragraph(datetime.now().strftime('%d de %B de %Y'), styles['Data'])
                    ]
                ]
                
                header_table = Table(header_data, colWidths=[80*mm, 90*mm])
                header_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),   # Logo à esquerda
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),  # Data à direita
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                
                story.append(header_table)
            else:
                # Fallback: apenas data
                data_atual = datetime.now().strftime('%d de %B de %Y')
                story.append(Paragraph(data_atual, styles['Data']))
        else:
            # Fallback: apenas data
            data_atual = datetime.now().strftime('%d de %B de %Y')
            story.append(Paragraph(data_atual, styles['Data']))
        
        story.append(Spacer(1, 30))
        
        # Título principal moderno
        story.append(Paragraph("PROPOSTA COMERCIAL", styles['TituloPrincipal']))
        
        # Subtítulo
        story.append(Paragraph("Serviços Contábeis e Consultoria", styles['SubtituloPrincipal']))
        
        # Linha separadora visual
        story.append(Spacer(1, 20))
        linha_separadora = Table([['']], colWidths=[170*mm])
        linha_separadora.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 2, colors.Color(0.8, 0.8, 0.8)),
        ]))
        story.append(linha_separadora)
        story.append(Spacer(1, 30))
        
        return story

    def _criar_cabecalho_temp(self, styles):
        """Cria o cabeçalho temporário com data e logo circular"""
        return self._criar_cabecalho(None, styles)
    
    def _criar_box_cliente(self, cliente, styles):
        """Cria seção moderna de informações do cliente"""
        story = []
        
        # Título da seção
        story.append(Paragraph("DESTINATÁRIO", styles['TituloSecao']))
        story.append(Spacer(1, 15))
        
        # Informações do cliente em formato estruturado
        cliente_data = [
            ['<b>Nome/Razão Social:</b>', cliente.nome],
            ['<b>CPF/CNPJ:</b>', cliente.cpf],
            ['<b>Email:</b>', cliente.email],
        ]
        
        # Tabela com informações do cliente
        cliente_table = Table(cliente_data, colWidths=[50*mm, 120*mm])
        cliente_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.98, 0.98, 0.98)),
            ('BOX', (0, 0), (-1, -1), 1, colors.Color(0.8, 0.8, 0.8)),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.Color(0.9, 0.9, 0.9)),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(cliente_table)
        story.append(Spacer(1, 30))
        return story

    def _criar_box_cliente_temp(self, styles):
        """Cria seção moderna de informações do cliente (temporário)"""
        story = []
        
        # Título da seção
        story.append(Paragraph("DESTINATÁRIO", styles['TituloSecao']))
        story.append(Spacer(1, 15))
        
        # Dados mock do cliente
        cliente_data = [
            ['<b>Nome/Razão Social:</b>', 'Cliente Exemplo Ltda'],
            ['<b>CPF/CNPJ:</b>', '12.345.678/0001-90'],
            ['<b>Email:</b>', 'cliente@exemplo.com'],
        ]
        
        # Tabela com informações do cliente
        cliente_table = Table(cliente_data, colWidths=[50*mm, 120*mm])
        cliente_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.98, 0.98, 0.98)),
            ('BOX', (0, 0), (-1, -1), 1, colors.Color(0.8, 0.8, 0.8)),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.Color(0.9, 0.9, 0.9)),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(cliente_table)
        story.append(Spacer(1, 30))
        return story
    
    def _criar_introducao(self, styles):
        """Cria o texto introdutório moderno e profissional"""
        story = []
        
        # Título da apresentação
        story.append(Paragraph("APRESENTAÇÃO", styles['TituloSecao']))
        story.append(Spacer(1, 15))
        
        introducao_texto = """
        Prezado(a) Cliente,<br/><br/>
        
        É com grande satisfação que apresentamos esta <b>proposta comercial</b> para prestação de serviços contábeis especializados. Nossa empresa tem o compromisso de oferecer soluções personalizadas que atendam às suas necessidades específicas com <b>excelência e confiabilidade</b>.<br/><br/>
        
        Esta proposta foi elaborada considerando as características do seu negócio e as melhores práticas do mercado contábil. Nosso objetivo é estabelecer uma <b>parceria estratégica duradoura</b>, proporcionando tranquilidade e segurança na gestão dos aspectos contábeis e fiscais da sua empresa.<br/><br/>
        
        Estamos à disposição para esclarecimentos adicionais e esperamos ter a oportunidade de demonstrar a qualidade dos nossos serviços.
        """
        
        story.append(Paragraph(introducao_texto, styles['TextoNormal']))
        story.append(Spacer(1, 30))
        
        return story
    
    def _criar_sobre_nos(self, styles):
        """Cria a seção 'Sobre Nós' moderna e profissional"""
        story = []
        
        # Título da seção
        story.append(Paragraph("NOSSA EMPRESA", styles['TituloSecao']))
        story.append(Spacer(1, 15))
        
        sobre_texto = """
        A <b>Christino Consultoria Contábil LTDA</b> é uma empresa especializada em serviços contábeis e consultoria empresarial, com sólida experiência no mercado desde 1995. Nossa missão é oferecer soluções contábeis completas e personalizadas para empresas de todos os portes.<br/><br/>
        
        <b>Nossos Diferenciais:</b><br/>
        • Equipe técnica altamente qualificada e em constante atualização<br/>
        • Atendimento personalizado e dedicado a cada cliente<br/>
        • Tecnologia de ponta para maior agilidade e segurança<br/>
        • Suporte completo em todas as obrigações fiscais e contábeis<br/>
        • Relacionamento próximo e consultivo com nossos clientes<br/><br/>
        
        Trabalhamos com <b>ética, transparência e excelência</b>, estabelecendo parcerias duradouras baseadas na confiança mútua e no comprometimento com o sucesso dos nossos clientes.
        """
        
        story.append(Paragraph(sobre_texto, styles['TextoNormal']))
        story.append(Spacer(1, 30))
        
        return story
    
    def _criar_servicos(self, itens, styles):
        """Cria a seção de serviços moderna e detalhada"""
        story = []
        
        # Título da seção
        story.append(Paragraph("SERVIÇOS PROPOSTOS", styles['TituloSecao']))
        story.append(Spacer(1, 15))
        
        # Texto introdutório
        intro_servicos = """
        Os serviços descritos abaixo foram selecionados especificamente para atender às necessidades da sua empresa, garantindo total conformidade legal e otimização dos processos contábeis e fiscais.
        """
        story.append(Paragraph(intro_servicos, styles['TextoNormal']))
        story.append(Spacer(1, 20))
        
        # Criar tabela de serviços mais organizada
        servicos_data = [['Item', 'Serviço', 'Descrição', 'Qtd', 'Valor Unit.']]
        
        for i, item in enumerate(itens, 1):
            if not item.ativo:
                continue
                
            servico = Servico.query.get(item.servico_id)
            if not servico:
                continue
            
            # Limitar descrição para não quebrar o layout
            descricao = servico.descricao[:100] + "..." if len(servico.descricao) > 100 else servico.descricao
            
            servicos_data.append([
                str(i),
                servico.nome,
                descricao,
                str(int(item.quantidade)),
                f"R$ {float(item.valor_unitario):,.2f}"
            ])
        
        # Criar tabela
        servicos_table = Table(servicos_data, colWidths=[15*mm, 60*mm, 60*mm, 20*mm, 25*mm])
        servicos_table.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Dados
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Item
            ('ALIGN', (1, 1), (2, -1), 'LEFT'),    # Serviço e Descrição
            ('ALIGN', (3, 1), (-1, -1), 'CENTER'), # Quantidade e Valor
            
            # Bordas e padding
            ('GRID', (0, 0), (-1, -1), 1, colors.Color(0.8, 0.8, 0.8)),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(servicos_table)
        story.append(Spacer(1, 25))
        
        return story
    
    def _criar_orcamento(self, proposta, styles):
        """Cria a seção de orçamento moderna e detalhada"""
        story = []
        
        # Título da seção
        story.append(Paragraph("RESUMO FINANCEIRO", styles['TituloSecao']))
        story.append(Spacer(1, 15))
        
        # Texto introdutório
        intro_orcamento = """
        Abaixo apresentamos o detalhamento financeiro completo dos serviços propostos, incluindo valores individuais e totais consolidados.
        """
        story.append(Paragraph(intro_orcamento, styles['TextoNormal']))
        story.append(Spacer(1, 20))
        
        # Dados da tabela
        table_data = [['Descrição do Serviço', 'Qtd', 'Valor Unitário', 'Valor Total']]
        
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
        
        # Linha de separação
        table_data.append(['', '', '', ''])
        
        # Totalizadores
        table_data.append(['<b>SUBTOTAL</b>', '', '', f"<b>R$ {subtotal:,.2f}</b>"])
        
        # Verificar se há desconto
        valor_proposta = float(proposta.valor_total)
        if valor_proposta < subtotal:
            desconto = subtotal - valor_proposta
            table_data.append(['<b>Desconto Aplicado</b>', '', '', f"<b>- R$ {desconto:,.2f}</b>"])
        
        table_data.append(['<b>VALOR TOTAL</b>', '', '', f"<b>R$ {valor_proposta:,.2f}</b>"])
        
        # Criar tabela moderna
        table = Table(table_data, colWidths=[90*mm, 25*mm, 30*mm, 35*mm])
        table.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.2, 0.2)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Dados
            ('FONTNAME', (0, 1), (-1, -4), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -4), 10),
            ('ALIGN', (0, 1), (0, -4), 'LEFT'),     # Descrição
            ('ALIGN', (1, 1), (-1, -4), 'RIGHT'),   # Números
            
            # Totais
            ('BACKGROUND', (0, -3), (-1, -1), colors.Color(0.95, 0.95, 0.95)),
            ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -3), (-1, -1), 11),
            ('ALIGN', (0, -3), (0, -1), 'LEFT'),
            ('ALIGN', (1, -3), (-1, -1), 'RIGHT'),
            
            # Bordas e espaçamento
            ('GRID', (0, 0), (-1, -4), 1, colors.Color(0.8, 0.8, 0.8)),
            ('GRID', (0, -3), (-1, -1), 1, colors.Color(0.6, 0.6, 0.6)),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 30))
        
        return story
    
    def _criar_detalhes_adicionais(self, proposta, styles):
        """Cria a seção de detalhes adicionais moderna e completa"""
        story = []
        
        # Título da seção
        story.append(Paragraph("CONDIÇÕES COMERCIAIS", styles['TituloSecao']))
        story.append(Spacer(1, 15))
        
        # Condições de Prestação dos Serviços
        story.append(Paragraph("<b>CONDIÇÕES DE PRESTAÇÃO DOS SERVIÇOS</b>", styles['TextoNormal']))
        condicoes_texto = """
        • <b>Início dos Serviços:</b> Após assinatura do contrato e fornecimento da documentação completa<br/>
        • <b>Prazo de Entrega:</b> Conforme cronograma estabelecido para cada tipo de serviço<br/>
        • <b>Documentação Necessária:</b> O cliente deverá fornecer toda documentação solicitada em até 5 dias úteis<br/>
        • <b>Certificado Digital:</b> Obrigatório para serviços fiscais e deve estar sempre atualizado<br/>
        • <b>Responsabilidades:</b> O cliente é responsável pela veracidade das informações fornecidas
        """
        story.append(Paragraph(condicoes_texto, styles['TextoNormal']))
        story.append(Spacer(1, 20))
        
        # Condições de Pagamento
        story.append(Paragraph("<b>CONDIÇÕES DE PAGAMENTO</b>", styles['TextoNormal']))
        
        valor_total = float(proposta.valor_total)
        valor_vista = valor_total * 0.95  # 5% desconto
        
        pagamento_texto = f"""
        <b>Opção 1 - À Vista (5% de desconto):</b><br/>
        • Valor: R$ {valor_vista:,.2f}<br/>
        • Formas: PIX, transferência bancária ou boleto<br/>
        • Vencimento: Na assinatura do contrato<br/><br/>
        
        <b>Opção 2 - Parcelado:</b><br/>
        • Valor: R$ {valor_total:,.2f}<br/>
        • Parcelas: Até 3x sem juros no cartão de crédito<br/>
        • Vencimento: Conforme acordo estabelecido
        """
        story.append(Paragraph(pagamento_texto, styles['TextoNormal']))
        story.append(Spacer(1, 20))
        
        # Validade da Proposta
        story.append(Paragraph("<b>VALIDADE DA PROPOSTA</b>", styles['TextoNormal']))
        validade_texto = """
        Esta proposta tem validade de <b>30 (trinta) dias</b> a partir da data de emissão. Após este período, os valores e condições poderão ser reavaliados conforme alterações de custos e legislação.
        """
        story.append(Paragraph(validade_texto, styles['TextoNormal']))
        story.append(Spacer(1, 25))
        
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
        """Cria rodapé moderno e profissional"""
        story = []
        story.append(Spacer(1, 40))
        
        # Linha separadora
        linha_separadora = Table([['']], colWidths=[170*mm])
        linha_separadora.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, -1), 2, colors.Color(0.8, 0.8, 0.8)),
        ]))
        story.append(linha_separadora)
        story.append(Spacer(1, 20))
        
        # Seção de contato
        story.append(Paragraph("CONTATO E INFORMAÇÕES", styles['TituloSecao']))
        story.append(Spacer(1, 15))
        
        # Informações da empresa em tabela organizada
        empresa_data = [
            ['<b>Empresa:</b>', 'Christino Consultoria Contábil LTDA'],
            ['<b>CNPJ:</b>', '00.000.000/0001-00'],
            ['<b>Endereço:</b>', 'Rua das Flores, 123 - Centro'],
            ['<b>Cidade:</b>', 'São Paulo - SP - CEP: 01234-567'],
            ['<b>Telefone:</b>', '(11) 99999-9999'],
            ['<b>Email:</b>', 'contato@christino.com.br'],
            ['<b>Website:</b>', 'www.christino.com.br'],
        ]
        
        empresa_table = Table(empresa_data, colWidths=[40*mm, 130*mm])
        empresa_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(empresa_table)
        story.append(Spacer(1, 20))
        
        # Agradecimento final
        agradecimento = """
        <b>Agradecemos a oportunidade de apresentar esta proposta e estamos à disposição para quaisquer esclarecimentos adicionais. Esperamos iniciar uma parceria de sucesso em breve!</b>
        """
        story.append(Paragraph(agradecimento, styles['TextoNormal']))
        
        return story

    def _criar_servicos_temp(self, styles):
        """Cria a seção de serviços temporária moderna com dados mock"""
        story = []
        
        # Título da seção
        story.append(Paragraph("SERVIÇOS PROPOSTOS", styles['TituloSecao']))
        story.append(Spacer(1, 15))
        
        # Texto introdutório
        intro_servicos = """
        Os serviços descritos abaixo foram selecionados especificamente para atender às necessidades da sua empresa, garantindo total conformidade legal e otimização dos processos contábeis e fiscais.
        """
        story.append(Paragraph(intro_servicos, styles['TextoNormal']))
        story.append(Spacer(1, 20))
        
        # Dados mock de serviços em tabela
        servicos_data = [['Item', 'Serviço', 'Descrição', 'Qtd', 'Valor Unit.']]
        servicos_data.append(['1', 'Serviço Contábil Básico', 'Escrituração contábil mensal completa', '1', 'R$ 450,00'])
        servicos_data.append(['2', 'Declaração de Impostos', 'Elaboração e entrega de declarações fiscais', '1', 'R$ 180,00'])
        servicos_data.append(['3', 'Folha de Pagamento', 'Processamento completo da folha de pagamento', '1', 'R$ 280,00'])
        
        # Criar tabela
        servicos_table = Table(servicos_data, colWidths=[15*mm, 60*mm, 60*mm, 20*mm, 25*mm])
        servicos_table.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Dados
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Item
            ('ALIGN', (1, 1), (2, -1), 'LEFT'),    # Serviço e Descrição
            ('ALIGN', (3, 1), (-1, -1), 'CENTER'), # Quantidade e Valor
            
            # Bordas e padding
            ('GRID', (0, 0), (-1, -1), 1, colors.Color(0.8, 0.8, 0.8)),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(servicos_table)
        story.append(Spacer(1, 25))
        
        return story

    def _criar_orcamento_temp(self, styles):
        """Cria a seção de orçamento temporária moderna com dados mock"""
        story = []
        
        # Título da seção
        story.append(Paragraph("RESUMO FINANCEIRO", styles['TituloSecao']))
        story.append(Spacer(1, 15))
        
        # Texto introdutório
        intro_orcamento = """
        Abaixo apresentamos o detalhamento financeiro completo dos serviços propostos, incluindo valores individuais e totais consolidados.
        """
        story.append(Paragraph(intro_orcamento, styles['TextoNormal']))
        story.append(Spacer(1, 20))
        
        # Dados mock da tabela
        table_data = [['Descrição do Serviço', 'Qtd', 'Valor Unitário', 'Valor Total']]
        table_data.append(['Serviço Contábil Básico', '1', 'R$ 450,00', 'R$ 450,00'])
        table_data.append(['Declaração de Impostos', '1', 'R$ 180,00', 'R$ 180,00'])
        table_data.append(['Folha de Pagamento', '1', 'R$ 280,00', 'R$ 280,00'])
        
        # Linha de separação
        table_data.append(['', '', '', ''])
        
        # Totalizadores
        table_data.append(['<b>SUBTOTAL</b>', '', '', '<b>R$ 910,00</b>'])
        table_data.append(['<b>VALOR TOTAL</b>', '', '', '<b>R$ 910,00</b>'])
        
        # Criar tabela moderna
        table = Table(table_data, colWidths=[90*mm, 25*mm, 30*mm, 35*mm])
        table.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.2, 0.2)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Dados
            ('FONTNAME', (0, 1), (-1, -3), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -3), 10),
            ('ALIGN', (0, 1), (0, -3), 'LEFT'),     # Descrição
            ('ALIGN', (1, 1), (-1, -3), 'RIGHT'),   # Números
            
            # Totais
            ('BACKGROUND', (0, -2), (-1, -1), colors.Color(0.95, 0.95, 0.95)),
            ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -2), (-1, -1), 11),
            ('ALIGN', (0, -2), (0, -1), 'LEFT'),
            ('ALIGN', (1, -2), (-1, -1), 'RIGHT'),
            
            # Bordas e espaçamento
            ('GRID', (0, 0), (-1, -3), 1, colors.Color(0.8, 0.8, 0.8)),
            ('GRID', (0, -2), (-1, -1), 1, colors.Color(0.6, 0.6, 0.6)),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 30))
        
        return story

    def _criar_detalhes_adicionais_temp(self, styles):
        """Cria a seção de detalhes adicionais temporária moderna e completa"""
        story = []
        
        # Título da seção
        story.append(Paragraph("CONDIÇÕES COMERCIAIS", styles['TituloSecao']))
        story.append(Spacer(1, 15))
        
        # Condições de Prestação dos Serviços
        story.append(Paragraph("<b>CONDIÇÕES DE PRESTAÇÃO DOS SERVIÇOS</b>", styles['TextoNormal']))
        condicoes_texto = """
        • <b>Início dos Serviços:</b> Após assinatura do contrato e fornecimento da documentação completa<br/>
        • <b>Prazo de Entrega:</b> Conforme cronograma estabelecido para cada tipo de serviço<br/>
        • <b>Documentação Necessária:</b> O cliente deverá fornecer toda documentação solicitada em até 5 dias úteis<br/>
        • <b>Certificado Digital:</b> Obrigatório para serviços fiscais e deve estar sempre atualizado<br/>
        • <b>Responsabilidades:</b> O cliente é responsável pela veracidade das informações fornecidas
        """
        story.append(Paragraph(condicoes_texto, styles['TextoNormal']))
        story.append(Spacer(1, 20))
        
        # Condições de Pagamento
        story.append(Paragraph("<b>CONDIÇÕES DE PAGAMENTO</b>", styles['TextoNormal']))
        
        # Valores mock
        valor_total = 910.00
        valor_vista = valor_total * 0.95  # 5% desconto
        
        pagamento_texto = f"""
        <b>Opção 1 - À Vista (5% de desconto):</b><br/>
        • Valor: R$ {valor_vista:,.2f}<br/>
        • Formas: PIX, transferência bancária ou boleto<br/>
        • Vencimento: Na assinatura do contrato<br/><br/>
        
        <b>Opção 2 - Parcelado:</b><br/>
        • Valor: R$ {valor_total:,.2f}<br/>
        • Parcelas: Até 3x sem juros no cartão de crédito<br/>
        • Vencimento: Conforme acordo estabelecido
        """
        story.append(Paragraph(pagamento_texto, styles['TextoNormal']))
        story.append(Spacer(1, 20))
        
        # Validade da Proposta
        story.append(Paragraph("<b>VALIDADE DA PROPOSTA</b>", styles['TextoNormal']))
        validade_texto = """
        Esta proposta tem validade de <b>30 (trinta) dias</b> a partir da data de emissão. Após este período, os valores e condições poderão ser reavaliados conforme alterações de custos e legislação.
        """
        story.append(Paragraph(validade_texto, styles['TextoNormal']))
        story.append(Spacer(1, 25))
        
        return story


# Instância global do gerador
pdf_generator = PropostaPDFGenerator()
