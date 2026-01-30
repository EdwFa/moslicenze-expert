from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class DocType(str, Enum):
    APPLICATION = "APPLICATION"  # 1. Заявление
    POWER_OF_ATTORNEY = "POA"   # 2. Доверенность
    FNS_TAX_DEBT = "FNS"        # 3. ФНС (Долги)
    EGRUL = "EGRUL"             # 4. ЕГРЮЛ
    RNIP_FINES = "RNIP_FINES"   # 5. РНиП (Штрафы)
    RNIP_DUTY = "RNIP_DUTY"     # 6. РНиП (Госпошлина)
    ROSREESTR = "ROSREESTR"     # 7. Росреестр
    KPP_TAX = "KPP"             # 8. КПП (Налоги)

class ValidationStatus(str, Enum):
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    FAILURE = "FAILURE"

class AgentResult(BaseModel):
    agent_id: str
    doc_id: str
    status: ValidationStatus
    data: Dict = Field(default_factory=dict)
    comment: Optional[str] = None

class FinalExpertiseReport(BaseModel):
    application_id: str
    overall_status: ValidationStatus
    agent_results: List[AgentResult]
    recommendation: str
    decision_draft: Optional[str] = None
