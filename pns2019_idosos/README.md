# PNS 2019 — pessoas idosas (60+)

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/adrianomanicoba/dados/blob/main/pns2019_idosos/PNS2019_idosos.ipynb)

Esta pasta transforma os microdados oficiais da **Pesquisa Nacional de Saúde 2019 (IBGE)** numa base só com os moradores de **60 anos ou mais**.

O notebook baixa os arquivos direto do IBGE, separa as colunas com o layout oficial e grava três arquivos:

| Arquivo | Conteúdo |
|---|---|
| `pns2019_idosos.csv.gz` | uma linha por morador com 60+ anos (43.554 linhas); as colunas são os códigos do IBGE |
| `dicionario_variaveis.csv` | código → descrição da variável |
| `dicionario_categorias.csv` | código + valor → descrição da categoria |

Os três arquivos já estão nesta pasta. Para carregar direto em qualquer notebook:

```python
import pandas as pd
BASE = "https://raw.githubusercontent.com/adrianomanicoba/dados/main/pns2019_idosos/"
df = pd.read_csv(BASE + "pns2019_idosos.csv.gz", low_memory=False)
dic_var = pd.read_csv(BASE + "dicionario_variaveis.csv")
dic_cat = pd.read_csv(BASE + "dicionario_categorias.csv", dtype=str)
```

## Leitura direta no R

```r
idosos <- read.csv("https://raw.githubusercontent.com/adrianomanicoba/dados/main/pns2019_idosos/pns2019_idosos.csv")
```

Versão com nomes descritivos nas colunas (código do IBGE + resumo da pergunta, ex.: `C008_idade_morador_data_referencia`, `K001_grau_dificuldade_comer_sozinho_prato`):

```r
idosos <- read.csv("https://raw.githubusercontent.com/adrianomanicoba/dados/main/pns2019_idosos/pns2019_idosos_nomeado.csv")
```

A coluna `nome` do `dicionario_variaveis.csv` liga cada código ao nome usado nesse arquivo.

(`pns2019_idosos.csv` tem ~65 MB, sem compressão; o `.csv.gz` tem o mesmo conteúdo em 7 MB.)

## Uso no Colab

Clique no botão acima. A primeira célula carrega a base pronta; as seções seguintes trazem conferências e exemplos de análise ponderada.

Em R, use o script `pns2019_idosos.R` (pacote `survey`): ele carrega a base, aplica os dicionários e monta o desenho amostral.

Para regenerar a base a partir dos arquivos originais do IBGE:

```python
!wget -q https://raw.githubusercontent.com/adrianomanicoba/dados/main/pns2019_idosos/pns_idosos.py
import pns_idosos
df, dic_var, dic_cat = pns_idosos.gerar("pns2019")
```

## Pesos amostrais

| Análise | Filtro | Peso |
|---|---|---|
| Variáveis de todos os moradores (inclui o **módulo K – saúde dos indivíduos com 60 anos ou mais**) | todos | `V00281` |
| Questionário individual (módulos L em diante) | `morador_selecionado == 1` (22.728 pessoas) | `V00291` |

Estrato: `V0024`; UPA: `UPA_PNS`. Com `V00281`, a população estimada com 60+ anos é de cerca de 34,4 milhões.

## Fonte

IBGE, Pesquisa Nacional de Saúde 2019 — https://ftp.ibge.gov.br/PNS/2019/Microdados/
