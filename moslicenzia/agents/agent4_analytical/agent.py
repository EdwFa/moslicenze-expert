import os
from typing import Dict, List, Any
from langgraph.graph import StateGraph, END
from moslicenzia.agents.agent4_analytical.state import ExpertiseState
from moslicenzia.agents.agent1_reception.agent import ReceptionAgent
from moslicenzia.agents.agent2_parser.agent import ParserAgent
from moslicenzia.agents.agent5_report.agent import ReportGeneratorAgent
from moslicenzia.schemas.models import DocType, ValidationStatus, AgentResult

class AnalyticalOrchestrator:
    """
    Агент 4: Центральный аналитический движок и оркестратор.
    Использует LangGraph для координации логики проверок.
    """
    def __init__(self):
        self.reception = ReceptionAgent()
        self.parser = ParserAgent()
        self.reporter = ReportGeneratorAgent()
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(ExpertiseState)
        
        # Определение узлов
        builder.add_node("classify_and_parse", self.classify_and_parse_node)
        builder.add_node("cross_document_check", self.cross_document_check_node)
        builder.add_node("mcp_validation", self.mcp_validation_node)
        builder.add_node("finalize_expertise", self.finalize_expertise_node)
        builder.add_node("generate_report", self.generate_report_node)
        
        # Определение ребер
        builder.set_entry_point("classify_and_parse")
        builder.add_edge("classify_and_parse", "cross_document_check")
        builder.add_edge("cross_document_check", "mcp_validation")
        builder.add_edge("mcp_validation", "finalize_expertise")
        builder.add_edge("finalize_expertise", "generate_report")
        builder.add_edge("generate_report", END)
        
        return builder.compile()

    def classify_and_parse_node(self, state: ExpertiseState) -> Dict:
        """
        Запускает Агента 1 и Агента 2 для всех предоставленных документов.
        """
        results = []
        all_extracted = {}
        findings = []
        
        for doc in state["documents"]:
            path = doc["path"]
            # 1. Классификация
            class_res = self.reception.classify_document(path)
            results.append(class_res)
            
            if class_res.status == ValidationStatus.SUCCESS:
                doc_type = class_res.data["doc_type"]
                # 2. Парсинг
                parse_res = self.parser.parse(doc_type, path)
                results.append(parse_res)
                
                if parse_res.status == ValidationStatus.SUCCESS:
                    all_extracted[doc_type] = parse_res.data
                else:
                    findings.append(f"Ошибка парсинга {doc_type}: {parse_res.comment}")
            else:
                findings.append(f"Ошибка классификации {os.path.basename(path)}: {class_res.comment}")

        return {
            "extracted_data": all_extracted,
            "agent_results": results,
            "analysis_findings": findings
        }

    def cross_document_check_node(self, state: ExpertiseState) -> Dict:
        """
        Выполняет логические проверки (совпадение ИНН, сумма пошлины и т.д.)
        """
        extracted = state["extracted_data"]
        findings = state["analysis_findings"]
        
        app = extracted.get(DocType.APPLICATION)
        egrul = extracted.get(DocType.EGRUL)
        duty = extracted.get(DocType.RNIP_DUTY)
        
        # Логика 1: Совпадение ИНН
        if app and egrul:
            if app["inn"] != egrul["inn"]:
                findings.append(f"КРИТИЧЕСКАЯ ОШИБКА: Несовпадение ИНН между заявлением ({app['inn']}) и ЕГРЮЛ ({egrul['inn']})")
            else:
                findings.append("УСПЕХ: ИНН в заявлении и ЕГРЮЛ совпадает.")
        
        # Логика 2: Проверка лицензионного сбора
        if duty:
            if duty["amount"] < 65000.0:
                findings.append(f"КРИТИЧЕСКАЯ ОШИБКА: Недостаточная сумма госпошлины: {duty['amount']} руб. (Ожидается 65000)")
            else:
                findings.append(f"УСПЕХ: Госпошлина в размере {duty['amount']} руб. подтверждена.")
        
        # Логика 3: Проверка кадастрового номера объекта недвижимости
        rosreestr = extracted.get(DocType.ROSREESTR)
        if app and rosreestr:
            app_cad = app["objects"][0]["cadastral_number"] if app["objects"] else None
            real_cad = rosreestr["cadastral_number"]
            if app_cad != real_cad:
                 findings.append(f"ПРЕДУПРЕЖДЕНИЕ: Несовпадение кадастровых номеров. Заявлено: {app_cad}, В Росреестре: {real_cad}")
            else:
                 findings.append(f"УСПЕХ: Кадастровый номер объекта {app_cad} подтвержден.")

        return {"analysis_findings": findings}

    def mcp_validation_node(self, state: ExpertiseState) -> Dict:
        """
        Вызывает Агента 6 (MCP) для валидации адреса и КПП.
        """
        import asyncio
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        
        findings = state["analysis_findings"]
        extracted = state["extracted_data"]
        app = extracted.get(DocType.APPLICATION)
        
        if not app:
            return {"analysis_findings": findings + ["ПРЕДУПРЕЖДЕНИЕ: Нет данных заявления для проверки в ФИАС."]}

        # Адрес из заявления
        obj = app["objects"][0] if app["objects"] else {}
        address_query = obj.get("address", "")
        
        async def run_mcp_check():
            server_params = StdioServerParameters(
                command="py",
                args=["moslicenzia/agents/agent6_mcp/server.py"]
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # 1. Проверка адреса
                    res_addr = await session.call_tool("check_address_fias", {"address_query": address_query})
                    addr_data = json.loads(res_addr.content[0].text) if res_addr.content else {}
                    
                    mcp_findings = []
                    fias_id = addr_data.get("fias_id")
                    
                    if addr_data.get("status") in ["VALID", "VALID_MOCK"]:
                        mcp_findings.append(f"УСПЕХ: Адрес подтвержден в ФИАС: {addr_data.get('normalized_address')}")
                        
                        # 2. Проверка КПП для этого адреса
                        if fias_id:
                            res_kpp = await session.call_tool("get_subdivision_kpp", {"fias_id": fias_id})
                            expected_kpp = res_kpp.content[0].text if res_kpp.content else None
                            
                            app_kpp = app.get("kpp")
                            if expected_kpp and app_kpp and expected_kpp != app_kpp:
                                mcp_findings.append(f"КРИТИЧЕСКАЯ ОШИБКА: Несоответствие КПП для данного адреса. В заявлении: {app_kpp}, По данным налоговой: {expected_kpp}")
                            elif expected_kpp:
                                mcp_findings.append(f"УСПЕХ: КПП {app_kpp} соответствует учетным данным для этого адреса.")
                    else:
                        mcp_findings.append(f"ПРЕДУПРЕЖДЕНИЕ: Адрес не найден или не валиден в ФИАС: {address_query}")
                        
                    return mcp_findings

        try:
            # Запуск асинхронного MCP-клиента в синхронном узле
            import json
            mcp_results = asyncio.run(run_mcp_check())
            return {"analysis_findings": findings + mcp_results}
        except Exception as e:
            return {"analysis_findings": findings + [f"ОШИБКА: Сбой сервиса MCP/ФИАС: {str(e)}"]}

    def finalize_expertise_node(self, state: ExpertiseState) -> Dict:
        """
        Определяет общий статус и черновик решения.
        """
        findings = state["analysis_findings"]
        status = ValidationStatus.SUCCESS
        
        if any("КРИТИЧЕСКАЯ" in f for f in findings):
            status = ValidationStatus.FAILURE
        elif any("ПРЕДУПРЕЖДЕНИЕ" in f for f in findings):
            status = ValidationStatus.WARNING
            
        recommendation = "Одобрить" if status == ValidationStatus.SUCCESS else "Отказать"
        if status == ValidationStatus.WARNING:
            recommendation = "Требуется уточнение"
            
        return {
            "overall_status": status,
            "recommendation": recommendation,
            "decision_draft": f"На основании анализа: {'; '.join(findings)}"
        }

    def generate_report_node(self, state: ExpertiseState) -> Dict:
        """
        Вызывает Агента 5 для генерации финального отчета.
        """
        report_res = self.reporter.generate_report(state)
        return {
            "agent_results": state["agent_results"] + [report_res],
            "decision_draft": report_res.data.get("report") if report_res.status == ValidationStatus.SUCCESS else state["decision_draft"]
        }

    def run_expertise(self, documents: List[Dict[str, str]], app_id: str = "REQ-001"):
        initial_state = {
            "application_id": app_id,
            "documents": documents,
            "extracted_data": {},
            "agent_results": [],
            "analysis_findings": [],
            "overall_status": ValidationStatus.SUCCESS,
            "recommendation": "",
            "decision_draft": "",
            "next_action": None
        }
        return self.graph.invoke(initial_state)
