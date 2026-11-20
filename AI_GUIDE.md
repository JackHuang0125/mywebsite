# AI 協作說明：Yang's World 部落格

> 這份文件是寫給協助修改這個網站的 AI（例如 Perplexity）看的。
> **每次對話開始時請先完整讀過，所有修改都要遵守這裡的規則。**
> 修改到架構（新增檔案、函式、設定欄位、網址規則）時，請一併提供這份文件要更新的段落。

---

## 1. 你的角色與合作方式

- 網站主人是資料分析初學者，熟悉 Python 基礎，但不熟網頁前端。請用**繁體中文（台灣用語）**回答，說明要具體、一步一步來。
- **合作方式是「在對話中貼程式碼」**：使用者會把這份文件和相關的程式碼直接貼在對話裡。你**無法**操作電腦、開啟檔案、執行指令或瀏覽使用者的專案，只看得到對話中貼上的文字（和截圖）。
- 使用者會自己把你給的程式碼貼回檔案、自己執行指令，所以你的回答必須能「照著做就完成」（格式見第 8 節）。
- **需要看程式碼時，明確說要貼哪一段**，用函式名稱或 CSS 選擇器指名，例如：「請貼上 `build.py` 裡整個 `def single(self, i: int)` 函式」、「請貼上 `style.css` 裡 `.post-entry` 開頭的那幾個區塊」。`build.py` 約 800 行，通常只需要相關的函式，不用整個檔案。小檔案（`site.toml`、`main.js`、`search.js`）可以請使用者整個貼上。
- **不要憑記憶或猜測**程式碼內容。你要修改的部分，必須是使用者在這次對話中貼給你的版本；如果使用者之後已經照你的建議改過，再改同一段前請先請他貼上最新版本。
- 一次只處理一件事。需求很大時，先拆成幾個步驟，讓使用者每完成一步就預覽確認。

---

## 2. 專案概要

這是一個**自己用 Python 寫的靜態網站產生器**，把 Markdown 文章轉成 HTML，在本機預覽。外觀仿照 Hugo 的 PaperMod 主題。

**不使用**：Hugo、Netlify、Node.js / npm、任何前端框架（React、Vue、Tailwind 等）或打包工具。請不要建議改用這些工具，也不要加入它們的設定檔。

| 項目 | 使用的東西 |
| --- | --- |
| 語言 | Python 3.11 以上（用到內建的 `tomllib`） |
| Markdown 解析 | `markdown-it-py`（CommonMark + 表格、刪除線、自動連結） |
| 程式碼上色 | `Pygments`（monokai 配色） |
| 數學公式 | KaTeX 0.16.21，從 jsdelivr CDN 在瀏覽器端渲染 |
| 前端 | 純 HTML + 一個 CSS 檔 + 兩個原生 JavaScript 檔 |
| 套件清單 | `requirements.txt` |

---

## 3. 目錄結構

```
mywebsite/
├─ build.py            產生器本體（所有 HTML 版型都寫在這裡）
├─ site.toml           網站設定：標題、選單、首頁介紹、社群連結
├─ requirements.txt    Python 套件
├─ assets/
│  ├─ style.css        全站樣式（深淺色、手機版都在這裡）
│  ├─ main.js          深淺色切換、回到頂端、程式碼複製、分享按鈕
│  └─ search.js        搜尋頁的搜尋邏輯
├─ content/posts/*.md  文章（一篇一個檔案）
├─ static/             圖片等檔案，原樣複製到網站根目錄
│  └─ images/          文章內文用的插圖
├─ public/             產出結果（自動產生，不進 git，不要手動改）
├─ README.md           給網站主人看的使用說明
└─ AI_GUIDE.md         本文件
```

---

## 4. 指令

```powershell
pip install -r requirements.txt          # 第一次使用
python build.py                          # 產生網站到 public/
python build.py serve                    # 預覽 http://localhost:1313，改檔自動重建並重新整理瀏覽器
python build.py serve --lan              # 同上，並開放同一個 Wi-Fi 的手機連線
python build.py new "文章標題"            # 建立新文章（draft = true）
python build.py --drafts --future        # 連草稿、未來日期文章一起產生
```

使用者的環境是 **Windows + PowerShell**。給指令時請用 PowerShell 語法（例如不要用 `&&`、`rm -rf`）。

---

## 5. build.py 架構

修改時請用**函式名稱**指出位置（行號會隨修改變動，不可靠）。

### 5.1 常數與工具函式

