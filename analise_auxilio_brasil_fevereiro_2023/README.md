# Análise do Auxílio Brasil - Fevereiro/2023

Pipeline automatizado para processamento, análise estatística e estudo de redes complexas sobre os dados de pagamento do programa Auxílio Brasil referentes ao mês de Fevereiro de 2023.

## 📋 Sobre o Projeto
Este sistema processa grandes volumes de dados públicos, extrai métricas financeiras, identifica padrões de similaridade entre municípios brasileiros e gera visualizações técnicas para suporte à tomada de decisão ou pesquisa acadêmica.

## 🏗️ Estrutura do Repositório
O projeto está organizado de forma modular para facilitar a manutenção:

* **`src/`**: Contém os módulos de lógica de negócio:
    * `data_processor.py`: Limpeza e filtragem de dados brutos.
    * `network_builder.py`: Algoritmos de grafos e similaridade.
    * `visualization.py`: Scripts de geração de gráficos e redes.
    * `analysis.py`: Cálculos estatísticos avançados.
    * `export_results.py`: Gerador de relatórios e exportação de arquivos.
* **`data/`**: Local destinado ao arquivo CSV original.
* **`outputs/`**: Pasta gerada automaticamente com os resultados da análise.

## 🚀 Como Utilizar

### 1. Requisitos
Certifique-se de ter o Python 3.8+ instalado e instale as dependências necessárias:
```bash
pip install pandas networkx matplotlib python-louvain


### 2. onde baixar o dado a ser analisado
O dado utilizado na análise é o arquivo CSV do programa Auxílio Brasil referente a Fevereiro de 2023.

O arquivo baixado foi:
- **Nome:** 202302_AuxilioBrasil.csv

O download foi realizado no site do Portal da Transparência:
https://portaldatransparencia.gov.br/download-de-dados/auxilio-brasil

Caminho no site:
- Exercícios Disponíveis: 2023
- Meses Disponíveis em 2023: Fevereiro

Após o download, o arquivo **202302_AuxilioBrasil.csv deve ser colocado na pasta `data/`** do projeto.
