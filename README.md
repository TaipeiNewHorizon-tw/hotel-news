# 飯店新聞追蹤

GitHub Actions 每天早上 8 點（台北時間）抓 Google 新聞 RSS → 更新 `docs/news.json` → GitHub Pages 顯示 `docs/index.html`。

- 改關鍵字：編輯 `scripts/fetch_news.py` 最上面的 `KEYWORDS`
- 立即更新：GitHub 的 Actions 頁籤 → update-news → Run workflow
