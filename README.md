# PolyGlue

## 專案簡述
- 本專案能同時呼叫 Gemini、Mistral 與 Cohere 旗下模型，並整合回覆
- 支援多回合對話、思考模式、文檔 RAG、圖片讀取

## 功能特色
- 使用者自備 API key
- 同時呼叫多個模型的回覆並整合
- 生成完整回答前先串流匯出即時簡答
- 多回合對話 (記憶系統)
- 快取系統 (Cache system)
- 思考模式 (Thinking / Reasoning)
- 思考內容顯示 (CoT / Chain-of-Thought)
- 圖片理解 (Image Understanding)
- 檢索增強生成 (RAG / Retrieval-Augmented Generation)
- 表格增強生成 (TAG / Table-Augmented Generation)
- RAG / TAG 支援多種檔案類型

## 使用說明
### Requirements
- [Python](https://www.python.org/downloads/) 3.7 或更高
- [Gemini](https://aistudio.google.com/api-keys)、[Mistral](https://console.mistral.ai/home?profile_dialog=api-keys) 及 [Cohere](https://dashboard.cohere.com/api-keys) 的 API Key
- 若使用 RAG / TAG 時需要更多檔案類型的支援，請安裝 [LibreOffice](https://www.libreoffice.org/download/download-libreoffice/)，**請安裝於其預設安裝位置**
### Install
1. Clone repo
```bash
git clone https://github.com/raccoonaura/PolyGlue
```
2. 設定路徑
```bash
cd PolyGlue
```
3. 安裝依賴
```bash
pip install -r requirements.txt
```
4. 運行 CLI / App
```bash
python cli.py
```
```bash
python app.py
```
5. 輸入 API Key
- 開啟程式後分別輸入API Key，或把API key輸入在.env裡 (不會儲存於伺服器/程式中)
### Usage
- 在問題前面加上"@"可以開啟思考模式 (Reasoning)
- 將需要被讀取的檔案放置在embeds資料夾
- 在問題前面加上"$"可以開啟文檔檢索模式 (圖片讀取/RAG/TAG)
- 在問題前面加上"$@"可以開啟文檔檢索及思考模式

## 專案架構
- [README.md](https://github.com/raccoonaura/PolyGlue/blob/main/README.md): 主入口說明
- [DOCS.md](https://github.com/raccoonaura/PolyGlue/tree/main/DOCS.md): 文檔
- [LICENSE](https://github.com/raccoonaura/PolyGlue/blob/main/LICENSE): 授權
- [requirements.txt](https://github.com/raccoonaura/PolyGlue/blob/main/requirements.txt): 環境需求
- [cli.py](https://github.com/raccoonaura/PolyGlue/blob/main/cli.py): CLI入口
- [app.py](https://github.com/raccoonaura/PolyGlue/blob/main/app.py): App入口
- [src/](https://github.com/raccoonaura/PolyGlue/tree/main/src): 程式碼