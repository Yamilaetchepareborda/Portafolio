import re

from markdown_it import MarkdownIt
from markupsafe import Markup

# Markdown seguro: html=False escapa cualquier HTML que venga en el contenido
# (no se puede inyectar <script>) y markdown-it ya bloquea links con
# javascript:, vbscript: y data:. Por eso no hace falta bleach.
_md = MarkdownIt("commonmark", {"html": False, "typographer": True}).enable("table")


def render_markdown(text: str) -> Markup:
    return Markup(_md.render(text or ""))


_STRIP_PATTERNS = [
    (re.compile(r"`([^`]*)`"), r"\1"),               # código en línea
    (re.compile(r"!\[[^\]]*\]\([^)]*\)"), ""),       # imágenes
    (re.compile(r"\[([^\]]*)\]\([^)]*\)"), r"\1"),   # links -> texto
    (re.compile(r"^\s*(?:[-*+>]|\d+\.)\s+", re.M), ""),  # viñetas y citas
    (re.compile(r"\*{1,3}|_{2,3}"), ""),              # negrita / cursiva
    (re.compile(r"\s+"), " "),
    (re.compile(r"\s+([,.;:])"), r"\1"),
]


def _first_paragraph(text: str) -> str:
    """Primer párrafo 'de texto' (salta títulos, código y tablas)."""
    without_code = re.sub(r"```.*?```", "", text or "", flags=re.S)
    for block in re.split(r"\n\s*\n", without_code):
        block = block.strip()
        if block and not block.startswith(("#", "|")):
            return block
    return ""


def excerpt(text: str, length: int = 160) -> str:
    """Texto plano corto para las tarjetas (sin Markdown)."""
    plain = _first_paragraph(text)
    for pattern, repl in _STRIP_PATTERNS:
        plain = pattern.sub(repl, plain)
    plain = plain.strip()
    if len(plain) <= length:
        return plain
    return plain[:length].rsplit(" ", 1)[0].rstrip(",.;:") + "…"
