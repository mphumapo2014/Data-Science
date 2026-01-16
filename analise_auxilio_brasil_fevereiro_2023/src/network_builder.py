"""
Módulo para construção e análise de redes do Auxílio Brasil
"""

import pandas as pd
import numpy as np
import networkx as nx
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

try:
    import community as community_louvain
    LOUVAIN_AVAILABLE = True
except ImportError:
    LOUVAIN_AVAILABLE = False
    print("Aviso: python-louvain não instalado. Use: pip install python-louvain")

class AuxilioBrasilNetwork:
    def __init__(self, df):
        """
        Inicializa com DataFrame do Auxílio Brasil
        
        Args:
            df: DataFrame com colunas do Auxílio Brasil
        """
        self.df = df
        self.municipio_stats = None
        self.G = None
        
    def prepare_municipio_stats(self):
        """
        Prepara estatísticas agregadas por município
        """
        print("Preparando estatísticas por município...")
        
        # Agrupar por município
        self.municipio_stats = self.df.groupby(['CÓDIGO MUNICÍPIO SIAFI', 'NOME MUNICÍPIO', 'UF']).agg({
            'VALOR PARCELA': ['mean', 'std', 'sum', 'count'],
            'NIS FAVORECIDO': 'nunique',
            'CPF FAVORECIDO': lambda x: (x != 'SEM_CPF').sum() if 'SEM_CPF' in str(x) else x.notna().sum()
        }).reset_index()
        
        # Ajustar nomes das colunas
        self.municipio_stats.columns = [
            'cod_municipio', 'nome_municipio', 'uf',
            'valor_mean', 'valor_std', 'valor_total', 'num_parcelas',
            'beneficiarios_unicos', 'com_cpf'
        ]
        
        # Calcular proporções
        self.municipio_stats['proporcao_cpf'] = self.municipio_stats['com_cpf'] / self.municipio_stats['beneficiarios_unicos']
        self.municipio_stats['valor_per_capita'] = self.municipio_stats['valor_total'] / self.municipio_stats['beneficiarios_unicos']
        
        # Tratar valores infinitos/NaN
        self.municipio_stats = self.municipio_stats.replace([np.inf, -np.inf], np.nan).fillna(0)
        
        print(f"Estatísticas preparadas para {len(self.municipio_stats)} municípios")
        return self.municipio_stats
    
    def build_similarity_network(self, similarity_threshold=0.85):
        """
        Constrói rede de similaridade entre municípios
        
        Args:
            similarity_threshold: Limiar mínimo de similaridade para criar aresta
            
        Returns:
            networkx.Graph: Grafo da rede
        """
        if self.municipio_stats is None:
            self.prepare_municipio_stats()
        
        print(f"Construindo rede com threshold {similarity_threshold}...")
        self.G = nx.Graph()
        
        # Adicionar nós com atributos
        for _, row in self.municipio_stats.iterrows():
            self.G.add_node(
                str(row['cod_municipio']),  # Converter para string
                nome_municipio=row['nome_municipio'],
                uf=row['uf'],
                valor_mean=float(row['valor_mean']),
                beneficiarios=int(row['beneficiarios_unicos']),
                valor_total=float(row['valor_total'])
            )
        
        # Features para similaridade
        features = self.municipio_stats[[
            'valor_mean', 'beneficiarios_unicos', 
            'proporcao_cpf', 'valor_per_capita'
        ]].fillna(0)
        
        # Normalizar
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Calcular similaridade cosseno
        print("Calculando matriz de similaridade...")
        similarity_matrix = cosine_similarity(features_scaled)
        
        # Adicionar arestas
        n = len(self.municipio_stats)
        edges_added = 0
        
        print(f"Processando {n} municípios...")
        for i in range(n):
            for j in range(i+1, n):
                similarity = similarity_matrix[i][j]
                
                if similarity > similarity_threshold:
                    cod_i = str(self.municipio_stats.iloc[i]['cod_municipio'])
                    cod_j = str(self.municipio_stats.iloc[j]['cod_municipio'])
                    
                    self.G.add_edge(
                        cod_i, cod_j,
                        weight=float(similarity),
                        distance=float(1-similarity)
                    )
                    edges_added += 1
        
        print(f"✓ Rede construída: {self.G.number_of_nodes()} nós, {edges_added} arestas")
        return self.G
    
    def detect_communities(self):
        """
        Detecta comunidades na rede usando Louvain
        
        Returns:
            tuple: (partition dict, communities dict)
        """
        if self.G is None:
            raise ValueError("Construa a rede primeiro com build_similarity_network()")
        
        if not LOUVAIN_AVAILABLE:
            print("Aviso: python-louvain não instalado. Instale para detecção de comunidades.")
            return {}, {}
        
        # Usar algoritmo de Louvain
        print("Detectando comunidades com algoritmo de Louvain...")
        partition = community_louvain.best_partition(self.G, weight='weight')
        
        # Adicionar comunidade como atributo dos nós
        nx.set_node_attributes(self.G, partition, 'community')
        
        # Estatísticas das comunidades
        communities = {}
        for node, comm_id in partition.items():
            if comm_id not in communities:
                communities[comm_id] = []
            communities[comm_id].append(node)
        
        print(f"✓ Detectadas {len(communities)} comunidades")
        return partition, communities
    
    def calculate_network_metrics(self):
        """
        Calcula métricas importantes da rede
        
        Returns:
            dict: Dicionário com métricas da rede
        """
        if self.G is None:
            raise ValueError("Construa a rede primeiro com build_similarity_network()")
        
        print("Calculando métricas da rede...")
        metrics = {
            'num_nodes': self.G.number_of_nodes(),
            'num_edges': self.G.number_of_edges(),
            'density': float(nx.density(self.G)),
            'avg_degree': float(np.mean([d for _, d in self.G.degree()])),
            'avg_clustering': float(nx.average_clustering(self.G)),
            'connected_components': nx.number_connected_components(self.G),
        }
        
        # Apenas para redes não vazias
        if metrics['num_edges'] > 0:
            # Encontrar maior componente conectado
            largest_cc = max(nx.connected_components(self.G), key=len)
            subgraph = self.G.subgraph(largest_cc)
            
            if len(largest_cc) > 1:
                try:
                    metrics['avg_shortest_path'] = float(nx.average_shortest_path_length(subgraph))
                except (nx.NetworkXError, ZeroDivisionError):
                    metrics['avg_shortest_path'] = None
            
            # Centralidade
            degree_centrality = nx.degree_centrality(self.G)
            betweenness_centrality = nx.betweenness_centrality(self.G, weight='weight')
            
            # Top 10 municípios por centralidade
            metrics['top_degree_centrality'] = [
                (node, float(value)) 
                for node, value in sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
            
            metrics['top_betweenness_centrality'] = [
                (node, float(value)) 
                for node, value in sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
        
        print("✓ Métricas calculadas")
        return metrics