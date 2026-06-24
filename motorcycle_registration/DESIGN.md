# DESIGN.md — 重機車隊報名系統 設計系統

> 本文件定義所有視覺 token，任何 CSS/模板變更必須 trace back 至此文件。
> 主題：Charcoal（木炭灰沈穩色系）

---

## 1. 色彩 (Colors)

### Primary（Charcoal 主調色）

| Token | Hex | 用途 |
|---|---|---|
| --color-primary | #2C2C2C | 導覽列、表頭 header、主要按鈕 |
| --color-primary-hover | #1F1F1F | 按鈕 hover、連結 hover |
| --color-primary-active | #121212 | 按鈕按下、active 狀態 |
| --color-primary-disabled | #8A8A8A | 按鈕 disabled、文字 disabled |
| --color-primary-surface | #383838 | 卡片 header（較淺灰色） |

### Surface（表面 / 背景）

| Token | Hex | 用途 |
|---|---|---|
| --color-surface | #ffffff | 卡片背景、內容區域背景 |
| --color-surface-secondary | #f5f5f5 | 頁面次要背景 |

### Text（文字）

| Token | Hex | 用途 |
|---|---|---|
| --color-text | #222222 | 主要文字 |
| --color-text-muted | #666666 | 次要文字、時間戳、輔助說明 |
| --color-text-on-primary | #ffffff | 在深色底上顯示白色字 |

### Border

| Token | Hex | 用途 |
|---|---|---|
| --color-border | #D4D4D4 | 卡片邊框、分隔線 |
| --color-accent | #8A8A8A | 導覽/頁腳邊框、次要點綴線 |

### Role Colors（角色色）

| Token | Hex | 用途 |
|---|---|---|
| --color-primary-action | #4A4A4A | 主要動作色 |
| --color-primary-action-hover | #3A3A3A | 主要動作 hover |
| --color-primary-action-active | #2A2A2A | 主要動作 active |
| --color-secondary-action | #6B7280 | 次要動作色 |
| --color-secondary-action-hover | #5A5F6B | 次要動作 hover |
| --color-selection | rgba(74,74,74,0.10) | 選取/高亮背景 |
| --color-nav-surface | #2C2C2C | 導覽列底色 |
| --color-nav-border | #4A4A4A | 導覽列邊框 |

### Accent（暖琥珀強調色 / Warm Amber）

> 單一品牌強調色，僅用於「互動 / 重點」，與炭灰底盤形成冷暖平衡；不入侵 nav / footer 等結構底色。

| Token | Hex | 用途 | 對比 |
|---|---|---|---|
| --color-accent | #E07A3F | 非文字填色：圖示、日曆今日標記、圖表 bar、focus ring | 僅作填色 |
| --color-accent-emphasis | #A8521C | 連結 / 強調文字、主要 CTA 填色 | 白底 / 白字 5.4:1（AA） |
| --color-accent-hover | #8F4615 | 連結 / CTA hover | 白字 6.9:1 |
| --color-accent-active | #76380F | 連結 / CTA active | 白字 9.0:1 |
| --color-accent-subtle | rgba(224,122,63,0.12) | active tab / 選取 / hover 淡底 | — |

### Semantic（語意色 — 沿用 Bootstrap 相容）

| Token | Hex | 用途 |
|---|---|---|
| --color-success | #198754 | 成功操作 |
| --color-danger | #dc3545 | 刪除 / 錯誤 / 危險操作 |
| --color-warning | #ffc107 | 警告訊息 |
| --color-info | #0dcaf0 | 資訊提示 |

---

## 2. 字體 (Typography)

### Font Family

```css
font-family: -apple-system, "Microsoft JhengHei", "Noto Sans TC", sans-serif;
```

### Scale

| Token | 用途 | 大小 | 字重 | 行高 |
|---|---|---|---|---|
| --font-size-2xl | 頁面主要標題 | 1.75rem | 700 | 1.2 |
| --font-size-xl | 卡片標題、區塊標題 | 1.5rem | 700 | 1.3 |
| --font-size-lg | 次標題、瀏覽連結 | 1.25rem | 600 | 1.4 |
| --font-size-md | 內文 | 1rem | 400 | 1.6 |
| --font-size-sm | 小字、timestamp | 0.875rem | 400 | 1.5 |

---

## 3. 間距 (Spacing)

4px base scale，與 Bootstrap 5 的 $spacer 對齊使用。

