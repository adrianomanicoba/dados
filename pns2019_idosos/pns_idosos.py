"""
Microdados da PNS 2019 (IBGE) filtrados para pessoas com 60 anos ou mais.

Baixa os arquivos oficiais do IBGE, lê o arquivo de largura fixa usando o
layout SAS oficial, filtra os moradores com 60+ anos e grava:
  - pns2019_idosos.csv.gz  (uma linha por morador idoso, colunas = códigos IBGE)
  - dicionario_variaveis.csv  (código -> descrição)
  - dicionario_categorias.csv (código, valor -> descrição)

Uso:  python pns_idosos.py [pasta_saida]
"""
import io
import os
import re
import sys
import urllib.request
import zipfile

import pandas as pd

URL_DADOS = "https://ftp.ibge.gov.br/PNS/2019/Microdados/Dados/PNS_2019_20220525.zip"
URL_DIC = "https://ftp.ibge.gov.br/PNS/2019/Microdados/Documentacao/Dicionario_e_input_20220530.zip"
IDADE_MIN = 60


def baixar(url, destino):
    if not os.path.exists(destino):
        print(f"Baixando {url} ...")
        urllib.request.urlretrieve(url, destino)
    return destino


def ler_layout(texto_sas):
    """Extrai (variavel, inicio, largura, texto?, decimais) do input SAS."""
    padrao = re.compile(r"@(\d+)\s+(\S+)\s+(\$?)(\d+)\.(\d*)")
    linhas = []
    for m in padrao.finditer(texto_sas):
        linhas.append(
            dict(variavel=m.group(2), inicio=int(m.group(1)) - 1,
                 largura=int(m.group(4)), texto=m.group(3) == "$",
                 decimais=int(m.group(5) or 0))
        )
    return pd.DataFrame(linhas)


def ler_dicionario(xls_bytes, nomes):
    """Lê o dicionário .xls do IBGE de forma tolerante a pequenas mudanças de layout."""
    bruto = pd.read_excel(io.BytesIO(xls_bytes), header=None, dtype=str)
    bruto = bruto.apply(lambda c: c.str.strip() if c.dtype == object else c)
    nomes = set(nomes)
    # coluna do código = a que mais contém nomes de variáveis do layout
    col_cod = max(bruto.columns, key=lambda c: bruto[c].isin(nomes).sum())
    ncol = len(bruto.columns)
    cat_cols = list(bruto.columns[-2:]) if ncol - list(bruto.columns).index(col_cod) > 3 else []
    var_rows, cat_rows, atual = [], [], None
    for _, r in bruto.iterrows():
        cod = r[col_cod]
        if isinstance(cod, str) and cod in nomes:
            atual = cod
            depois = [v for c, v in r.items()
                      if list(bruto.columns).index(c) > list(bruto.columns).index(col_cod)
                      and c not in cat_cols and isinstance(v, str)]
            desc = max(depois, key=len) if depois else ""
            var_rows.append((cod, desc))
        if atual and cat_cols:
            val, rot = r[cat_cols[0]], r[cat_cols[1]]
            if isinstance(val, str) and isinstance(rot, str) and val and rot:
                cat_rows.append((atual, val, rot))
    dv = pd.DataFrame(var_rows, columns=["variavel", "descricao"]).drop_duplicates("variavel")
    dc = pd.DataFrame(cat_rows, columns=["variavel", "valor", "descricao"])
    return dv, dc


def ler_idosos(zip_dados, layout, idade_min=IDADE_MIN):
    """Lê o .txt de largura fixa e devolve só os moradores com idade >= idade_min."""
    c = layout.set_index("variavel").loc["C008"]
    ini, fim = int(c.inicio), int(c.inicio + c.largura)
    # 1º passo (rápido): filtra as linhas pela idade antes de separar as 1.000+ colunas
    linhas = []
    with zipfile.ZipFile(zip_dados) as z:
        nome_txt = [n for n in z.namelist() if n.lower().endswith(".txt")][0]
        with z.open(nome_txt) as f:
            for linha in io.TextIOWrapper(f, encoding="latin1"):
                idade = linha[ini:fim].strip()
                if idade.isdigit() and int(idade) >= idade_min:
                    linhas.append(linha)
    # 2º passo: separa as colunas só das linhas selecionadas
    df = pd.read_fwf(
        io.StringIO("".join(linhas)),
        colspecs=list(zip(layout.inicio, layout.inicio + layout.largura)),
        names=list(layout.variavel), dtype=str, header=None,
    )
    # converte variáveis numéricas (as não marcadas com $ no layout SAS)
    num = list(layout.loc[~layout.texto, "variavel"])
    df[num] = df[num].apply(pd.to_numeric, errors="coerce")
    df = df.copy()
    # indicador de morador selecionado (respondeu o questionário individual)
    df["morador_selecionado"] = df["V00291"].notna().astype(int)
    return df


def gerar(pasta="."):
    os.makedirs(pasta, exist_ok=True)
    zd = baixar(URL_DADOS, os.path.join(pasta, "PNS_2019.zip"))
    zi = baixar(URL_DIC, os.path.join(pasta, "PNS_2019_dicionario.zip"))
    with zipfile.ZipFile(zi) as z:
        nomes = z.namelist()
        sas = z.read([n for n in nomes if n.lower().endswith(".sas")][0]).decode("latin1")
        xls = z.read([n for n in nomes if n.lower().endswith(".xls")][0])
    layout = ler_layout(sas)
    df = ler_idosos(zd, layout)
    df.to_csv(os.path.join(pasta, "pns2019_idosos.csv.gz"), index=False, compression="gzip")
    try:
        dv, dc = ler_dicionario(xls, layout.variavel)
        dv.to_csv(os.path.join(pasta, "dicionario_variaveis.csv"), index=False)
        dc.to_csv(os.path.join(pasta, "dicionario_categorias.csv"), index=False)
    except Exception as e:  # o CSV de dados não depende do dicionário
        print("Aviso: não consegui ler o dicionário .xls:", e)
        dv = dc = None
    print(f"{len(df):,} moradores com {IDADE_MIN}+ anos | "
          f"{df.morador_selecionado.sum():,} moradores selecionados | "
          f"{df.shape[1]:,} colunas")
    return df, dv, dc


if __name__ == "__main__":
    gerar(sys.argv[1] if len(sys.argv) > 1 else ".")
