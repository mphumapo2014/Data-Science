"""
ANÁLISE DE REDES DE CONVÊNIOS PÚBLICOS

OBJETIVO:
Analisar a rede de convênios públicos federais a partir da relação
entre órgãos concedentes e convenentes, utilizando técnicas de
Análise de Redes Complexas, estatística descritiva e visualização
de dados.

FONTE DOS DADOS:
Portal da Transparência do Governo Federal – Convênios

Dados disponíveis em:
https://portaldatransparencia.gov.br/download-de-dados/convenios

Data de download/acesso:
14/01/2026

OBSERVAÇÕES:
- Os dados são públicos e foram utilizados exclusivamente para fins
  acadêmicos e de avaliação técnica.
- O tratamento inclui limpeza, conversão de valores monetários e
  filtragem dos órgãos mais relevantes para análise de rede.

TECNOLOGIAS UTILIZADAS:
- Python
- Pandas, NumPy
- NetworkX
- Matplotlib, Seaborn
- Louvain Community Detection

Autor: Lourenço Jamba Mphili
"""

### ⚠️ Aviso sobre o Arquivo de Dados
# 
# **O arquivo CSV original não está incluído neste repositório** devido ao seu tamanho (aproximadamente 323 MB).
# Para executar a análise completa:
#
# 1. **Baixe os dados diretamente do Portal da Transparência:**
#    - Acesse: https://portaldatransparencia.gov.br/download-de-dados/convenios
#    - Baixe o arquivo referente ao período desejado
#    - Coloque o arquivo CSV na raiz do projeto
#
# 2. **Script principal para download alternativo:**
#    - Devido ao tamanho do arquivo CSV, disponibilizei o arquivo usado na análise neste link do Google Drive:
#      📥 Download do CSV: https://drive.google.com/file/d/1Bl1a0zvKIXzImwprm3rsB-XZBd1MkFUa/view?usp=sharing
#    - Após baixar, coloque o arquivo CSV na pasta principal do projeto
#


import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
from community import community_louvain  # python-louvain

# ============================================================================
# CONFIGURAÇÕES INICIAIS
# ============================================================================

