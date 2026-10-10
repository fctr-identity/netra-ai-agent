"""Compatibility result for a specialist path with no Netra implementations yet."""
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from src.data.schemas.artifact_manifest import DelegationResult

class SpecialToolResult(BaseModel):
    """Typed execution result for the current special-tool path."""
    success: bool
    tool_operation: Optional[str] = None
    tool_name: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    raw_result: Optional[Dict[str, Any]] = None
    summary_text: Optional[str] = None
    response_text: Optional[str] = None
    display_type: Literal["markdown", "table"] = "markdown"
    response_mode: Literal["direct", "synthesis_ready"] = "direct"
    artifact_keys: List[str] = Field(default_factory=list)
    result_set_refs: List[str] = Field(default_factory=list)
    delegation_result: Optional[DelegationResult] = None
    error: Optional[str] = None

def get_special_tool_capability_summary():
    return {"available": False, "operations": []}


async def handle_special_query(*args, **kwargs):
    error = "No specialized analysis is available; use the reviewed Graph or SQL catalog."
    return SpecialToolResult(success=False, error=error,
        delegation_result=DelegationResult(success=False, source_specialist="special",
            result_mode="failed", summary=error, capability_gaps=[error], error=error))
