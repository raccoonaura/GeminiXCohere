# 部署 / Hosting / Domain
## 本地部署
- Python env及pip install
- 啟動本地CLI demo
## 安全提醒
- 不在server儲存使用者 key
- API key建議短期使用
### *以下內容正在計畫 (WIP)*
## Hosting 平台
- Vercel / Netlify / Railway / Cloud Run / etc.
## Web UI 技術選型
- HTML + CSS + JS
- 可選Flask/React
## 網域購買與設定
1. 選擇域名供應商 (Namecheap / Google Domains / GoDaddy / etc.)
2. 購買域名
3. 設定DNS → CNAME指向host
4. 啟用HTTPS / SSL
## 安全設定
- 不在伺服器儲存 key
- 使用者於前端輸入key (session儲存)
- 開啟CORS / rate-limit避免濫用