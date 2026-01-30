import os
import lxml.etree as ET
from typing import Dict, Any, Optional
from moslicenzia.schemas.models import DocType, AgentResult, ValidationStatus

class ReceptionAgent:
    """
    Agent 1: Reception and Classification.
    Identifies the type of the document and performs basic integrity checks.
    """
    def __init__(self):
        # Mapping of root tags or key elements to DocType
        self.doc_signatures = {
            "Файл": self._classify_file_tag,
            "root": self._classify_root_tag,
            "ReestrExtract": lambda _: DocType.ROSREESTR,
        }

    def _classify_file_tag(self, root: ET._Element) -> Optional[DocType]:
        # Distinctive logic for generic "Файл" tag
        # FNS Tax Debt usually has a specific namespace or attribute
        title = root.findtext(".//ЗагДок")
        if title and "задолженности" in title.lower():
            return DocType.FNS_TAX_DEBT
        
        # Check for EGRUL
        if root.find(".//СвЮЛ") is not None:
            return DocType.EGRUL
            
        # Check for KPP info
        if root.find(".//СвУчОргМН") is not None: # Note: This was empty in our sample but we should handle it
            return DocType.KPP_TAX
            
        return None

    def _classify_root_tag(self, root: ET._Element) -> Optional[DocType]:
        # Application usually starts with <root> or similar in some systems, 
        # but the specific file provided starts with <Документ> or generic wrapper.
        # Let's adjust based on the seen XMLs.
        pass

    def classify_document(self, file_path: str) -> AgentResult:
        if not os.path.exists(file_path):
            return AgentResult(
                agent_id="agent_1",
                doc_id=os.path.basename(file_path),
                status=ValidationStatus.FAILURE,
                comment=f"File not found: {file_path}"
            )

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            tag = root.tag
            
            doc_type = None
            
            # 1. Check by filename (fallback or hint)
            filename = os.path.basename(file_path).lower()
            if "заявление" in filename:
                doc_type = DocType.APPLICATION
            elif "егрн" in filename:
                doc_type = DocType.ROSREESTR
            elif "егрюл" in filename:
                doc_type = DocType.EGRUL
            elif "рнип" in filename:
                if "оплатах" in filename:
                    doc_type = DocType.RNIP_DUTY
                else:
                    doc_type = DocType.RNIP_FINES
            elif "фнс" in filename and "задолженност" in filename:
                doc_type = DocType.FNS_TAX_DEBT

            # 2. Refine by content if needed (robustness)
            if not doc_type:
               # Generic content analysis logic here
               pass

            if doc_type:
                return AgentResult(
                    agent_id="agent_1",
                    doc_id=os.path.basename(file_path),
                    status=ValidationStatus.SUCCESS,
                    data={"doc_type": doc_type},
                    comment=f"Classified as {doc_type}"
                )
            else:
                return AgentResult(
                    agent_id="agent_1",
                    doc_id=os.path.basename(file_path),
                    status=ValidationStatus.WARNING,
                    comment="Could not determine document type."
                )

        except Exception as e:
            return AgentResult(
                agent_id="agent_1",
                doc_id=os.path.basename(file_path),
                status=ValidationStatus.FAILURE,
                comment=f"XML Parsing Error: {str(e)}"
            )
