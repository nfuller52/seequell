def format_duration(seconds: float) -> str:
    return f"{seconds:.1f}s" if seconds >= 1 else f"{int(seconds * 1000)}ms"
