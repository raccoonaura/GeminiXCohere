# Gemini X Cohere

## 專案簡述
- 本專案能同時呼叫 Gemini 與 Cohere，整合回覆
- 支援多回合對話、思考模式、文檔 RAG、圖片讀取

## 功能特色
- 使用者自備 API key
- 同時呼叫Gemini及Cohere的回覆並整合
- 生成完整回答前先串流匯出即時簡答
- 多回合對話 (記憶系統)
- 快取系統 (Cache)
- 思考模式 (Reasoning)
- 檔案檢索 (RAG / 圖片讀取)
- CoT 內容顯示 (Chain-of-Thought)

## 環境需求
- Python 3.13.x
- 必要套件：請參考 `requirements.txt`
- Gemini及Cohere的API Key

## 專案架構
- README.md: 主入口說明
- LICENSE: 授權
- requirements.txt: 環境需求
- main.py: 主程式
- src/: 程式碼
- docs/: 文檔