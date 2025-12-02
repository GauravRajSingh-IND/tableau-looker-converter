# domain/lookml_project.py
from __future__ import annotations

from typing import List
from pydantic import BaseModel


class LookMLFile(BaseModel):
    """
    A single LookML file (model, view, or dashboard).

    - filename: how it will be written in the LookML project
    - content: full text content of the .lkml file
    """
    filename: str
    content: str


class LookMLProject(BaseModel):
    """
    In-memory representation of the generated LookML project.

    We separate files by type so it's easy to:
    - decide folder layout,
    - handle model/view/dashboard differently if needed,
    - report counts to the user/QA.
    """
    model_files: List[LookMLFile]
    view_files: List[LookMLFile]
    dashboard_files: List[LookMLFile]

    def all_files(self) -> List[LookMLFile]:
        """
        Convenience helper: return all files together,
        in a stable order (model → views → dashboards).
        """
        return self.model_files + self.view_files + self.dashboard_files