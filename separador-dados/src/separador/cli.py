"""Interface de linha de comando."""
from __future__ import annotations

import argparse
import sys

from separador.config import FORMATOS_SAIDA, PipelineConfig
from separador.exceptions import SeparadorError
from separador.logger import configurar_logger
from separador.pipeline import executar


def montar_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="separador",
        description="Lê, limpa, valida e separa dados (CSV, JSON ou Excel).",
    )
    p.add_argument("entrada", nargs="?", help="Arquivo de entrada (.csv, .json, .xlsx)")
    p.add_argument("-c", "--config", help="Arquivo JSON de configuração (substitui as demais opções)")
    p.add_argument("-o", "--saida", default="saida", help="Pasta de saída (padrão: saida)")
    p.add_argument("-s", "--separar-por", help="Coluna para gerar um arquivo por valor")
    p.add_argument("-f", "--formato", choices=FORMATOS_SAIDA, default="csv", help="Formato de saída")
    p.add_argument("-r", "--obrigatorias", nargs="*", default=[], help="Colunas obrigatórias")
    p.add_argument("--email", help="Coluna de e-mail a validar")
    p.add_argument("--cpf", help="Coluna de CPF a validar")
    p.add_argument("--datas", nargs="*", default=[], help="Colunas de data a validar/padronizar")
    p.add_argument("--duplicados-por", nargs="*", default=[], help="Colunas que definem duplicidade")
    p.add_argument("-v", "--verboso", action="store_true", help="Logs detalhados")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = montar_parser()
    args = parser.parse_args(argv)
    configurar_logger(args.verboso)

    try:
        if args.config:
            cfg = PipelineConfig.de_json(args.config)
        elif args.entrada:
            cfg = PipelineConfig(
                entrada=args.entrada,
                saida=args.saida,
                separar_por=args.separar_por,
                formato_saida=args.formato,
                colunas_obrigatorias=args.obrigatorias,
                coluna_email=args.email,
                coluna_cpf=args.cpf,
                colunas_data=args.datas,
                duplicados_por=args.duplicados_por,
            )
        else:
            parser.error("informe um arquivo de entrada ou --config")
        rel = executar(cfg)
    except (SeparadorError, FileNotFoundError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1

    print(f"\nLinhas lidas: {rel.linhas_lidas}")
    print(f"Duplicados removidos: {rel.duplicados_removidos}")
    print(f"Válidas: {rel.linhas_validas} | Inválidas: {rel.linhas_invalidas}")
    for erro, qtd in rel.erros_por_tipo.items():
        print(f"  - {erro}: {qtd}")
    print(f"Saída em: {cfg.saida}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
