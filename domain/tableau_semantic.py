# domain/tableau_semantic.py
from __future__ import annotations

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# -------------------------
# Workbook
# -------------------------
class TableauWorkbook(BaseModel):
    """Basic info about the Tableau workbook."""
    id: str
    name: str
    description: Optional[str] = None


# -------------------------
# Connection / Tables / Joins
# -------------------------
class TableauConnection(BaseModel):
    """How the datasource connects to data."""
    type: Literal["table", "custom_sql", "extract", "unknown"] = "unknown"
    dialect: Optional[str] = None       # e.g. snowflake, bigquery, postgres
    database: Optional[str] = None
    schema: Optional[str] = None
    table: Optional[str] = None         # main table name if known
    raw_sql: Optional[str] = None       # if Tableau uses custom SQL


class TableauTable(BaseModel):
    """Logical table inside a datasource."""
    id: str
    name: str
    database: Optional[str] = None
    schema: Optional[str] = None
    table: Optional[str] = None
    is_primary: bool = False            # best guess: main fact table


class TableauJoin(BaseModel):
    """Join between logical tables."""
    id: str
    left_table_id: str                  # references TableauTable.id
    right_table_id: str                 # references TableauTable.id
    join_type: Literal["inner", "left", "right", "full", "unknown"] = "unknown"
    condition: str                      # raw join expression (Tableau style)
    needs_manual_review: bool = False   # parser/heuristic flag


# -------------------------
# Fields & Calculations
# -------------------------
class TableauField(BaseModel):
    """
    Single field (dimension or measure) in a datasource.
    This is the MOST important structure for LookML generation.
    """
    id: str
    name: str                           # Tableau field name
    caption: Optional[str] = None       # user-friendly label if exists
    table_id: Optional[str] = None      # which TableauTable this belongs to

    # Core semantics
    role: Literal["dimension", "measure", "unknown"] = "unknown"
    datatype: Literal["string", "number", "date", "datetime", "boolean", "unknown"] = "unknown"
    aggregation: Optional[str] = None   # sum, avg, count, etc. (for measures)

    # Where it comes from
    source: Literal["column", "calculation", "parameter", "unknown"] = "unknown"
    column_name: Optional[str] = None           # underlying physical column name (if known)
    calculation_id: Optional[str] = None        # link into TableauCalculation.id

    is_hidden: bool = False
    tags: List[str] = Field(default_factory=list)


class TableauCalculation(BaseModel):
    """
    A calculated field definition.

    We separate this from TableauField so:
    - Fields can point to a shared calc by calculation_id.
    - QA/LLM can reason about calc complexity independent of display name.
    """
    id: str
    name: str                               # usually same as field name
    datasource_id: str                      # which datasource this belongs to
    expression: str                         # raw Tableau calc expression
    datatype: Literal[
        "string", "number", "date", "datetime", "boolean", "unknown"
    ] = "unknown"
    category: Literal[
        "simple", "lod", "table_calc", "parameter_based", "unknown"
    ] = "unknown"                           # high-level type of calc
    complexity_score: float = 0.0           # 0–1 heuristic (optional, parser can set later)


# -------------------------
# Sheets, Filters & Viz
# -------------------------
class TableauSheetFilter(BaseModel):
    """Filter applied on a sheet."""
    field_id: str
    expression: str                         # Tableau-style filter expression
    applied_to: Literal["rows", "columns", "table", "unknown"] = "unknown"


class TableauSheetVisualization(BaseModel):
    """
    Minimal visualization metadata per sheet.

    This will help us:
    - pick chart types for LookML dashboards,
    - select which fields go into which tiles.
    """
    chart_type: Literal[
        "table", "bar", "line", "area", "scatter", "pie", "single_value", "unknown"
    ] = "unknown"

    primary_dimension_id: Optional[str] = None         # x-axis / main grouping
    primary_measure_ids: List[str] = Field(default_factory=list)   # y-axis metrics
    split_by_dimension_ids: List[str] = Field(default_factory=list)  # series/color splits

    sort_order: Optional[str] = None       # e.g. "by_primary_dimension_asc"
    granularity: Optional[str] = None      # e.g. "day", "month", "year", "category"


class TableauSheet(BaseModel):
    """
    A worksheet in Tableau (a 'view').

    For MVP:
    - we care about which fields are used (used_field_ids),
    - plus basic viz metadata (visualization),
    - plus filters (for dashboard filters or query filters).
    """
    id: str
    name: str
    datasource_id: str
    used_field_ids: List[str] = Field(default_factory=list)
    filters: List[TableauSheetFilter] = Field(default_factory=list)
    visualization: Optional[TableauSheetVisualization] = None
    description: Optional[str] = None


# -------------------------
# Datasource (ties tables, joins, fields, calcs together)
# -------------------------
class TableauDatasource(BaseModel):
    """Represents a Tableau datasource (logical model)."""
    id: str
    name: str
    connection: TableauConnection
    tables: List[TableauTable] = Field(default_factory=list)
    joins: List[TableauJoin] = Field(default_factory=list)
    fields: List[TableauField] = Field(default_factory=list)


# -------------------------
# TOP-LEVEL MODEL
# -------------------------
class TableauSemanticModel(BaseModel):
    """
    TOP-LEVEL MODEL:
    This is what:
    - the parser will output,
    - we will save as semantic_model.json,
    - we will send (in summarized form) to Vertex AI.
    """
    schema_version: str = "1.0"
    workbook: TableauWorkbook
    datasources: List[TableauDatasource] = Field(default_factory=list)
    calculations: List[TableauCalculation] = Field(default_factory=list)
    sheets: List[TableauSheet] = Field(default_factory=list)
