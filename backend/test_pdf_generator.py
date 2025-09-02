#!/usr/bin/env python3
"""
Teste do gerador de PDF para propostas.
Este arquivo demonstra como usar o PropostaPDFGenerator.
"""

import os
import sys

# Adicionar o diretório atual ao path para importar o módulo
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.pdf_generator import pdf_generator

def test_gerar_pdf_temp():
    """Testa a geração de PDF temporário"""
    try:
        print("🔄 Gerando PDF temporário...")
        
        # Gerar PDF temporário
        caminho_pdf = pdf_generator.gerar_pdf_proposta_temp()
        
        if os.path.exists(caminho_pdf):
            print(f"✅ PDF gerado com sucesso!")
            print(f"📁 Caminho: {caminho_pdf}")
            print(f"📊 Tamanho: {os.path.getsize(caminho_pdf)} bytes")
            
            # Abrir o PDF (se possível)
            try:
                import platform
                if platform.system() == "Windows":
                    os.startfile(caminho_pdf)
                elif platform.system() == "Darwin":  # macOS
                    os.system(f"open {caminho_pdf}")
                else:  # Linux
                    os.system(f"xdg-open {caminho_pdf}")
                print("🔍 PDF aberto automaticamente!")
            except Exception as e:
                print(f"⚠️ Não foi possível abrir o PDF automaticamente: {e}")
                print(f"💡 Abra manualmente: {caminho_pdf}")
        else:
            print("❌ Erro: PDF não foi gerado")
            
    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")
        import traceback
        traceback.print_exc()

def test_gerar_pdf_com_dados():
    """Testa a geração de PDF com dados reais (se disponível)"""
    try:
        print("\n🔄 Tentando gerar PDF com dados reais...")
        
        # Tentar gerar PDF com ID 1 (exemplo)
        caminho_pdf = pdf_generator.gerar_pdf_proposta(1)
        
        if os.path.exists(caminho_pdf):
            print(f"✅ PDF com dados reais gerado com sucesso!")
            print(f"📁 Caminho: {caminho_pdf}")
            print(f"📊 Tamanho: {os.path.getsize(caminho_pdf)} bytes")
        else:
            print("⚠️ PDF temporário gerado (dados reais não disponíveis)")
            
    except Exception as e:
        print(f"⚠️ Erro ao gerar PDF com dados reais: {e}")
        print("📝 Gerando PDF temporário como fallback...")
        test_gerar_pdf_temp()

def main():
    """Função principal"""
    print("🚀 Teste do Gerador de PDF para Propostas")
    print("=" * 50)
    
    # Testar geração de PDF temporário
    test_gerar_pdf_temp()
    
    print("\n" + "=" * 50)
    
    # Tentar gerar PDF com dados reais
    test_gerar_pdf_com_dados()
    
    print("\n" + "=" * 50)
    print("✨ Teste concluído!")

if __name__ == "__main__":
    main()
