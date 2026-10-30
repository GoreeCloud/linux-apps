"""Small, deterministic Markdown subset for the read-only native preview.

No HTML interpretation, network loading or executable content.
"""
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Run:
    text: str
    style: str = ""


@dataclass(frozen=True)
class Line:
    runs: tuple[Run, ...]
    block: str = "body"


INLINE = re.compile(
    r"(\*\*([^*\n]+)\*\*|__([^_\n]+)__|~~([^~\n]+)~~|"
    r"\x60([^\x60\n]+)\x60|\*([^*\n]+)\*|_([^_\n]+)_|"
    r"\[([^\]\n]+)\]\(([^)\s]+)\))"
)
HEADING = re.compile(r"^ {0,3}(#{1,3})\s+(.+?)\s*$")
TASK = re.compile(r"^\s{0,3}[-*+]\s+\[([xX ])\]\s+(.*)$")
BULLET = re.compile(r"^\s{0,3}[-*+]\s+(.+)$")
ORDERED = re.compile(r"^\s{0,3}(\d{1,4})[.)]\s+(.+)$")
QUOTE = re.compile(r"^ {0,3}>\s?(.*)$")
FENCE = re.compile(r"^ {0,3}\x60\x60\x60")
RULE = re.compile(r"^\s{0,3}([-*_])(?:\s*\1){2,}\s*$")


def inline_runs(text: str) -> tuple[Run, ...]:
    runs = []
    pos = 0
    for match in INLINE.finditer(text):
        if match.start() > pos:
            runs.append(Run(text[pos:match.start()]))
        values = (("bold", 2), ("bold", 3), ("strike", 4),
                  ("code", 5), ("italic", 6), ("italic", 7), ("link", 8))
        for style, group in values:
            if match.group(group) is not None:
                runs.append(Run(match.group(group), style))
                break
        pos = match.end()
    if pos < len(text):
        runs.append(Run(text[pos:]))
    return tuple(runs)


def parse_markdown(text: str) -> list[Line]:
    result = []
    in_code = False
    for raw in text.splitlines():
        if FENCE.match(raw):
            in_code = not in_code
            continue
        if in_code:
            result.append(Line((Run(raw or " ", "code"),), "code"))
        elif not raw.strip():
            result.append(Line((Run(" "),), "blank"))
        elif (m := HEADING.match(raw)):
            result.append(Line(inline_runs(m.group(2)), "h" + str(len(m.group(1)))))
        elif RULE.match(raw):
            result.append(Line((Run("────────────────────────────"),), "rule"))
        elif (m := TASK.match(raw)):
            result.append(Line((Run("☑ " if m.group(1).lower() == "x" else "☐ ", "task"),)
                               + inline_runs(m.group(2)), "list"))
        elif (m := BULLET.match(raw)):
            result.append(Line((Run("• ", "bullet"),) + inline_runs(m.group(1)), "list"))
        elif (m := ORDERED.match(raw)):
            result.append(Line((Run(m.group(1) + ". ", "bullet"),) + inline_runs(m.group(2)), "list"))
        elif (m := QUOTE.match(raw)):
            result.append(Line((Run("│ ", "quote"),) + inline_runs(m.group(1)), "quote"))
        else:
            result.append(Line(inline_runs(raw)))
    return result or [Line((Run(" "),), "blank")]
