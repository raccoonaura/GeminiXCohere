# Gemini X Cohere

## 專案簡述
本專案能同時呼叫 Gemini 與 Cohere，整合回覆，支援多回合對話、思考模式，並允許使用者自備 API key。

## 功能特色
- 使用者自備API key
- 同時呼叫Gemini及Cohere的回覆並整合
- 生成完整回答前先匯出即時簡答
- 多回合對話（記憶系統）
- 思考模式 (Reasoning)

## 環境需求
- Python 3.10+
- 必要套件：請參考 `requirements.txt`
- Gemini及Cohere的API Key

## 專案架構
- README.md: 主入口說明
- LICENSE: 授權
- requirements.txt: 環境需求
- main.py: 主程式
- src/: 程式碼
- docs/: 文檔