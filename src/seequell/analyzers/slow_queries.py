from .base import QueryAnalyzer


class SlowQueryAnalyzer(QueryAnalyzer):
    def analyze(self):
        if not self.context["slow_queries"]:
            return

        self.console.print(
            f"\n[bold magenta]🐢 Slow Queries (>{self.config.max_query_threshold:.4f}ms):[/bold magenta]"
        )
        for query in self.context["slow_queries"]:
            self.console.print(query.formatted())
            self.console.print(f"[dim]⤷ ({query.time:.3f}s)[/dim]\n")
