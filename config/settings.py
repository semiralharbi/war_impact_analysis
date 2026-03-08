"""Project paths and constants."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_DIR = PROJECT_ROOT / "dataset"
WAR_ECONOMIC_CSV = DATASET_DIR / "war_economic_impact_dataset.csv"

OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def get_analysis_output_dir(analysis_name: str) -> Path:
    """Return output directory for a given analysis (created if needed)."""
    path = OUTPUT_DIR / analysis_name
    path.mkdir(parents=True, exist_ok=True)
    return path
