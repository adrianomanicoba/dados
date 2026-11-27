# PNS 2019 — pessoas idosas (60+)

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/adrianomanicoba/dados/blob/main/pns2019_idosos/PNS2019_idosos.ipynb)

Esta pasta transforma os microdados oficiais da **Pesquisa Nacional de Saúde 2019 (IBGE)** numa base só com os moradores de **60 anos ou mais**.

O notebook baixa os arquivos direto do IBGE, separa as colunas com o layout oficial e grava três arquivos:

| Arquivo | Conteúdo |
|---|---|
| `pns2019_idosos.csv.gz` | uma linha por morador com 60+ anos (43.554 linhas); as colunas são os códigos do IBGE |
| `dicionario_variaveis.csv` | código → descrição da variável |
| `dicionario_categorias.csv` | código + valor → descrição da categoria |

## Uso rápido no Colab

Clique no botão acima e rode todas as células (Ambiente de execução → Executar tudo). O processo leva poucos minutos.

Para usar em outro notebook:

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
