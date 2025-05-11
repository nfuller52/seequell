import json

from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from ..utils import format_duration
from .base import QueryAnalyzer


class MetricsAnalyzer(QueryAnalyzer):
    def analyze(self):
        if not self.context["query_times"]:
            return

        query_times = self.context["query_times"]
        slowest = max(query_times)
        avg_time = self.duration / len(query_times)
        sql_total = sum(query_times)

        footer = Text()
        footer.append("\n🟡 Metrics", style="bold yellow")
        self.console.print(footer)

        table = Table(show_header=False, show_lines=False, box=None, padding=(0, 1))
        table.add_row("Path", self.request.path)
        table.add_row("Method", self.request.method)

        query_dict = dict(self.request.GET.items())
        if query_dict:
            try:
                pretty_params = json.dumps(query_dict, indent=2)
                table.add_row(
                    "Params",
                    Syntax(
                        pretty_params,
                        "json",
                        theme="ansi_dark",
                        line_numbers=False,
                        word_wrap=True,
                    ),
                )
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass

        if self.request.method in ("POST", "PUT", "PATCH"):
            try:
                body_data = json.loads(self.request.body)
                if body_data:
                    pretty_body = json.dumps(body_data, indent=2)
                    table.add_row(
                        "Body",
                        Syntax(
                            pretty_body,
                            "json",
                            theme="ansi_dark",
                            line_numbers=False,
                            word_wrap=True,
                        ),
                    )
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass

        table.add_row("Queries", str(len(query_times)))
        table.add_row("SQL avg time", format_duration(avg_time))
        table.add_row("SQL slowest time", format_duration(slowest))
        table.add_row("SQL execution time", format_duration(sql_total))
        self.console.print(table)

        duplicates = self.context.get("duplicates", {})
        if self.config.duplicates_enabled and duplicates:
            self.console.print()
            self.console.print(
                f"[bold red]🚨 {len(duplicates)} duplicate SQL queries detected![/bold red]"
            )
            self.console.print(
                "[red]This is a likely sign of an [italic]N+1 query problem[/italic]. "
                "Consider using select_related or prefetch_related.[/red]"
            )

        self.console.print()