| Token | 值 | Bootstrap 對應 |
|---|---|---|
| --space-xs | 4px | 1 |
| --space-sm | 8px | 2 |
| --space-md | 16px | 4 |
| --space-lg | 24px | 6 |
| --space-xl | 32px | 8 |
| --space-2xl | 48px | 12 |

---

## 4. 陰影 (Shadows)

3 層 elevation，從微陰影到最突出。

| Token | 值 | 對應 CSS class | 用途 |
|---|---|---|---|
| --shadow-sm | 0 1px 3px rgba(0,0,0,0.10) | .card.raised | 一般內容卡（登入、活動資訊） |
| --shadow-md | 0 4px 6px rgba(0,0,0,0.10) | .card.shadow (Bootstrap) | 主要內容卡片 |
| --shadow-lg | 0 10px 15px rgba(0,0,0,0.12) | .card.prominent | 最突出卡片（儀表板統計） |

.card 預設無陰影（flat）。
---

## 5. 圓角 (Border Radius)

| Token | 值 | 適用元件 |
|---|---|---|
| --radius-button | 6px | .btn |
| --radius-card | 8px | .card |
| --radius-input | 4px | input, textarea, select |
| --radius-badge | 12px | .badge |

---

## 6. 轉場 (Transitions)

| Token | 值 | 適用 |
|---|---|---|
| --transition-fast | 0.15s ease | hover 效果、按鈕 |
| --transition-normal | 0.3s ease | 卡片浮起、Toast 滑入 |

---

## 7. 自然系色彩與裝飾 (Nature Colors & Decorations)

> 以下為自然風 UI 注入專用 token，多數色票延伸自主色 #2C2C2C 色系。

### 自然色調 (Nature Palette)

| Token | Hex | 色系 |
|---|---|---|
| --color-nature-forest | #2d5a3d | 森林綠 — 活動 card hover |
| --color-nature-mountain | #4A5568 | 山岩灰 — 按鈕 hover |
| --color-nature-maple | #b85c3a | 楓紅 — 系統 card hover |
| --color-nature-plant | #4a7c59 | 植物綠 — 管理 card hover |
| --color-nature-petal | #d4a5b8 | 花瓣粉 — 用戶 card hover |
| --color-nature-waterfall | #4a90d9 | 瀑布藍 — 表單 card hover |

### 漸層 (Gradients)

| Token | 角度／色票 |
|---|---|
| --gradient-forest | linear-gradient(135deg, #2d5a3d, #4a7c59) |
| --gradient-mountain | linear-gradient(135deg, #4A5568, #4a90d9) |
| --gradient-maple | linear-gradient(135deg, #b85c3a, #d4a5b8) |
| --gradient-waterfall | linear-gradient(135deg, #4a90d9, #c8e6f5) |

### SVG Pattern（data URI 嵌入）

| Token | 簡短說明 |
|---|---|
| --pattern-mist | 淡霧網格 background pattern，SVG stroke opacity 0.05~0.06（body 水印，維持極淡不搶內容） |
| --pattern-leaves | 落葉輪廓 lineart pattern，底層 opacity 0.02（footer ::after） |
| --pattern-ripples | 漣漪水波紋 pattern，stroke opacity ~0.03（目前未啟用） |

> 注意：所有 pattern 的「實際視覺強度」由 SVG 內 `opacity` 控制，非外層 CSS opacity。
> body 水印的 SVG stroke opacity 限制（無外層 opacity）值直接壓在 0.05~0.06。
> 任何調整後須在淺底與深底（404 設定頁）實際檢查，確認達到「可感知但不搶內容」的水印效果。

### 動畫 (Animations)

| Token | 動畫邏輯 |
|---|---|
| --anim-fall | 自然飄落：translateY 垂直移動 + 微旋轉 |
| --anim-ripple | 漣漪擴散：scale 放大 + opacity 漸淡 |

---

## 變更記錄 (Changelog)

| 日期 | 版本 | 變更 |
|---|---|---|
| 2026-06-22 | v1.0 | 初始設計系統建立 |
| 2026-06-23 | v1.1 | 新增第 7 章自然系色彩與裝飾 token |
| 2026-06-23 | v1.2 | UI/UX 稽核修正 |
| 2026-06-24 | v2.0 | 主題改版：從海軍藍 (#1a1a2e) 更改為 Charcoal (#2C2C2C) 灰色系 |
| 2026-06-24 | v2.1 | 導入暖琥珀強調色（連結 / CTA / active / focus / 圖表 / 日曆今日標記）；連結改用強調色提升可辨識度；統計卡圖示統一並上色；移除詳情頁重複統計卡 |
