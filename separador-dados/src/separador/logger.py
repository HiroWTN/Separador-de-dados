"""Configuração central de logging."""
import logging


def configurar_logger(verboso: bool = False) -> logging.Logger:
    nivel = logging.DEBUG if verboso else logging.INFO
    logging.basicConfig(
        level=nivel,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger("separador")
