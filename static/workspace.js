(function () {
  'use strict';

  var LS = window.localStorage;

  // ─── State ──────────────────────────────────
  var currentView = 'dashboard';
  var currentLessonId = null;

  // ─── DOM refs ───────────────────────────────
  var content = document.getElementById('ws-content');
  var termOutput = document.getElementById('ws-terminal-output');
  var termInput = document.getElementById('ws-terminal-input');
  var signalsFeed = document.getElementById('ws-signals-feed');
  var notesTA = document.getElementById('ws-notes-ta');

  // nav targets for keyboard shortcuts (set while a lesson is open)
  var wsNav = { module: null, prev: null, next: null };
  var readBar = null;

  // guided ("tour guide") lesson state
  var guided = { active: false, steps: [], idx: 0, l: null, module: null, slug: null, typing: false, timer: null, skip: null };

  // ─── Reading-progress bar (fills as you scroll a lesson) ──
  (function initReadBar() {
    var center = document.querySelector('.ws-center');
    if (!center) return;
    readBar = document.createElement('div');
    readBar.className = 'ws-read-progress';
    readBar.innerHTML = '<span></span>';
    center.insertBefore(readBar, center.firstChild);
    if (content) content.addEventListener('scroll', updateReadProgress, { passive: true });
  })();

  // In guided mode a single step can be short, so pure scroll-based progress
  // barely moves (or jumps straight to 100%). Instead, treat the bar as
  // "how far through the tour" — completed steps count fully, and the
  // current step contributes its own scroll fraction on top, so the bar
  // always advances meaningfully as you move through the lesson regardless
  // of any one step's length. Read mode keeps plain whole-document scroll.
  function updateReadProgress() {
    if (!readBar || !content) return;
    var pct;
    if (guided.active && guided.steps.length) {
      var total = guided.steps.length;
      var base = guided.idx / total;
      var max = content.scrollHeight - content.clientHeight;
      var withinStep = max > 0 ? Math.min(content.scrollTop / max, 1) : 1;
      pct = (base + withinStep * (1 / total)) * 100;
    } else {
      var docMax = content.scrollHeight - content.clientHeight;
      pct = docMax > 0 ? (content.scrollTop / docMax) * 100 : 0;
    }
    readBar.firstChild.style.width = pct + '%';
  }

  // ─── Keyboard nav: ←/k = prev, →/j = next (while in a lesson) ──
  document.addEventListener('keydown', function (e) {
    var t = e.target;
    if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA')) return;
    // guided mode: arrows/space step through the tour
    if (guided.active) {
      if (e.key === 'ArrowRight' || e.key === 'j' || e.key === ' ') { e.preventDefault(); guidedNext(); }
      else if (e.key === 'ArrowLeft' || e.key === 'k') { e.preventDefault(); guidedPrev(); }
      return;
    }
    if (!wsNav.module) return;
    if ((e.key === 'ArrowRight' || e.key === 'j') && wsNav.next) {
      e.preventDefault(); window.wsOpenLesson(wsNav.module, wsNav.next);
    } else if ((e.key === 'ArrowLeft' || e.key === 'k') && wsNav.prev) {
      e.preventDefault(); window.wsOpenLesson(wsNav.module, wsNav.prev);
    }
  });

  // ─── Helpers ────────────────────────────────
  function escapeHtml(str) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }

  function relTime(iso) {
    if (!iso) return null;
    var diff = Date.now() - new Date(iso).getTime();
    var mins = Math.floor(diff / 60000);
    if (mins < 1) return 'just now';
    if (mins < 60) return mins + 'm ago';
    var hrs = Math.floor(mins / 60);
    mins = mins % 60;
    if (hrs < 24) return hrs + 'h ' + mins + 'm ago';
    return Math.floor(hrs / 24) + 'd ago';
  }

  function lsGet(key, def) {
    try { var v = LS.getItem(key); return v !== null ? v : def; } catch (e) { return def; }
  }
  function lsSet(key, val) {
    try { LS.setItem(key, val); } catch (e) {}
  }

  function setFocus(type, slug, title) {
    lsSet('ws_focus_type', type);
    lsSet('ws_focus_slug', slug);
    lsSet('ws_focus_title', title);
    lsSet('ws_focus_time', new Date().toISOString());
  }

  // Returns true if message contains the historical source tag
  function isHistorical(message) {
    return typeof message === 'string' && message.indexOf('[source: historical]') !== -1;
  }

  // ─── Nav ────────────────────────────────────
  document.querySelectorAll('.ws-nav-item').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var view = btn.getAttribute('data-view');
      showView(view);
    });
  });

  function showView(view) {
    currentView = view;
    wsNav.module = null;
    document.querySelectorAll('.ws-nav-item').forEach(function (b) {
      b.classList.toggle('active', b.getAttribute('data-view') === view);
    });

    if (view === 'dashboard') renderDashboard();
    else if (view === 'lessons') renderModuleList();
    else if (view === 'maps') renderConcept('stock');
  }

  // ─── Dashboard / Workspace Home ─────────────
  function renderDashboard() {
    currentView = 'dashboard';

    // read focus from localStorage
    var focusType = lsGet('ws_focus_type', null);
    var focusTitle = lsGet('ws_focus_title', null);
    var focusTime = lsGet('ws_focus_time', null);

    // build focus bar
    var focusHtml;
    if (focusType && focusTitle) {
      var ago = relTime(focusTime);
      focusHtml = '<div class="ws-focus-bar">'
        + '<span class="ws-focus-label">focus</span>'
        + '<span class="ws-focus-value">' + escapeHtml(focusTitle) + '</span>'
        + '<span class="ws-focus-time">' + (ago || '') + '</span>'
        + '</div>';
    } else {
      focusHtml = '<div class="ws-focus-bar ws-focus-empty">'
        + '<span class="ws-focus-label">focus</span>'
        + '<span class="ws-focus-value muted">&mdash; no active session</span>'
        + '</div>';
    }

    // build recent activity from localStorage log
    var recentLog = [];
    var lc = lsGet('ws_last_concept_title', null);
    var lcTime = lsGet('ws_last_concept_time', null);
    if (lc && lcTime) recentLog.push({ text: 'viewed concept: ' + lc, time: lcTime });

    var ll = lsGet('ws_last_lesson_title', null);
    var llTime = lsGet('ws_last_lesson_time', null);
    if (ll && llTime) recentLog.push({ text: 'opened lesson: ' + ll, time: llTime });

    var ln = lsGet('ws_last_note_time', null);
    if (ln) recentLog.push({ text: 'updated notes', time: ln });

    var lsig = lsGet('ws_last_signal_time', null);
    if (lsig) recentLog.push({ text: 'signals updated', time: lsig });

    recentLog.sort(function (a, b) { return b.time.localeCompare(a.time); });
    recentLog = recentLog.slice(0, 5);

    var recentHtml;
    if (recentLog.length === 0) {
      recentHtml = '<div class="ws-recent-activity">'
        + '<div class="ws-block-title">recent</div>'
        + '<div class="ws-activity-row muted">no activity yet &mdash; open a lesson or concept to begin</div>'
        + '</div>';
    } else {
      recentHtml = '<div class="ws-recent-activity">'
        + '<div class="ws-block-title">recent</div>';
      recentLog.forEach(function (r) {
        recentHtml += '<div class="ws-activity-row"><span class="ws-activity-text">' + escapeHtml(r.text) + '</span><span class="ws-activity-time">' + (relTime(r.time) || '') + '</span></div>';
      });
      recentHtml += '</div>';
    }

    // status strip (static — updated on each dashboard render)
    var sigCount = lsGet('ws_signal_count', '0');
    var noteStatus = notesTA && notesTA.value.trim() ? 'saved' : 'empty';
    var lessonProg = lsGet('ws_lesson_progress', '?');

    var statusHtml = '<div class="ws-status-strip">'
      + '<span class="ws-status-item"><span class="ws-status-label">pane</span> dashboard</span>'
      + '<span class="ws-status-item"><span class="ws-status-label">signals</span> ' + sigCount + '</span>'
      + '<span class="ws-status-item"><span class="ws-status-label">notes</span> ' + noteStatus + '</span>'
      + '<span class="ws-status-item"><span class="ws-status-label">lessons</span> ' + lessonProg + '</span>'
      + '</div>';

    // put it all together (progress snapshot loads async)
    content.innerHTML = focusHtml
      + '<div class="ws-progress-block" id="ws-progress-block">'
      + '<div class="ws-block-title">progress</div>'
      + '<div class="ws-progress-loading muted">loading...</div>'
      + '</div>'
      + '<div class="ws-next-action" id="ws-next-action">'
      + '<span class="ws-next-label">next</span>'
      + '<span class="ws-next-value muted">determining...</span>'
      + '</div>'
      + recentHtml
      + statusHtml;

    // fetch module data for progress + next action
    fetch('/workspace/api/modules')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var modules = data.modules || [];
        renderProgressBlock(modules);
      })
      .catch(function () {
        var pb = document.getElementById('ws-progress-block');
        if (pb) pb.innerHTML = '<div class="ws-block-title">progress</div><div class="ws-progress-loading muted">unavailable</div>';
      });
  }

  function renderProgressBlock(modules) {
    var pb = document.getElementById('ws-progress-block');
    var na = document.getElementById('ws-next-action');
    if (!pb) return;

    var totalDone = 0, totalLessons = 0;
    var firstIncomplete = null;

    var html = '<div class="ws-block-title">progress</div>';

    modules.forEach(function (m) {
      var done = m.completed_count || 0;
      var total = m.lesson_count || 0;
      totalDone += done;
      totalLessons += total;
      var pct = total > 0 ? (done / total * 100) : 0;

      if (firstIncomplete === null && done < total) {
        firstIncomplete = m;
      }

      html += '<div class="ws-progress-row">'
        + '<span class="ws-progress-name">' + escapeHtml(m.title) + '</span>'
        + '<span class="ws-progress-bar-mini"><span data-pct="' + pct + '" style="width:0%"></span></span>'
        + '<span class="ws-progress-count">' + done + '/' + total + '</span>'
        + '</div>';
    });

    var totalPct = totalLessons > 0 ? (totalDone / totalLessons * 100) : 0;
    html += '<div class="ws-progress-sep"></div>'
      + '<div class="ws-progress-row ws-progress-total">'
      + '<span class="ws-progress-name">total</span>'
      + '<span class="ws-progress-bar-mini"><span data-pct="' + totalPct + '" style="width:0%"></span></span>'
      + '<span class="ws-progress-count">' + totalDone + '/' + totalLessons + '</span>'
      + '</div>';

    pb.innerHTML = html;

    // animate the bars filling in
    requestAnimationFrame(function () {
      var bars = pb.querySelectorAll('.ws-progress-bar-mini > span');
      for (var b = 0; b < bars.length; b++) {
        bars[b].style.width = (bars[b].getAttribute('data-pct') || 0) + '%';
      }
    });

    // persist total for status strip
    lsSet('ws_lesson_progress', totalDone + '/' + totalLessons);

    // update next action
    if (na) {
      if (firstIncomplete) {
        var actionText;
        if (firstIncomplete.completed_count === 0 || firstIncomplete.completed_count === undefined) {
          actionText = 'Start ' + firstIncomplete.title;
        } else {
          actionText = 'Continue ' + firstIncomplete.title + ' (' + firstIncomplete.completed_count + '/' + firstIncomplete.lesson_count + ' complete)';
        }
        na.innerHTML = '<span class="ws-next-label">next</span><span class="ws-next-value">' + escapeHtml(actionText) + '</span>';
      } else if (totalLessons > 0) {
        na.innerHTML = '<span class="ws-next-label">next</span><span class="ws-next-value">all ' + totalLessons + ' lessons completed &mdash; review concepts in Maps</span>';
      } else {
        na.innerHTML = '<span class="ws-next-label">next</span><span class="ws-next-value muted">no lessons available</span>';
      }
    }

    // update status strip lesson count
    var stripItems = document.querySelectorAll('.ws-status-item');
    for (var i = 0; i < stripItems.length; i++) {
      var item = stripItems[i];
      var label = item.querySelector('.ws-status-label');
      if (label && label.textContent === 'lessons') {
        item.innerHTML = '<span class="ws-status-label">lessons</span> ' + totalDone + '/' + totalLessons;
        break;
      }
    }
  }

  // ─── Concept tree expansion ────────────────
  document.querySelectorAll('.ws-tree-group-title').forEach(function (title) {
    title.addEventListener('click', function () {
      var children = title.nextElementSibling;
      if (!children) return;
      var isHidden = children.style.display === 'none';
      children.style.display = isHidden ? '' : 'none';
    });
  });

  document.querySelectorAll('.ws-tree-node').forEach(function (node) {
    node.addEventListener('click', function () {
      var concept = node.getAttribute('data-concept');
      if (concept) renderConcept(concept);
    });
  });

  function renderConcept(slug) {
    currentView = 'maps';
    content.innerHTML = '<div class="ws-concept-detail"><em class="muted">loading...</em></div>';
    fetch('/api/concepts/' + encodeURIComponent(slug))
      .then(function (r) {
        if (!r.ok) throw new Error('Not found');
        return r.json();
      })
      .then(function (data) {
        var html = '<div class="ws-concept-detail">';
        html += '<h2>' + (data.title || data.id) + '</h2>';
        html += '<p>' + (data.description || '') + '</p>';
        if (data.lesson_slug) {
          html += '<div class="ws-lesson-nav"><button class="ws-lesson-nav-btn" onclick="wsOpenLesson(\'' + data.module_slug + '\',\'' + data.lesson_slug + '\')">Read related lesson: ' + (data.lesson_title || data.lesson_slug) + '</button></div>';
        }
        html += '</div>';
        content.innerHTML = html;

        // track focus
        setFocus('concept', data.id, data.title || data.id);
        lsSet('ws_last_concept_title', data.title || data.id);
        lsSet('ws_last_concept_time', new Date().toISOString());
      })
      .catch(function () {
        content.innerHTML = '<div class="ws-concept-detail"><p class="muted">Concept not found.</p></div>';
      });
  }

  // ─── Lessons ────────────────────────────────
  function renderModuleList() {
    content.innerHTML = '<div class="ws-lesson-body"><em class="muted">loading modules...</em></div>';
    fetch('/workspace/api/modules')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var modules = data.modules || [];
        var html = '<div class="ws-module-list">';
        modules.forEach(function (m) {
          html += '<div class="ws-module-card" onclick="wsOpenModule(\'' + m.slug + '\')">';
          html += '<div class="ws-module-card-title">' + m.title + '</div>';
          if (m.description) html += '<div class="ws-module-card-desc">' + m.description + '</div>';
          var done = m.completed_count || 0;
          var total_known = m.lesson_count || '?';
          html += '<div class="ws-module-card-meta">' + done + '/' + total_known + ' lessons</div>';
          html += '</div>';
        });
        html += '</div>';
        content.innerHTML = html;
      })
      .catch(function () {
        content.innerHTML = '<div class="ws-lesson-body"><p class="muted">Could not load modules.</p></div>';
      });
  }

  window.wsOpenModule = function (slug) {
    wsNav.module = null;
    content.innerHTML = '<div class="ws-lesson-body"><em class="muted">loading...</em></div>';
    fetch('/workspace/api/modules/' + encodeURIComponent(slug))
      .then(function (r) { return r.json(); })
      .then(function (m) {
        var html = '<button class="ws-back-btn" onclick="wsBackToModules()">&larr; back to modules</button>';
        html += '<div class="ws-module-card" style="margin-bottom:12px;cursor:default">';
        html += '<div class="ws-module-card-title">' + m.title + '</div>';
        if (m.description) html += '<div class="ws-module-card-desc">' + m.description + '</div>';
        html += '</div>';
        html += '<div class="ws-lesson-list">';
        var lessons = m.lessons || [];
        lessons.forEach(function (l) {
          var completed = l.is_completed ? 'completed' : '';
          html += '<div class="ws-lesson-row ' + completed + '" onclick="wsOpenLesson(\'' + m.slug + '\',\'' + l.slug + '\')">';
          html += '<span class="ws-lesson-row-title">' + (l.title || 'Untitled') + '</span>';
          html += '<span class="ws-lesson-row-meta">' + (l.item_type || 'lesson').toUpperCase() + ' • ' + (l.estimated_minutes || '?') + ' min' + (completed ? ' &check;' : '') + '</span>';
          html += '</div>';
        });
        html += '</div>';
        content.innerHTML = html;
      })
      .catch(function () {
        content.innerHTML = '<div class="ws-lesson-body"><p class="muted">Module not found.</p></div>';
      });
  };

  window.wsBackToModules = function () {
    showView('lessons');
  };

  window.wsOpenLesson = function (moduleSlug, lessonSlug) {
    currentLessonId = moduleSlug + '/' + lessonSlug;
    content.innerHTML = '<div class="ws-lesson-body"><em class="muted">loading lesson...</em></div>';
    fetch('/workspace/api/lessons/' + encodeURIComponent(moduleSlug) + '/' + encodeURIComponent(lessonSlug))
      .then(function (r) { return r.json(); })
      .then(function (l) {
        renderLesson(l, moduleSlug, lessonSlug);
        setFocus('lesson', moduleSlug + '/' + lessonSlug, l.title || lessonSlug);
        lsSet('ws_last_lesson_title', l.title || lessonSlug);
        lsSet('ws_last_lesson_time', new Date().toISOString());
      })
      .catch(function () {
        content.innerHTML = '<div class="ws-lesson-body"><p class="muted">Lesson not found.</p></div>';
      });
  };

  // ═══ Lesson rendering: guided ("tour") + read modes ═══

  function lessonHeaderHtml(l, moduleSlug, mode) {
    var isActivity = (l.item_type === 'activity');
    var typeLabel = (l.item_type || 'lesson').toUpperCase();
    return '<button class="ws-back-btn" onclick="wsOpenModule(\'' + moduleSlug + '\')">&larr; back to module</button>'
      + '<div class="ws-lesson-header ws-anim">'
      + '<div class="ws-lesson-kicker">'
      + '<span class="ws-type-badge' + (isActivity ? ' activity' : '') + '">' + typeLabel + '</span>'
      + '<span class="ws-lesson-mins">' + (l.estimated_minutes || '?') + ' min ' + (isActivity ? 'exercise' : 'read') + '</span>'
      + '<span class="ws-mode-toggle" id="ws-mode-toggle">'
      + '<button data-mode="guided" class="' + (mode === 'guided' ? 'active' : '') + '">guided</button>'
      + '<button data-mode="read" class="' + (mode === 'read' ? 'active' : '') + '">read</button>'
      + '</span>'
      + '</div>'
      + '<h1>' + escapeHtml(l.title || '') + '</h1>'
      + '</div>';
  }

  function lessonFooterHtml(l, moduleSlug) {
    var html = '<div class="ws-lesson-footer ws-anim"><div class="ws-lesson-nav">';
    html += l.prev_lesson_slug
      ? '<button class="ws-lesson-nav-btn" onclick="wsOpenLesson(\'' + moduleSlug + '\',\'' + l.prev_lesson_slug + '\')">&larr; ' + escapeHtml(l.prev_lesson_title || 'Previous') + '</button>'
      : '<span></span>';
    html += l.next_lesson_slug
      ? '<button class="ws-lesson-nav-btn" onclick="wsOpenLesson(\'' + moduleSlug + '\',\'' + l.next_lesson_slug + '\')">' + escapeHtml(l.next_lesson_title || 'Next') + ' &rarr;</button>'
      : '<span></span>';
    html += '</div>';
    html += l.is_completed
      ? '<button class="ws-btn-complete done" disabled>✓ completed</button>'
      : '<button class="ws-btn-complete" id="ws-btn-mark-complete">mark complete</button>';
    html += '</div>';
    return html;
  }

  function bindComplete() {
    var btn = document.getElementById('ws-btn-mark-complete');
    if (!btn) return;
    btn.addEventListener('click', function () {
      btn.disabled = true;
      btn.textContent = 'completing...';
      fetch('/workspace/api/lessons/' + encodeURIComponent(guided.module) + '/' + encodeURIComponent(guided.slug) + '/complete', { method: 'POST' })
        .then(function (r) { return r.json(); })
        .then(function (res) {
          if (res && res.ok) {
            btn.classList.add('done');
            btn.textContent = '✓ completed';
            if (guided.l) guided.l.is_completed = true;
          } else {
            btn.disabled = false;
            btn.textContent = 'mark complete';
          }
        })
        .catch(function () { btn.disabled = false; btn.textContent = 'mark complete'; });
    });
  }

  function bindModeToggle() {
    var t = document.getElementById('ws-mode-toggle');
    if (!t) return;
    t.querySelectorAll('button').forEach(function (b) {
      b.addEventListener('click', function () {
        lsSet('ws_lesson_mode', b.getAttribute('data-mode'));
        renderLesson(guided.l, guided.module, guided.slug);
      });
    });
  }

  // split rendered lesson HTML into sections at each <h2>
  function parseSections(html) {
    var tmp = document.createElement('div');
    tmp.innerHTML = html || '';
    var sections = [], cur = null;
    Array.prototype.forEach.call(tmp.childNodes, function (node) {
      if (node.nodeType === 1 && node.tagName === 'H2') {
        cur = { title: node.textContent.trim(), body: '' };
        sections.push(cur);
      } else {
        if (!cur) { cur = { title: '', body: '' }; sections.push(cur); }
        if (node.nodeType === 1) cur.body += node.outerHTML;
        else if (node.nodeType === 3 && node.textContent.trim()) cur.body += node.textContent;
      }
    });
    if (!sections.length) sections.push({ title: '', body: html || '' });
    return sections;
  }

  function renderLesson(l, moduleSlug, lessonSlug) {
    guided.l = l; guided.module = moduleSlug; guided.slug = lessonSlug;
    var mode = lsGet('ws_lesson_mode', 'guided');
    var isActivity = (l.item_type === 'activity');
    var header = lessonHeaderHtml(l, moduleSlug, mode);

    if (mode === 'guided') {
      guided.active = true;
      guided.steps = parseSections(l.content_html || l.content || '');
      guided.idx = 0;
      content.innerHTML = header + '<div class="ws-guided" id="ws-guided"></div>';
      content.scrollTop = 0;
      bindModeToggle();
      wsNav.module = null; // step nav owns the keyboard now
      renderGuidedStep();
      updateReadProgress();
    } else {
      guided.active = false;
      var body = l.content_html || l.content || '<p>No content yet.</p>';
      content.innerHTML = header
        + '<div class="ws-lesson-body ws-anim' + (isActivity ? ' is-activity' : '') + '">' + body + '</div>'
        + lessonFooterHtml(l, moduleSlug);
      content.scrollTop = 0;
      bindModeToggle();
      bindComplete();
      hydrateBlocks(content, false); // read mode: stat counts up as it scrolls into view
      wsNav.module = moduleSlug;
      wsNav.prev = l.prev_lesson_slug || null;
      wsNav.next = l.next_lesson_slug || null;
      updateReadProgress();
    }
  }

  function renderGuidedStep() {
    var l = guided.l, steps = guided.steps, idx = guided.idx;
    var sec = steps[idx];
    var isActivity = (l.item_type === 'activity');
    var isLast = (idx === steps.length - 1);
    var isFirst = (idx === 0);

    var dots = '';
    for (var i = 0; i < steps.length; i++) {
      dots += '<span class="ws-step-dot' + (i < idx ? ' done' : '') + (i === idx ? ' current' : '') + '"></span>';
    }

    var backLabel = isFirst ? (l.prev_lesson_slug ? '← previous lesson' : '← back') : '← back';
    var backDisabled = (isFirst && !l.prev_lesson_slug) ? ' disabled' : '';
    var controls;
    if (isLast) {
      controls = '<div class="ws-guided-controls">'
        + '<button class="ws-guided-btn" id="ws-g-back"' + backDisabled + '>' + backLabel + '</button>'
        + '<div class="ws-guided-finish">'
        + (l.is_completed
            ? '<button class="ws-btn-complete done" disabled>✓ completed</button>'
            : '<button class="ws-btn-complete" id="ws-btn-mark-complete">mark complete</button>')
        + (l.next_lesson_slug ? '<button class="ws-guided-btn primary" id="ws-g-nextlesson">next lesson →</button>' : '')
        + '</div></div>';
    } else {
      controls = '<div class="ws-guided-controls">'
        + '<button class="ws-guided-btn" id="ws-g-back"' + backDisabled + '>' + backLabel + '</button>'
        + '<button class="ws-guided-btn primary" id="ws-g-next">continue →</button>'
        + '</div>';
    }

    var g = document.getElementById('ws-guided');
    g.innerHTML = '<div class="ws-step ws-anim' + (isActivity ? ' is-activity' : '') + '">'
      + '<div class="ws-step-topbar"><span class="ws-step-dots">' + dots + '</span>'
      + '<span class="ws-step-count">' + (idx + 1) + ' / ' + steps.length + '</span></div>'
      + (sec.title ? '<h2 class="ws-step-title" id="ws-step-title"></h2>' : '')
      + '<div class="ws-lesson-body ws-step-body revealing' + (isActivity ? ' is-activity' : '') + '" id="ws-step-body">' + sec.body + '</div>'
      + controls + '</div>';

    var back = document.getElementById('ws-g-back');
    if (back) back.addEventListener('click', guidedPrev);
    var next = document.getElementById('ws-g-next');
    if (next) next.addEventListener('click', guidedNext);
    var nl = document.getElementById('ws-g-nextlesson');
    if (nl) nl.addEventListener('click', function () { window.wsOpenLesson(guided.module, l.next_lesson_slug); });
    if (isLast) bindComplete();

    // reveal: type the section heading like a guide, then fade the body in
    var titleEl = document.getElementById('ws-step-title');
    var bodyEl = document.getElementById('ws-step-body');
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    function showBody() {
      if (bodyEl) {
        bodyEl.classList.remove('revealing'); bodyEl.classList.add('shown');
        hydrateBlocks(bodyEl, true); // guided mode: step is already in view, animate now
      }
    }
    if (sec.title && titleEl && !reduce) {
      typewrite(titleEl, sec.title, showBody);
    } else {
      if (titleEl) titleEl.textContent = sec.title;
      showBody();
    }
  }

  function typewrite(el, text, done) {
    guided.typing = true;
    el.classList.add('tw-caret');
    el.textContent = '';
    var i = 0;
    clearTimeout(guided.timer);
    function finish() {
      clearTimeout(guided.timer);
      el.textContent = text;
      el.classList.remove('tw-caret');
      guided.typing = false;
      guided.skip = null;
      if (done) done();
    }
    guided.skip = finish;
    (function tick() {
      el.textContent = text.slice(0, i);
      if (i < text.length) { i++; guided.timer = setTimeout(tick, 24); }
      else { finish(); }
    })();
  }

  function skipTyping() {
    if (guided.typing && guided.skip) { guided.skip(); return true; }
    return false;
  }

  function guidedNext() {
    if (skipTyping()) return;               // first press reveals, next advances
    if (guided.idx < guided.steps.length - 1) { guided.idx++; renderGuidedStep(); afterStep(); }
    else if (guided.l.next_lesson_slug) { window.wsOpenLesson(guided.module, guided.l.next_lesson_slug); }
  }

  function guidedPrev() {
    if (guided.idx > 0) { guided.idx--; renderGuidedStep(); afterStep(); }
    else if (guided.l.prev_lesson_slug) { window.wsOpenLesson(guided.module, guided.l.prev_lesson_slug); }
  }

  function afterStep() { content.scrollTop = 0; updateReadProgress(); }

  // ═══ Lesson blocks: hydrate interactive elements inside rendered content ═══
  // `immediate`: true when the block is already on-screen (a guided step just
  // revealed) so it should animate right away; false in read mode, where a
  // stat block instead waits to scroll into view before counting up.

  function hydrateBlocks(root, immediate) {
    if (!root) return;
    root.querySelectorAll('[data-block="stat"]').forEach(function (el) { initStatBlock(el, immediate); });
    root.querySelectorAll('[data-block="reveal"]').forEach(initRevealBlock);
    root.querySelectorAll('[data-block="quiz"]').forEach(initQuizBlock);
    root.querySelectorAll('[data-block="calc"]').forEach(initCalcBlock);
  }

  function parseNum(s) {
    var n = parseFloat(String(s).replace(/,/g, ''));
    return isNaN(n) ? 0 : n;
  }

  function fmtNum(n) {
    var rounded = Math.round(n);
    return rounded.toLocaleString('en-US');
  }

  function animateStat(el) {
    if (el.dataset.wsAnimated === '1') return;
    el.dataset.wsAnimated = '1';
    var from = parseNum(el.getAttribute('data-from'));
    var to = parseNum(el.getAttribute('data-to'));
    var prefix = el.getAttribute('data-prefix') || '';
    var suffix = el.getAttribute('data-suffix') || '';
    var valueEl = el.querySelector('.ws-stat-value');
    if (!valueEl) return;
    el.classList.add(to >= from ? 'is-up' : 'is-down');

    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce) { valueEl.textContent = prefix + fmtNum(to) + suffix; return; }

    var duration = 1100, start = null;
    function ease(t) { return 1 - Math.pow(1 - t, 3); } // ease-out-cubic
    function frame(ts) {
      if (start === null) start = ts;
      var p = Math.min((ts - start) / duration, 1);
      var current = from + (to - from) * ease(p);
      valueEl.textContent = prefix + fmtNum(current) + suffix;
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  function initStatBlock(el, immediate) {
    if (immediate) { animateStat(el); return; }
    if (!('IntersectionObserver' in window)) { animateStat(el); return; }
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { animateStat(el); obs.disconnect(); }
      });
    }, { threshold: 0.5 });
    obs.observe(el);
  }

  function initRevealBlock(el) {
    var btn = el.querySelector('.ws-reveal-prompt');
    if (!btn) return;
    btn.addEventListener('click', function () {
      el.classList.toggle('open');
    });
  }

  function initQuizBlock(el) {
    var options = el.querySelectorAll('.ws-quiz-option');
    var feedback = el.querySelector('.ws-quiz-feedback');
    options.forEach(function (opt) {
      opt.addEventListener('click', function () {
        if (el.classList.contains('answered')) return;
        el.classList.add('answered');
        var isCorrect = opt.getAttribute('data-correct') === 'true';
        options.forEach(function (o) {
          if (o.getAttribute('data-correct') === 'true') o.classList.add('correct');
          else if (o === opt) o.classList.add('incorrect');
        });
        if (feedback) {
          feedback.hidden = false;
          feedback.classList.toggle('is-wrong', !isCorrect);
          feedback.textContent = isCorrect
            ? 'Correct — locked in.'
            : 'Not quite — the highlighted option is correct.';
        }
      });
    });
  }

  function initCalcBlock(el) {
    var type = el.getAttribute('data-type') || 'ownership';
    if (type !== 'ownership') return;

    var symbol = el.getAttribute('data-symbol') || 'the company';
    var price = parseNum(el.getAttribute('data-price')) || 1;
    var sharesOut = parseNum(el.getAttribute('data-shares-outstanding')) || 1;

    el.innerHTML =
      '<div class="ws-calc-title">Ownership calculator — ' + escapeHtml(symbol) + '</div>' +
      '<div class="ws-calc-row"><label>You invest</label>' +
      '<input type="number" class="ws-calc-input" id="ws-calc-amount" value="1000" min="1" step="1"></div>' +
      '<div class="ws-calc-result">' +
      '<div class="ws-calc-result-row"><span>Shares purchased</span><span class="v" id="ws-calc-shares">—</span></div>' +
      '<div class="ws-calc-result-row"><span>Your ownership</span><span class="v" id="ws-calc-pct">—</span></div>' +
      '</div>' +
      '<div class="ws-calc-note">Illustrative price ($' + fmtNum(price) + ') and shares outstanding for teaching purposes — check today’s real numbers as part of the activity.</div>';

    var input = el.querySelector('#ws-calc-amount');
    var sharesEl = el.querySelector('#ws-calc-shares');
    var pctEl = el.querySelector('#ws-calc-pct');

    function formatPercent(pct) {
      if (pct <= 0) return '0%';
      if (pct >= 0.01) return pct.toFixed(4) + '%';
      // very small ownership % — show enough decimals to be non-zero,
      // matching the "0.000003%" style the activity text uses
      var decimals = Math.min(12, Math.max(6, Math.ceil(-Math.log10(pct)) + 2));
      return pct.toFixed(decimals) + '%';
    }

    function recompute() {
      var amount = parseNum(input.value);
      var shares = amount / price;
      var pct = (shares / sharesOut) * 100;
      sharesEl.textContent = shares.toLocaleString('en-US', { maximumFractionDigits: 4 });
      pctEl.textContent = formatPercent(pct);
    }

    input.addEventListener('input', recompute);
    recompute();
  }

  // ─── Signals (right-rail) ──────────────────
  function buildSignalRow(s) {
    var historical = isHistorical(s.message);
    var row = '<div class="ws-signal-row' + (historical ? ' ws-signal-historical' : '') + '">';
    row += '<span class="ws-signal-event-badge event-' + (s.event || 'scan') + '">' + (s.event ? s.event.slice(0, 4) : 'scan') + '</span>';
    if (historical) {
      row += '<span class="ws-signal-hist-badge" title="Backtest trade — historical data">hist</span>';
    }
    row += '<span class="ws-signal-sym">' + (s.symbol || '--') + '</span>';
    row += '<span class="ws-signal-desc">' + escapeHtml(s.summary || '') + '</span>';
    row += '</div>';
    return row;
  }

  function pollSignals() {
    fetch('/api/signals/live')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var rows = data.signals || [];
        if (!signalsFeed) return;
        if (rows.length === 0) {
          signalsFeed.innerHTML = '<div class="ws-empty muted">waiting for signals...</div>';
          return;
        }
        var html = '';
        rows.slice(0, 15).forEach(function (s) {
          html += buildSignalRow(s);
        });
        signalsFeed.innerHTML = html;
        lsSet('ws_signal_count', String(rows.length));
        lsSet('ws_last_signal_time', new Date().toISOString());
      })
      .catch(function () {});
  }

  // ─── Notes (right-rail only) ────────────────
  function loadNotes() {
    try {
      var saved = LS.getItem('ws_notes');
      if (saved && notesTA) notesTA.value = saved;
    } catch (e) {}
  }

  function saveNotes() {
    try {
      if (notesTA) {
        LS.setItem('ws_notes', notesTA.value);
        LS.setItem('ws_last_note_time', new Date().toISOString());
      }
    } catch (e) {}
  }

  if (notesTA) {
    notesTA.addEventListener('input', saveNotes);
    loadNotes();
  }

  // ─── Terminal ───────────────────────────────
  function appendTerminal(text, cls) {
    if (!termOutput) return;
    var line = document.createElement('div');
    line.className = 'ws-term-line' + (cls ? ' ' + cls : '');
    line.textContent = text;
    termOutput.appendChild(line);
    termOutput.scrollTop = termOutput.scrollHeight;
  }

  function terminalSubmit() {
    if (!termInput) return;
    var cmd = termInput.value.trim();
    termInput.value = '';
    if (!cmd) return;

    appendTerminal('> ' + cmd, 'ws-term-accent');

    if (cmd === 'help') {
      appendTerminal('Available commands:', 'ws-term-accent');
      appendTerminal('  help          — show this message', '');
      appendTerminal('  dashboard     — switch to dashboard view', '');
      appendTerminal('  lessons       — open lesson browser', '');
      appendTerminal('  maps          — open concept map', '');
      appendTerminal('  signals       — refresh signals feed', '');
      appendTerminal('  clear         — clear terminal', '');
      appendTerminal('Any other input is sent to the Delta AI assistant.', 'ws-term-muted');
      return;
    }

    if (cmd === 'clear') {
      termOutput.innerHTML = '<div class="ws-term-line ws-term-muted">Delta One Copilot — type \'help\' for commands</div>';
      return;
    }

    if (cmd === 'dashboard') { showView('dashboard'); return; }
    if (cmd === 'lessons') { showView('lessons'); return; }
    if (cmd === 'maps') { showView('maps'); return; }
    if (cmd === 'signals') { pollSignals(); appendTerminal('Signals refreshed.', 'ws-term-muted'); return; }

    var typingLine = document.createElement('div');
    typingLine.className = 'ws-term-line ws-term-muted';
    typingLine.textContent = 'Delta is thinking...';
    termOutput.appendChild(typingLine);
    termOutput.scrollTop = termOutput.scrollHeight;

    function removeTyping() {
      if (typingLine.parentNode) typingLine.parentNode.removeChild(typingLine);
    }

    fetch('/api/ai/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: cmd })
    })
      .then(function (r) {
        if (r.status === 429) {
          return r.json().then(function (data) {
            removeTyping();
            var msg = 'Daily limit reached. You used ' + (data.usage || '') + ' of your queries. Upgrade to Pro for unlimited access.';
            appendTerminal(msg, 'ws-term-muted');
            return null;
          });
        }
        if (!r.ok) throw new Error('API error');
        return r.json();
      })
      .then(function (res) {
        if (!res) return;
        removeTyping();
        appendTerminal(res.response || '');
      })
      .catch(function () {
        removeTyping();
        appendTerminal('The AI assistant is temporarily unavailable. Please try again in a moment.', 'ws-term-muted');
      });
  }

  if (termInput) {
    termInput.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        terminalSubmit();
      }
    });
  }

  // ─── Focus param ───────────────────────────
  function handleFocusParam() {
    var params = new URLSearchParams(window.location.search);
    var focus = params.get('focus');
    if (focus) {
      var validViews = ['dashboard', 'lessons', 'maps'];
      if (validViews.indexOf(focus) !== -1) {
        showView(focus);
        return true;
      }
    }
    return false;
  }

  // ─── Expose globals for inline onclick ─────
  window.wsGoToLesson = window.wsOpenLesson;

  // ─── Boot ───────────────────────────────────
  if (!handleFocusParam()) {
    renderDashboard();
  }
  pollSignals();
  setInterval(pollSignals, 15000);

})();
