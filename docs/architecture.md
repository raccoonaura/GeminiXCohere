# 系統架構
## 模型呼叫流程
1. 使用者輸入prompt
2. 並行呼叫Gemini及Cohere API
3. 先顯示Gemini的原始回答(parallel display)
4. 將兩份回答丟回Gemini → 生成整合版
5. 將整合版覆蓋原本的答案, 顯示在介面
## 記憶系統
- 使用列表儲存過往輪次(user / model 對話)
- 每次發問時將歷史對話一併送出, 形成多回合上下文
## Reasoning / Thinking
- 系統會偵測問題前是否有prefix "@"
- 有 → 同時開啟兩個模型的思考功能 並以文字提示思考已開啟
- 無 → 不開啟思考功能 生成較快且節省token
## Key 輸入機制
- 使用者在本地輸入, 不會以任何形式儲存
### *以下內容正在計畫 (WIP)*
## RAG 流程
1. 檔案讀取
2. Embedding生成 (?)
3. Top-k檢索 (?)
4. 將檢索結果插入prompt
## 並行呼叫
- loading, fallback