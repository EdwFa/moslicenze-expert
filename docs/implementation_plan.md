# Implementation Plan - Moslicenzia Hybrid 6-Agent Subsystem

The system follows a hybrid multi-agent architecture with a clear separation of concerns across 6 specialized agents:

## Workflow Diagram

```mermaid
graph TD
    A1["Агент 1: Прием"] --> A2["Агент 2: Парсер XML"]
    A1 --> A3["Агент 3: OCR + LLM"]
    
    A2 --> A4["Агент 4: Аналитический движок (LLM)"]
    A3 --> A4
    
    subgraph MCP_Integration ["MCP-интеграция"]
        A4 <-->|1. Запрос инструментов / 4. Результат| A6["Агент 6: MCP-сервер"]
        A6 <-->|2. Вызов API / 3. Данные| FIAS["API ФИАС"]
    end
    
    A4 --> A5["Агент 5: Генератор отчетов"]
```

## Technical Stack

- **Backend/Orchestration**: Python, LangGraph.
- **UI**: Streamlit.
- **Protocol**: MCP (Model Context Protocol).
- **External API**: Dadata (FIAS/GAR).

## Proposed Agent Architecture

### 1. Agent 1: Reception and Classification

### 2. Agent 2: Structured Data Parser

### 3. Agent 3: Unstructured Doc Processor (OCR)

### 4. Agent 4: Analytical Engine & Orchestrator

### 5. Agent 5: Report Generator

### 6. Agent 6: MCP FIAS Integrator
