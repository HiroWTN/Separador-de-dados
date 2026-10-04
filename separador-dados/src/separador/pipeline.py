"""Orquestra: ler -> limpar -> validar -> separar -> gravar -> relatório."""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime

import pandas as pd

from separador import cleaning, readers, splitter, validators, writers
from separador.config import PipelineConfig

log = logging.getLogger(__name__)


@dataclass
class Relatorio:
    arquivo_entrada: str
    gerado_em: str
    linhas_lidas: int = 0
    duplicados_removidos: int = 0
    linhas_validas: int = 0
    linhas_invalidas: int = 0
    arquivos_gerados: dict[str, object] = field(default_factory=dict)
    erros_por_tipo: dict[str, int] = field(default_factory=dict)


def _contar_erros(invalidos: pd.DataFrame) -> dict[str, int]:
    if invalidos.empty:
        return {}
    contagem = invalidos[validators.COLUNA_ERROS].str.split("; ").explode().value_counts()
    return {str(k): int(v) for k, v in contagem.items()}


def executar(cfg: PipelineConfig) -> Relatorio:
    bruto = readers.ler_arquivo(cfg.entrada)
    relatorio = Relatorio(str(cfg.entrada), datetime.now().isoformat(timespec="seconds"))
    relatorio.linhas_lidas = len(bruto)

    limpo, removidos = cleaning.limpar(bruto, cfg.duplicados_por)
    relatorio.duplicados_removidos = removidos

    validado = validators.validar(limpo, cfg)
    validos, invalidos = splitter.separar_validos_invalidos(validado)
    relatorio.linhas_validas = len(validos)
    relatorio.linhas_invalidas = len(invalidos)
    relatorio.erros_por_tipo = _contar_erros(invalidos)

    fmt = cfg.formato_saida
    gerados: dict[str, object] = {}
    if cfg.separar_por:
        grupos = splitter.separar_por_coluna(validos, cfg.separar_por)
        gerados["validos"] = writers.escrever_grupos(grupos, cfg.saida / "validos", fmt)
    else:
        gerados["validos"] = str(writers.escrever(validos, cfg.saida / "validos", fmt))
    if not invalidos.empty:
        gerados["invalidos"] = str(writers.escrever(invalidos, cfg.saida / "invalidos", fmt))
    relatorio.arquivos_gerados = gerados

    caminho_rel = cfg.saida / "relatorio.json"
    caminho_rel.parent.mkdir(parents=True, exist_ok=True)
    caminho_rel.write_text(
        json.dumps(asdict(relatorio), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    log.info("Concluído: %d válidas, %d inválidas", relatorio.linhas_validas, relatorio.linhas_invalidas)
    return relatorio
