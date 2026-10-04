"""Validação linha a linha. Cada erro encontrado é registrado na coluna `_erros`."""
from __future__ import annotations

import re

import pandas as pd

from separador.config import PipelineConfig
from separador.exceptions import ColunaAusenteError

COLUNA_ERROS = "_erros"
_EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")


def cpf_valido(cpf: object) -> bool:
    if cpf is None or pd.isna(cpf):
        return False
    digitos = re.sub(r"\D", "", str(cpf))
    if len(digitos) != 11 or digitos == digitos[0] * 11:
        return False
    for tamanho in (9, 10):
        soma = sum(int(digitos[i]) * (tamanho + 1 - i) for i in range(tamanho))
        dv = (soma * 10 % 11) % 10
        if dv != int(digitos[tamanho]):
            return False
    return True


def email_valido(email: object) -> bool:
    if email is None or pd.isna(email):
        return False
    return bool(_EMAIL_RE.match(str(email)))


def _exigir_colunas(df: pd.DataFrame, colunas: list[str]) -> None:
    ausentes = [c for c in colunas if c not in df.columns]
    if ausentes:
        raise ColunaAusenteError(f"Colunas ausentes nos dados: {ausentes}. Disponíveis: {list(df.columns)}")


def _anotar(erros: list[list[str]], mascara: pd.Series, mensagem: str) -> None:
    """Acrescenta `mensagem` nas posições onde `mascara` é True."""
    for i, tem_erro in enumerate(mascara.tolist()):
        if tem_erro:
            erros[i].append(mensagem)


def validar(df: pd.DataFrame, cfg: PipelineConfig) -> pd.DataFrame:
    """Retorna cópia do df com coluna `_erros` (string com erros separados por '; ')."""
    _exigir_colunas(df, cfg.colunas_obrigatorias)
    for opcional in (cfg.coluna_email, cfg.coluna_cpf, cfg.separar_por):
        if opcional:
            _exigir_colunas(df, [opcional])
    _exigir_colunas(df, cfg.colunas_data)

    df = df.copy()
    erros: list[list[str]] = [[] for _ in range(len(df))]

    for col in cfg.colunas_obrigatorias:
        _anotar(erros, df[col].isna(), f"{col} obrigatório")

    if cfg.coluna_email:
        col = cfg.coluna_email
        _anotar(erros, df[col].notna() & ~df[col].map(email_valido).astype(bool), f"{col} inválido")

    if cfg.coluna_cpf:
        col = cfg.coluna_cpf
        _anotar(erros, df[col].notna() & ~df[col].map(cpf_valido).astype(bool), f"{col} inválido")

    for col in cfg.colunas_data:
        convertido = pd.to_datetime(df[col], dayfirst=True, errors="coerce", format="mixed")
        _anotar(erros, df[col].notna() & convertido.isna(), f"{col} com data inválida")
        df[col] = convertido.dt.strftime("%Y-%m-%d").where(convertido.notna(), df[col])

    df[COLUNA_ERROS] = ["; ".join(e) for e in erros]
    return df
