from .base import QueryAnalyzer


class DuplicateQueryAnalyzer(QueryAnalyzer):
    def analyze(self):
        if not self.config.duplicates_enabled:
            return

        if not self.context["normalized_counter"]:
            self.context["duplicates"] = []
            return

        self.context["duplicates"] = {
            sql: count for sql, count in self.context["normalized_counter"].items() if count > 1
        }
        if self.context["duplicates"]:
            self.console.print(
                f"\n[bold red]🚨 {len(self.context["duplicates"])} Duplicate Queries Detected:[/bold red]"
            )

            for sql, count in self.context["duplicates"].items():
                self.console.print(f"  [red]×{count}[/red] → {sql}")
