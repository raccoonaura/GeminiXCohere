# GeminiXCohere
Gemini + Cohere 多模型聊天整合器  

Period: 10/01/25 ~ 01/31/26  
Minimum Viable Products: CLI demo, GitHub repo, Demo的展示影片  
Commit標題形式: 月 + 日 + 年 + 當天第幾個版本  

已知問題:  
輸入API時不輸入任何東西就按enter會產生錯誤  
Gemini的串流回覆太長時 整合過後的回答無法覆蓋全部  
Gemini整合時有時依然會解釋問題/說明自己要做什麼  

**新增模型步驟**:  

輸入自備API Keys  
定義詢問模型的功能 並產出text回覆  
把回覆寫入主程式  
新增記憶功能 能自動寫入每次的問題和回覆  