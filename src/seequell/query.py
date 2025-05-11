from dataclasses import dataclass

from rich.syntax import Syntax
from sqlparse import format as sql_format


@dataclass
class Query:
    raw_sql: str
    time: float
    normalized_sql: str

    @classmethod
    def from_raw(cls, raw_query: dict) -> "Query":
        attrs = {
            "raw_sql": raw_query["sql"].strip(),
            "time": float(raw_query["time"]),
        }

        normalized_sql = sql_format(
            attrs["raw_sql"],
            "sql",
            keyword_case="upper",
            strip_comments=True,
            reindent=False,
            strip_whitespace=True,
        )

        attrs["normalized_sql"] = normalized_sql

        return cls(**attrs)

    def is_slow(self, max_time: float) -> bool:
        return self.time > max_time

    def formatted(self) -> Syntax:
        return Syntax(
            self.raw_sql,
            "sql",
            theme="ansi_dark",
            line_numbers=False,
            word_wrap=True,
        )