| 名稱 | 用途 |
| --- | --- |
| `ROOT`, `CONTENT`, `STATIC`, `ASSETS`, `OUT`, `CONFIG` | 各資料夾、檔案路徑 |
| `TZ` | 時區 +08:00（front matter 日期沒寫時區時使用） |
| `esc(s)` | HTML 跳脫。**所有放進 HTML 的文字（標題、標籤、設定值）都必須經過 `esc()`** |
| `urlize(s)` | 檔名、標籤轉網址片段：小寫、空白轉 `-`、去掉多數標點 |
| `heading_id(text)` | 產生標題的錨點 id |
| `strip_tags(s)` | 去掉 HTML 標籤（做摘要、搜尋索引用） |
| `reading_minutes(text, wpm)` | 閱讀時間：中日韓文字每分鐘 500 字，英文單字依 `site.toml` 的 `words_per_minute` |
| `write(path, content)` | 寫檔（自動建立資料夾，UTF-8） |

### 5.2 Markdown

| 名稱 | 用途 |
| --- | --- |
| `make_md()` / `MD` | 建立 markdown-it 解析器。設定 `"html": False`：**文章裡寫的 HTML 會被當純文字顯示** |
| `highlight_code()` | 用 Pygments 為有標語言的程式碼區塊上色（例如 ```` ```python ````）；沒標語言的輸出一般 `<pre><code>` |
| `render_markdown(src)` | 轉成 HTML，同時收集標題清單（`Heading`）並幫標題加上 id 與 `#` 錨點 |
| `toc_html(headings)` | 產生文章頁的「目錄」區塊 |

### 5.3 內容讀取

| 名稱 | 用途 |
| --- | --- |
| `Post`（dataclass） | 一篇文章的所有資料；`post.url` 是 `/posts/<slug>/` |
| `parse_front_matter()` | 讀 `+++` 包住的 TOML front matter（也勉強支援 `---` 的簡單 YAML） |
| `to_datetime()` | 把 front matter 的日期轉成有時區的 datetime |
| `resolve_static(ref)` | 把封面等圖片轉成網址；找不到檔案時改找同檔名不同副檔名並印出警告 |
| `load_posts()` | 讀全部文章：略過草稿與未來日期文章、轉 HTML、算摘要（前 140 字或 `description`）與閱讀時間，依日期新到舊排序 |

### 5.4 版型（`Site` 類別）

所有頁面的 HTML 都由 `Site` 的方法用 f-string 產生，**沒有另外的模板檔**。

| 方法 | 產生什麼 |
| --- | --- |
| `header(current)` | 頁首：網站名稱、深淺色按鈕、選單（`current` 開頭符合選單網址時加 `active`） |
| `footer()` | 頁尾版權文字、回到頂端按鈕 |
| `page(title=, body=, current=, is_list=, description=, math=, extra_head=)` | 整頁外框（`<head>`、頁首、`<main>`、頁尾、JS）。`math=True` 才會載入 KaTeX；`is_list=True` 時 body 加 `list` class（灰底） |
| `meta(p)` | 日期與閱讀時間那一行，例如 `July 29, 2025 · 3 分鐘` |
| `entry(p, show_cover)` | 列表中的一張文章卡片 |
| `paginated(posts, base_url, heading, ...)` | 分頁列表，每頁 `posts_per_page` 篇，第 2 頁起網址為 `<base_url>page/2/` |
| `home()` | 首頁（大頭貼、標題、副標、社群圖示） |
| `single(i)` | 文章頁：麵包屑、標題、meta、封面、目錄、內文、標籤、上一篇/下一篇、分享按鈕 |
| `archives()` | Archive 頁（依年、月分組） |
| `terms(kind, label, groups)` | Tags / Categories 總覽頁 |
| `search()` | 搜尋頁 |
| `not_found()` | 404 頁 |
| `search_index()` | 產生 `/index.json`（搜尋用） |
| `rss()` / `sitemap()` | `/index.xml`、`/sitemap.xml` |

其他：`SVG`（社群與分享圖示的字典，key 是小寫名稱）、`MOON_SUN`（深淺色按鈕圖示）、`KATEX`（KaTeX 載入片段與分隔符號設定）、`LIVE_JS`（預覽時自動重新整理，只在 `serve` 時加入）。

### 5.5 建置與伺服器

| 名稱 | 用途 |
| --- | --- |
| `build()` | 清空 `public/` → 複製 `static/`、`assets/` → 把 Pygments 配色附加到 `style.css` 後面 → 用內部函式 `emit(url, html)` 輸出每一頁 |
| `serve()` | 本機伺服器 + 每秒檢查檔案變更自動重建；找不到的路徑回傳 404.html |
| `snapshot()` | 監看 `content/posts`、`static`、`assets`、`site.toml`、`build.py` 的修改時間 |
| `lan_ip()` | 找出區網 IP（`--lan` 用） |
| `new_post()` | `new` 指令：建立含 front matter 範本的新文章 |
| `main()` | 解析命令列參數 |

**新增一個頁面一定要在 `build()` 裡呼叫 `emit()`**，否則不會被輸出。

---

