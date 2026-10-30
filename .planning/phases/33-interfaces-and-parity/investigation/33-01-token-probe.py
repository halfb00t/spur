"""The tokens a Chromium number box blanks, on every number field Phase 33 serves (33-01).

D-02 makes the browser's own table the authority for the server's number rule, not a
hand-written regex, so this prints what Chromium reads back for each token on each input,
beside what pydantic and the API make of the same token. Plan 33-03 transcribes
`33-01-token-table.json` (one `{"token", "blank"}` per token, `blank` true only when the box
blanked the token on every probed input) into `tests/number_box_tokens.py`.

Each input is an `<input type=number>` carrying the attributes `buildForm()` gives it
(`min`, `max` from the schema, `step = prop.step ?? (integer ? 1 : 'any')`), plus the
page's `mate_teeth` box. Each token is assigned through `.value` and read back. The Python
columns are: pydantic's lax `int` and `float` parse; the status `/api/info` answers when the
token is the value of each gear number field and of `mate_teeth`; whether `ShaftParams`
validates the token in each shaft number field; the four-condition rule of 33-RESEARCH
Pattern 3; and whether `float()` reads the token as a non-finite number.

Run from the repository root: `.venv/bin/python <this file>`. The rows are printed as the
Markdown table `bench/RESULTS.md` carries.
"""

from __future__ import annotations

import html
import importlib.metadata
import json
import math
import os
from pathlib import Path

from fastapi.testclient import TestClient
from playwright.sync_api import sync_playwright
from pydantic import BaseModel, TypeAdapter, ValidationError

from spur.app import app
from spur.params import GearParams
from spur.shaft_params import ShaftParams

HERE = Path(__file__).resolve().parent
TABLE = HERE / "33-01-token-table.json"
ROOT = HERE.parents[3]
MATE_TEETH = "mate_teeth"
Bound = int | float | None  # a schema `minimum` or `maximum`, absent when unbounded

# D-02's list first, then 33-RESEARCH's observed table, then the empty string (L44 D-06's
# boundary), the lone space and the two tokens 28-01 probed that the research table lacks.
# Invisible and non-ASCII characters are escapes, so this file stays ASCII.
RAW_TOKENS: list[str] = [
    # D-02: the WR-02 class, then the controls that must stay accepted.
    " 22", "22 ", "%2022", "1_0", "22.", "5.", "+5", "+22", "2.",
    "22", "2.5", "-1", "1e1", ".5",
    # 33-RESEARCH: blank, pydantic parses (whitespace of every kind around the number).
    "\t22", "22\n", "22\x0b", "\x0c22", "22" + chr(0x2028), "\xa0 22", "22\xa0",
    chr(0x2003) + "22", "22" + chr(0x2003),
    "2_2", "1_000", "+0",
    "0.", "-5.",
    "+.5", "+5e1", "+1e1", "1e1_0",
    # blank, pydantic parses, the field's bounds or the finite check refuse.
    "Infinity", "inf", "-inf", "infinity", "NaN", "nan", "1e400", "1e309", "-1e309", "9" * 400,
    # blank, pydantic refuses.
    "abc", "0x10", "1e", "1e+", "--5", "1,5", "0.5.", "- 5", "1__0", "_1", "1_", "-+5", "+-5",
    "0b1", "5.e", ".e1", "-.", "1e0.5", "1.5.2", "1 0", "1\xa00", "%",
    chr(0x663), chr(0xFF12) * 2, chr(0xFEFF) + "22" + chr(0xFEFF),
    # held: the box reads the token back.
    "-.5", "1E+1", "1e+1", "1e-1", "00022", "0022", "022", "-0", "5.0", "1.e1", "5.e1", "5e0",
    "5E0", "1E5", "00.5", "-.5e1", "0e0", "1e-400", "1e308", "0.1e1",
    # 28-01 and the empty string.
    " ", "22,5", "NaN ", "",
]


