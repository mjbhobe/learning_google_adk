"""logging.py - sets up basic rich logger"""

import logging
from rich.logging import RichHandler


def setup_logger(name: str):
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=True)],
    )
    return logging.getLogger(name)
