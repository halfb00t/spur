"""The tokens a Chromium number box blanks and the ones it holds (WR-02, D-02).

The table 33-01 measured in the gate's own Chromium (Playwright's headless shell), over every
number input of the page: `bench/RESULTS.md`, `### Tokens the number box blanks, every field
(33-01)`. No token read differently on two inputs. D-02 makes this table, and not the HTML
spec, the authority for `app.blank_in_a_number_box`: tests/test_number_as_written.py walks it
over the gear routes, and the browser step `number box tokens` re-reads every row on the
page's own inputs at each gate run, so a Chromium upgrade that moves a row fails there and
not in a user's browser.

`blank` is True when the box reads the token back as the empty string. A non-ASCII or
invisible character is written as an escape so this file stays ASCII.
"""

from __future__ import annotations

from typing import NamedTuple


class Token(NamedTuple):
    text: str
    blank: bool


TOKENS: tuple[Token, ...] = (
    Token(" 22", True),
    Token("22 ", True),
    Token("%2022", True),
    Token("1_0", True),
    Token("22.", True),
    Token("5.", True),
    Token("+5", True),
    Token("+22", True),
    Token("2.", True),
    Token("22", False),
    Token("2.5", False),
    Token("-1", False),
    Token("1e1", False),
    Token(".5", False),
    Token("\t22", True),
    Token("22\n", True),
    Token("22\x0b", True),
    Token("\x0c22", True),
    Token("22\u2028", True),
    Token("\xa0 22", True),
    Token("22\xa0", True),
    Token("\u200322", True),
    Token("22\u2003", True),
    Token("2_2", True),
    Token("1_000", True),
    Token("+0", True),
    Token("0.", True),
    Token("-5.", True),
    Token("+.5", True),
    Token("+5e1", True),
    Token("+1e1", True),
    Token("1e1_0", True),
    Token("Infinity", True),
    Token("inf", True),
    Token("-inf", True),
    Token("infinity", True),
    Token("NaN", True),
    Token("nan", True),
    Token("1e400", True),
    Token("1e309", True),
    Token("-1e309", True),
    Token("9" * 400, True),
    Token("abc", True),
    Token("0x10", True),
    Token("1e", True),
    Token("1e+", True),
    Token("--5", True),
    Token("1,5", True),
    Token("0.5.", True),
    Token("- 5", True),
    Token("1__0", True),
    Token("_1", True),
    Token("1_", True),
    Token("-+5", True),
    Token("+-5", True),
    Token("0b1", True),
    Token("5.e", True),
    Token(".e1", True),
    Token("-.", True),
    Token("1e0.5", True),
    Token("1.5.2", True),
    Token("1 0", True),
    Token("1\xa00", True),
    Token("%", True),
    Token("\u0663", True),
    Token("\uff12\uff12", True),
    Token("\ufeff22\ufeff", True),
    Token("-.5", False),
    Token("1E+1", False),
    Token("1e+1", False),
    Token("1e-1", False),
    Token("00022", False),
    Token("0022", False),
    Token("022", False),
    Token("-0", False),
    Token("5.0", False),
    Token("1.e1", False),
    Token("5.e1", False),
    Token("5e0", False),
    Token("5E0", False),
    Token("1E5", False),
    Token("00.5", False),
    Token("-.5e1", False),
    Token("0e0", False),
    Token("1e-400", False),
    Token("1e308", False),
    Token("0.1e1", False),
    Token(" ", True),
    Token("22,5", True),
    Token("NaN ", True),
    Token("", True),
)