def unique(tokens: list[str]) -> list[str]:
    """Drop repeats, keep the first occurrence's place."""
    return list(dict.fromkeys(tokens))


def label(token: str) -> str:
    """The token as an ASCII Python literal, long digit runs shortened."""
    if len(token) > 40 and len(set(token)) == 1:
        return f"{token[0]!r} * {len(token)}"
    return ascii(token)


def number_inputs(model: type[BaseModel]) -> list[tuple[str, Bound, Bound, str]]:
    """`(name, min, max, step)` of every integer/number property without an enum.

    This is `buildForm()`'s branch: `input.type = 'number'` for a non-enum property,
    `min`/`max` from `minimum`/`maximum`, `step = prop.step ?? (integer ? 1 : 'any')`.
    """
    out = []
    for name, prop in model.model_json_schema()["properties"].items():
        if "enum" in prop or prop.get("type") not in ("integer", "number"):
            continue
        step = prop.get("step", 1 if prop["type"] == "integer" else "any")
        out.append((name, prop.get("minimum"), prop.get("maximum"), str(step)))
    return out


def input_html(key: str, name: str, low: Bound, high: Bound, step: str) -> str:
    """One `<input>` the way `buildForm()` leaves it; `key` tells the two models' fields apart."""
    attrs = f'type="number" inputmode="decimal" name="{html.escape(name)}" data-key="{key}"'
    if low is not None:
        attrs += f' min="{low}"'
    if high is not None:
        attrs += f' max="{high}"'
    return f'<input {attrs} step="{html.escape(step)}">'


def lax_parses(adapter: TypeAdapter[int] | TypeAdapter[float], token: str) -> bool:
    """True when pydantic's lax mode reads the string as that type."""
    try:
        adapter.validate_python(token)
    except ValidationError:
        return False
    return True


def rule_refuses(token: str) -> bool:
    """33-RESEARCH Pattern 3's four conditions."""
    return token != token.strip() or "_" in token or token.startswith("+") or token.endswith(".")


def non_finite(token: str) -> bool:
    """True when Python's `float()` reads the token as inf or nan."""
    try:
        return not math.isfinite(float(token))
    except ValueError:
        return False


def read_back(inputs: list[str], tokens: list[str]) -> tuple[dict[str, list[str]], str]:
    """Assign every token to every input in Chromium and read `.value` back."""
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            page = browser.new_page()
            page.set_content("<!doctype html><form>" + "".join(inputs) + "</form>")
            got = page.evaluate(
                """(tokens) => {
                    const out = {};
                    for (const el of document.querySelectorAll('input')) {
                        out[el.dataset.key] = tokens.map((t) => { el.value = t; return el.value; });
                    }
                    return out;
                }""",
                tokens,
            )
            return got, browser.version
        finally:
            browser.close()


