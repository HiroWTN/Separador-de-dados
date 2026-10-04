"""Exceções específicas do projeto."""


class SeparadorError(Exception):
    """Erro base do projeto."""


class FormatoNaoSuportadoError(SeparadorError):
    """Extensão de arquivo não suportada."""


class ColunaAusenteError(SeparadorError):
    """Coluna exigida não existe nos dados."""


class ConfiguracaoInvalidaError(SeparadorError):
    """Arquivo ou parâmetros de configuração inválidos."""
