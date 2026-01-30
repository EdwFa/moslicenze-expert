import streamlit as st
import os
import tempfile
import json
from datetime import datetime
from moslicenzia.agents.agent4_analytical.agent import AnalyticalOrchestrator
from moslicenzia.schemas.models import ValidationStatus

# Настройка страницы
st.set_page_config(
    page_title="Moslicenzia AI Expert",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Пользовательский CSS для премиум-вида
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #2e7d32;
        color: white;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #388e3c;
        transform: scale(1.02);
    }
    .finding-card {
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2e7d32;
        background-color: #1e2227;
        margin-bottom: 10px;
    }
    .critical { border-left-color: #d32f2f; }
    .warning { border-left-color: #fbc02d; }
    .success { border-left-color: #2e7d32; }
    
    .report-container {
        padding: 20px;
        background-color: #ffffff;
        color: #333333;
        border-radius: 10px;
        font-family: 'Courier New', Courier, monospace;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🛡️ Moslicenzia: Предварительная Экспертиза")
    st.subheader("Автоматизированное рабочее место эксперта (Subsystem AI)")

    with st.sidebar:
        st.header("Настройки и Инфо")
        st.info("Система проверяет документы на лицензию по продаже алкогольной продукции.")
        st.divider()
        st.markdown("### Агенты в работе:")
        st.markdown("- **A1:** Прием & Классификация ✅")
        st.markdown("- **A2:** Парсер XML ✅")
        st.markdown("- **A4:** Аналитический движок ✅")
        st.markdown("- **A5:** Генератор отчетов ✅")
        st.markdown("- **A6:** Интеграция ФИАС 🔄")
        
        st.divider()
        if st.button("Очистить кэш"):
            st.rerun()

    # Основной интерфейс
    st.markdown("### 📥 Загрузка документов")
    uploaded_files = st.file_uploader(
        "Выберите XML файлы (Заявление, ЕГРЮЛ, ФНС, РНиП, Росреестр)", 
        type=["xml"], 
        accept_multiple_files=True,
        help="Вы можете загрузить сразу несколько файлов, относящихся к одной заявке."
    )

    if uploaded_files:
        st.success(f"Загружено файлов: {len(uploaded_files)}")
        
        if st.button("🚀 Начать экспертизу"):
            with st.status("Выполнение анализа агентами...", expanded=True) as status:
                st.write("Создание временного хранилища...")
                with tempfile.TemporaryDirectory() as tmp_dir:
                    doc_list = []
                    for uploaded_file in uploaded_files:
                        tmp_path = os.path.join(tmp_dir, uploaded_file.name)
                        with open(tmp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        doc_list.append({"path": tmp_path})
                    
                    st.write("Запуск оркестратора Agent 4...")
                    orchestrator = AnalyticalOrchestrator()
                    
                    try:
                        result = orchestrator.run_expertise(doc_list, app_id=f"APP-{datetime.now().strftime('%H%M%S')}")
                        
                        status.update(label="Экспертиза завершена!", state="complete", expanded=False)
                        
                        # Отображение результатов
                        st.divider()
                        col1, col2, col3 = st.columns(3)
                        
                        status_map = {
                            ValidationStatus.SUCCESS: "✅ УСПЕШНО",
                            ValidationStatus.FAILURE: "❌ ОТКАЗ",
                            ValidationStatus.WARNING: "⚠️ ЗАМЕЧАНИЯ",
                        }
                        
                        with col1:
                            st.metric("ID Заявки", result["application_id"])
                        with col2:
                            st.metric("Статус", status_map.get(result["overall_status"], "НЕИЗВЕСТНО"))
                        with col3:
                            st.metric("Рекомендация", result["recommendation"])

                        # Результаты проверок
                        st.markdown("### 🔍 Результаты проверок")
                        for finding in result["analysis_findings"]:
                            css_class = "success"
                            if "КРИТИЧЕСКАЯ" in finding: css_class = "critical"
                            elif "ПРЕДУПРЕЖДЕНИЕ" in finding: css_class = "warning"
                            
                            st.markdown(f"""
                            <div class="finding-card {css_class}">
                                {finding}
                            </div>
                            """, unsafe_allow_html=True)

                        # Отчет
                        st.markdown("### 📄 Итоговое заключение")
                        st.markdown(result['decision_draft'])
                        
                        # Кнопка скачивания
                        st.download_button(
                            label="⬇️ Скачать отчет (Markdown)",
                            data=result['decision_draft'],
                            file_name=f"Expertise_{result['application_id']}.md",
                            mime="text/markdown"
                        )

                    except Exception as e:
                        st.error(f"Ошибка в ходе экспертизы: {str(e)}")
                        st.exception(e)

    else:
        st.info("Пожалуйста, загрузите файлы для начала работы. Вы также можете использовать примеры из папки `data`.")
        
        if st.checkbox("Использовать встроенные примеры"):
            docs_dir = "moslicenzia/data/application_docs"
            if os.path.exists(docs_dir):
                example_files = os.listdir(docs_dir)
                st.write(f"Найдено примеров: {len(example_files)}")
                doc_list = [{"path": os.path.join(docs_dir, f)} for f in example_files if f.endswith(".xml")]
                
                if st.button("🚀 Запустить экспертизу на примерах"):
                    with st.status("Выполнение анализа на примерах...", expanded=True) as status:
                        orchestrator = AnalyticalOrchestrator()
                        try:
                            result = orchestrator.run_expertise(doc_list, app_id="EXAMPLE-APP-001")
                            status.update(label="Экспертиза на примерах завершена!", state="complete", expanded=False)
                            
                            # Отображение результатов
                            st.divider()
                            col1, col2, col3 = st.columns(3)
                            
                            status_map = {
                                ValidationStatus.SUCCESS: "✅ УСПЕШНО",
                                ValidationStatus.FAILURE: "❌ ОТКАЗ",
                                ValidationStatus.WARNING: "⚠️ ЗАМЕЧАНИЯ",
                            }
                            
                            col1.metric("ID Заявки", result["application_id"])
                            col2.metric("Статус", status_map.get(result["overall_status"], "НЕИЗВЕСТНО"))
                            col3.metric("Рекомендация", result["recommendation"])

                            st.markdown("### 🔍 Результаты проверок")
                            for finding in result["analysis_findings"]:
                                css_class = "success"
                                if "КРИТИЧЕСКАЯ" in finding: css_class = "critical"
                                elif "ПРЕДУПРЕЖДЕНИЕ" in finding: css_class = "warning"
                                
                                st.markdown(f"""
                                <div class="finding-card {css_class}">
                                    {finding}
                                </div>
                                """, unsafe_allow_html=True)

                            st.markdown("### 📄 Итоговое заключение")
                            st.markdown(result['decision_draft'])
                        except Exception as e:
                            st.error(f"Ошибка: {str(e)}")
            else:
                st.error(f"Директория {docs_dir} не найдена.")

if __name__ == "__main__":
    main()
