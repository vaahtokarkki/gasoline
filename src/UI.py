import logging

from rich.console import Console
from rich.logging import RichHandler


FORMAT = "%(message)s"
logging.basicConfig(
    level="ERROR", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

console = Console()