## 6. 網址規則（不要任意更改）

| 頁面 | 網址 |
| --- | --- |
| 首頁 | `/` |
| 文章列表 | `/posts/`、`/posts/page/2/` … |
| 文章 | `/posts/<slug>/`，slug = front matter 的 `slug`，沒有的話是 `urlize(檔名)` |
| 標籤 | `/tags/`、`/tags/<urlize(標籤)>/` |
| 分類 | `/categories/`、`/categories/<urlize(分類)>/` |
| Archive、搜尋 | `/archives/`、`/search/` |
| 搜尋索引、RSS、Sitemap | `/index.json`、`/index.xml`、`/sitemap.xml` |

文章網址和舊的 Hugo 網站一致，改 `urlize()` 或 `Post.url` 會讓所有舊連結失效，**除非使用者明確要求，否則不要改**。

站內連結一律用 `/` 開頭的根目錄相對路徑（例如 `/tags/`），不要寫死 `http://localhost:1313`。

---

## 7. 資料格式

### 7.1 文章 front matter（TOML，用 `+++` 包住）

```toml
+++
title = "文章標題"
date = 2025-07-29T11:00:00+08:00
draft = false
tags = ["Learning Record", "Bayes"]
categories = ["Learning"]
description = ""          # 選填；有填就當作摘要
slug = ""                 # 選填；固定文章網址

[cover]
    image = "PCA.png"     # static/ 底下的檔名
    alt = "圖片替代文字"
    caption = "圖片說明"
+++

內文（Markdown）
```

- 標籤、分類以 `urlize()` 後的結果合併，所以大小寫不同會被視為同一個。
- 內文插圖：`![說明](/images/xxx.png)`，檔案放 `static/images/`。

### 7.2 數學公式的跳脫規則

Markdown 先處理，KaTeX 才在瀏覽器渲染，所以公式要寫成「經過 Markdown 後仍然正確」的樣子：

- 公式換行 `\\` 要寫成 `\\\\`
- `*` 要寫成 `\*`（同一段有兩個 `*` 會變斜體）
- 底線被吃掉、公式中間變斜體時，把 `_` 寫成 `\_`
- 不要寫 `^'`，撇號直接寫 `'`

幫使用者寫含公式的文章時，**請直接輸出已經跳脫好的版本**。不要為了「修正」這個行為去改 Markdown 解析流程，這會讓所有舊文章的公式壞掉。

### 7.3 site.toml

```toml
title = "Yang's World"
language = "zh-TW"
base_url = ""             # 只影響 RSS / sitemap 的絕對網址
posts_per_page = 10
words_per_minute = 213

[profile]                 # 首頁
title = "Hi There"
subtitle = "..."
image = "ID.jpg"          # static/ 底下的檔名
image_width = 200
image_height = 200

[[menu]]                  # 可重複，依順序顯示；網址含 :// 會開新分頁並加外部連結圖示
name = "Archive"
url = "/archives/"

[[social]]                # 可重複；name 必須對應 build.py 中 SVG 字典的 key
name = "github"
url = "https://github.com/..."
```

目前 `SVG` 字典有：`github`、`linkedin`、`kaggle`、`instagram`、`x`、`facebook`、`link`、`external`。

---

## 8. 回答格式（請務必遵守）

每次給修改方案時：

