# Gemini X Cohere

## 專案簡述
- 本專案能同時呼叫 Gemini 與 Cohere 旗下模型，並整合回覆
- 支援多回合對話、思考模式、文檔 RAG、圖片讀取

## 功能特色
- 使用者自備 API key
- 同時呼叫 Gemini 及 Command 的回覆並整合
- 生成完整回答前先串流匯出即時簡答
- 多回合對話 (記憶系統)
- 快取系統 (Cache system)
- 思考模式 (Thinking / Reasoning)
- 思考內容顯示 (CoT / Chain-of-Thought)
- 圖片理解 (Image Understanding)
- 檢索增強生成 (RAG / Retrieval-Augmented Generation)
- 表格增強生成 (TAG / Table-Augmented Generation)
- RAG / TAG 支援多種檔案類型

## 環境需求
- [Python](https://www.python.org/downloads/) 3.13.x
- 必要套件請參考 [`requirements.txt`](https://github.com/raccoonaura/GeminiXCohere/blob/main/requirements.txt)
- [Gemini](https://aistudio.google.com/api-keys) 及 [Cohere](https://dashboard.cohere.com/api-keys) 的 API Key
- 若使用 RAG / TAG 時需要更多檔案類型的支援，請安裝 [LibreOffice](https://www.libreoffice.org/download/download-libreoffice/)，**請安裝於其預設安裝位置**

## 專案架構
- [README.md](https://github.com/raccoonaura/GeminiXCohere/blob/main/README.md): 主入口說明
- [LICENSE](https://github.com/raccoonaura/GeminiXCohere/blob/main/LICENSE): 授權
- [requirements.txt](https://github.com/raccoonaura/GeminiXCohere/blob/main/requirements.txt): 環境需求
- [main.py](https://github.com/raccoonaura/GeminiXCohere/blob/main/main.py): 主程式
- [src/](https://github.com/raccoonaura/GeminiXCohere/tree/main/src): 程式碼
- [docs/](https://github.com/raccoonaura/GeminiXCohere/tree/main/docs): 文檔