"""
Módulo para análises estatísticas
"""

import pandas as pd
import numpy as np
from scipy import stats

class StatisticalAnalysis:
    def __init__(self, df):
        self.df = df
    
    def descriptive_statistics(self):
        """Estatísticas descritivas completas"""
        stats_dict = {
            'geral': {
                'registros': int(len(self.df)),
                'municipios': int(self.df['CÓDIGO MUNICÍPIO SIAFI'].nunique()),
                'beneficiarios_unicos': int(self.df['NIS FAVORECIDO'].nunique()),
                'valor_total': float(self.df['VALOR PARCELA'].sum()),
                'valor_medio': float(self.df['VALOR PARCELA'].mean()),
                'valor_mediano': float(self.df['VALOR PARCELA'].median()),
                'valor_desvio_padrao': float(self.df['VALOR PARCELA'].std()),
                'valor_minimo': float(self.df['VALOR PARCELA'].min()),
                'valor_maximo': float(self.df['VALOR PARCELA'].max()),
            }
        }
        
        # Estatísticas por UF
        uf_stats = self.df.groupby('UF').agg({
            'VALOR PARCELA': ['sum', 'mean', 'std', 'count'],
            'NIS FAVORECIDO': 'nunique'
        }).round(2)
        
        uf_stats.columns = ['valor_total', 'valor_medio', 'valor_desvio', 
                           'num_parcelas', 'beneficiarios']
        
        stats_dict['por_uf'] = uf_stats.to_dict('index')
        
        # Percentis
        stats_dict['percentis'] = {
            f'p{p}': float(np.percentile(self.df['VALOR PARCELA'], p))
            for p in [10, 25, 50, 75, 90, 95, 99]
        }
        
        # Beneficiários com CPF
        com_cpf = (self.df['CPF FAVORECIDO'] != 'SEM_CPF').sum()
        stats_dict['identificacao'] = {
            'com_cpf': int(com_cpf),
            'com_cpf_percent': float(com_cpf / len(self.df) * 100),
            'apenas_nis': int(len(self.df) - com_cpf)
        }
        
        return stats_dict