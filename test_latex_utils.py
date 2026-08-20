from core.latex_utils import escape_latex


def test_escape_special_chars():
    assert escape_latex("50% & A_B #1") == r"50\% \& A\_B \#1"


def test_unicode_cleanup():
    assert "--" in escape_latex("A–B")
