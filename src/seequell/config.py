class SeequellConfig:
    @property
    def enabled(self) -> bool:
        return True

    @property
    def duplicates_enabled(self) -> bool:
        return "seequell.analyzers.duplicates.DuplicateQueryAnalyzer" in self.enabled_analyzers()

    def enabled_analyzers(self) -> list[str]:
        return [
            "seequell.analyzers.slow_queries.SlowQueryAnalyzer",
            "seequell.analyzers.duplicates.DuplicateQueryAnalyzer",
            "seequell.analyzers.metrics.MetricsAnalyzer",
        ]

    @property
    def max_query_threshold(self) -> float:
        return 1.0
