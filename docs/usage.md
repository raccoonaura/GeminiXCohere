# 使用說明
## 1. 環境設定
1. Clone repo
```bash
git clone https://github.com/raccoonaura/GeminiXCohere
```
2. 設定路徑
```bash
cd GeminiXCohere
```
3. 安裝依賴
```bash
pip install -r requirements.txt
```
4. 運行 CLI
```bash
python main.py
```
## 2. API Key輸入
分別輸入Gemini及Cohere的API Key (不會儲存於伺服器/程式中)
## 3. 問答流程
1. 輸入問題 → 系統同時呼叫Gemini與Cohere
2. 先顯示Gemini的回覆, 再由其做整合兩個模型的回覆並覆蓋
3. 兩個模型以及整合過後的問題及回覆會分別記錄為txt檔, 儲存於main.py所在的資料夾
4. 可以連續對話, 記憶系統會記錄歷史訊息
5. 在問題前面加上"@"可以開啟思考模式 (Reasoning)
6. 將需要被讀取的檔案放置在embeds資料夾
7. 在問題前面加上"$"可以開啟文檔檢索模式 (RAG)
8. 在問題前面加上"$@"可以開啟文檔檢索及思考模式