def configurar_ambiente():
    """Configura o ambiente de plotagem e exibição"""
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette("husl")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.float_format', lambda x: f'R$ {x:,.2f}')
    
    # Criar diretórios de saída
    os.makedirs('outputs/graficos', exist_ok=True)
    os.makedirs('outputs/dados_processados', exist_ok=True)
    
    print("=" * 70)
    print("ANÁLISE DE REDES DE CONVÊNIOS PÚBLICOS")
    print(f"Execução: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 70)

# ============================================================================
# CARREGAMENTO E LIMPEZA DOS DADOS
# ============================================================================

def carregar_dados(caminho_arquivo):
    """Carrega e prepara os dados dos convênios"""
    print("\n[1/5] CARREGANDO DADOS...")
    
    # Carregar CSV
    df = pd.read_csv(caminho_arquivo, delimiter=';', encoding='latin1', low_memory=False)
    print(f"   • Arquivo carregado: {caminho_arquivo}")
    print(f"   • Registros: {len(df):,}")
    print(f"   • Colunas: {len(df.columns)}")
    
    # Converter valores para numérico
    df['VALOR_CONVENIO_NUM'] = df['VALOR CONVÊNIO'].str.replace(',', '.').astype(float)
    df['VALOR_LIBERADO_NUM'] = df['VALOR LIBERADO'].str.replace(',', '.').astype(float)
    
    # Informações básicas
    print(f"\n   • Órgãos únicos: {df['NOME ÓRGÃO CONCEDENTE'].nunique():,}")
    print(f"   • Convenentes únicos: {df['NOME CONVENENTE'].nunique():,}")
    print(f"   • Valor total: R$ {df['VALOR_CONVENIO_NUM'].sum():,.2f}")
    
    return df

# ============================================================================
# PRÉ-PROCESSAMENTO PARA ANÁLISE DE REDES
# ============================================================================

def preparar_dados_rede(df, top_n_orgaos=50):
    """Prepara os dados para construção da rede"""
    print(f"\n[2/5] PREPARANDO DADOS PARA REDE (top {top_n_orgaos} órgãos)...")
    
    # Selecionar órgãos mais ativos
    top_orgaos = df['NOME ÓRGÃO CONCEDENTE'].value_counts().head(top_n_orgaos).index
    df_filtrado = df[df['NOME ÓRGÃO CONCEDENTE'].isin(top_orgaos)].copy()
    
    print(f"   • Convênios após filtro: {len(df_filtrado):,}")
    print(f"   • Órgãos analisados: {len(top_orgaos)}")
    
    # Criar dataframe de conexões
    conexoes = df_filtrado[[
        'NOME ÓRGÃO CONCEDENTE', 
        'NOME CONVENENTE',
        'VALOR_CONVENIO_NUM',
        'UF'
    ]].copy()
    
    conexoes.columns = ['orgao', 'convenente', 'valor', 'uf']
    
    return conexoes, df_filtrado

# ============================================================================
# CONSTRUÇÃO E ANÁLISE DA REDE
# ============================================================================

def construir_e_analisar_rede(conexoes):
    """Constrói a rede e calcula métricas"""
    print("\n[3/5] CONSTRUINDO E ANALISANDO REDE...")
    
    # Criar grafo bipartido
    G = nx.Graph()
    
    # Adicionar nós e arestas
    for _, row in conexoes.iterrows():
        # Nó do órgão
        if not G.has_node(row['orgao']):
            G.add_node(row['orgao'], tipo='orgao')
        
        # Nó do convenente
        if not G.has_node(row['convenente']):
            G.add_node(row['convenente'], tipo='convenente', uf=row['uf'])
        
        # Aresta (atualizar peso se existir)
        if G.has_edge(row['orgao'], row['convenente']):
            G[row['orgao']][row['convenente']]['weight'] += row['valor']
        else:
            G.add_edge(row['orgao'], row['convenente'], weight=row['valor'])
    
    # Informações da rede
    print(f"   • Nós totais: {G.number_of_nodes():,}")
    print(f"   • Arestas totais: {G.number_of_edges():,}")
    print(f"   • Densidade: {nx.density(G):.6f}")
    
    return G

def calcular_metricas(G):
    """Calcula métricas de centralidade"""
    print("\n   • Calculando métricas de centralidade...")
    
    # Separar órgãos
    orgaos = [n for n, attr in G.nodes(data=True) if attr['tipo'] == 'orgao']
    
    # Degree centrality
    degree_cent = nx.degree_centrality(G)
    
    # Criar dataframe de métricas
    metricas = []
    for orgao in orgaos:
        grau = G.degree(orgao)
        valor_total = sum(G[orgao][vizinho]['weight'] for vizinho in G.neighbors(orgao))
        
        metricas.append({
            'orgao': orgao,
            'grau': grau,
            'degree_centrality': degree_cent.get(orgao, 0),
            'valor_total': valor_total,
            'num_convenentes': len(list(G.neighbors(orgao)))
        })
    
    df_metricas = pd.DataFrame(metricas)
    df_metricas = df_metricas.sort_values('valor_total', ascending=False)
    
    return df_metricas

# ============================================================================
# VISUALIZAÇÕES
# ============================================================================

def criar_visualizacoes(G, df_metricas, conexoes):
    """Cria gráficos e visualizações"""
    print("\n[4/5] CRIANDO VISUALIZAÇÕES...")
    
    # 1. TOP 10 ÓRGÃOS POR VALOR
    plt.figure(figsize=(12, 6))
    top_10 = df_metricas.head(10)
    
    bars = plt.barh(range(len(top_10)), top_10['valor_total'], color='steelblue')
    plt.yticks(range(len(top_10)), [orgao[:40] + '...' if len(orgao) > 40 else orgao 
                                    for orgao in top_10['orgao']])
    plt.xlabel('Valor Total (R$)')
    plt.title('Top 10 Órgãos por Valor em Convênios', fontsize=14, fontweight='bold')
    
    # Adicionar valores nas barras
    for i, bar in enumerate(bars):
        valor = top_10.iloc[i]['valor_total']
        plt.text(bar.get_width() * 0.5, bar.get_y() + bar.get_height()/2,
                f'R$ {valor:,.0f}', 
                ha='center', va='center', color='white', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('outputs/graficos/top10_orgaos_valor.png', dpi=300, bbox_inches='tight')
    print("   ✓ Gráfico 1 salvo: top10_orgaos_valor.png")
    
    # 2. DISTRIBUIÇÃO POR UF
    plt.figure(figsize=(14, 7))
    
    # Calcular estatísticas por UF
    uf_stats = conexoes.groupby('uf').agg({
        'valor': ['sum', 'count'],
        'orgao': 'nunique'
    }).round(2)
    
    uf_stats.columns = ['valor_total', 'num_convenios', 'num_orgaos']
    uf_stats = uf_stats.sort_values('valor_total', ascending=False)
    
    # Gráfico de barras
    ax1 = plt.subplot(1, 2, 1)
    ax1.bar(uf_stats.index, uf_stats['valor_total'], color='darkorange')
    ax1.set_xlabel('UF')
    ax1.set_ylabel('Valor Total (R$)')
    ax1.set_title('Valor Total por UF', fontweight='bold')
    ax1.tick_params(axis='x', rotation=45)
    
    # Gráfico de pizza (top 5 UFs)
    ax2 = plt.subplot(1, 2, 2)
    top_5_ufs = uf_stats.head(5)
    ax2.pie(top_5_ufs['valor_total'], 
            labels=top_5_ufs.index, 
            autopct='%1.1f%%',
            startangle=90,
            colors=sns.color_palette("Set2"))
    ax2.set_title('Distribuição entre Top 5 UFs', fontweight='bold')
    
    plt.suptitle('Análise Geográfica dos Convênios', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('outputs/graficos/distribuicao_uf.png', dpi=300, bbox_inches='tight')
    print("   ✓ Gráfico 2 salvo: distribuicao_uf.png")
    
    # 3. REDE SIMPLIFICADA (apenas órgãos)
    plt.figure(figsize=(14, 10))
    
    # Criar subgrafo apenas com órgãos
    G_orgaos = nx.Graph()
    orgaos = [n for n, attr in G.nodes(data=True) if attr['tipo'] == 'orgao']
    
    # Adicionar nós
    for orgao in orgaos:
        G_orgaos.add_node(orgao, valor_total=df_metricas[df_metricas['orgao'] == orgao]['valor_total'].values[0])
    
    # Conectar órgãos que compartilham convenentes
    for i, orgao1 in enumerate(orgaos):
        convenentes1 = set(G.neighbors(orgao1))
        for orgao2 in orgaos[i+1:]:
            convenentes2 = set(G.neighbors(orgao2))
            overlap = len(convenentes1.intersection(convenentes2))
            if overlap > 0:
                G_orgaos.add_edge(orgao1, orgao2, weight=overlap)
    
    # Layout e visualização
    pos = nx.spring_layout(G_orgaos, k=0.8, iterations=100, seed=42)
    
    # Tamanho dos nós proporcional ao valor total
    node_sizes = [G_orgaos.nodes[n]['valor_total'] / 1000000 for n in G_orgaos.nodes()]
    
    # Desenhar
    nx.draw_networkx_nodes(G_orgaos, pos, 
                          node_size=node_sizes, 
                          node_color='lightcoral',
                          alpha=0.8,
                          linewidths=1,
                          edgecolors='darkred')
    
    nx.draw_networkx_edges(G_orgaos, pos, 
                          width=0.5, 
                          alpha=0.3,
                          edge_color='gray')
    
    # Labels apenas para nós grandes
    large_nodes = [n for n in G_orgaos.nodes() if node_sizes[list(G_orgaos.nodes()).index(n)] > 50]
    labels = {n: n[:25] + '...' if len(n) > 25 else n for n in large_nodes}
    nx.draw_networkx_labels(G_orgaos, pos, labels, font_size=8, font_weight='bold')
    
    plt.title('Rede de Colaboração entre Órgãos Públicos\n(Tamanho ∝ Valor Total, Conexões = Convenentes Compartilhados)', 
             fontsize=14, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('outputs/graficos/rede_colaboracao.png', dpi=300, bbox_inches='tight')
    print("   ✓ Gráfico 3 salvo: rede_colaboracao.png")
    
    # 4. HISTOGRAMA DE DISTRIBUIÇÃO
    plt.figure(figsize=(12, 5))
    
    # Distribuição do valor dos convênios
    plt.subplot(1, 2, 1)
    plt.hist(conexoes['valor'], bins=50, log=True, alpha=0.7, color='seagreen')
    plt.xlabel('Valor do Convênio (R$)')
    plt.ylabel('Frequência (log)')
    plt.title('Distribuição dos Valores dos Convênios', fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    # Distribuição do grau dos órgãos
    plt.subplot(1, 2, 2)
    plt.hist(df_metricas['grau'], bins=20, alpha=0.7, color='mediumpurple')
    plt.xlabel('Grau (Número de Conexões)')
    plt.ylabel('Frequência')
    plt.title('Distribuição do Grau dos Órgãos', fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    plt.suptitle('Distribuições Estatísticas', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('outputs/graficos/distribuicoes.png', dpi=300, bbox_inches='tight')
    print("   ✓ Gráfico 4 salvo: distribuicoes.png")
    
    plt.close('all')  # Fechar todas as figuras

# ============================================================================
# EXPORTAÇÃO DE RESULTADOS
# ============================================================================

def exportar_resultados(G, df_metricas, conexoes):
    """Exporta resultados para arquivos"""
    print("\n[5/5] EXPORTANDO RESULTADOS...")
    
    # 1. Salvar métricas principais
    df_metricas.to_csv('outputs/dados_processados/metricas_orgaos.csv', 
                      index=False, encoding='utf-8-sig')
    print("   ✓ Arquivo 1: metricas_orgaos.csv")
    
    # 2. Salvar conexões (edges)
    edges_data = []
    for u, v, data in G.edges(data=True):
        if G.nodes[u]['tipo'] == 'orgao':
            edges_data.append({
                'orgao': u,
                'convenente': v,
                'valor_total': data['weight'],
                'uf': G.nodes[v].get('uf', 'N/A')
            })
    
    pd.DataFrame(edges_data).to_csv('outputs/dados_processados/conexoes_rede.csv', 
                                   index=False, encoding='utf-8-sig')
    print("   ✓ Arquivo 2: conexoes_rede.csv")
    
    # 3. Salvar grafo para Gephi (opcional)
    try:
        nx.write_gexf(G, 'outputs/dados_processados/rede_convenios.gexf')
        print("   ✓ Arquivo 3: rede_convenios.gexf (para Gephi)")
    except:
        print("   ! Não foi possível salvar arquivo GEXF")
    
    # 4. Criar relatório de análise
    criar_relatorio_analise(df_metricas, conexoes)
    
    print("\n" + "=" * 70)
    print("ANÁLISE CONCLUÍDA COM SUCESSO!")
    print("=" * 70)

def criar_relatorio_analise(df_metricas, conexoes):
    """Cria um relatório textual com os principais insights"""
    relatorio = f"""
    ====================================================
    RELATÓRIO DE ANÁLISE - REDES DE CONVÊNIOS PÚBLICOS
    ====================================================
    Data da análise: {datetime.now().strftime('%d/%m/%Y %H:%M')}
    Total de conexões analisadas: {len(conexoes):,}
    
    PRINCIPAIS INSIGHTS:
    ====================
    
    1. ÓRGÃO MAIS ATIVO:
       • Nome: {df_metricas.iloc[0]['orgao'][:80]}
       • Valor total: R$ {df_metricas.iloc[0]['valor_total']:,.2f}
       • Número de parceiros: {df_metricas.iloc[0]['num_convenentes']:,}
    
    2. TOP 3 ÓRGÃOS POR VALOR:
       1. {df_metricas.iloc[0]['orgao'][:60]}: R$ {df_metricas.iloc[0]['valor_total']:,.2f}
       2. {df_metricas.iloc[1]['orgao'][:60]}: R$ {df_metricas.iloc[1]['valor_total']:,.2f}
       3. {df_metricas.iloc[2]['orgao'][:60]}: R$ {df_metricas.iloc[2]['valor_total']:,.2f}
    
    3. DISTRIBUIÇÃO GEOGRÁFICA:
       • UFs com mais convênios: {conexoes['uf'].value_counts().head(3).index.tolist()}
       • Total de UFs atendidas: {conexoes['uf'].nunique()}
    
    4. ESTATÍSTICAS GERAIS:
       • Valor médio por convênio: R$ {conexoes['valor'].mean():,.2f}
       • Mediana do valor: R$ {conexoes['valor'].median():,.2f}
       • Maior convênio individual: R$ {conexoes['valor'].max():,.2f}
       • Órgãos analisados: {len(df_metricas)}
    
    5. CONCENTRAÇÃO DE RECURSOS:
       • Top 10 órgãos concentram: {(df_metricas.head(10)['valor_total'].sum() / df_metricas['valor_total'].sum() * 100):.1f}% do valor total
       • Top 5 órgãos concentram: {(df_metricas.head(5)['valor_total'].sum() / df_metricas['valor_total'].sum() * 100):.1f}% do valor total
    
    RECOMENDAÇÕES PARA ANÁLISE FUTURA:
    ==================================
    1. Investigar os órgãos mais centrais para entender padrões de atuação
    2. Analisar clusters/communities na rede para identificar grupos de colaboração
    3. Cruzar com dados socioeconômicos para verificar correlações
    4. Estudo longitudinal: como a rede evolui ao longo do tempo
    
    ====================================================
    """
    
    with open('outputs/relatorio_analise.txt', 'w', encoding='utf-8') as f:
        f.write(relatorio)
    
    print("   ✓ Relatório: relatorio_analise.txt")

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Função principal do script"""
    try:
        # Configurar ambiente
        configurar_ambiente()
        
        # Carregar dados
        df = carregar_dados('20260109_Convenios.csv')
        
        # Preparar dados para rede
        conexoes, df_filtrado = preparar_dados_rede(df, top_n_orgaos=50)
        
        # Construir e analisar rede
        G = construir_e_analisar_rede(conexoes)
        df_metricas = calcular_metricas(G)
        
        # Criar visualizações
        criar_visualizacoes(G, df_metricas, conexoes)
        
        # Exportar resultados
        exportar_resultados(G, df_metricas, conexoes)
        
        # Mostrar resumo no console
        print("\n" + "=" * 70)
        print("RESUMO FINAL DA ANÁLISE")
        print("=" * 70)
        print(f"• Arquivos processados: 1")
        print(f"• Gráficos gerados: 4")
        print(f"• Arquivos exportados: 3")
        print(f"• Órgãos analisados: {len(df_metricas)}")
        print(f"• Conexões mapeadas: {len(conexoes):,}")
        print(f"• Valor total analisado: R$ {conexoes['valor'].sum():,.2f}")
        
        # Mostrar top 5 órgãos
        print("\nTOP 5 ÓRGÃOS (por valor total):")
        for i, (_, row) in enumerate(df_metricas.head(5).iterrows(), 1):
            print(f"  {i}. {row['orgao'][:50]:50} R$ {row['valor_total']:>15,.2f}")
        
        print("\n✅ Análise concluída! Verifique a pasta 'outputs' para resultados.")
        
    except FileNotFoundError:
        print("\n❌ ERRO: Arquivo 'dados/20260109_Convenios.csv' não encontrado!")
        print("   Certifique-se de que:")
        print("   1. O arquivo está na pasta 'dados/'")
        print("   2. O nome do arquivo está correto")
        print("   3. Você está executando o script da pasta correta")
        
    except Exception as e:
        print(f"\n❌ ERRO inesperado: {e}")
        print("   Tipo do erro:", type(e).__name__)

# ============================================================================
# EXECUÇÃO
# ============================================================================

if __name__ == "__main__":
    main()