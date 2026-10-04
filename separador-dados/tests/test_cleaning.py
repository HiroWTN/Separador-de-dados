import pandas as pd

from separador.cleaning import limpar, normalizar_nome_coluna


def test_normaliza_nome_coluna():
    assert normalizar_nome_coluna(" Data de Nascimento ") == "data_de_nascimento"
    assert normalizar_nome_coluna("E-mail") == "e_mail"


def test_limpar_remove_espacos_vazios_e_duplicados():
    df = pd.DataFrame({"Nome": [" Ana ", "Ana", "", None], "Cidade": ["SP", "SP", None, None]})
    limpo, removidos = limpar(df)
    assert list(limpo["nome"]) == ["Ana"]
    assert removidos == 1
