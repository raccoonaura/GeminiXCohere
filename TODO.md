# 待辦事項 (TODOS)

## 預計實作 (Will Implement)
- **OCR 文件讀取**
    - 使用 Mistral OCR 3 或 OCRmyPDF 等工具來讀取並輸出由圖片（扁平化）組成的 PDF（或可能的其他檔案類型）內容。
- **多模態 RAG (Multimodal RAG)**
    - 鑑於 Gemini Embedding 與 Cohere Embed 皆支援圖片向量化，將使 RAG 系統能夠包含文件中的圖片。
- **聯網搜尋整合 (Web Search Integration)**
    - 增加前綴（如 `#`）來觸發聯網搜尋工具。使用 DuckDuckGo 等 Library 來獲取即時資訊。

## 考慮中的想法 (Considered Ideas)
- **動態模型路由 (Dynamic Model Routing)**
    - 使用輕量化「路由」模型（如 Gemini Flash Lite）來分類使用者提示詞的複雜度。若僅是簡單的問候，則只調用單一模型以節省 API 額度；若問題複雜，則觸發完整的多模型協作。
- **篩選模式 (Refine Mode)**
    - 不僅僅是將三份回答整合為一，而是讓模型相互改進彼此的內容。在呈現「已驗證」的最終答案前，由 Gemini 識別 Mistral 輸出中的幻覺，反之亦然。
- **角色預設 (Persona Presets)**
    - 允許使用者或系統定義角色（例如：「程式碼審查員」、「創意寫作師」），並同時對所有三個模型套用特定的系統指示 (System Instructions)。
- **本地紀錄搜尋 (Local History Search)**
    - 允許使用者使用與 RAG 相同的邏輯來查詢 logs 或 histories 資料夾中的過往對話紀錄，類似於 ChatGPT 和 Gemini 讀取當前對話以外紀錄的功能。
- **上下文視窗管理 (Context Window Management)**
    - 針對極長對話實作「基於摘要的記憶 (Summary-based Memory)」，將對話最舊的部分總結為幾句話而非直接捨棄，幫助模型記住長對話的開端。

### Concept: 動態模型路由與篩選模式
- 由小型模型（可能是 Gemini 3.1 Flash Lite 或 Mistral 4 Small）決定應使用的模型數量、種類以及程式處理模式。例如：
    - **簡單問題**：觸發**迅速模式 (Swift Mode)**，僅提供 Gemini 3.1 Flash Lite 的回答，不進行整合。
    - **一般問題**：觸發**整合模式 (Merge Mode)**，讓 Gemini 整合來自 Gemini 3 Flash、Mistral Small 4 與 Command A 的回答。
    - **複雜問題**：觸發**篩選模式 (Refine Mode)**，由 Gemini 改進 Command 的回答，Mistral 改進 Gemini 的回答，Command 改進 Mistral 的回答，最後由 Gemini 整合並生成最終答案。
    - **程式碼相關問題**：根據問題複雜度觸發整合或篩選模式，並使用如 Codestral (效率回覆) 或 Devstral 2 (複雜問題) 等模型。
- 結構化輸出 (Structured outputs) 非常適合此功能。例如：
    ```json
    // example 1 "What is a monitor?"
    {
        "mode": "swift mode",
        "coding related": false,
        "models": {
            "gemini": "gemini-3-flash-preview",
            "mistral": null,
            "cohere": null,
            "merge": null
        }
    }
    // example 2 "Which one is better for beginners, C++ or Python?"
    {
        "mode": "merge mode",
        "coding related": false,
        "models": {
            "gemini": "gemini-3-flash-preview",
            "mistral": "mistral-small-2603",
            "cohere": "command-a-03-2025",
            "merge": "gemini-3-flash-preview"
        }
    }
    // example 3 "*A really complex coding problem*"
    {
        "mode": "refine mode",
        "coding related": true,
        "models": {
            "gemini": "gemini-3.1-pro-preview",
            "mistral": "devstral-2512",
            "cohere": "command-a-reasoning-08-2025",
            "merge": "gemini-3.1-pro-preview"
        }
    }
    ```