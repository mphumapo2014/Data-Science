"""
Módulo para visualização de dados e redes
"""

import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import pandas as pd

class Visualizer:
    def __init__(self, df, network_builder=None):
        self.df = df
        self.nb = network_builder
        
    def plot_value_distribution(self, figsize=(14, 5)):
        """Distribuição dos valores das parcelas"""
        fig, axes = plt.subplots(1, 2, figsize=figsize)
        
        # Histograma
        axes[0].hist(self.df['VALOR PARCELA'], bins=50, edgecolor='black', alpha=0.7, color='skyblue')
        axes[0].set_xlabel('Valor da Parcela (R$)')
        axes[0].set_ylabel('Frequência')
        axes[0].set_title('Distribuição dos Valores das Parcelas')
        axes[0].grid(True, alpha=0.3)
        
        # Boxplot por UF (top 10)
        top_ufs = self.df['UF'].value_counts().index[:10]
        df_top = self.df[self.df['UF'].isin(top_ufs)]
        
        sns.boxplot(data=df_top, x='UF', y='VALOR PARCELA', ax=axes[1], palette='Set2')
        axes[1].set_title('Valor da Parcela por UF (Top 10)')
        axes[1].tick_params(axis='x', rotation=45)
        axes[1].set_ylabel('Valor (R$)')
        
        plt.tight_layout()
        return fig
    
    def plot_network(self, G, figsize=(12, 10), with_labels=False, node_size_factor=50):
        """Visualização da rede"""
        fig = plt.figure(figsize=figsize)
        
        # Layout
        pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
        
        # Desenhar nós (tamanho por grau)
        node_size = [G.degree(node) * node_size_factor for node in G.nodes()]
        
        # Cores por comunidade se existir
        if 'community' in list(G.nodes(data=True))[0][1]:
            communities = [G.nodes[node]['community'] for node in G.nodes()]
            nx.draw_networkx_nodes(G, pos, node_size=node_size, 
                                  node_color=communities, cmap=plt.cm.Set3, alpha=0.8)
        else:
            # Cores por UF se disponível
            try:
                uf_colors = {'SP': 0, 'RJ': 1, 'MG': 2, 'RS': 3, 'PR': 4, 'BA': 5, 'SC': 6, 'GO': 7, 'PE': 8, 'CE': 9}
                node_colors = [uf_colors.get(G.nodes[node].get('uf', 'OUT'), 10) for node in G.nodes()]
                nx.draw_networkx_nodes(G, pos, node_size=node_size, 
                                      node_color=node_colors, cmap=plt.cm.tab20, alpha=0.8)
            except:
                nx.draw_networkx_nodes(G, pos, node_size=node_size, 
                                      node_color='lightblue', alpha=0.8)
        
        # Desenhar arestas (largura por peso)
        if G.number_of_edges() > 0:
            edge_width = [G[u][v].get('weight', 1) * 2 for u, v in G.edges()]
            nx.draw_networkx_edges(G, pos, width=edge_width, alpha=0.3, edge_color='gray')
        
        if with_labels and G.number_of_nodes() <= 100:
            labels = {node: G.nodes[node].get('uf', '') for node in G.nodes()}
            nx.draw_networkx_labels(G, pos, labels, font_size=8)
        
        plt.title(f'Rede de Similaridade entre Municípios\n'
                 f'{G.number_of_nodes()} nós, {G.number_of_edges()} arestas')
        plt.axis('off')
        
        return fig
    
    def plot_uf_comparison(self, figsize=(12, 6)):
        """Comparação entre Unidades Federativas"""
        fig, axes = plt.subplots(1, 2, figsize=figsize)
        
        # Valor total por UF
        uf_total = self.df.groupby('UF')['VALOR PARCELA'].sum().sort_values(ascending=False)
        axes[0].bar(uf_total.index, uf_total.values / 1e6, color='steelblue', alpha=0.7)
        axes[0].set_xlabel('UF')
        axes[0].set_ylabel('Valor Total (Milhões R$)')
        axes[0].set_title('Valor Total por UF')
        axes[0].tick_params(axis='x', rotation=45)
        axes[0].grid(True, alpha=0.3, axis='y')
        
        # Número de beneficiários por UF
        uf_benef = self.df.groupby('UF')['NIS FAVORECIDO'].nunique().sort_values(ascending=False)
        axes[1].bar(uf_benef.index, uf_benef.values / 1e3, color='coral', alpha=0.7)
        axes[1].set_xlabel('UF')
        axes[1].set_ylabel('Beneficiários (Milhares)')
        axes[1].set_title('Número de Beneficiários por UF')
        axes[1].tick_params(axis='x', rotation=45)
        axes[1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        return fig