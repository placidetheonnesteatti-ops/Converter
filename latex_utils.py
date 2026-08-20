from __future__ import annotations

import html
import re
import unicodedata

SPECIALS = {"&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}"}
UNICODE_MAP = {
    "–": "--", "—": "---", "…": r"\ldots{}", "“": "``", "”": "''", "„": "``", "’": "'", "‘": "'",
    " ": " ", " ": " ", "−": "-", "×": r"$\\times$", "÷": r"$\\div$", "≤": r"$\\leq$", "≥": r"$\\geq$", "≠": r"$\\neq$",
}


def normalize_text(text: str) -> str:
    text = html.unescape(text or "")
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    for src, dst in UNICODE_MAP.items():
        text = text.replace(src, dst)
    text = re.sub(r"[ \t]+", " ", text)
    return text


def escape_latex(text: str) -> str:
    text = normalize_text(text)
    return "".join(SPECIALS.get(ch, ch) for ch in text)


def latex_comment(text: str) -> str:
    return "% " + text.replace("\n", " ")


def safe_filename(name: str, fallback: str = "document") -> str:
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name.strip())
    name = name.strip("._")
    return name or fallback
