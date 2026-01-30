# Walkthrough: Moslicenzia Expertise Subsystem

This document demonstrates the completed pipeline for the **Preliminary Expertise Subsystem**.

## 1. System Architecture

The system is orchestrated by **LangGraph (Agent 4)** and localized to **Russian**.

## 2. Integrated FIAS Validation

Agent 6 provides real-time address normalization and KPP verification via the MCP protocol.

## 3. Streamlit Dashboard

A premium UI is available for experts to upload documents, run analysis, and download results.

### To start

```bash
py -m streamlit run streamlit_app.py
```

## 4. Final Results (Markdown Report)

The system generates polished Markdown reports with specialized alerts for critical errors.

![Screenshot of Streamlit](file:///c:/Users/user/.gemini/antigravity/brain/9b365600-a2b4-4953-a892-304c2d494382/verify_streamlit_app_1769765007198.webp)
