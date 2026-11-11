"""Shared test setup: put the Worker source on the import path and expose the
legacy result fixtures."""

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures"
sys.path.insert(0, str(ROOT / "src"))

_ROW = re.compile(r"^(?P<name>[^&]+) & (?P<state>[A-Z]{2})(?P<pops>( & \d+)+)\\\\ $")


def read_legacy_table(name):
    """County rows from a legacy justPop LaTeX table: [(name, state, [pops])]."""
    rows = []
    for line in (FIXTURES / name).read_text().splitlines():
        m = _ROW.match(line)
        if m:
            pops = [int(p) for p in m["pops"].split(" & ")[1:]]
            rows.append((m["name"].strip(), m["state"], pops))
    return rows


@pytest.fixture
def legacy_table():
    return read_legacy_table
