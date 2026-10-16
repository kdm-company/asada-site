(function () {
  "use strict";

  var root = document.documentElement;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  // 初回かどうかは head のインラインスクリプトが既に判定済み
  var isFirstVisit = root.classList.contains("is-first-visit");

  /* --- ローディング（初回アクセス時のみ） ---
     一瞬で消えると点滅して見えるため、最低表示時間を設ける */
  var LOADING_MIN_MS = 1200;
  var startedAt = Date.now();

  var hideLoading = function () {
    var loading = document.getElementById("loading");
    if (!loading) return;
    var wait = Math.max(0, LOADING_MIN_MS - (Date.now() - startedAt));
    window.setTimeout(function () {
      loading.classList.add("is-hidden");
    }, wait);
  };

  if (isFirstVisit) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", hideLoading);
    } else {
      hideLoading();
    }
  }

  // --- スマホメニュー開閉（背面スクロールロック） ---
  var menuBtn = document.getElementById("menuBtn");
  var gnav = document.getElementById("gnav");

  if (menuBtn && gnav) {
    var setMenu = function (isOpen) {
      document.body.classList.toggle("is-menu-open", isOpen);
      menuBtn.setAttribute("aria-expanded", String(isOpen));
      menuBtn.setAttribute("aria-label", isOpen ? "メニューを閉じる" : "メニューを開く");
    };

    menuBtn.addEventListener("click", function () {
      setMenu(!document.body.classList.contains("is-menu-open"));
    });

    // 実際にタップされるのはa内のspan/imgなので、祖先までさかのぼって判定する
    gnav.addEventListener("click", function (e) {
      if (e.target.closest("a")) setMenu(false);
    });

    // 開いている間はEscで閉じられるようにする
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && document.body.classList.contains("is-menu-open")) {
        setMenu(false);
        menuBtn.focus();
      }
    });
  }

  // --- タブナビゲーション（パネル切り替え / リストフィルタ） ---
  document.querySelectorAll(".tab-nav").forEach(function (nav) {
    var mode = nav.getAttribute("data-mode");
    var btns = nav.querySelectorAll(".tab-nav__btn");

    btns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        btns.forEach(function (b) {
          b.classList.remove("is-active");
          b.setAttribute("aria-selected", "false");
        });
        btn.classList.add("is-active");
        btn.setAttribute("aria-selected", "true");

        if (mode === "filter") {
          var cat = btn.getAttribute("data-cat");
          var container = nav.parentElement;
          container.querySelectorAll("li[data-cat]").forEach(function (item) {
            item.style.display =
              cat === "all" || item.getAttribute("data-cat") === cat ? "" : "none";
          });
        }
      });
    });
  });

  // --- サイドバーナビ スムーズスクロール ---
  document.querySelectorAll(".page-nav__list a[href^='#']").forEach(function (a) {
    a.addEventListener("click", function (e) {
      var id = a.getAttribute("href").slice(1);
      var target = document.getElementById(id);
      if (target) {
        e.preventDefault();
        var headerH = document.getElementById("header")
          ? document.getElementById("header").offsetHeight
          : 0;
        var top = target.getBoundingClientRect().top + window.scrollY - headerH - 24;
        window.scrollTo({ top: top, behavior: "smooth" });
      }
    });
  });

  // --- サイドバーアクティブ状態（IntersectionObserver） ---
  var pageNavLinks = document.querySelectorAll(".page-nav__list a[href^='#']");

  if (pageNavLinks.length) {
    var sectionIds = Array.prototype.map.call(pageNavLinks, function (a) {
      return a.getAttribute("href").slice(1);
    });

    var activateLink = function (id) {
      pageNavLinks.forEach(function (a) {
        a.classList.toggle("is-active", a.getAttribute("href") === "#" + id);
      });
    };

    var headerHeight = document.getElementById("header")
      ? document.getElementById("header").offsetHeight
      : 0;

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            activateLink(entry.target.id);
          }
        });
      },
      {
        rootMargin: "-" + (headerHeight + 16) + "px 0px -60% 0px",
        threshold: 0,
      }
    );

    sectionIds.forEach(function (id) {
      var el = document.getElementById(id);
      if (el) observer.observe(el);
    });
  }

  /* --- ヒーロー内 新着情報ティッカー：1件流し終えたら次の記事へ --- */
  var ticker = document.getElementById("heroTicker");

  if (ticker) {
    var tickerItems = Array.prototype.slice.call(
      ticker.querySelectorAll(".hero-ticker__item")
    );

    // 視差軽減を希望するユーザーには流さない（インラインstyleはCSSのMQを
    // 上書きしてしまうため、JS側で判定して起動自体を止める）
    if (tickerItems.length && !reduceMotion) {
      var current = 0;

      // 流れる速さ(px/秒)はCSSの--ticker-speedから取得（SPは遅め）
      var getSpeed = function () {
        var v = parseFloat(
          getComputedStyle(ticker).getPropertyValue("--ticker-speed")
        );
        return v > 0 ? v : 90;
      };

      var play = function (index) {
        var item = tickerItems[index];
        var title = item.querySelector(".hero-ticker__title");
        var track = item.querySelector(".hero-ticker__track");
        if (!title || !track) return;

        // 右端の外から左端の外まで＝窓幅＋テキスト幅を移動する
        var distance = track.offsetWidth + title.offsetWidth;
        var seconds = Math.max(distance / getSpeed(), 4);

        // アニメーションを頭から再生させるためリフローを挟む
        title.style.animation = "none";
        void title.offsetWidth;
        title.style.animation =
          "heroTickerFlow " + seconds + "s linear";
      };

      var next = function () {
        tickerItems[current].classList.remove("is-active");
        current = (current + 1) % tickerItems.length;
        tickerItems[current].classList.add("is-active");
        play(current);
      };

      tickerItems.forEach(function (item) {
        var title = item.querySelector(".hero-ticker__title");
        if (title) title.addEventListener("animationend", next);
      });

      // Webフォント読み込み後だと実測幅がずれるため、確定を待って初回再生
      if (document.fonts && document.fonts.ready) {
        document.fonts.ready.then(function () {
          play(current);
        });
      } else {
        play(current);
      }
    }
  }

  /* --- Contact Form 7：送信成功で送信完了ページへ --- */
  document.addEventListener("wpcf7mailsent", function () {
    var url = document.body.getAttribute("data-thanks-url");
    if (url) window.location.href = url;
  }, false);

  /* --- スクロールでセクションをフェードイン ---
     data-reveal はテンプレート側で出力済み。
     JSで後から付けると、一度表示されたものが隠れてちらつくため */
  (function () {
    if (reduceMotion || !("IntersectionObserver" in window)) return;

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-revealed");
        io.unobserve(entry.target);   // 一度出したら監視をやめる
      });
    }, { rootMargin: "0px 0px -12% 0px", threshold: 0.05 });

    document.querySelectorAll("[data-reveal]").forEach(function (el) {
      if (el.closest(".hero-area")) {   // ヒーローは初期表示なので対象外
        el.removeAttribute("data-reveal");
        return;
      }
      io.observe(el);
    });

    // 下層のページ見出しとパンくずは、スクロールを待たず読み込み直後に出す。
    // 順番に出したいので、並び順に応じた遅延をCSS変数で渡す
    var onload = document.querySelectorAll("[data-reveal-onload]");
    if (onload.length) {
      onload.forEach(function (el, i) {
        el.style.setProperty("--reveal-delay", i * 120 + "ms");
      });
      // requestAnimationFrame はバックグラウンドタブでは発火しないため使わない。
      // 一度レイアウトを確定させてからクラスを付け、確実に遷移させる
      void document.body.offsetHeight;
      onload.forEach(function (el) {
        el.classList.add("is-revealed");
      });
    }
  })();

})();
