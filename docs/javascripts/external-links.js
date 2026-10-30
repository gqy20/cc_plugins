/* 标记站外链接。
 *
 * 为什么不能用纯 CSS 的 `a[href^="http"]`：
 *   Material 的运行时会把页面里所有相对 href 改写成绝对地址
 *   （bundle 里的 os()：`r[o] = new URL(r.getAttribute(o), t).toString()`），
 *   站内链接因此也会命中 `^="http"`，图标会撒得到处都是。
 *
 * 做法：按 origin 判断是不是真的跳到站外，打上 data-cc-external，
 *      由 CSS 决定要不要加 ↗。
 */
(function () {
  "use strict";

  var MARK = "data-cc-external";

  function mark() {
    var here = window.location.origin;
    var links = document.querySelectorAll(".md-typeset a[href]");
    for (var i = 0; i < links.length; i++) {
      var a = links[i];
      var href = a.getAttribute("href");
      if (!href) continue;
      var abs;
      try {
        abs = new URL(href, window.location.href);
      } catch (err) {
        continue;
      }
      if (abs.protocol !== "http:" && abs.protocol !== "https:") continue;
      if (abs.origin === here) continue;
      a.setAttribute(MARK, "");
    }
  }

  function schedule() {
    if (window.requestAnimationFrame) window.requestAnimationFrame(mark);
    else mark();
  }

  if (window.MutationObserver && document.body) {
    /* instant 导航会整块替换 <article>，新节点要重新标记 */
    new MutationObserver(schedule).observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mark);
  } else {
    mark();
  }
})();
