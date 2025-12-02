# services/parser_service.py
from __future__ import annotations

from typing import Any, Dict

from domain.tableau_semantic import TableauSemanticModel, TableauWorkbook
from adapters import twb_xml_parser


def parse_twb_to_semantic_model(twb_bytes: bytes) -> TableauSemanticModel:
    """
    High-level entrypoint:
    - Takes raw .twb file bytes
    - Uses a low-level XML parser to get a raw spec (Python dict)
    - Converts that raw spec into our TableauSemanticModel

    This is the ONLY function other layers should import for parsing.
    """
    # 1) Low-level parse: .twb XML → raw Python dict
    raw_spec: Dict[str, Any] = twb_xml_parser.parse_twb_xml_to_raw_spec(twb_bytes)

    # 2) Map raw spec → typed TableauSemanticModel
    semantic_model: TableauSemanticModel = twb_xml_parser.raw_spec_to_semantic_model(raw_spec)

    # 3) Safety: ensure workbook is always present
    if semantic_model.workbook is None:
        semantic_model.workbook = TableauWorkbook(
            id="unknown",
            name="Unknown Workbook",
            description=None,
        )

    return semantic_model
