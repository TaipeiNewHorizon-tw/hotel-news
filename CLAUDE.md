# 飯店新聞追蹤（hotel-news）

來源 repo：`TaipeiNewHorizon-tw/hotel-news`（公開）。本資料夾是 commit `df89f9c`（2026-11-25，機器人自動更新）的完整內容。`_prototype-artifact/` 是舊的 Apps Script 介面原型，已不使用，可刪。

## 這是什麼
追蹤台北世聯商旅、梅樓驛站、府中棧精品商旅的新聞，給同事共用。

## 架構
- `scripts/fetch_news.py`：只用 Python 內建套件，抓 Google 新聞 RSS（zh-TW），每個關鍵字取最新 20 則，累積寫入 `docs/news.json`（欄位 `updated`、`news`）。
- 關鍵字在檔案最上方 `KEYWORDS`：台北世聯商旅、世聯商旅、台北梅樓驛站、府中棧精品商旅、府中棧商旅。
- `docs/index.html`：讀 `news.json` 顯示，有搜尋、媒體與日期篩選、排序。
- GitHub Pages 以 `docs/` 為來源。
- `.github/workflows/update-news.yml`：cron `0 0 * * *`（UTC 00:00，也就是台北 08:00）加手動觸發；跑腳本後若 `news.json` 有變就由 `news-bot` 提交並 push。需要 `contents: write` 權限。

## 啟動
本機測試：`python scripts/fetch_news.py`，再 `python -m http.server -d docs` 開 `http://localhost:8000/`。
立即更新：GitHub → Actions → update-news → Run workflow。

## 環境變數／密鑰
無（只用公開 RSS 與 GitHub 內建 `GITHUB_TOKEN`）。

## 注意
- GitHub 對長時間沒有活動的 repo 會自動停用排程 workflow；這個 repo 因為機器人每天提交，正常情況不會觸發，但若連續多日都沒有新新聞（沒有提交），要留意。
- Google 新聞 RSS 沒有正式 SLA，格式改變時腳本會壞。

## 待辦清單
1. ~~失敗通知~~（2026-11-25 完成，**尚未推到 GitHub，也尚未在 Actions 上實際跑過**）。
   - 原本的問題：`fetch_news.py` 會吞掉每個關鍵字的錯誤、永遠以 0 結束、還照常更新 `updated`，所以即使 Google 改版或全部抓取失敗，Actions 仍是綠燈，GitHub 內建的失敗信也不會發。
   - 現在：5 個關鍵字全部失敗，或抓取成功但解析不到任何新聞（RSS 格式可能改了）→ 腳本以 1 結束、不寫入 `news.json`（保留舊的「更新時間」，讓問題看得出來）。只有部分關鍵字失敗仍算成功，但會輸出 `::warning::`（Actions 頁會有黃色註記）。
   - workflow 加了 `issues: write`，任一步失敗時（含 `git push`）自動開一個「飯店新聞自動更新失敗」Issue；已有同名未關閉 Issue 就只留言，不會每天重複開。**排查完要手動關閉 Issue**，否則之後的失敗只會留言（仍會通知）。
   - 通知對象：訂閱此 repo（Watch）的人，以及 GitHub 內建對「最後修改排程的人」寄的 Actions 失敗信。要讓同事收到，請他們 Watch 這個 repo。
   - 本機測試過：全部失敗、空 RSS、部分失敗三種情境的結束碼與檔案是否被改動。Issue 建立那一步無法在本機測，**推上去後請到 Actions 手動 Run workflow 一次確認成功路徑，並可臨時把關鍵字抓取弄壞驗證 Issue 是否會開**。
   - 仍待你決定：長期沒有新新聞（不是失敗）不會通知。
2. 關鍵字是否涵蓋別稱與錯字，由使用者決定。
3. 長期使用時考慮移到公司組織帳號。
