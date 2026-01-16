"""
Módulo para processamento de dados do Auxílio Brasil
"""

import pandas as pd
import numpy as np

class DataProcessor:
    """Processa e limpa dados do Auxílio Brasil"""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = None
    
    def load_data(self):
        """Carrega dados do CSV"""
        print(f"Carregando dados de: {self.filepath}")
        
        try:
            # Tentar detectar encoding automaticamente
            self.df = pd.read_csv(
                self.filepath, 
                sep=';', 
                encoding='utf-8',
                low_memory=False,
                dtype={
                    'CÓDIGO MUNICÍPIO SIAFI': str,
                    'CPF FAVORECIDO': str,
                    'NIS FAVORECIDO': str
                }
            )
            
            print(f"✓ Dados carregados: {len(self.df):,} registros")
            return self.df
            
        except UnicodeDecodeError:
            print("Tentando encoding latin-1...")
            self.df = pd.read_csv(
                self.filepath, 
                sep=';', 
                encoding='latin-1',
                low_memory=False,
                dtype={
                    'CÓDIGO MUNICÍPIO SIAFI': str,
                    'CPF FAVORECIDO': str,
                    'NIS FAVORECIDO': str
                }
            )
            print(f"✓ Dados carregados com latin-1: {len(self.df):,} registros")
            return self.df
    
    def clean_data(self):
        """Limpeza básica dos dados"""
        if self.df is None:
            self.load_data()
        
        print("Limpando dados...")
        
        # Converter tipos
        self.df['VALOR PARCELA'] = pd.to_numeric(
            self.df['VALOR PARCELA'].astype(str).str.replace(',', '.'), 
            errors='coerce'
        )
        
        # Remover valores nulos ou zerados
        initial_count = len(self.df)
        self.df = self.df.dropna(subset=['VALOR PARCELA', 'NOME FAVORECIDO'])
        self.df = self.df[self.df['VALOR PARCELA'] > 0]
        
        # Remover duplicatas se houver
        self.df = self.df.drop_duplicates()
        
        # Tratar valores nulos em identificadores
        self.df['CPF FAVORECIDO'] = self.df['CPF FAVORECIDO'].fillna('SEM_CPF')
        self.df['NIS FAVORECIDO'] = self.df['NIS FAVORECIDO'].fillna('SEM_NIS')
        
        # Limpar strings
        self.df['NOME FAVORECIDO'] = self.df['NOME FAVORECIDO'].str.strip().str.upper()
        self.df['NOME MUNICÍPIO'] = self.df['NOME MUNICÍPIO'].str.strip().str.upper()
        self.df['UF'] = self.df['UF'].str.strip().str.upper()
        
        print(f"✓ Dados limpos: {len(self.df):,} registros "
              f"(removidos {initial_count - len(self.df):,})")
        
        return self.df
    
    def get_basic_stats(self):
        """Retorna estatísticas básicas"""
        if self.df is None:
            self.clean_data()
        
        stats = {
            'total_registros': len(self.df),
            'total_municipios': self.df['CÓDIGO MUNICÍPIO SIAFI'].nunique(),
            'total_beneficiarios': self.df['NIS FAVORECIDO'].nunique(),
            'valor_total': float(self.df['VALOR PARCELA'].sum()),
            'valor_medio': float(self.df['VALOR PARCELA'].mean()),
            'valor_mediano': float(self.df['VALOR PARCELA'].median()),
            'periodo': str(self.df['MÊS COMPETÊNCIA'].iloc[0]) if len(self.df) > 0 else 'N/A'
        }
        
        return stats