import json
from collections import Counter
from time import perf_counter

from django.db import connection
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from sqlparse import format as sql_format

console = Console()


class SeequellMiddleware:
    SLOW_QUERY_THRESHOLD = 1.0

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = perf_counter()
        response = self.get_response(request)
        duration = perf_counter() - start

        queries = connection.queries
        if not queries:
            return response

        query_len = len(queries)
        normalized_counter = Counter()

        slow_queries = []

        for q in queries:
            sql = q["sql"].strip()
            time = float(q["time"])

            if time > self.SLOW_QUERY_THRESHOLD:
                slow_queries.append((sql, time))

            normalized_sql = sql_format(
                sql,
                keyword_case="upper",
                strip_comments=True,
                reindent=False,
                strip_whitespace=True,
            )
            normalized_counter[normalized_sql] += 1

            syntax = Syntax(
                sql,
                "sql",
                theme="ansi_dark",
                line_numbers=False,
                word_wrap=True,
            )

            console.print(syntax)
            console.print(f"[dim]⤷ ({time:.3f}s)[/dim]")

        duplicates = {sql: count for sql, count in normalized_counter.items() if count > 1}
        if duplicates:
            console.print("\n[bold red]🚨 Duplicate Queries Detected:[/bold red]")
            for sql, count in duplicates.items():
                console.print(f"  [red]×{count}[/red] → {sql}")

        if slow_queries:
            console.print(
                f"\n[bold magenta]🐢 Slow Queries (>{self.SLOW_QUERY_THRESHOLD:.0f}ms):[/bold magenta]"
            )
            for sql, time in slow_queries:
                formatted = sql_format(sql, reindent=True, keyword_case="upper")
                syntax = Syntax(
                    formatted,
                    "sql",
                    theme="ansi_dark",
                    line_numbers=False,
                    word_wrap=True,
                )
                console.print(syntax)
                console.print(f"[dim]⤷ ({time:.3f}s)[/dim]\n")

        query_times = [float(q["time"]) for q in queries]
        slowest = max(query_times)
        avg_time = duration / len(query_times)
        sql_total = sum(query_times)

        footer = Text()
        footer.append("\n🟡 Metrics", style="bold yellow")
        console.print(footer)

        table = Table(show_header=False, show_lines=False, box=None, padding=(0, 1))
        table.add_row("Path", request.path)
        table.add_row("Method", request.method)

        query_dict = dict(request.GET.items())
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

        if request.method in ("POST", "PUT", "PATCH"):
            try:
                body_data = json.loads(request.body)
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

        table.add_row("Queries", str(query_len))
        table.add_row("SQL avg time", f"{avg_time:.4f}s")
        table.add_row("SQL slowest time", f"{slowest:.4f}s")
        table.add_row("SQL execution time", f"{sql_total:.4f}s")
        table.add_row("SQL duplicates", str(len(duplicates)))
        console.print(table)
        console.print()

        return response
