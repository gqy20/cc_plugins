/* 让插图跟随页面的浅色/深色主题切换。
 *
 * 为什么需要它：SVG 用 <img> 引用时是独立文档，内部的
 * `@media (prefers-color-scheme: dark)` 只看操作系统设置，看不到
 * MkDocs Material 的主题开关。系统是浅色、用户手动切到深色时，
 * 页面是深色的、插图还是浅色的 —— 视觉割裂。
 *
 * 做法：每张图生成两份（fig-x.svg / fig-x.dark.svg），
 * 这里按 <body data-md-color-scheme> 换 src。
 */
(function () {
  "use strict";

  var DARK = ".dark.svg";
  var LIGHT = ".svg";

  function isDark() {
    var scheme = document.body && document.body.getAttribute("data-md-color-scheme");
    if (scheme) return scheme === "slate";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  }

  /** 把任意一边的 src 归一化，再按目标模式生成。 */
  function urlFor(src, dark) {
    if (!src || src.indexOf(".svg") < 0) return src;
    var base = src.slice(0, src.lastIndexOf(".svg"));
    if (base.slice(-5) === ".dark") base = base.slice(0, -5);
    return base + (dark ? DARK : LIGHT);
  }

  function apply() {
    var dark = isDark();
    var imgs = document.querySelectorAll(".md-typeset figure img");
    for (var i = 0; i < imgs.length; i++) {
      var img = imgs[i];
      var want = urlFor(img.getAttribute("src"), dark);
      if (img.getAttribute("src") !== want) img.setAttribute("src", want);
    }
  }

  /* 预取另一份，避免切换主题时闪一下空白 */
  function prefetch() {
    var dark = isDark();
    var imgs = document.querySelectorAll(".md-typeset figure img");
    for (var i = 0; i < imgs.length; i++) {
      var other = urlFor(imgs[i].getAttribute("src"), !dark);
      if (other) { var pre = new Image(); pre.src = other; }
    }
  }

  function schedule() {
    if (window.requestAnimationFrame) window.requestAnimationFrame(apply);
    else apply();
  }

  /* 1. 主题开关：Material 在 <body> 上改 data-md-color-scheme */
  if (window.MutationObserver && document.body) {
    new MutationObserver(schedule).observe(document.body, {
      attributes: true,
      attributeFilter: ["data-md-color-scheme"]
    });
    /* 2. instant 导航：整块 <article> 被替换，figure 是新节点 */
    new MutationObserver(schedule).observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  /* 3. 系统主题变化（用户没手动锁死时 Material 也会跟着变） */
  if (window.matchMedia) {
    var mq = window.matchMedia("(prefers-color-scheme: dark)");
    if (mq.addEventListener) mq.addEventListener("change", schedule);
    else if (mq.addListener) mq.addListener(schedule);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { apply(); prefetch(); });
  } else {
    apply();
    prefetch();
  }
})();
