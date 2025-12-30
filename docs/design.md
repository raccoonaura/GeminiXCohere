# 設計理念與技術決策
## 選用Gemini及Cohere的原因
- Gemini: 整體較聰明，答案較完整，為整體核心
- Command: 成本低，速度快，可作為second opinion來源
- 兩者皆支援文件讀取，圖片輸入，思考模式，系統指示，etc.
- 兩者都沒有限制使用次數，僅限制rate-limit
## 融合策略
- 串流生成: Gemini相較於Command，答案通常較完整，因此讓Gemini先生成簡答
- 自動整合: 由Gemini做回覆的合併，產生最終版本
## API Key 安全策略
- 不保留、不上傳 key
- 使用者自行輸入並管理，避免配額消耗與安全風險
## 快取策略
- 近似 (90%+) / 相同prompt命中提示cached
## 文檔 RAG 策略
- 偵測embeds檔案類型
- 根據檔案類型，統一轉換為String (Markdown語法)
- 在embeds裡搜尋與輸入相似的檔案
- 全文遇到。！？.!?…等標點符號時進行分行
- 將區塊加入分段後的句子，直到超出字數上限500字，或遇到以#開頭的句子
- 若超出字數上限，開啟新的區塊，加入上個區塊最後兩行 (overlap)
- 若區塊最後兩行本身已經超過字數上限，嘗試只加入一行，若依然超過，則不加入
- 若遇到以#開頭的句子，開啟新的區塊且不加入overlap
- 將問題和完成後的區塊給模型產出向量
- 以cosine計算向量相似度，產生十個top-k
- 將這些top-k進行rerank，產生三個新的top-k
- 將新的top-k以系統訊息給予模型以回答問題
## Text-to-SQL RAG 流程
- 偵測embeds檔案類型
- 根據檔案類型，統一轉換為DataFrame
- 將DataFrame儲存到暫時的database裡
- 讓Gemini使用函式呼叫來尋找prompt要求的答案