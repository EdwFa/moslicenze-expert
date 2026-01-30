import os
import json
from moslicenzia.agents.agent4_analytical.agent import AnalyticalOrchestrator

def verify_full_pipeline():
    orchestrator = AnalyticalOrchestrator()
    
    docs_dir = "moslicenzia/data/application_docs"
    # Список документов для обработки в одном пакете (одно заявление)
    documents = [
        {"path": os.path.join(docs_dir, "Заявление о выдаче лицензии.xml")},
        {"path": os.path.join(docs_dir, "Выписка из ЕГРЮЛ по запросам органов государственной власти (СМЭВ 3).xml")},
        {"path": os.path.join(docs_dir, "ФНС. Cведения о наличии (отсутствии) задолженности свыше 3000 рублей.xml")},
        {"path": os.path.join(docs_dir, "РНиП. Cведения об оплатах [запрос+ответ].xml")},
        {"path": os.path.join(docs_dir, "Выписка из ЕГРН об объекте недвижимости [из zip-файла, находящегося в ЦХЭД].xml")}
    ]
    
    print("=== Running Full Analytical Pipeline (Agent 4) ===")
    
    result = orchestrator.run_expertise(documents, app_id="TEST-APP-001")
    
    print(f"\nApplication ID: {result['application_id']}")
    print(f"Overall Status: {result['overall_status']}")
    print(f"Recommendation: {result['recommendation']}")
    
    print("\n--- Findings ---")
    for finding in result["analysis_findings"]:
        print(f"- {finding}")
        
    print("\n--- Final Decision Draft ---")
    print(result["decision_draft"])
    
    # Сохранение результата в файл для проверки
    with open("expertise_result_sample.json", "w", encoding="utf-8") as f:
        # Фильтрация результатов агентов для сериализации (AgentResult — это модель pydantic)
        serializable_result = {
            "application_id": result["application_id"],
            "overall_status": str(result["overall_status"]),
            "recommendation": result["recommendation"],
            "findings": result["analysis_findings"],
            "decision_draft": result["decision_draft"]
        }
        json.dump(serializable_result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify_full_pipeline()
