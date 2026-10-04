import pandas as pd

from separador.config import PipelineConfig
from separador.validators import COLUNA_ERROS, cpf_valido, email_valido, validar


def test_cpf():
    assert cpf_valido("529.982.247-25")
    assert not cpf_valido("111.111.111-11")
    assert not cpf_valido("123.456.789-00")
    assert not cpf_valido(None)


def test_email():
    assert email_valido("a@b.com")
    assert not email_valido("a@b")


def test_validar_marca_erros():
    df = pd.DataFrame(
        {
            "nome": ["Ana", None],
            "email": ["ana@x.com", "ruim"],
            "nasc": ["15/03/1998", "31/02/2000"],
        }
    )
    cfg = PipelineConfig(
        entrada="x.csv", colunas_obrigatorias=["nome"], coluna_email="email", colunas_data=["nasc"]
    )
    out = validar(df, cfg)
    assert out.loc[0, COLUNA_ERROS] == ""
    assert "nome obrigatório" in out.loc[1, COLUNA_ERROS]
    assert "email inválido" in out.loc[1, COLUNA_ERROS]
    assert "nasc com data inválida" in out.loc[1, COLUNA_ERROS]
    assert out.loc[0, "nasc"] == "1998-03-15"
