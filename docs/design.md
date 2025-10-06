# 設計理念與技術決策
## 選用Gemini及Cohere的原因
- Gemini: 整體較聰明, 答案較完整, 為整體核心
- Cohere: 成本低, 速度快, 可作為second opinion來源
- 兩者皆支援文件讀取 (RAG), 圖片輸入, 思考模式, 系統訊息, etc.
## 融合策略
- 串流生成: Gemini相較於Cohere 答案通常較完整 因此讓Gemini先生成簡答
- 自動整合: 由Gemini做回覆的合併，產生最終版本
## API Key 安全策略
- 不保留、不上傳 key
- 使用者自行輸入並管理，避免配額消耗與安全風險
### *以下內容正在計畫 (WIP)*
## 快取策略
- 相同prompt命中快取
- 近似prompt命中提示cached + source