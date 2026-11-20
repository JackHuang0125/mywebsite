// 站內搜尋：讀取 /index.json，在標題、標籤、內文中找關鍵字（空白分隔的每個詞都要符合）
(function () {
  var input = document.getElementById('searchInput');
  var list = document.getElementById('searchResults');
  if (!input || !list) return;

  var docs = null;
  var current = -1;

  fetch('/index.json')
    .then(function (r) { return r.json(); })
    .then(function (data) {
      docs = data.map(function (d) {
        d._title = d.title.toLowerCase();
        d._tags = (d.tags || []).join(' ').toLowerCase();
        d._content = d.content.toLowerCase();
        return d;
      });
      var q = new URLSearchParams(location.search).get('q');
      if (q) { input.value = q; run(); }
    });

  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function highlight(text, terms) {
    var out = escapeHtml(text);
    terms.forEach(function (t) {
      var re = new RegExp('(' + escapeHtml(t).replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi');
      out = out.replace(re, '<mark>$1</mark>');
    });
    return out;
  }

  function snippet(doc, term) {
    var i = doc._content.indexOf(term);
    if (i < 0) return doc.summary;
    var start = Math.max(0, i - 40);
    return (start > 0 ? '…' : '') + doc.content.slice(start, i + 80) + '…';
  }

  function run() {
    current = -1;
    var q = input.value.trim().toLowerCase();
    if (!q || !docs) { list.innerHTML = ''; return; }
    var terms = q.split(/\s+/);
    var results = [];
    docs.forEach(function (d) {
      var score = 0;
      for (var k = 0; k < terms.length; k++) {
        var t = terms[k], s = 0;
        if (d._title.indexOf(t) >= 0) s += 10;
        if (d._tags.indexOf(t) >= 0) s += 5;
        if (d._content.indexOf(t) >= 0) s += 1;
        if (!s) return;  // 每個詞都要出現
        score += s;
      }
      results.push({ doc: d, score: score });
    });
    results.sort(function (a, b) { return b.score - a.score || (a.doc.date < b.doc.date ? 1 : -1); });

    if (!results.length) {
      list.innerHTML = '<li class="empty">找不到符合「' + escapeHtml(input.value.trim()) + '」的文章</li>';
      return;
    }
    list.innerHTML = results.map(function (r) {
      var d = r.doc;
      return '<li class="post-entry">' + highlight(d.title, terms) + '&nbsp;»' +
        '<span class="search-snippet">' + highlight(snippet(d, terms[0]), terms) + '</span>' +
        '<a href="' + d.permalink + '" aria-label="' + escapeHtml(d.title) + '"></a></li>';
    }).join('');
  }

  input.addEventListener('input', run);

  // 方向鍵選擇結果、Enter 開啟、Esc 清除
  document.addEventListener('keydown', function (e) {
    var items = list.querySelectorAll('li:not(.empty)');
    if (e.key === 'Escape') { input.value = ''; run(); input.focus(); return; }
    if (!items.length) return;
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      if (current >= 0) items[current].classList.remove('focus');
      current = e.key === 'ArrowDown' ? Math.min(current + 1, items.length - 1) : current - 1;
      if (current < 0) { input.focus(); return; }
      items[current].classList.add('focus');
      items[current].querySelector('a').focus();
    }
  });
})();
