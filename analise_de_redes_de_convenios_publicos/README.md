# 📊 Análise de Redes de Convênios Públicos

**Projeto demonstrativo Analisar a rede de convênios públicos federais a partir da relação entre órgãos concedentes e convenentes**


## 📋 Sobre o Projeto

Este projeto realiza uma **análise de redes sociais (Social Network Analysis - SNA)** sobre convênios públicos brasileiros, utilizando dados abertos do Portal da Transparência. O objetivo é mapear e analisar as relações de colaboração entre órgãos públicos e entidades convenentes (municípios, estados, OSC).

### 🎯 Objetivos da Análise:
- Identificar **órgãos mais centrais** na rede de convênios
- Mapear **padrões de colaboração** entre diferentes entidades
- Analisar **distribuição geográfica** dos recursos
- Calcular **métricas de rede** (centralidade, densidade, comunidades)
- Gerar **insights** sobre a articulação Estado-Sociedade Civil

## 🚀 Funcionalidades

### 📈 Análises Realizadas:
1. **Carregamento e limpeza** de dados do Portal da Transparência
2. **Construção de rede bipartida**: Órgãos ↔ Convenentes
3. **Cálculo de métricas** de centralidade (degree, betweenness)
4. **Detecção de comunidades** (algoritmo de Louvain)
5. **Visualizações** profissionais e interpretáveis

### 📊 Saídas Geradas:
- **4 gráficos** em alta resolução
- **3 datasets** processados (CSV + GEXF)
- **Relatório completo** com insights
- **Métricas quantitativas** da rede

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+**
- **Pandas**: Manipulação de dados
- **NetworkX**: Análise de redes complexas
- **Matplotlib/Seaborn**: Visualização de dados
- **Python-Louvain**: Detecção de comunidades

## 📁 Estrutura do Projeto


### ⚠️ Aviso sobre o Arquivo de Dados

**O arquivo CSV original não está incluído neste repositório** devido ao seu tamanho (aproximadamente 2.5 GB). Para executar a análise completa:

1. **Baixe os dados diretamente do Portal da Transparência:**
   - Acesse: [Portal da Transparência - Convênios](https://portaldatransparencia.gov.br/download-de-dados/convenios)
   - Baixe o arquivo referente ao período desejado
   - Coloque o arquivo CSV na raiz do projeto

2. **Script principal para download:**
   - **Devido ao tamanho do arquivo CSV**, disponibilizei o arquivo CSV usado na análise no link abaido do google drive
   - 📥 **Download do arquivo CSV (https://drive.google.com/file/d/1Bl1a0zvKIXzImwprm3rsB-XZBd1MkFUa/view?usp=sharing)
   - Após baixar, coloque o arquivo CSV na pasta principal do projeto
