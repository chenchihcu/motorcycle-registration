# OAuth 第三方登入申請指南

本文件說明如何申請 Google 與 Line 的 OAuth 憑證，以啟用本系統的第三方快速登入功能。

---

## 環境變數設定

在專案根目錄的 .env 檔案中設定以下變數：

`ini
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Line OAuth
LINE_CHANNEL_ID=your_line_channel_id
LINE_CHANNEL_SECRET=your_line_channel_secret
`

> 設定完成後重新啟動應用程式，系統會自動偵測並啟用對應的登入按鈕。
> 若未設定憑證，該 provider 的登入按鈕將自動隱藏。

---

## Google 登入申請步驟

### 1. 前往 Google Cloud Console
- 開啟 https://console.cloud.google.com/
- 使用您的 Google 帳號登入

### 2. 建立或選擇專案
- 點擊頂端專案下拉選單 → 「新增專案」
- 輸入專案名稱（如「重機車隊報名系統」）
- 點擊「建立」

### 3. 啟用 OAuth 同意畫面
- 左側導覽：API 和服務 → OAuth 同意畫面
- User Type 選擇「外部」
- 填寫必要資訊：
  - 應用程式名稱
  - 使用者支援電子郵件
  - 開發者聯絡資訊
- 範圍（Scopes）：加入 .../auth/userinfo.email 和 .../auth/userinfo.profile
- 測試使用者：若為外部發布，需加入測試用的 Google 帳號

### 4. 建立憑證
- 左側導覽：API 和服務 → 憑證
- 點擊「建立憑證」→ 「OAuth 用戶端 ID」
- 應用程式類型：選擇「網頁應用程式」
- 名稱：輸入識別名稱
- 授權的重新導向 URI：加入
  `
  http://localhost:5000/oauth/callback/google
  `
- 點擊「建立」

### 5. 取得憑證
- 複製顯示的「用戶端 ID」和「用戶端密碼」
- 填入 .env 檔案的 GOOGLE_CLIENT_ID 與 GOOGLE_CLIENT_SECRET

---

## Line 登入申請步驟

### 1. 前往 Line Developers Console
- 開啟 https://developers.line.biz/console/
- 使用您的 Line 帳號登入

### 2. 建立 Provider
- 點擊「Create new provider」
- 輸入 Provider 名稱（如「重機車隊」）
- 點擊「Create」

### 3. 建立 Channel（LINE Login）
- 在 Provider 頁面點擊「Create a LINE Login channel」
- 填寫必要資訊：
  - Channel 名稱
  - Channel 描述
  - 應用程式類型：選擇「Web app」
  - Email 信箱（必填）
- 同意條款後點擊「Create」

### 4. 設定 Callback URL
- 在 Channel 設定頁面找到「LINE Login」→「Callback URL」
- 點擊「Edit」
- 加入：
  `
  http://localhost:5000/oauth/callback/line
  `
- 點擊「Save」

### 5. 取得憑證
- 在 Channel 設定頁面 →「Basic settings」
- 找到 Channel ID 和 Channel Secret
- 填入 .env 檔案的 LINE_CHANNEL_ID 與 LINE_CHANNEL_SECRET

---

## 驗證設定

1. 將 .env 檔案填寫完整
2. 重新啟動應用程式
3. 開啟登入頁面，確認 Google 與 Line 按鈕已顯示
4. 點擊各按鈕測試登入流程

---

## 常見問題

### Q: 登入後顯示「缺少憑證」錯誤
A: 請檢查 .env 檔案的變數名稱是否正確，重新啟動應用程式。

### Q: Callback 後顯示「redirect_uri_mismatch」
A: 請確認 Google Cloud Console / Line Developers 中設定的回調 URI 與應用程式實際網址完全一致（包含 http:// 與埠號）。

### Q: 如何新增其他 OAuth provider？
A: 本系統目前僅支援 Google 與 Line。新增 provider 需修改 outes/oauth.py，於 _PROVIDER_CONFIGS 中加入對應設定。

### Q: 正式上線時需要修改什麼？
A: 將回調 URI 中的 localhost:5000 改為正式的網域名稱，並在 Google / Line 後台更新對應的 URI 設定。