1. **先用一兩句話說明要怎麼改、會影響哪裡。**
2. **列出要動的檔案。** 每個檔案分開寫。
3. **給出修改內容**。使用者是用複製貼上的方式改檔案，請選最不容易貼錯的方式，優先順序如下：
   1. **整個函式取代**（`build.py` 最推薦）：「把 `build.py` 裡整個 `def footer(self) -> str:` 函式（從 `def` 那行到下一個 `def` 之前）換成以下內容」，然後給出完整的函式。
   2. **整個 CSS 區塊取代或新增**：「把 `style.css` 裡 `.post-entry { ... }` 整個區塊換成以下內容」，或「在 `/* ---------- 頁尾 ---------- */` 這行上面加入以下內容」。
   3. **整個檔案取代**：只用在小檔案（`site.toml`、`main.js`、`search.js`），並註明「整個檔案取代」。
   4. **找到這段 → 換成這段**：只在改動很小時使用。「找到這段」必須從使用者這次貼給你的程式碼**原封不動複製**，並包含足夠上下文讓它在檔案中只出現一次。
   - **新增**的函式、區塊要說清楚放在哪個既有函式／區塊的前面或後面。
   - 不要只給一小段程式碼卻沒說要放在哪裡；不要用 `...` 省略你要使用者貼上的程式碼內容。
   - **Python 縮排要正確**：`Site` 類別裡的方法本身縮排 4 個空格、內容 8 個空格；最外層函式不縮排。給程式碼時保留完整縮排，並在說明中提醒使用者貼上時不要改到縮排。
   - 每段程式碼都放在程式碼區塊（```）裡，並標上語言（`python`、`css`、`javascript`、`toml`）。
4. **新增套件時**：同時更新 `requirements.txt`，並提醒使用者執行 `pip install -r requirements.txt`。盡量避免新增套件。
5. **說明怎麼確認**：要開哪個網址、看哪裡、預期看到什麼。至少包含執行 `python build.py serve` 並檢查相關頁面。
6. 如果改動影響到本文件描述的架構，**最後附上 AI_GUIDE.md 需要更新的段落**。

---

## 9. 修改規則與注意事項

- **深淺色模式**：深色時 `<html>` 元素有 `dark` class（不是 `<body>`）。顏色一律用 `style.css` 開頭的 CSS 變數（`--theme`、`--entry`、`--primary`、`--secondary`、`--tertiary`、`--content`、`--code-bg`、`--code-block-bg`、`--border`），不要寫死顏色；真的需要新顏色時，在 `:root` 和 `:root.dark` 各定義一次。
- **手機版**：斷點是 `max-width: 768px`（另有 900px 給回到頂端按鈕）。新增的版面要在手機寬度（約 375px）下不會出現左右捲動。
- **HTML 安全**：放進 HTML 的動態文字一律用 `esc()`；JavaScript 裡插入文字用 `textContent` 或 `search.js` 中的 `escapeHtml()`。
- **外部資源**：目前只用 jsdelivr 的 KaTeX。新增 CDN 資源要指定確切版本號。
- **介面文字**用繁體中文（現有英文選單名稱 Archive、Tags 等維持原樣）。
- **不要修改 `public/`**：它每次建置都會被整個清空重建。
- **不要動 `content/posts/` 裡的既有文章**，除非使用者要求。改檔名會改變文章網址。
- 草稿（`draft = true`）和日期在未來的文章不會產生，使用者說「文章不見了」時先檢查這兩項。
- 程式碼上色配色在 `build()` 的 `HtmlFormatter(style="monokai")`，不在 `style.css` 裡。
- 檔案編碼一律 UTF-8。

---

## 10. 常見修改範例

| 想做的事 | 改哪裡 |
| --- | --- |
| 新增或刪除選單項目 | `site.toml` 的 `[[menu]]` |
| 改首頁標題、副標、大頭貼 | `site.toml` 的 `[profile]`；圖片放 `static/` |
| 新增社群連結 | `site.toml` 加 `[[social]]`；圖示不在 `SVG` 字典裡時，到 `build.py` 的 `SVG` 加一個小寫 key 的 SVG 字串（`fill`／`stroke` 用 `currentColor`） |
| 每頁文章數 | `site.toml` 的 `posts_per_page` |
| 改顏色、字體、間距 | `assets/style.css`（顏色改 `:root` 與 `:root.dark` 的變數） |
| 改日期顯示格式 | `build.py` 的 `Site.meta()`；Archive 的月份在 `Site.archives()` |
| 改頁尾文字 | `build.py` 的 `Site.footer()` |
| 改文章頁的版面（區塊順序、分享按鈕） | `build.py` 的 `Site.single()`；分享按鈕行為在 `assets/main.js` |
| 改文章卡片 | `build.py` 的 `Site.entry()` |
| 改搜尋邏輯或結果樣式 | `assets/search.js`；索引欄位在 `Site.search_index()`（`title`、`permalink`、`summary`、`content`、`tags`、`date`） |
| 新增 front matter 欄位 | `Post` 加欄位 → `load_posts()` 用 `fm.get()` 讀取 → 在 `single()` 或 `entry()` 使用 → `new_post()` 的範本也加上 |
| 新增獨立頁面（例如 About） | 在 `Site` 加一個方法回傳 `self.page(title=..., body=..., current="/about/")`（內容可用 `parse_front_matter()` + `render_markdown()` 讀 `content/about.md`）→ 在 `build()` 加 `emit("/about/", site.about())` → `site.toml` 加選單 → `sitemap()` 的網址清單加上 → 若讀了新的資料夾，`snapshot()` 也要監看 |
| 允許文章內寫 HTML | `make_md()` 把 `"html": False` 改成 `True`（注意：既有文章中被當成文字的 `<...>` 會開始被當成 HTML） |

---

## 11. 已知狀況

- `20250330_ExtremeGradientBoost.md` 的封面寫 `XGBoost.webp`，實際檔案是 `XGBoost.png`，由 `resolve_static()` 自動改用 png（建置時會印警告）。
- `20250204_PrincipalComponentAnalysis.md` 有兩處 `j^'`，KaTeX 會顯示紅字錯誤，是文章內容的問題。
- 兩篇 Meeting 文章的日期年份寫成 2026（推測原本是 2025）。
