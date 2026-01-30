from typing import Annotated, List, Dict, Any, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel
from moslicenzia.schemas.models import AgentResult, ValidationStatus

class ExpertiseState(TypedDict):
    """
    Состояние графа для процесса предварительной экспертизы.
    """
    application_id: str
    documents: List[Dict[str, str]]  # List of {path, type}
    extracted_data: Dict[str, Any]  # Data from Agent 2 and Agent 3
    agent_results: List[AgentResult]
    analysis_findings: List[str]
    overall_status: ValidationStatus
    recommendation: str
    decision_draft: str
    next_action: Optional[str]
