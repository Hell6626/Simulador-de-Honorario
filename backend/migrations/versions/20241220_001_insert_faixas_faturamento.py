"""Insert faixas de faturamento

Revision ID: 20241220_001
Revises: d40f383ff0d1
Create Date: 2024-12-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20241220_001'
down_revision = '20241220_000'
branch_labels = None
depends_on = None


def upgrade():
    """Inserir faixas de faturamento para os regimes tributários"""
    
    # Importar a função de inicialização
    from models import inicializar_faixas_faturamento
    
    # Executar a inicialização das faixas
    print("🔄 Inicializando faixas de faturamento...")
    resultado = inicializar_faixas_faturamento()
    
    if resultado:
        print("✅ Faixas de faturamento inseridas com sucesso!")
    else:
        print("❌ Erro ao inserir faixas de faturamento")


def downgrade():
    """Remover faixas de faturamento"""
    
    # Conectar ao banco
    connection = op.get_bind()
    
    # Remover todas as faixas de faturamento
    print("🔄 Removendo faixas de faturamento...")
    
    # Primeiro, remover as faixas dos regimes específicos
    regimes_codigos = ['SN', 'LP', 'LR', 'MEI']
    
    for codigo in regimes_codigos:
        # Buscar o regime
        regime = connection.execute(
            sa.text("SELECT id FROM regime_tributario WHERE codigo = :codigo"),
            {"codigo": codigo}
        ).fetchone()
        
        if regime:
            # Remover faixas deste regime
            connection.execute(
                sa.text("DELETE FROM faixa_faturamento WHERE regime_tributario_id = :regime_id"),
                {"regime_id": regime[0]}
            )
            print(f"✅ Faixas removidas para o regime {codigo}")
        else:
            print(f"⚠️  Regime {codigo} não encontrado")
    
    print("✅ Todas as faixas de faturamento foram removidas!")
