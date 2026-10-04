import json
from pathlib import Path

import pytest

from separador.cli import main
from separador.config import PipelineConfig
from separador.exceptions import ColunaAusenteError, FormatoNaoSuportadoError
from separador.pipeline import executar
from separador.splitter import nome_seguro

CSV = (
    "Nome,Email,Cidade\n"
    "Ana,ana@x.com,São Paulo\n"
    "Bia,bia@x.com,Campinas\n"
    "Caio,ruim,Campinas\n"
)


@pytest.fixture
def csv_path(tmp_path: Path) -> Path:
    p = tmp_path / "dados.csv"
    p.write_text(CSV, encoding="utf-8")
    return p


def test_nome_seguro():
    assert nome_seguro("São Paulo") == "sao_paulo"
    assert nome_seguro(None) == "sem_valor"


def test_pipeline_separa_por_cidade(csv_path, tmp_path):
    cfg = PipelineConfig(
        entrada=csv_path, saida=tmp_path / "out", separar_por="cidade", coluna_email="email"
    )
    rel = executar(cfg)
    assert rel.linhas_validas == 2 and rel.linhas_invalidas == 1
    assert (tmp_path / "out/validos/sao_paulo.csv").exists()
    assert (tmp_path / "out/validos/campinas.csv").exists()
    assert (tmp_path / "out/invalidos.csv").exists()
    dados = json.loads((tmp_path / "out/relatorio.json").read_text(encoding="utf-8"))
    assert dados["erros_por_tipo"] == {"email inválido": 1}


@pytest.mark.parametrize("fmt", ["json", "xlsx"])
def test_formatos_de_saida(csv_path, tmp_path, fmt):
    cfg = PipelineConfig(entrada=csv_path, saida=tmp_path / "out", formato_saida=fmt)
    executar(cfg)
    assert (tmp_path / f"out/validos.{fmt}").exists()


def test_coluna_ausente(csv_path, tmp_path):
    cfg = PipelineConfig(entrada=csv_path, saida=tmp_path, separar_por="inexistente")
    with pytest.raises(ColunaAusenteError):
        executar(cfg)


def test_formato_nao_suportado(tmp_path):
    arq = tmp_path / "x.txt"
    arq.write_text("a")
    with pytest.raises(FormatoNaoSuportadoError):
        executar(PipelineConfig(entrada=arq, saida=tmp_path / "o"))


def test_cli_retorna_erro_para_arquivo_inexistente(tmp_path, capsys):
    assert main([str(tmp_path / "nao_existe.csv")]) == 1
    assert "Erro" in capsys.readouterr().err
