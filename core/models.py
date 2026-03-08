"""Shared data models / types for the project."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class ConflictRecord:
    """Represents one row of war economic impact data (conceptual model)."""
    conflict_name: str
    conflict_type: str
    region: str
    start_year: int
    end_year: int
    status: str
    primary_country: str
    gdp_change_pct: float
    inflation_rate: Optional[float] = None
    cost_of_war_usd: Optional[float] = None

    @property
    def duration_years(self) -> int:
        return max(0, self.end_year - self.start_year)
