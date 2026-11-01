"""Split source lines using GTK4 TextBuffer's newline boundaries."""
import re

_GTK_NEWLINE = re.compile(r"\r\n|[\r\n\u2029]")


def gtk_source_lines(text: str, *, keepends: bool = False) -> list[str]:
    """GTK treats CR, LF, CRLF, and paragraph separator as line breaks."""
    lines: list[str] = []
    start = 0
    for match in _GTK_NEWLINE.finditer(text):
        lines.append(text[start:match.end() if keepends else match.start()])
        start = match.end()
    if start < len(text):
        lines.append(text[start:])
    return lines
