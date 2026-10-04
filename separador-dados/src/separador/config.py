"""Configuração do pipeline (via código, CLI ou arquivo JSON)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field, fields
from pathlib import Path

from separador.exceptions import ConfiguracaoInvalidaError

FORMATOS_SAIDA = ("csv", "json", "xlsx")


@dataclass
class PipelineConfig:
    entrada: Path
    saida: Path = Path("saida")
    separar_por: str | None = None          # coluna usada para criar um arquivo por valor
    formato_saida: str = "csv"              # csv | json | xlsx
    colunas_obrigatorias: list[str] = field(default_factory=list)
    coluna_email: str | None = None
    coluna_cpf: str | None = None
    colunas_data: list[str] = field(default_factory=list)
    duplicados_por: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.entrada = Path(self.entrada)
        self.saida = Path(self.saida)
        if self.formato_saida not in FORMATOS_SAIDA:
            raise ConfiguracaoInvalidaError(
                f"Formato de saída inválido: {self.formato_saida!r}. Use um de {FORMATOS_SAIDA}."
            )

    @classmethod
    def de_json(cls, caminho: str | Path) -> "PipelineConfig":
        caminho = Path(caminho)
        try:
            dados = json.loads(caminho.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ConfiguracaoInvalidaError(f"Não foi possível ler {caminho}: {exc}") from exc
        validos = {f.name for f in fields(cls)}
        desconhecidos = set(dados) - validos
        if desconhecidos:
            raise ConfiguracaoInvalidaError(f"Chaves desconhecidas na configuração: {sorted(desconhecidos)}")
        return cls(**dados)
