#!/usr/bin/env python3
"""
Pipeline completo de análise do Auxílio Brasil
"""

import sys
import os
import json
from datetime import datetime

# Adicionar src ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from src.data_processor import DataProcessor
from src.network_builder import AuxilioBrasilNetwork
from src.visualization import Visualizer
from src.analysis import StatisticalAnalysis
from src.export_results import ResultExporter

def main():
    print("=" * 60)
    print("ANÁLISE DO AUXÍLIO BRASIL - FEVEREIRO/2023")
    print("=" * 60)
    
    # 1. Configuração
    data_path = os.path.join(parent_dir, "data", "202302_AuxilioBrasil.csv")
    output_dir = os.path.join(parent_dir, "outputs")
    
    # Verificar se arquivo existe
    if not os.path.exists(data_path):
        print(f"ERRO: Arquivo não encontrado: {data_path}")
        print("Certifique-se de que o arquivo está em data/202302_AuxilioBrasil.csv")
        sys.exit(1)
    
    # Criar diretórios de saída
    for subdir in ["figures", "data", "reports", "networks"]:
        os.makedirs(os.path.join(output_dir, subdir), exist_ok=True)
    
    # 2. Processar dados
    print("\n[1/5] PROCESSANDO DADOS...")
    processor = DataProcessor(data_path)
    df = processor.load_data()
    df_clean = processor.clean_data()
    
    basic_stats = processor.get_basic_stats()
    print(f"  • Registros: {basic_stats['total_registros']:,}")
    print(f"  • Municípios: {basic_stats['total_municipios']:,}")
    print(f"  • Beneficiários únicos: {basic_stats['total_beneficiarios']:,}")
    print(f"  • Valor total: R$ {basic_stats['valor_total']:,.2f}")
    
    # 3. Estatísticas descritivas
    print("\n[2/5] CALCULANDO ESTATÍSTICAS...")
    stats_analyzer = StatisticalAnalysis(df_clean)
    desc_stats = stats_analyzer.descriptive_statistics()
    
    # Salvar estatísticas
    with open(os.path.join(output_dir, "data", "estatisticas_descritivas.json"), 'w') as f:
        json.dump(desc_stats, f, indent=2, ensure_ascii=False)
    print("  • estatisticas_descritivas.json salvo")
    
    # 4. Construir rede
    print("\n[3/5] CONSTRUINDO REDE DE SIMILARIDADE...")
    network = AuxilioBrasilNetwork(df_clean)
    municipio_stats = network.prepare_municipio_stats()
    G = network.build_similarity_network(similarity_threshold=0.85)
    
    # 5. Analisar rede
    print("\n[4/5] ANALISANDO REDE...")
    partition, communities = network.detect_communities()
    network_metrics = network.calculate_network_metrics()
    
    # Salvar métricas
    with open(os.path.join(output_dir, "data", "metricas_rede.json"), 'w') as f:
        json.dump(network_metrics, f, indent=2, ensure_ascii=False, default=str)
    print("  • metricas_rede.json salvo")
    
    # 6. Visualizações
    print("\n[5/5] GERANDO VISUALIZAÇÕES...")
    viz = Visualizer(df_clean, network)
    
    # Gráficos
    fig1 = viz.plot_value_distribution()
    fig1.savefig(os.path.join(output_dir, "figures", "distribuicao_valores.png"), 
                 dpi=300, bbox_inches='tight')
    print("  • distribuicao_valores.png salvo")
    
    if G.number_of_nodes() > 0:
        fig2 = viz.plot_network(G, with_labels=False)
        fig2.savefig(os.path.join(output_dir, "figures", "rede_municipios.png"), 
                     dpi=300, bbox_inches='tight')
        print("  • rede_municipios.png salvo")
    
    fig3 = viz.plot_uf_comparison()
    fig3.savefig(os.path.join(output_dir, "figures", "comparacao_uf.png"), 
                 dpi=300, bbox_inches='tight')
    print("  • comparacao_uf.png salvo")
    
    # 7. Exportar resultados
    print("\n[6/6] EXPORTANDO RESULTADOS...")
    exporter = ResultExporter(output_dir)
    
    # Exportar DataFrames
    municipio_stats_df = pd.DataFrame(municipio_stats)
    exporter.export_dataframes({
        'municipio_stats': municipio_stats_df
    })
    
    # Exportar rede
    if G is not None:
        exporter.export_network(G, 'rede_municipios')
    
    # Gerar relatório
    exporter.generate_report(desc_stats, network_metrics, communities)
    
    print("\n" + "=" * 60)
    print("✅ ANÁLISE CONCLUÍDA COM SUCESSO!")
    print(f"📁 Resultados salvos em: {output_dir}/")
    print("=" * 60)

if __name__ == "__main__":
    main()