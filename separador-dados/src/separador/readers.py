"""Leitura de arquivos de entrada para DataFrame."""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from separador.exceptions import FormatoNaoSuportadoError

log = logging.getLogger(__name__)


def _ler_csv(caminho: Path) -> pd.DataFrame:
    # sep=None + engine python detecta automaticamente ',' ou ';'
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(caminho, sep=None, engine="python", dtype=str, encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("utf-8", b"", 0, 1, f"Encoding não reconhecido em {caminho}")


def _ler_json(caminho: Path) -> pd.DataFrame:
    df = pd.read_json(caminho, dtype=False)
    return df.astype(object).where(df.notna(), None).map(lambda v: v if v is None else str(v))


def _ler_excel(caminho: Path) -> pd.DataFrame:
    return pd.read_excel(caminho, dtype=str)


LEITORES = {
    ".csv": _ler_csv,
    ".json": _ler_json,
    ".xlsx": _ler_excel,
    ".xls": _ler_excel,
}


def ler_arquivo(caminho: str | Path) -> pd.DataFrame:
    caminho = Path(caminho)
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
    leitor = LEITORES.get(caminho.suffix.lower())
    if leitor is None:
        raise FormatoNaoSuportadoError(
            f"Formato {caminho.suffix!r} não suportado. Use: {', '.join(LEITORES)}"
        )
    df = leitor(caminho)
    log.info("Lidas %d linhas e %d colunas de %s", len(df), df.shape[1], caminho.name)
    return df
