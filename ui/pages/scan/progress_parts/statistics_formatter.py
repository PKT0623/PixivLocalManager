def format_extension_counts(
    extension_counts: dict,
) -> str:
    if not extension_counts:
        return "-"

    parts = []

    for extension, count in sorted(extension_counts.items()):
        parts.append(f"{extension}: {count}")

    return ", ".join(parts)


def format_diff(
    value: int,
) -> str:
    value = int(value or 0)

    if value > 0:
        return f"+{value}"

    return str(value)
