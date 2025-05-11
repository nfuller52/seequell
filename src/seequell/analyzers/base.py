from typing import Any

from django.http import HttpRequest
from rich.console import Console

from ..config import SeequellConfig


class QueryAnalyzer:
    def __init__(
        self,
        config: SeequellConfig,
        console: Console,
        duration: float,
        request: HttpRequest,
        context: dict[str, Any] = None,
    ):
        self.config = config
        self.console = console
        self.duration = duration
        self.request = request
        self.context = context if context is not None else {}

    def analyze(self) -> None: ...