def main() -> int:
    # The gate's own headless shell: the Makefile exports this path (line 28) and Playwright's
    # default cache holds no browser on this host, so a bare run would not find Chromium.
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(ROOT / ".venv" / "ms-playwright"))
    tokens = unique(RAW_TOKENS)
    gear = number_inputs(GearParams)
    shaft = number_inputs(ShaftParams)
    # `module` and `teeth` are fields of both models, so each box is keyed by its model too.
    boxes = [
        *[(f"gear.{n}", n, lo, hi, st) for n, lo, hi, st in gear],
        (MATE_TEETH, MATE_TEETH, 6, 1000, "1"),
        *[(f"shaft.{n}", n, lo, hi, st) for n, lo, hi, st in shaft],
    ]
    names = [b[0] for b in boxes]
    assert len(set(names)) == len(names)
    got, chromium = read_back([input_html(*b) for b in boxes], tokens)
    assert sorted(got) == sorted(names)

    client = TestClient(app)
    gear_names = [g[0] for g in gear] + [MATE_TEETH]
    shaft_names = [s[0] for s in shaft]
    int_adapter, float_adapter = TypeAdapter(int), TypeAdapter(float)

    print(f"Chromium: {chromium}")
    print(f"playwright: {importlib.metadata.version('playwright')}")
    print(f"probed inputs: {len(names)} ({len(gear)} gear + {MATE_TEETH} + {len(shaft)} shaft)")
    print(f"names: {', '.join(names)}")
    print(f"tokens: {len(tokens)}")
    print()
    print("| Token | Box | int | float | /api/info 200 (gear) | ShaftParams validates | Rule "
          "| Non-finite |")
    print("|---|---|---|---|---|---|---|---|")

    rows = []
    for i, token in enumerate(tokens):
        blank_on = sum(1 for n in names if got[n][i] == "")
        ok_gear = sum(
            client.get("/api/info", params={n: token}).status_code == 200 for n in gear_names
        )
        ok_shaft = sum(
            _shaft_validates(n, token) for n in shaft_names
        )
        row = {
            "token": token,
            "blank_on": blank_on,
            "int": lax_parses(int_adapter, token),
            "float": lax_parses(float_adapter, token),
            "gear200": ok_gear,
            "shaft": ok_shaft,
            "rule": rule_refuses(token),
            "non_finite": non_finite(token),
        }
        rows.append(row)
        print(
            f"| `{label(token)}` | {blank_on}/{len(names)} | {_yn(row['int'])} | "
            f"{_yn(row['float'])} | {ok_gear}/{len(gear_names)} | {ok_shaft}/{len(shaft_names)} | "
            f"{'refuses' if row['rule'] else 'lets through'} | {_yn(row['non_finite'])} |"
        )

    def blank_all(r: dict[str, object]) -> bool:
        return r["blank_on"] == len(names)

    def held_all(r: dict[str, object]) -> bool:
        return r["blank_on"] == 0

    def accepted(r: dict[str, object]) -> bool:
        return bool(r["gear200"]) or bool(r["shaft"])

    held_refused = [r for r in rows if held_all(r) and r["rule"]]
    through_accepted = [r for r in rows if blank_all(r) and not r["rule"] and accepted(r)]
    through_refused = [r for r in rows if blank_all(r) and not r["rule"] and not accepted(r)]
    mixed = [r for r in rows if not blank_all(r) and not held_all(r)]

    print()
    print(f"held but the rule refuses: {_labels(held_refused)}")
    print(f"blank, accepted somewhere, the rule lets it through: {_labels(through_accepted)}")
    print(f"blank, refused everywhere already, the rule lets it through: "
          f"{_labels(through_refused)}")
    print(f"  of which pydantic parses it (a bound or the finite check refuses): "
          f"{_labels([r for r in through_refused if r['int'] or r['float']])}")
    print(f"  of which pydantic refuses to parse it: "
          f"{_labels([r for r in through_refused if not (r['int'] or r['float'])])}")
    print(f"  of which float() reads non-finite: "
          f"{_labels([r for r in through_refused if r['non_finite']])}")
    print(f"not uniform: {_labels(mixed)}")
    for r in mixed:
        blank_names = [n for n in names if got[n][tokens.index(str(r['token']))] == ""]
        print(f"  {label(str(r['token']))} blank on: {', '.join(blank_names)}")

    TABLE.write_text(
        json.dumps([{"token": r["token"], "blank": blank_all(r)} for r in rows], indent=2) + "\n",
        encoding="ascii",
    )
    print()
    blank_count = sum(blank_all(r) for r in rows)
    print(f"blank on every input: {blank_count} of {len(rows)}; wrote {TABLE.name}")
    return 0


def _shaft_validates(name: str, token: str) -> bool:
    """True when `ShaftParams` accepts the token as the value of that one field."""
    try:
        ShaftParams.model_validate({name: token})
    except ValidationError:
        return False
    return True


def _yn(value: object) -> str:
    return "yes" if value else "no"


def _labels(rows: list[dict[str, object]]) -> str:
    return ", ".join(label(str(r["token"])) for r in rows) if rows else "none"


if __name__ == "__main__":
    raise SystemExit(main())
