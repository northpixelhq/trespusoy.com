/* Tres – Pusoy Dos · trespusoy.com — the home page's behaviour.
   Everything here is an enhancement. Without it the page reads in full,
   both store buttons work, and the video plays from its own controls.
   No cookie, no storage, nothing sent anywhere. */
(function () {
  'use strict';

  var GOOGLE_PLAY = 'https://play.google.com/store/apps/details?id=dev.tres.app';
  var APP_STORE = 'https://apps.apple.com/app/id6815482151';

  var root = document.documentElement;
  // The head's one-line script has already named the platform, with the
  // same rules as /get/ (an iPad asking for the desktop site counts as iOS).
  var platform = /\bis-android\b/.test(root.className) ? 'android'
    : /\bis-ios\b/.test(root.className) ? 'ios' : 'other';
  var reduceMotion = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  var conn = navigator.connection || {};
  var lightData = !!conn.saveData || /2g$/.test(conn.effectiveType || '');
  var canObserve = 'IntersectionObserver' in window;

  function all(selector, scope) {
    return Array.prototype.slice.call((scope || document).querySelectorAll(selector));
  }

  // A muted video that plays only while it is on screen, once the page has
  // finished loading, and rests when it leaves. Its own Pause/Play button
  // shows (the holder gets .is-autoplay). Reduced motion or a data saver
  // leave it still, with the video's own controls, for the visitor to start.
  function autoplay(video, toggle, holder) {
    if (reduceMotion || lightData || !canObserve || !toggle || !holder) return;
    var toggleText = toggle.querySelector('.see__toggle-text');
    video.removeAttribute('controls');
    holder.classList.add('is-autoplay');
    var inView = false;
    var userPaused = false;
    var pageLoaded = document.readyState === 'complete';
    var showControls = function () {
      video.setAttribute('controls', '');
      holder.classList.remove('is-autoplay');
    };
    // A browser that refuses to start the video by itself (a battery saver,
    // say) gets the video's own controls back. A play cut short by a pause
    // is not a refusal.
    var onRefused = function (error) {
      if (error && error.name === 'NotAllowedError') showControls();
    };
    var start = function () {
      video.preload = 'auto';
      var attempt = video.play();
      if (attempt && attempt.catch) attempt.catch(onRefused);
    };
    var tryPlay = function () {
      if (inView && !userPaused && pageLoaded) start();
    };
    var syncToggle = function () {
      var playing = !video.paused;
      toggle.setAttribute('data-state', playing ? 'playing' : 'paused');
      if (toggleText) toggleText.textContent = playing ? 'Pause' : 'Play';
    };
    window.addEventListener('load', function () { pageLoaded = true; tryPlay(); });
    new IntersectionObserver(function (entries) {
      inView = entries[0].isIntersecting;
      if (inView) tryPlay(); else video.pause();
    }, { threshold: 0.4 }).observe(video);
    toggle.addEventListener('click', function () {
      if (video.paused) { userPaused = false; start(); } else { userPaused = true; video.pause(); }
    });
    video.addEventListener('play', syncToggle);
    video.addEventListener('pause', syncToggle);
    syncToggle();
  }

  // 1. "Get Tres" goes straight to this phone's store; elsewhere to /get/.
  var direct = platform === 'android' ? GOOGLE_PLAY : platform === 'ios' ? APP_STORE : null;
  if (direct) all('[data-get]').forEach(function (a) { a.href = direct; });

  // 2. Sections arrive as they scroll in. Anything already on screen when
  //    this runs is left exactly as it is, so nothing blinks.
  if (!reduceMotion && canObserve) {
    var revealers = all('[data-reveal]');
    var fold = window.innerHeight * 0.95;
    var pending = revealers.filter(function (el) {
      if (el.getBoundingClientRect().top < fold) { el.classList.add('is-in'); el.classList.add('is-seen'); return false; }
      return true;
    });
    root.classList.add('reveal-ready');
    var revealIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-in');
          revealIO.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    pending.forEach(function (el) { revealIO.observe(el); });
  }

  // 3. The hero's idle drift rests while the hero is off screen.
  var hero = document.querySelector('[data-hero]');
  if (hero && canObserve) {
    new IntersectionObserver(function (entries) {
      hero.classList.toggle('is-away', !entries[0].isIntersecting);
    }).observe(hero);
  }

  // 4. On a phone, once the top of the page (its store buttons, on the home
  //    page) has scrolled away, a slim bar keeps the store one tap away,
  //    until the last call or the footer shows.
  var bar = document.querySelector('[data-getbar]');
  var heroStores = document.querySelector('[data-getbar-start]');
  var finalSection = document.querySelector('[data-final]');
  var footer = document.querySelector('.site-footer');
  if (bar && heroStores && canObserve) {
    var seen = { hero: true, end: false };
    var barLink = bar.querySelector('a');
    var update = function () {
      var show = !seen.hero && !seen.end;
      bar.classList.toggle('is-shown', show);
      bar.setAttribute('aria-hidden', show ? 'false' : 'true');
      barLink.tabIndex = show ? 0 : -1;
    };
    new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.target === heroStores) {
          // only "gone" once scrolled past, not before it is reached
          seen.hero = entry.isIntersecting || entry.boundingClientRect.top > 0;
        } else {
          seen.end = entries.some(function (e) { return e.target !== heroStores && e.isIntersecting; }) ||
            (finalSection && finalSection.getBoundingClientRect().top < window.innerHeight);
        }
      });
      update();
    }).observe(heroStores);
    var endIO = new IntersectionObserver(function () {
      seen.end = (finalSection && finalSection.getBoundingClientRect().top < window.innerHeight) ||
        (footer && footer.getBoundingClientRect().top < window.innerHeight);
      update();
    });
    if (finalSection) endIO.observe(finalSection);
    if (footer) endIO.observe(footer);
  }

  // 5. The gameplay clip. It loads only once it is nearly on screen and the
  //    page has finished loading, plays muted while in view, and rests when
  //    it leaves. Reduced motion or a data saver keep it still, with its own
  //    controls, for the visitor to start.
  var video = document.querySelector('.clip-video');
  if (video) {
    var cues = (video.getAttribute('data-cues') || '').split(/\s+/).map(Number);
    var list = document.getElementById('clip-steps');
    var steps = list ? all('li', list) : [];
    var lit = all('[data-lit]');
    var live = document.querySelector('.see__live');
    var lastIndex = -2;
    var swapTimer = 0;

    var paint = function () {
      var t = video.currentTime || 0;
      var index = -1;
      for (var i = 0; i < cues.length; i++) if (t >= cues[i]) index = i;
      if (list && video.duration) list.style.setProperty('--p', Math.min(1, t / video.duration).toFixed(4));
      if (index === lastIndex) return;
      lastIndex = index;
      steps.forEach(function (li, i) {
        li.classList.toggle('is-done', i < index);
        li.classList.toggle('is-now', i === index);
      });
      lit.forEach(function (chip) {
        var at = (chip.getAttribute('data-lit') || '').split(/\s+/);
        chip.classList.toggle('is-lit', at.indexOf(String(index)) !== -1);
      });
      // Beside the phone, the step being shown, so it reads with the picture.
      if (live && steps[index]) {
        var words = steps[index].getAttribute('data-live') || steps[index].textContent;
        live.classList.add('is-swapping');
        clearTimeout(swapTimer);
        swapTimer = setTimeout(function () {
          live.textContent = words;
          live.classList.remove('is-swapping');
        }, 200);
      }
    };
    var ticking = false;
    var tick = function () {
      paint();
      if (!video.paused && !video.ended) requestAnimationFrame(tick); else ticking = false;
    };
    video.addEventListener('playing', function () {
      root.classList.add('clip-live');
      if (!ticking) { ticking = true; requestAnimationFrame(tick); }
    });
    video.addEventListener('seeked', paint);

    autoplay(video, document.querySelector('.see__media .see__toggle'), video.closest('.see__media'));
  }

  // The Neon Coast loop in the themes section follows the same rules. Its
  // still is given to it as a poster only as it nears the screen (a poster
  // in the page would download with the first screen), so it shows under the
  // video's own controls when the loop does not play by itself.
  var themeVideo = document.querySelector('.theme-video');
  if (themeVideo) {
    var setPoster = function () { themeVideo.poster = themeVideo.getAttribute('data-poster'); };
    if (canObserve) {
      var posterIO = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) { setPoster(); posterIO.disconnect(); }
      }, { rootMargin: '600px 0px' });
      posterIO.observe(themeVideo);
    } else {
      setPoster();
    }
    autoplay(themeVideo, document.querySelector('.theme-toggle'), themeVideo.closest('.spotlight__media'));
  }

  // 6. On a desktop, each theme table tilts a little toward the pointer.
  var finePointer = !!(window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches);
  if (finePointer && !reduceMotion) {
    all('.tile').forEach(function (tile) {
      tile.addEventListener('pointermove', function (event) {
        var box = tile.getBoundingClientRect();
        var x = (event.clientX - box.left) / box.width - 0.5;
        var y = (event.clientY - box.top) / box.height - 0.5;
        tile.style.setProperty('--ry', (x * 10).toFixed(2) + 'deg');
        tile.style.setProperty('--rx', (y * -8).toFixed(2) + 'deg');
        tile.classList.add('is-pointed');
      });
      tile.addEventListener('pointerleave', function () {
        tile.style.setProperty('--rx', '0deg');
        tile.style.setProperty('--ry', '0deg');
        tile.classList.remove('is-pointed');
      });
    });
  }

  // 7. Each theme table opens large in a dialog, with its big play beside
  //    it and the others a step away. Without the script, or a browser with
  //    no dialog, each link simply opens the large picture.
  var viewer = document.querySelector('.viewer');
  var tiles = all('.tile__link');
  if (viewer && tiles.length && typeof viewer.showModal === 'function') {
    // The large picture is made here, so nothing downloads until a table is opened.
    var vImg = document.createElement('img');
    vImg.className = 'viewer__img';
    vImg.width = 1080;
    vImg.height = 1772;
    vImg.alt = '';
    viewer.querySelector('.viewer__figure').appendChild(vImg);
    var vName = viewer.querySelector('.viewer__name');
    var vLine = viewer.querySelector('.viewer__line');
    var vCount = viewer.querySelector('.viewer__count');
    var vCaption = viewer.querySelector('.viewer__caption');
    var views = all('.viewer__view', viewer);
    var current = 0;
    var view = 'table';
    var opener = null;
    var wanted = '';
    var show = function (index, which) {
      current = (index + tiles.length) % tiles.length;
      view = which || 'table';
      var link = tiles[current];
      var d = link.dataset;
      var url = view === 'bigplay' ? d.bigplay : d.table;
      var small = link.querySelector('img');
      // The tile's own picture shows at once; the large one replaces it
      // when it has arrived.
      if (view === 'table' && small) vImg.src = small.currentSrc || small.src;
      vImg.alt = view === 'bigplay' ? d.bigplayAlt : d.tableAlt;
      wanted = url;
      var large = new Image();
      large.onload = function () { if (wanted === url) vImg.src = url; };
      large.src = url;
      vName.textContent = d.name;
      vLine.textContent = d.line;
      vCount.textContent = 'Theme Pack ' + (current + 1) + ' of ' + tiles.length;
      vCaption.textContent = view === 'bigplay' ? d.bigplayCaption : 'A hand of thirteen, dealt';
      views.forEach(function (b) {
        b.setAttribute('aria-pressed', b.getAttribute('data-view') === view ? 'true' : 'false');
      });
    };
    all('[data-viewer]').forEach(function (link) {
      link.addEventListener('click', function (event) {
        if (event.metaKey || event.ctrlKey || event.shiftKey || event.button > 0) return;
        event.preventDefault();
        opener = link;
        show(Number(link.getAttribute('data-viewer')), link.getAttribute('data-start') || 'table');
        viewer.showModal();
        root.classList.add('viewer-open');
      });
    });
    views.forEach(function (b) {
      b.addEventListener('click', function () { show(current, b.getAttribute('data-view')); });
    });
    all('.viewer__step', viewer).forEach(function (b) {
      b.addEventListener('click', function () { show(current + Number(b.getAttribute('data-step')), view); });
    });
    viewer.querySelector('.viewer__close').addEventListener('click', function () { viewer.close(); });
    viewer.addEventListener('keydown', function (event) {
      if (event.key === 'ArrowRight') { event.preventDefault(); show(current + 1, view); }
      if (event.key === 'ArrowLeft') { event.preventDefault(); show(current - 1, view); }
    });
    viewer.addEventListener('close', function () {
      root.classList.remove('viewer-open');
      if (opener) opener.focus();
    });
  }

  // 8. The phone menu closes on a tap outside it or on Escape.
  var menu = document.querySelector('.menu');
  if (menu) {
    document.addEventListener('click', function (event) {
      if (menu.open && !menu.contains(event.target)) menu.open = false;
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && menu.open) {
        menu.open = false;
        menu.querySelector('summary').focus();
      }
    });
  }
})();
