"""Separação dos dados em grupos."""
from __future__ import annotations

import re
import unicodedata

import pandas as pd

from separador.validators import COLUNA_ERROS


def separar_validos_invalidos(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Válidos (sem a coluna de erros) e inválidos (com a coluna de erros)."""
    tem_erro = df[COLUNA_ERROS] != ""
    validos = df.loc[~tem_erro].drop(columns=COLUNA_ERROS).reset_index(drop=True)
    invalidos = df.loc[tem_erro].reset_index(drop=True)
    return validos, invalidos


def nome_seguro(valor: object) -> str:
    """Converte um valor qualquer em nome de arquivo seguro."""
    if valor is None or pd.isna(valor):
        return "sem_valor"
    texto = unicodedata.normalize("NFKD", str(valor)).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "_", texto).strip("_").lower() or "sem_valor"


def separar_por_coluna(df: pd.DataFrame, coluna: str) -> dict[str, pd.DataFrame]:
    """Um DataFrame por valor distinto da coluna (NA vira 'sem_valor')."""
    chaves = df[coluna].map(nome_seguro)
    return {
        chave: grupo.reset_index(drop=True)
        for chave, grupo in df.groupby(chaves, sort=True)
    }
