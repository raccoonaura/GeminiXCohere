# 設計理念，技術決策，與系統架構
## 目錄
- 前言
    - [選用模型的原因](#選用模型的原因)
- 基礎架構
    - [API Key 輸入系統](#api-key-輸入系統)
    - [模型呼叫系統](#模型呼叫系統)
    - [所有支援的模型及 Fallback 順序](#所有支援的模型及-fallback-順序)
- 常見功能
    - [錯誤處理系統](#錯誤處理系統)
    - [訊息歷史系統](#訊息歷史系統)
    - [記憶系統](#記憶系統)
    - [快取系統](#快取系統)
- 進階技術
    - [思考系統](#思考系統)
    - [檔案檢索系統](#檔案檢索系統)
    - [圖片讀取系統](#圖片讀取系統)
    - [RAG 系統](#rag-系統)
    - [TAG 系統](#tag-系統)

## 選用模型的原因
- Gemini: 整體聰明，圖片理解強，函式呼叫方便，為整體核心
- Mistral: 成本低，速度快，可作為second opinion來源
- Command: 搭配自家強大的RAG相關模型 以做context讀取
- 模型皆支援文件讀取，圖片輸入，思考模式，系統指示，etc.
- 模型都沒有限制使用次數，僅限制rate-limit
## API Key 輸入系統
- 使用者在本地輸入或放在本地檔案，不會以任何形式儲存在線上
- 使用者自行輸入並管理，避免配額消耗與安全風險
## 模型呼叫系統
1. 使用者輸入prompt
2. 並行呼叫Gemini，Mistral及Cohere API
3. 先以串流方式顯示Gemini的原始回答
4. 將三份回答丟回Gemini並生成整合版
5. 將整合版覆蓋原本的答案，顯示在介面
6. 生成後顯示生成字數，思考/生成時長及使用的模型
## 所有支援的模型及 Fallback 順序
- **Gemini**
    - Gemini 3.1 Pro → Gemini 3 Flash → Gemini 3.1 Flash Lite → Gemini 2.5 Pro → Gemini 2.5 Flash → Gemini 2.5 Flash Lite → Gemini 2.0 Flash → Gemini 2.0 Flash Lite
- **Mistral**
    - ***(Reasoning)*** Mistral Small 4 → Magistral Medium 1.2 → Mistral Large 3 → Mistral Medium 3.1 → Mistral Medium 3 → Magistral Small 1.2
    - ***(No reasoning)*** Mistral Small 4 → Mistral Small 3.2 → Ministral 3 14B → Ministral 3 8B → Mistral Nemo 12B → Ministral 3 3B
- **Command**
    - Command A → Command R+ → Command R → Command R7B
- **Embed**
    - Embed 4 → Gemini Embedding 2 → Gemini Embedding → Embed 3 → Embed Light 3 → Mistral Embed
- **Rerank**
    - Rerank 4 Pro → Rerank 4 Fast → Rerank 3.5 → Rerank 3
## 錯誤處理系統
- 產生一個以當下時間為名txt檔儲存錯誤紀錄
- 每次的錯誤都儲存於檔案中，方便查看問題
- 若為模型生成之錯誤，自動啟用對應之fallback模型
## 訊息歷史系統
- 產生一個以當下時間為名的json檔儲存訊息歷史
- 每次的來回問答都根據模型所需格式儲存於檔案中
- 在程式開始時顯示每個儲存起來的json檔
- 使用者決定要從哪個對話開始，或開啟新的對話
## 記憶系統
- 使用列表儲存過往輪次(user/model 對話)
- 每次發問時將歷史對話一併送出，形成多回合上下文
- 將問答生成為Markdown格式供使用者閱讀
## 快取系統
- 偵測輸入的prompt和之前輸入內容是否有90%以上的相似
- 如果符合，則重新提示原答案，以節省token
- 可以透過輸入提示詞來重新發送
## 思考系統
- 系統會偵測問題前是否有prefix "@"
- 有 → 同時開啟三個模型的思考功能，並以文字提示思考已開啟
- 無 → 不開啟思考功能 生成較快且節省token
- 在思考過程中顯示模型的思考過程 (CoT/Chain-of-Thought)
## 檔案檢索系統
- 系統會偵測問題前是否有prefix "$"
- 有 → 進行檔案選擇 可選擇圖片/文檔/資料
- 無 → 不開啟檔案檢索功能
- 程式本身支援以下檔案
    - 文檔: .**txt**, .**md**/.**markdown**, .**pdf**, .**html**/.**htm**, .**epub**
    - 圖片: .**png**, .**jpg**/.**jpeg**, .**webp**, .**heic**, .**heif**, .**gif**
    - 資料: .**xlsx**, .**xlsm**, .**xltx**, .**xltm**, .**xls**, .**xlsb**, .**odf**, .**ods**, .**odt**, .**csv**, .**tsv**, .**xml**, .**json**, .**yaml**
- 若LibreOffice已安裝 會延伸支援以下檔案:
    - 文檔: .**rtf**, .**odt**, .**ott**, .**fodt**, .**odp**, .**otp**, .**fodp**, .**odm**, .**oth**, .**sxw**, .**stw**, .**sxg**, .**sxi**, .**sti**, .**docx**, .**dotx**, .**docm**, .**dotm**, .**doc**, .**dot**, .**pptx**, .**potx**, .**pptm**, .**potm**, .**ppt**, .**pot**
    - 資料: .**ots**, .**fods**, .**xlt**
## 圖片讀取系統
1. 偵測輸入檔案類型，根據檔案類型，選擇回覆的模型
2. 將圖片暫時上傳至雲端 固定在一個小時內刪除圖片
3. 將雲端的圖片連結插入prompt給予模型以回答問題
## RAG 系統
- **Convert**
    - 偵測輸入檔案類型，根據檔案類型，統一轉換為String (Markdown語法)
- **Chunk**
    - 全文遇到。！？.!?…等標點符號時進行分行
    - 將區塊加入分段後的句子，直到超出字數上限500字，或遇到以#開頭的句子
    - 若超出字數上限，開啟新的區塊，加入上個區塊最後兩行 (overlap)
    - 若區塊最後兩行本身已經超過字數上限，嘗試只加入一行，若依然超過，則不加入
    - 若遇到以#開頭的句子，開啟新的區塊且不加入overlap
- **Embed**
    - 將問題和完成後的區塊給模型產出向量
- **Calculate**
    - 以cosine計算向量相似度，產生十個top-k
- **Rerank**
    - 將這些top-k進行rerank，產生三個新的top-k
- **Prompt**
    - 將新的top-k以系統訊息給予模型以回答問題
## TAG 系統
- 偵測輸入檔案類型，根據檔案類型，統一轉換為DataFrame
- 將DataFrame儲存到暫時的SQL database裡
- 讓Gemini使用函式呼叫來尋找prompt要求的答案