# Gemini X Cohere

## 專案簡述
- 本專案能同時呼叫 Gemini 與 Cohere 旗下模型，並整合回覆
- 支援多回合對話、思考模式、文檔 RAG、圖片讀取

## 功能特色
- 使用者自備 API key
- 同時呼叫 Gemini 及 Command 的回覆並整合
- 生成完整回答前先串流匯出即時簡答
- 多回合對話 (記憶系統)
- 快取系統 (Cache)
- 思考模式 (Reasoning)
- 圖片理解 (Image Understanding)
- 檔案檢索 (文檔 / Text-to-SQL RAG)
- RAG 支援多種檔案類型
- CoT 內容顯示 (Chain-of-Thought)

## 環境需求
- Python 3.13.x
- 必要套件：請參考 `requirements.txt`
- Gemini 及 Cohere 的 API Key
- 若使用 RAG 時需要更多檔案類型的支援，請安裝[LibreOffice](https://www.libreoffice.org/download/download-libreoffice/)，**請安裝於其預設安裝位置**

## 專案架構
- README.md: 主入口說明
- LICENSE: 授權
- requirements.txt: 環境需求
- main.py: 主程式
- src/: 程式碼
- docs/: 文檔