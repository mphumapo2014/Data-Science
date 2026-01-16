#!/usr/bin/env python3
"""
Análise exploratória rápida dos dados
"""

import pandas as pd
import matplotlib.pyplot as plt
import sys

def quick_explore(filepath):
    """Análise rápida do dataset"""
    
    print("📊 ANÁLISE EXPLORATÓRIA RÁPIDA")
    print("=" * 50)
    
    # Carregar dados
    df = pd.read_csv(filepath, sep=';', encoding='utf-8', low_memory=False)
    
    print(f"\n📁 DADOS BRUTOS:")
    print(f"• Registros: {len(df):,}")
    print(f"• Colunas: {len(df.columns)}")
    print(f"• Período: {df['MÊS COMPETÊNCIA'].iloc[0] if len(df) > 0 else 'N/A'}")
    
    print(f"\n📈 ESTATÍSTICAS BÁSICAS:")
    print(df[['VALOR PARCELA']].describe().round(2))
    
    print(f"\n🗺️  DISTRIBUIÇÃO GEOGRÁFICA:")
    print(f"• UFs: {df['UF'].nunique()}")
    print(f"• Municípios: {df['CÓDIGO MUNICÍPIO SIAFI'].nunique()}")
    
    # Top 10 municípios por valor total
    top_municipios = df.groupby(['CÓDIGO MUNICÍPIO SIAFI', 'NOME MUNICÍPIO']).agg({
        'VALOR PARCELA': 'sum',
        'NIS FAVORECIDO': 'nunique'
    }).nlargest(10, 'VALOR PARCELA')
    
    print(f"\n🏆 TOP 10 MUNICÍPIOS (VALOR TOTAL):")
    for idx, (cod, nome) in enumerate(top_municipios.index, 1):
        valor = top_municipios.loc[(cod, nome), 'VALOR PARCELA']
        beneficiarios = top_municipios.loc[(cod, nome), 'NIS FAVORECIDO']
        print(f"{idx:2d}. {nome[:30]:30} R$ {valor:12,.2f} ({beneficiarios:6,} ben.)")
    
    # Distribuição por UF
    print(f"\n📊 DISTRIBUIÇÃO POR UF:")
    uf_dist = df.groupby('UF').agg({
        'VALOR PARCELA': ['sum', 'mean', 'count'],
        'NIS FAVORECIDO': 'nunique'
    }).round(2)
    
    uf_dist.columns = ['valor_total', 'valor_medio', 'num_parcelas', 'beneficiarios']
    print(uf_dist.sort_values('valor_total', ascending=False))
    
    # Plot rápido
    plt.figure(figsize=(10, 6))
    df['VALOR PARCELA'].hist(bins=50, edgecolor='black', alpha=0.7)
    plt.title('Distribuição do Valor da Parcela - Auxílio Brasil')
    plt.xlabel('Valor (R$)')
    plt.ylabel('Frequência')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('distribuicao_rapida.png', dpi=150)
    
    print(f"\n✅ Gráfico salvo como: distribuicao_rapida.png")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python explore_data.py <caminho_para_csv>")
        sys.exit(1)
    
    quick_explore(sys.argv[1])