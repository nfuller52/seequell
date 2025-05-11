from collections import Counter
from time import perf_counter

from django.db import connection
from django.utils.module_loading import import_string
from rich.console import Console

from .analyzers.base import QueryAnalyzer
from .config import SeequellConfig
from .query import Query
from .utils import format_duration

console = Console()


class SeequellMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.config = SeequellConfig()
        self.analyzers: list[type[QueryAnalyzer]] = [
            import_string(path) for path in self.config.enabled_analyzers()
        ]

    def __call__(self, request):
        start = perf_counter()
        response = self.get_response(request)
        duration = perf_counter() - start
        raw_queries = connection.queries

        if self.config.enabled and raw_queries:
            query_times: list[float] = []
            slow_queries: list[Query] = []
            normalized_counter = Counter()

            for raw_query in raw_queries:
                query = Query.from_raw(raw_query)
                query_times.append(query.time)

                normalized_counter[query.normalized_sql] += 1

                if query.is_slow(self.config.max_query_threshold):
                    slow_queries.append(query)

                console.print(query.formatted())
                console.print(f"[dim]⤷ ({format_duration(query.time)})[/dim]")

            context = {
                "normalized_counter": normalized_counter,
                "slow_queries": slow_queries,
                "query_times": query_times,
            }

            for analyzer_class in self.analyzers:
                instance = analyzer_class(
                    config=self.config,
                    console=console,
                    duration=duration,
                    request=request,
                    context=context,
                )

                instance.analyze()

        return response
