// 深淺色切換、回到頂端、程式碼複製、分享按鈕
(function () {
  var root = document.documentElement;

  // 深淺色切換
  var toggle = document.getElementById('theme-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var dark = root.classList.toggle('dark');
      try { localStorage.setItem('pref-theme', dark ? 'dark' : 'light'); } catch (e) {}
    });
  }

  // 選單捲動位置記憶（手機上選單可橫向捲動）
  var menu = document.getElementById('menu');
  if (menu) {
    try { menu.scrollLeft = +localStorage.getItem('menu-scroll-position') || 0; } catch (e) {}
    menu.addEventListener('scroll', function () {
      try { localStorage.setItem('menu-scroll-position', menu.scrollLeft); } catch (e) {}
    });
  }

  // 頁內錨點平滑捲動
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    var id = decodeURIComponent(a.getAttribute('href').slice(1));
    if (!id) return;
    a.addEventListener('click', function (e) {
      var el = document.getElementById(id);
      if (!el) return;
      e.preventDefault();
      el.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' });
      if (id === 'top') history.replaceState(null, '', ' ');
      else history.pushState(null, '', '#' + id);
    });
  });

  // 回到頂端按鈕
  var top = document.getElementById('top-link');
  if (top) {
    var onScroll = function () {
      top.classList.toggle('show', (document.documentElement.scrollTop || document.body.scrollTop) > 800);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // 程式碼區塊複製按鈕
  document.querySelectorAll('.post-content pre > code').forEach(function (code) {
    var btn = document.createElement('button');
    btn.className = 'copy-code';
    btn.textContent = '複製';
    btn.addEventListener('click', function () {
      var done = function () {
        btn.textContent = '已複製！';
        setTimeout(function () { btn.textContent = '複製'; }, 2000);
      };
      if (navigator.clipboard) {
        navigator.clipboard.writeText(code.textContent).then(done);
      } else {
        var range = document.createRange();
        range.selectNodeContents(code);
        var sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
        try { document.execCommand('copy'); done(); } catch (e) {}
        sel.removeAllRanges();
      }
    });
    code.parentNode.appendChild(btn);
  });

  // 分享按鈕（用目前網址，所以本機或任何網域都能用）
  var share = document.querySelector('.share-buttons');
  if (share) {
    var title = share.getAttribute('data-title') || document.title;
    share.addEventListener('click', function (e) {
      var a = e.target.closest('a[data-share]');
      if (!a) return;
      e.preventDefault();
      var url = location.href.split('#')[0];
      var u = encodeURIComponent(url), t = encodeURIComponent(title);
      var target = {
        x: 'https://x.com/intent/tweet/?text=' + t + '&url=' + u,
        linkedin: 'https://www.linkedin.com/shareArticle?mini=true&url=' + u + '&title=' + t,
        facebook: 'https://facebook.com/sharer/sharer.php?u=' + u
      }[a.getAttribute('data-share')];
      if (target) {
        window.open(target, '_blank', 'noopener,noreferrer');
      } else if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(function () {
          a.classList.add('copied');
          setTimeout(function () { a.classList.remove('copied'); }, 1500);
        });
      }
    });
  }
})();
