"""Logika listowania katalogów i uruchamiania analiz (bez Streamlit)."""
from __future__ import annotations

import importlib
import matplotlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import OUTPUT_DIR, WAR_ECONOMIC_CSV

ANALYSIS_MODULES: dict[str, str] = {
    "economic_resilience_hyperinflation": "analyses.economic_resilience_hyperinflation.analysis",
    "black_market_informal_economy": "analyses.black_market_informal_economy.analysis",
}


def list_analysis_dirs() -> list[Path]:
    if not OUTPUT_DIR.is_dir():
        return []
    return sorted(
        [p for p in OUTPUT_DIR.iterdir() if p.is_dir()],
        key=lambda p: p.name.lower(),
    )


def list_pngs(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return sorted(folder.glob("*.png"), key=lambda p: p.name.lower())


def run_analysis(module_path: str, csv_path: Path | None) -> list[Path]:
   

    matplotlib.use("Agg")
    mod = importlib.import_module(module_path)
    return mod.run(csv_path)


def fmt_size(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n / (1024 * 1024):.1f} MB"


def resolve_csv_path(csv_custom: str) -> Path | None:
    if csv_custom.strip():
        p = Path(csv_custom.strip()).expanduser()
        return p if p.is_file() else None
    if WAR_ECONOMIC_CSV.is_file():
        return WAR_ECONOMIC_CSV
    return None
