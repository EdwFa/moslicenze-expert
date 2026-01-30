import os
import lxml.etree as ET
from typing import Dict, Any, Optional
from moslicenzia.schemas.models import DocType, AgentResult, ValidationStatus

class ReceptionAgent:
    """
    Агент 1: Прием и Классификация.
    Определяет тип документа и выполняет базовые проверки целостности.
    """
    def __init__(self):
        # Сопоставление корневых тегов или ключевых элементов с DocType
        self.doc_signatures = {
            "Файл": self._classify_file_tag,
            "root": self._classify_root_tag,
            "ReestrExtract": lambda _: DocType.ROSREESTR,
        }

    def _classify_file_tag(self, root: ET._Element) -> Optional[DocType]:
        # Логика классификации для общего тега "Файл"
        # Задолженность ФНС обычно имеет специфический неймспейс или атрибут
        title = root.findtext(".//ЗагДок")
        if title and "задолженности" in title.lower():
            return DocType.FNS_TAX_DEBT
        
        # Проверка на ЕГРЮЛ
        if root.find(".//СвЮЛ") is not None:
            return DocType.EGRUL
            
        # Check for KPP info
        if root.find(".//СвУчОргМН") is not None: # Примечание: В нашем примере это поле было пустым, но мы должны его обрабатывать
            return DocType.KPP_TAX
            
        return None

    def _classify_root_tag(self, root: ET._Element) -> Optional[DocType]:
        # Заявление обычно начинается с <root> или аналогичного тега в некоторых системах, 
        # но предоставленный файл начинается с <Документ> или общей обертки.
        # Настроим на основе просмотренных XML.
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
            
            # 1. Проверка по имени файла (fallback или подсказка)
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

            # 2. Уточнение по содержимому, если необходимо (для надежности)
               # Логика общего анализа содержимого здесь
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
