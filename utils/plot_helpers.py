"""Shared plotting utilities (style, save)."""
import matplotlib.pyplot as plt
from pathlib import Path


def setup_plot_style(ax=None):
    """Apply consistent style for analysis charts."""
    try:
        plt.style.use("seaborn-v0_8-whitegrid")
    except OSError:
        try:
            plt.style.use("seaborn-whitegrid")
        except OSError:
            pass
    return ax


def save_figure(fig, path: Path, dpi: int = 150):
    """Save figure to path; create parent dirs if needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
