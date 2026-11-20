# Yang's World

自刻的靜態部落格（不再使用 Hugo / Netlify），版型參考原本的 PaperMod。

## 第一次使用

```powershell
pip install -r requirements.txt
```

## 常用指令

| 指令 | 用途 |
| --- | --- |
| `python build.py serve` | 本機預覽 http://localhost:1313 ，存檔後會自動重建並重新整理瀏覽器 |
| `python build.py serve --lan` | 同上，並讓同一個 Wi-Fi 的手機也能連進來預覽 |
| `python build.py` | 只產生網站到 `public/` |
| `python build.py new "標題"` | 在 `content/posts/` 建立新文章（預設是草稿） |
| `--drafts` / `--future` | 連草稿、未來日期的文章一起產生 |

## 檔案結構

- `content/posts/*.md`：文章（TOML front matter：title、date、draft、tags、categories、cover）
- `static/`：圖片等靜態檔，原樣複製到網站根目錄
- `assets/`：版型的 CSS 與 JS
- `site.toml`：網站標題、選單、首頁介紹、社群連結
- `build.py`：產生器本體
- `public/`：產出結果（不進 git）

數學公式用 `$...$`、`$$...$$`，由 KaTeX 在瀏覽器端渲染。

## 注意事項

### 環境與預覽

- 需要 Python 3.11 以上（用到內建的 `tomllib`），第一次要先 `pip install -r requirements.txt`。
- `serve` 只是本機預覽用的伺服器，不要拿來對外公開網站。
- 預設只有這台電腦連得到；加 `--lan` 才會開放給同一個 Wi-Fi 的裝置。第一次用 `--lan` 時，Windows 防火牆若跳出詢問，選「允許私人網路」即可，不要勾公用網路。
- 改了 `build.py` 裡的伺服器相關程式（例如 `serve` 的參數），要按 Ctrl+C 停掉再重開才會生效；改文章、圖片、CSS、`site.toml` 則會自動重建。
- 數學公式的 KaTeX 是從 CDN（jsdelivr）載入，離線時公式會顯示成原始的 `$...$` 文字。

### 寫文章

- 文章的網址由**檔名**決定：轉小寫、空白換成 `-`。例如 `20250318_Monte Carlo Integration.md` → `/posts/20250318_monte-carlo-integration/`。**已經公開的文章不要改檔名**，不然舊網址會失效；真的要改，可以在 front matter 加 `slug = "原本的網址片段"` 固定網址。
- `draft = true` 的文章不會產生；`date` 在未來的文章也不會產生（建置時會印出「略過未來日期文章」）。日期記得寫成 `2025-07-10T16:00:00+08:00` 這種格式，年份別打錯。
- 封面圖 `cover.image` 寫 `static/` 底下的檔名即可（例如 `"PCA.png"`）。副檔名寫錯時產生器會自動找同名的其他格式並印出警告，看到 `! 找不到` 就去修正。
- 內文插圖用 `![說明](/images/xxx.png)`，圖片放在 `static/images/`。檔名盡量不要有空白或特殊符號。
- 標籤、分類不分大小寫，`Learning` 和 `learning` 會被合併成同一個；拼錯字（例如 `Learninig Record`）則會變成另一個標籤。
- 內文不支援直接寫 HTML，會被當成純文字顯示。

### 數學公式

Markdown 會先處理一次文字，KaTeX 才接手，所以公式裡有些符號要多加反斜線：

| 情況 | 寫法 | 原因 |
| --- | --- | --- |
| 公式換行 `\\`（矩陣、多行式） | 寫成 `\\\\` | Markdown 會把 `\\` 變成 `\` |
| 星號，例如 `y^*` | 寫成 `y^\*` | 同一段有兩個 `*` 會被當成斜體 |
| 底線 `_` 不見、公式中間變斜體 | 把那段的 `_` 寫成 `\_`（例如 `\hat{I}\_M`） | `_..._` 被當成斜體 |
| 撇號，例如 j 撇 | 寫 `j'` | 不要寫 `j^'`，KaTeX 不接受 |

公式顯示成紅字代表 KaTeX 解析失敗，打開瀏覽器看那段原始碼通常就知道哪裡要跳脫。

### Git

- `public/` 是產出結果，已列在 `.gitignore`，不要 commit；隨時用 `python build.py` 重新產生。
- 原本連到 Netlify 的網站要到 Netlify 後台刪除（Site configuration → Delete site）。**在刪除之前不要 push**，不然 Netlify 會拿新程式碼去跑 Hugo 建置而失敗。
