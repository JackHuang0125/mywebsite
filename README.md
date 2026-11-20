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
- `AI_GUIDE.md`：給 AI（Perplexity 等）讀的專案說明，見最後一節

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
- 原本連到 Netlify 的網站已刪除，push 到 GitHub 不會再觸發任何建置。
- 看這次改了什麼：`git diff`；放棄某個檔案還沒 commit 的修改：`git restore 檔名`。

## 用 Perplexity（或其他 AI）修改網站

[AI_GUIDE.md](AI_GUIDE.md) 是寫給 AI 看的專案說明，裡面有架構、規則和回答格式。**每次開新對話，都要先把這份文件貼給它。**

做法是**在對話裡貼程式碼**：AI 不會操作你的電腦，只看得到你貼給它的文字和截圖。流程是：

1. 開新對話，先貼上 AI_GUIDE.md 全文。
2. 說明想改什麼，並貼上相關的程式碼。
3. 它回覆修改內容，你自己貼回檔案。
4. 預覽確認沒問題後 commit。

### 怎麼複製檔案內容

在專案資料夾的 PowerShell 執行下面這行，檔案內容會直接進到剪貼簿，再到 Perplexity 按 `Ctrl+V` 貼上：

```powershell
Get-Content AI_GUIDE.md -Raw -Encoding UTF8 | Set-Clipboard
```

把檔名換掉就能複製其他檔案，例如 `site.toml`、`assets\main.js`、`content\posts\檔名.md`。

`build.py` 很長（約 800 行），通常只需要貼**相關的函式**：

1. 用 VS Code 打開 `build.py`，按 `Ctrl+Shift+O`，輸入函式名稱（例如 `footer`）跳過去。
2. 從 `def` 那一行，選到下一個 `def` 的前一行，複製。

`style.css` 也一樣，用 `Ctrl+F` 搜尋 class 名稱，只貼相關的區塊。要貼哪一段可以先看 AI_GUIDE.md 第 10 節的對照表；不確定的話就直接問它（範本在下面）。

### 一開始的指令（每次開新對話）

```
我有一個自己寫的靜態部落格（Python 產生器，不是 Hugo）。我會把程式碼貼在對話裡請你修改，你不能也不需要操作我的電腦。下面是這個專案的說明文件 AI_GUIDE.md，請完整讀過，之後所有回答都遵守裡面的規則和第 8 節的回答格式。

讀完後，請先用三到五句話說明你理解的專案架構，這一則先不要修改任何東西。

（在這裡貼上 AI_GUIDE.md 全文）
```

確認它的理解沒錯（例如知道版型寫在 `build.py`、沒有用 Hugo、它不能操作電腦），再開始提需求。如果訊息太長被截斷，就把 AI_GUIDE.md 分成兩則貼。

### 之後要修改時

不知道該貼哪段程式碼時，先問：

```
我想要＿＿＿＿＿。請告訴我該貼哪個檔案的哪幾個函式或 CSS 區塊給你，先不要給修改內容。
```

提出修改，照這個格式寫，越具體越好：

````
【想做的事】把首頁大頭貼改成圓角方形
【目前狀況】（可省略；可以附截圖）
【相關程式碼】
build.py 的 home 函式：
```python
（貼上）
```
style.css 的 .profile img 區塊：
```css
（貼上）
```
請依照 AI_GUIDE.md 第 8 節的格式回答，告訴我每段要貼在哪裡，以及怎麼確認改好了。
````

寫新文章：

```
請幫我把下面的筆記整理成一篇文章，照 AI_GUIDE.md 第 7 節的 front matter 格式，數學公式照 7.2 節的規則跳脫好，直接給我完整的 .md 檔內容，並告訴我建議的檔名。
（貼上筆記）
```

改完出錯時：

```
我照你的修改做了，執行 python build.py serve 後出現下面的錯誤（或：畫面變成附圖那樣）。
錯誤訊息（從 Traceback 那行開始，整段貼上）：
（貼上）
我改過之後的程式碼：
（貼上）
```

改動比較大（新增頁面、新增設定欄位、新檔案）之後：

```
這次的修改有影響 AI_GUIDE.md 描述的架構嗎？有的話，請給我 AI_GUIDE.md 要更新的段落（用「找到這段 → 換成這段」的格式）。
```

同一個對話改了很多地方之後，AI 容易搞混新舊版本的程式碼。這時建議開一個新對話，重新貼上最新的 AI_GUIDE.md 再繼續。

### 收到 AI 的回答後

1. 照它說的位置貼上並存檔。它說「整個函式取代」時，先把舊函式從 `def` 那行到下一個 `def` 前面整段選起來，再直接貼上新的。
2. **Python 的縮排（行首的空格）不要改到**：貼上後，`def` 那行開頭的空格要跟上下其他函式對齊。執行時出現 `IndentationError` 就是縮排跑掉了。
3. 確認結果（`python build.py serve` 開著的話，瀏覽器會自動重新整理）：電腦版、手機版（`--lan`）、深淺色都看一下。
4. 有問題就把錯誤訊息貼回去給它；改壞了想放棄，用 `git restore 檔名` 還原到上次 commit 的狀態。
5. 確認沒問題後再 commit：

   ```powershell
   git add -A
   git commit -m "說明這次改了什麼"
   git push
   ```

6. 如果它給了 AI_GUIDE.md 要更新的段落，也一起改進去，下次開新對話貼的就會是最新版。

**小技巧**：一次只請它改一件事；它給的「找到這段」在你的檔案裡用 `Ctrl+F` 找不到時，代表它看的不是最新版本，把最新的程式碼再貼一次給它。
