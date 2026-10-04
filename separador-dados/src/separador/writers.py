"""Escrita dos resultados em disco."""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

log = logging.getLogger(__name__)


def escrever(df: pd.DataFrame, caminho_sem_extensao: Path, formato: str) -> Path:
    caminho = Path(f"{caminho_sem_extensao}.{formato}")
    caminho.parent.mkdir(parents=True, exist_ok=True)
    if formato == "csv":
        df.to_csv(caminho, index=False, encoding="utf-8-sig")
    elif formato == "json":
        df.to_json(caminho, orient="records", force_ascii=False, indent=2)
    elif formato == "xlsx":
        df.to_excel(caminho, index=False)
    else:
        raise ValueError(f"Formato desconhecido: {formato}")
    log.info("Gravado %s (%d linhas)", caminho, len(df))
    return caminho


def escrever_grupos(
    grupos: dict[str, pd.DataFrame], pasta: Path, formato: str
) -> dict[str, str]:
    """Grava um arquivo por grupo. Retorna {grupo: caminho}."""
    return {nome: str(escrever(df, pasta / nome, formato)) for nome, df in grupos.items()}
