"""Limpeza e padronização dos dados."""
from __future__ import annotations

import re
import unicodedata

import pandas as pd


def normalizar_nome_coluna(nome: str) -> str:
    """'Data de Nascimento ' -> 'data_de_nascimento'."""
    sem_acento = unicodedata.normalize("NFKD", str(nome)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", sem_acento.lower()).strip("_")


def normalizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns=normalizar_nome_coluna)


def limpar_textos(df: pd.DataFrame) -> pd.DataFrame:
    """Remove espaços extras e transforma vazios em NA."""
    df = df.copy()
    for col in df.columns:
        serie = df[col].astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
        df[col] = serie.replace("", pd.NA)
    return df


def remover_linhas_vazias(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna(how="all").reset_index(drop=True)


def remover_duplicados(df: pd.DataFrame, colunas: list[str] | None = None) -> tuple[pd.DataFrame, int]:
    """Retorna (df sem duplicados, quantidade removida)."""
    antes = len(df)
    df = df.drop_duplicates(subset=colunas or None, keep="first").reset_index(drop=True)
    return df, antes - len(df)


def limpar(df: pd.DataFrame, duplicados_por: list[str] | None = None) -> tuple[pd.DataFrame, int]:
    df = normalizar_colunas(df)
    df = limpar_textos(df)
    df = remover_linhas_vazias(df)
    return remover_duplicados(df, duplicados_por)
