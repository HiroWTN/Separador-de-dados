# Separador de Dados

Pipeline em Python que **lê**, **limpa**, **valida** e **separa** dados tabulares
(CSV, JSON ou Excel) em arquivos organizados, gerando um relatório da execução.

## O que ele faz

1. **Leitura**: CSV (detecta `,`/`;` e encoding), JSON e Excel.
2. **Limpeza**: padroniza nomes de colunas (`Data de Nascimento` → `data_de_nascimento`),
   remove espaços extras, linhas vazias e duplicados.
3. **Validação**: campos obrigatórios, e-mail, CPF (com dígitos verificadores) e datas
   (padronizadas para `AAAA-MM-DD`). Cada erro é registrado na coluna `_erros`.
4. **Separação**:
   - válidos × inválidos;
   - opcionalmente, um arquivo por valor de uma coluna (ex.: um por cidade).
5. **Saída**: CSV, JSON ou XLSX + `relatorio.json` com estatísticas.

## Estrutura

```
separador-dados/
├── src/separador/
│   ├── cli.py          # interface de linha de comando
│   ├── config.py       # PipelineConfig (código, CLI ou JSON)
│   ├── readers.py      # leitura de CSV/JSON/Excel
│   ├── cleaning.py     # limpeza e padronização
│   ├── validators.py   # regras de validação
│   ├── splitter.py     # separação em grupos
│   ├── writers.py      # escrita dos resultados
│   ├── pipeline.py     # orquestra todas as etapas
│   ├── exceptions.py   # erros específicos
│   └── logger.py       # logging
├── tests/              # testes com pytest
├── configs/exemplo.json
└── data/clientes_exemplo.csv
```

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .                 # ou: pip install -r requirements.txt
```

## Uso

Por argumentos:

```bash
python -m separador data/clientes_exemplo.csv \
  --separar-por cidade \
  --obrigatorias nome cidade \
  --email e_mail --cpf cpf --datas data_de_nascimento \
  --duplicados-por cpf nome \
  --formato csv -o saida
```

Por arquivo de configuração:

```bash
python -m separador --config configs/exemplo.json
```

> Use os nomes de coluna **já normalizados** (minúsculos, sem acento, com `_`).

### Saída gerada

```
saida/
├── validos/
│   ├── campinas.csv
│   ├── santos.csv
│   └── sao_paulo.csv
├── invalidos.csv        # linhas com erro + coluna _erros
└── relatorio.json
```

## Como usar como biblioteca

```python
from separador.config import PipelineConfig
from separador.pipeline import executar

rel = executar(PipelineConfig(entrada="data/clientes_exemplo.csv", separar_por="cidade"))
print(rel.linhas_validas, rel.linhas_invalidas)
```

## Testes

```bash
pytest
```

## Ideias de evolução

- Regras de separação customizadas (faixas de valor, expressões);
- Validação de telefone e CEP;
- Leitura de bancos de dados (SQLAlchemy);
- Empacotar com GitHub Actions rodando `pytest`.
