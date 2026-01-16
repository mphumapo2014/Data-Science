"""
Módulo para exportação de resultados
"""

import json
import pandas as pd
import networkx as nx
from datetime import datetime

class ResultExporter:
    def __init__(self, output_dir='outputs'):
        self.output_dir = output_dir
    
    def export_dataframes(self, dataframes_dict):
        """Exporta DataFrames para CSV"""
        for name, df in dataframes_dict.items():
            if isinstance(df, pd.DataFrame):
                filepath = f"{self.output_dir}/data/{name}.csv"
                df.to_csv(filepath, index=False, encoding='utf-8')
                print(f"  • {name}.csv salvo")
    
    def export_network(self, G, filename):
        """Exporta rede para GraphML"""
        try:
            nx.write_graphml(G, f"{self.output_dir}/networks/{filename}.graphml")
            print(f"  • {filename}.graphml salvo")
        except Exception as e:
            print(f"  • Erro ao salvar GraphML: {e}")
    
    def generate_report(self, desc_stats, network_metrics, communities=None):
        """Gera relatório simples em texto"""
        report = f"""
        RELATÓRIO DE ANÁLISE - AUXÍLIO BRASIL
        Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        
        1. ESTATÍSTICAS GERAIS:
        -------------------------
        • Registros totais: {desc_stats.get('geral', {}).get('registros', 0):,}
        • Municípios: {desc_stats.get('geral', {}).get('municipios', 0):,}
        • Beneficiários únicos: {desc_stats.get('geral', {}).get('beneficiarios_unicos', 0):,}
        • Valor total distribuído: R$ {desc_stats.get('geral', {}).get('valor_total', 0):,.2f}
        • Valor médio da parcela: R$ {desc_stats.get('geral', {}).get('valor_medio', 0):,.2f}
        
        2. MÉTRICAS DA REDE:
        ---------------------
        • Nós: {network_metrics.get('num_nodes', 0)}
        • Arestas: {network_metrics.get('num_edges', 0)}
        • Densidade: {network_metrics.get('density', 0):.4f}
        • Grau médio: {network_metrics.get('avg_degree', 0):.2f}
        • Coeficiente de agrupamento: {network_metrics.get('avg_clustering', 0):.3f}
        • Componentes conectados: {network_metrics.get('connected_components', 0)}
        """
        
        if communities:
            report += f"""
        3. COMUNIDADES DETECTADAS:
        ---------------------------
        • Número de comunidades: {len(communities)}
        """
        
        # Salvar relatório
        with open(f"{self.output_dir}/reports/relatorio_analise.txt", 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"  • relatorio_analise.txt salvo")