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
        + '<span class="ws-progress-bar-mini"><span style="width:' + pct + '%"></span></span>'
        + '<span class="ws-progress-count">' + done + '/' + total + '</span>'
        + '</div>';
    });

    var totalPct = totalLessons > 0 ? (totalDone / totalLessons * 100) : 0;
    html += '<div class="ws-progress-sep"></div>'
      + '<div class="ws-progress-row ws-progress-total">'
      + '<span class="ws-progress-name">total</span>'
      + '<span class="ws-progress-bar-mini"><span style="width:' + totalPct + '%"></span></span>'
      + '<span class="ws-progress-count">' + totalDone + '/' + totalLessons + '</span>'
      + '</div>';

    pb.innerHTML = html;

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
          html += '<span class="ws-lesson-row-meta">' + (l.estimated_minutes || '?') + ' min' + (completed ? ' &check;' : '') + '</span>';
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
        var html = '<button class="ws-back-btn" onclick="wsOpenModule(\'' + moduleSlug + '\')">&larr; back</button>';
        html += '<div class="ws-lesson-header"><h1>' + (l.title || '') + '</h1>';
        html += '<div class="ws-lesson-estimate">' + (l.estimated_minutes || '?') + ' min read</div></div>';
        html += '<div class="ws-lesson-body">' + (l.content_html || l.content || '<p>No content yet.</p>') + '</div>';
        html += '<div class="ws-lesson-footer">';
        html += '<div class="ws-lesson-nav">';
        if (l.prev_lesson_slug) html += '<button class="ws-lesson-nav-btn" onclick="wsOpenLesson(\'' + moduleSlug + '\',\'' + l.prev_lesson_slug + '\')">&larr; ' + (l.prev_lesson_title || 'Previous') + '</button>';
        if (l.next_lesson_slug) html += '<button class="ws-lesson-nav-btn" onclick="wsOpenLesson(\'' + moduleSlug + '\',\'' + l.next_lesson_slug + '\')">' + (l.next_lesson_title || 'Next') + ' &rarr;</button>';
        html += '</div>';
        if (!l.is_completed) {
          html += '<button class="ws-btn-complete" id="ws-btn-mark-complete">mark complete</button>';
        } else {
          html += '<button class="ws-btn-complete" disabled>&checkmark; completed</button>';
        }
        html += '</div></div>';
        content.innerHTML = html;

        // track focus
        setFocus('lesson', moduleSlug + '/' + lessonSlug, l.title || lessonSlug);
        lsSet('ws_last_lesson_title', l.title || lessonSlug);
        lsSet('ws_last_lesson_time', new Date().toISOString());

        var btn = document.getElementById('ws-btn-mark-complete');
        if (btn) {
          btn.addEventListener('click', function () {
            btn.disabled = true;
            btn.textContent = 'completing...';
            fetch('/workspace/api/lessons/' + encodeURIComponent(moduleSlug) + '/' + encodeURIComponent(lessonSlug) + '/complete', { method: 'POST' })
              .then(function (r) { return r.json(); })
              .then(function (res) {
                if (res.ok) {
                  btn.textContent = '\u2713 completed';
                } else {
                  btn.disabled = false;
                  btn.textContent = 'mark complete';
                }
              })
              .catch(function () {
                btn.disabled = false;
                btn.textContent = 'mark complete';
              });
          });
        }
      })
      .catch(function () {
        content.innerHTML = '<div class="ws-lesson-body"><p class="muted">Lesson not found.</p></div>';
      });
  };

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
