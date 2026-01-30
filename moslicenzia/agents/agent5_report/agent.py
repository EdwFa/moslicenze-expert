import os
from datetime import datetime
from typing import Dict, Any, List
from jinja2 import Template
from moslicenzia.schemas.models import AgentResult, ValidationStatus

REPORT_TEMPLATE = """
# ЗАКЛЮЧЕНИЕ ПО ПРЕДВАРИТЕЛЬНОЙ ЭКСПЕРТИЗЕ № {{ app_id }}
**Дата:** {{ date }}

## 1. ОБЩИЕ СВЕДЕНИЯ
- **Наименование организации:** {{ company_name }}
- **ИНН:** `{{ inn }}`
- **КПП:** `{{ kpp }}`

## 2. РЕЗУЛЬТАТЫ ПРОВЕРОК
{% for finding in findings %}
{% if 'CRITICAL' in finding %}
> [!CAUTION]
> {{ finding }}
{% elif 'WARNING' in finding %}
> [!WARNING]
> {{ finding }}
{% else %}
- ✅ {{ finding }}
{% endif %}
{% endfor %}

## 3. ИТОГОВОЕ РЕШЕНИЕ
- **Статус:** `{{ status }}`
- **Рекомендация:** **{{ recommendation }}**

### Пояснение:
{{ decision_draft }}

---
*Эксперт: Агент 5 (Автоматизированная система)*
"""

class ReportGeneratorAgent:
    """
    Agent 5: Report Generator.
    Produces formal documents based on findings from Agent 4.
    """
    def generate_text_report(self, state: Dict[str, Any]) -> str:
        extracted = state.get("extracted_data", {})
        app_data = extracted.get("APPLICATION", {})
        
        template = Template(REPORT_TEMPLATE)
        report = template.render(
            app_id=state.get("application_id", "Unknown"),
            date=datetime.now().strftime("%d.%m.%Y %H:%M"),
            company_name=app_data.get("company_name", "Н/Д"),
            inn=app_data.get("inn", "Н/Д"),
            kpp=app_data.get("kpp", "Н/Д"),
            findings=state.get("analysis_findings", []),
            status=state.get("overall_status", "UNKNOWN"),
            recommendation=state.get("recommendation", "Н/Д"),
            decision_draft=state.get("decision_draft", "")
        )
        return report

    def generate_report(self, state: Dict[str, Any]) -> AgentResult:
        try:
            report_text = self.generate_text_report(state)
            
            # In a real app, this might save a PDF or send to a database
            return AgentResult(
                agent_id="agent_5",
                doc_id=state.get("application_id", "Unknown"),
                status=ValidationStatus.SUCCESS,
                data={"report": report_text},
                comment="Report generated successfully."
            )
        except Exception as e:
            return AgentResult(
                agent_id="agent_5",
                doc_id=state.get("application_id", "Unknown"),
                status=ValidationStatus.FAILURE,
                comment=f"Report Generation Error: {str(e)}"
            )
