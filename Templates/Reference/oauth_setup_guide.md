# Google OAuth 登入申請指南

本系統的一般使用者只使用 Google 帳號登入；管理員仍可使用本地帳密登入後台。

## 環境變數

在本機 `.env` 或 Render 環境變數中設定：

```ini
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

未設定時，登入頁會顯示 Google 登入尚未啟用，並保留管理員登入表單。

## Google Cloud Console 設定

1. 前往 https://console.cloud.google.com/ 。
2. 建立或選擇專案。
3. 到「API 和服務」設定 OAuth 同意畫面。
4. 建立「OAuth 用戶端 ID」，應用程式類型選「網頁應用程式」。
5. 加入授權重新導向 URI：

```text
http://localhost:5000/oauth/callback/google
https://<Render 網域>/oauth/callback/google
```

6. 複製 Client ID 與 Client Secret 到環境變數。
7. 重新啟動應用程式。

## 驗證

1. 開啟 `/login`。
2. 確認顯示 Google 登入按鈕。
3. 用 Google 登入後，首次使用者應導到 `/oauth/complete-profile`。
4. 補齊姓名、車牌、手機、緊急聯絡人姓名、緊急聯絡人電話後，應可瀏覽活動並報名。

## 常見問題

- `redirect_uri_mismatch`：Google Cloud Console 的 redirect URI 必須與實際網址完全一致。
- 登入頁沒有 Google 按鈕：確認 `GOOGLE_CLIENT_ID` 與 `GOOGLE_CLIENT_SECRET` 都已設定，並重新啟動服務。
