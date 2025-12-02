# domain/qa_report.py
from __future__ import annotations

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class DashboardSummary(BaseModel):
    """
    Optional high-level summary of dashboard conversion,
    useful for reporting and debugging.
    """
    total_sheets: int
    dashboards_created: int
    tiles_created: int
    tiles_by_type: Dict[str, int] = Field(default_factory=dict)
    # e.g. {"table": 3, "bar": 1, "line": 1}


class QAReport(BaseModel):
    """
    Output of QA step (LLM Call 2) and what we persist as qa_report.json.
    """
    manual_intervention_required: bool
    reasons: List[str] = Field(default_factory=list)

    # Optional: more structured info about dashboards
    dashboard_summary: Optional[DashboardSummary] = None

    # Free-form notes / commentary (optional)
    notes: Optional[str] = None