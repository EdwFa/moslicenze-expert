import os
import sys

# Добавление корня проекта в путь поиска модулей
sys.path.append(os.getcwd())

from moslicenzia.agents.agent1_reception.agent import ReceptionAgent
from moslicenzia.agents.agent2_parser.agent import ParserAgent
from moslicenzia.schemas.models import DocType

def test_pipeline():
    reception = ReceptionAgent()
    parser = ParserAgent()
    
    docs_dir = "moslicenzia/data/application_docs"
    files = [
        "Заявление о выдаче лицензии.xml",
        "Выписка из ЕГРЮЛ по запросам органов государственной власти (СМЭВ 3).xml",
        "ФНС. Cведения о наличии (отсутствии) задолженности свыше 3000 рублей.xml",
        "РНиП. Cведения об оплатах [запрос+ответ].xml",
        "Выписка из ЕГРН об объекте недвижимости [из zip-файла, находящегося в ЦХЭД].xml"
    ]
    
    print("--- Starting Verification ---")
    
    for filename in files:
        path = os.path.join(docs_dir, filename)
        if not os.path.exists(path):
            print(f"Skipping {filename}: Not found")
            continue
            
        print(f"\nProcessing: {filename}")
        
        # 1. Классификация
        res1 = reception.classify_document(path)
        print(f"Agent 1 (Classifier): {res1.status} - {res1.data.get('doc_type') if res1.data else res1.comment}")
        
        if res1.data and "doc_type" in res1.data:
            doc_type = res1.data["doc_type"]
            
            # 2. Парсинг
            res2 = parser.parse(doc_type, path)
            print(f"Agent 2 (Parser): {res2.status}")
            if res2.data:
                print(f"Extracted Data: {res2.data}")
            else:
                print(f"Error: {res2.comment}")
        else:
            print("Failed to classify, skipping parser.")

if __name__ == "__main__":
    test_pipeline()
