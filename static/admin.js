(function () {
  'use strict';

  // ─── State ──────────────────────────────────
  var currentView = null;
  var currentUserId = null;
  var botPollInterval = null;
  var quickStatInterval = null;

  // ─── DOM refs ───────────────────────────────
  var content = document.getElementById('ws-content');
  var termOutput = document.getElementById('ws-terminal-output');
  var termInput = document.getElementById('ws-terminal-input');

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

  function tierBadge(tier) {
    var cls = tier === 'pro' ? 'admin-tier-pro' : tier === 'admin' ? 'admin-tier-admin' : 'admin-tier-core';
    return '<span class="admin-tier-badge ' + cls + '">' + escapeHtml(tier) + '</span>';
  }

  function fetchJSON(url, cb) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url);
    xhr.onload = function () {
      if (xhr.status === 200) cb(null, JSON.parse(xhr.responseText));
      else cb('fetch error ' + xhr.status);
    };
    xhr.onerror = function () { cb('network error'); };
    xhr.send();
  }

  // ─── Nav ────────────────────────────────────
  document.querySelectorAll('.ws-nav-item').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var view = btn.getAttribute('data-view');
      if (view) showView(view);
    });
  });

  function showView(view) {
    currentView = view;
    document.querySelectorAll('.ws-nav-item').forEach(function (b) {
      b.classList.toggle('active', b.getAttribute('data-view') === view);
    });

    if (view === 'usage') renderUsage();
    else if (view === 'users') renderUsers();
    else if (view === 'system') renderSystem();
    else if (view === 'bot') renderBotHealth();
  }

  // ─── Todo List ────────────────────────────────
  var TODO_KEY = 'admin_todos';

  function loadTodos() {
    var list = document.getElementById('admin-todo-list');
    if (!list) return;
    var todos;
    try { todos = JSON.parse(localStorage.getItem(TODO_KEY)) || []; } catch (e) { todos = []; }
    list.innerHTML = '';
    todos.forEach(function (t, i) {
      var item = document.createElement('div');
      item.className = 'admin-todo-item';

      var check = document.createElement('span');
      check.className = 'admin-todo-check' + (t.done ? ' done' : '');
      check.addEventListener('click', function (e) { e.stopPropagation(); toggleTodo(i); });

      var text = document.createElement('span');
      text.className = 'admin-todo-text' + (t.done ? ' done' : '');
      text.textContent = t.text;
      text.addEventListener('click', function () { toggleTodo(i); });

      var del = document.createElement('span');
      del.className = 'admin-todo-del';
      del.textContent = '×';
      del.addEventListener('click', function (e) { e.stopPropagation(); deleteTodo(i); });

      item.appendChild(check);
      item.appendChild(text);
      item.appendChild(del);
      list.appendChild(item);
    });
  }

  function saveTodos(todos) {
    try { localStorage.setItem(TODO_KEY, JSON.stringify(todos)); } catch (e) {}
    loadTodos();
  }

  function addTodo(text) {
    text = text.trim();
    if (!text) return;
    var todos;
    try { todos = JSON.parse(localStorage.getItem(TODO_KEY)) || []; } catch (e) { todos = []; }
    todos.push({ text: text, done: false, created: Date.now() });
    saveTodos(todos);
  }

  function toggleTodo(idx) {
    var todos;
    try { todos = JSON.parse(localStorage.getItem(TODO_KEY)) || []; } catch (e) { todos = []; }
    if (todos[idx]) { todos[idx].done = !todos[idx].done; }
    saveTodos(todos);
  }

  function deleteTodo(idx) {
    var todos;
    try { todos = JSON.parse(localStorage.getItem(TODO_KEY)) || []; } catch (e) { todos = []; }
    todos.splice(idx, 1);
    saveTodos(todos);
  }

  var todoInput = document.getElementById('admin-todo-input');

  if (todoInput) {
    todoInput.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        var text = todoInput.value.trim();
        if (text) {
          addTodo(text);
          todoInput.value = '';
        }
      }
    });
  }

  loadTodos();

  // ─── Usage Dashboard ─────────────────────────
  function renderUsage() {
    currentUserId = null;
    content.innerHTML = '<div class="admin-heading">Usage Dashboard</div><div class="admin-subheading">Loading...</div>';

    fetchJSON('/admin/api/usage', function (err, data) {
      if (err) {
        content.innerHTML = '<div class="admin-heading">Usage Dashboard</div><div class="ws-term-line ws-term-muted">Failed to load usage data.</div>';
        return;
      }

      var html = '<div class="admin-heading">Usage Dashboard</div>'
        + '<div class="admin-stat-row">'
        + '<div class="admin-stat-box"><div class="admin-stat-box-label">Queries Today</div><div class="admin-stat-box-value">' + data.total_queries + '</div></div>'
        + '<div class="admin-stat-box"><div class="admin-stat-box-label">Tokens Used</div><div class="admin-stat-box-value">' + data.total_tokens + '</div></div>'
        + '</div>';

      if (data.top_users && data.top_users.length) {
        html += '<div class="admin-subheading">Top Users Today</div>'
          + '<table class="admin-table"><thead><tr><th>Email</th><th>Tier</th><th>Queries</th><th>Tokens</th></tr></thead><tbody>';
        data.top_users.forEach(function (u) {
          html += '<tr><td>' + escapeHtml(u.email) + '</td><td>' + tierBadge(u.tier) + '</td><td>' + u.queries + '</td><td class="muted">' + u.tokens + '</td></tr>';
        });
        html += '</tbody></table>';
      }

      if (data.daily_trend && data.daily_trend.length) {
        html += '<div class="admin-subheading">Daily Trend (7 days)</div>'
          + '<table class="admin-trend-table"><thead><tr><th>Day</th><th>Queries</th></tr></thead><tbody>';
        data.daily_trend.forEach(function (d) {
          html += '<tr><td>' + escapeHtml(d.day) + '</td><td>' + d.count + '</td></tr>';
        });
        html += '</tbody></table>';
      }

      content.innerHTML = html;
    });
  }

  // ─── User Management ─────────────────────────
  function renderUsers(searchTerm) {
    currentUserId = null;
    var q = searchTerm || '';
    content.innerHTML = '<div class="admin-heading">User Management</div>'
      + '<input type="text" class="admin-search" id="admin-user-search" placeholder="search by email..." value="' + escapeHtml(q) + '">'
      + '<div id="admin-user-list"><div class="admin-subheading">Loading...</div></div>';

    var searchEl = document.getElementById('admin-user-search');
    searchEl.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') renderUsers(searchEl.value.trim());
    });

    var url = '/admin/api/users';
    if (q) url += '?q=' + encodeURIComponent(q);

    fetchJSON(url, function (err, data) {
      if (err) {
        document.getElementById('admin-user-list').innerHTML = '<div class="ws-term-line ws-term-muted">Failed to load users.</div>';
        return;
      }

      if (!data.users || !data.users.length) {
        document.getElementById('admin-user-list').innerHTML = '<div class="ws-term-line ws-term-muted">No users found.</div>';
        return;
      }

      var html = '<table class="admin-table"><thead><tr><th>Email</th><th>Tier</th><th>Last Login</th><th>AI Today</th><th>Actions</th></tr></thead><tbody>';
      data.users.forEach(function (u) {
        html += '<tr style="cursor:pointer" data-user-id="' + escapeHtml(u.id) + '">'
          + '<td>' + escapeHtml(u.email) + '</td>'
          + '<td>' + tierBadge(u.tier) + '</td>'
          + '<td class="muted">' + (u.last_login ? relTime(u.last_login) : 'never') + '</td>'
          + '<td>' + u.ai_queries_today + '</td>'
          + '<td><span class="admin-tier-btn" data-tier-action="' + escapeHtml(u.id) + '">change tier</span></td>'
          + '</tr>';
      });
      html += '</tbody></table>';
      document.getElementById('admin-user-list').innerHTML = html;

      document.querySelectorAll('#admin-user-list tr[data-user-id]').forEach(function (row) {
        row.addEventListener('click', function (e) {
          if (e.target.getAttribute('data-tier-action')) return;
          renderUserDetail(row.getAttribute('data-user-id'));
        });
      });

      document.querySelectorAll('[data-tier-action]').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
          e.stopPropagation();
          var uid = btn.getAttribute('data-tier-action');
          var tiers = ['core', 'pro', 'admin'];
          var current = btn.closest('tr').querySelector('.admin-tier-badge').textContent.trim();
          var nextIdx = (tiers.indexOf(current) + 1) % tiers.length;
          var next = tiers[nextIdx];
          changeTier(uid, next, btn);
        });
      });
    });
  }

  function renderUserDetail(userId) {
    content.innerHTML = '<div class="admin-heading">User Detail</div><div class="admin-subheading">Loading...</div>';

    fetchJSON('/admin/api/users/' + userId, function (err, data) {
      if (err) {
        content.innerHTML = '<div class="admin-heading">User Detail</div><div class="ws-term-line ws-term-muted">Failed to load user.</div>';
        return;
      }

      var u = data.user;
      var html = '<button class="admin-back-btn" id="admin-back-to-users">← back to users</button>'
        + '<div class="admin-user-detail">'
        + '<h3>' + escapeHtml(u.email) + '</h3>'
        + '<div class="admin-stat-row">'
        + '<div class="admin-stat-box"><div class="admin-stat-box-label">Tier</div><div class="admin-stat-box-value" style="font-size:14px">' + tierBadge(u.tier) + '</div></div>'
        + '<div class="admin-stat-box"><div class="admin-stat-box-label">Active</div><div class="admin-stat-box-value" style="font-size:14px">' + (u.is_active ? 'yes' : 'no') + '</div></div>'
        + '<div class="admin-stat-box"><div class="admin-stat-box-label">Pro</div><div class="admin-stat-box-value" style="font-size:14px">' + (u.is_pro ? 'yes' : 'no') + '</div></div>'
        + '<div class="admin-stat-box"><div class="admin-stat-box-label">Admin</div><div class="admin-stat-box-value" style="font-size:14px">' + (u.is_admin ? 'yes' : 'no') + '</div></div>'
        + '</div>'
        + '<div class="admin-subheading">Last Login: ' + (u.last_login || 'never') + '</div>'
        + '<div class="admin-subheading">Created: ' + (u.created_at || 'unknown') + '</div>'
        + '</div>';

      if (data.ai_interactions && data.ai_interactions.length) {
        html += '<div class="admin-subheading">Recent AI Interactions (last 50)</div>'
          + '<table class="admin-table"><thead><tr><th>Message</th><th>Response</th><th>Tokens</th><th>Model</th><th>Time</th></tr></thead><tbody>';
        data.ai_interactions.forEach(function (i) {
          html += '<tr>'
            + '<td class="muted">' + escapeHtml(i.message) + '</td>'
            + '<td class="muted">' + escapeHtml(i.response) + '</td>'
            + '<td>' + i.tokens_used + '</td>'
            + '<td class="muted">' + (i.model_name || '—') + '</td>'
            + '<td class="muted">' + relTime(i.created_at) + '</td>'
            + '</tr>';
        });
        html += '</tbody></table>';
      } else {
        html += '<div class="admin-subheading">No AI interactions</div>';
      }

      content.innerHTML = html;
      document.getElementById('admin-back-to-users').addEventListener('click', function () { renderUsers(); });
    });
  }

  function changeTier(userId, newTier, btn) {
    btn.textContent = '...';
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/admin/api/users/' + userId + '/tier');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function () {
      if (xhr.status === 200) {
        renderUsers();
      } else {
        btn.textContent = 'error';
      }
    };
    xhr.onerror = function () { btn.textContent = 'error'; };
    xhr.send(JSON.stringify({ tier: newTier }));
  }

  // ─── System Overview ─────────────────────────
  function renderSystem() {
    content.innerHTML = '<div class="admin-heading">System Overview</div><div class="admin-subheading">Loading...</div>';

    fetchJSON('/admin/api/system', function (err, data) {
      if (err) {
        content.innerHTML = '<div class="admin-heading">System Overview</div><div class="ws-term-line ws-term-muted">Failed to load system data.</div>';
        return;
      }

      var html = '<div class="admin-heading">System Overview</div>'
        + '<div class="admin-stat-row">'
        + '<div class="admin-stat-box"><div class="admin-stat-box-label">Total Users</div><div class="admin-stat-box-value">' + data.total_users + '</div></div>'
        + '<div class="admin-stat-box"><div class="admin-stat-box-label">Users Today</div><div class="admin-stat-box-value">' + data.users_today + '</div></div>'
        + '<div class="admin-stat-box"><div class="admin-stat-box-label">AI Interactions</div><div class="admin-stat-box-value">' + data.total_ai_interactions + '</div></div>'
        + '<div class="admin-stat-box"><div class="admin-stat-box-label">AI Today</div><div class="admin-stat-box-value">' + data.ai_today + '</div></div>'
        + '</div>'
        + '<div class="admin-stat-row">'
        + '<div class="admin-stat-box"><div class="admin-stat-box-label">Bot Events (total)</div><div class="admin-stat-box-value">' + data.total_bot_events + '</div></div>'
        + '<div class="admin-stat-box"><div class="admin-stat-box-label">Events Today</div><div class="admin-stat-box-value">' + data.events_today + '</div></div>'
        + '<div class="admin-stat-box"><div class="admin-stat-box-label">Waitlist</div><div class="admin-stat-box-value">' + data.total_waitlist + '</div></div>'
        + '</div>';

      content.innerHTML = html;
    });
  }

  // ─── Bot Health ──────────────────────────────
  function renderBotHealth() {
    content.innerHTML = '<div class="admin-heading">Bot Health</div><div class="admin-subheading">Loading live data...</div>';

    fetchBotHealth();

    if (botPollInterval) clearInterval(botPollInterval);
    botPollInterval = setInterval(fetchBotHealth, 15000);
  }

  function fetchBotHealth() {
    fetchJSON('/admin/api/bot/health', function (err, data) {
      if (err) {
        content.innerHTML = '<div class="admin-heading">Bot Health</div><div class="ws-term-line ws-term-muted">Failed to load bot health.</div>';
        return;
      }

      var dotClass = data.status === 'healthy' ? 'healthy' : data.status === 'warning' ? 'warning' : 'critical';

      var html = '<div class="admin-heading">Bot Health</div>'
        + '<div class="admin-health-grid">'
        + '<div class="admin-health-card">'
        + '<div class="admin-health-card-label">Status</div>'
        + '<div class="admin-health-card-value"><span class="admin-health-dot ' + dotClass + '"></span>' + escapeHtml(data.status) + ' — ' + escapeHtml(data.status_note) + '</div>'
        + '</div>'
        + '<div class="admin-health-card">'
        + '<div class="admin-health-card-label">Market</div>'
        + '<div class="admin-health-card-value">' + escapeHtml(data.market_state) + '</div>'
        + '</div>'
        + '<div class="admin-health-card">'
        + '<div class="admin-health-card-label">Equity</div>'
        + '<div class="admin-health-card-value">' + (data.equity ? '$' + data.equity.toLocaleString() : '—') + '</div>'
        + '</div>'
        + '<div class="admin-health-card">'
        + '<div class="admin-health-card-label">Active Positions</div>'
        + '<div class="admin-health-card-value">' + data.active_positions + '</div>'
        + '</div>'
        + '<div class="admin-health-card">'
        + '<div class="admin-health-card-label">Events Today</div>'
        + '<div class="admin-health-card-value">' + data.events_today + '</div>'
        + '</div>'
        + '<div class="admin-health-card">'
        + '<div class="admin-health-card-label">Errors Today</div>'
        + '<div class="admin-health-card-value">' + data.errors_today + '</div>'
        + '</div>'
        + '<div class="admin-health-card">'
        + '<div class="admin-health-card-label">Last Event</div>'
        + '<div class="admin-health-card-value" style="font-size:11px">' + (data.last_event_time ? relTime(data.last_event_time) : '—') + '</div>'
        + '</div>'
        + '<div class="admin-health-card">'
        + '<div class="admin-health-card-label">Last Scan</div>'
        + '<div class="admin-health-card-value" style="font-size:11px">' + (data.last_scan_time ? relTime(data.last_scan_time) : '—') + '</div>'
        + '</div>'
        + '</div>';

      // Per-symbol
      html += '<div class="admin-sym-grid">';
      for (var sym in data.symbols) {
        var s = data.symbols[sym];
        var symDot = s.status === 'scanning' || s.status === 'flat' ? 'healthy' : s.status === 'error' ? 'critical' : 'warning';
        html += '<div class="admin-sym-card">'
          + '<div class="admin-sym-card-label">' + sym + ' <span class="admin-health-dot ' + symDot + '"></span></div>'
          + '<div class="admin-sym-card-status">' + escapeHtml(s.status) + '</div>'
          + '<div class="admin-sym-card-detail">Last: ' + (s.last_event || '—') + ' ' + (s.last_time ? relTime(s.last_time) : '') + '</div>';
        if (s.position) {
          html += '<div class="admin-sym-card-detail">' + escapeHtml(s.position.side) + ' @ $' + s.position.price + ' qty:' + s.position.qty + '</div>';
        }
        html += '</div>';
      }
      html += '</div>';

      // Recent events
      if (data.recent_events && data.recent_events.length) {
        html += '<div class="admin-subheading">Recent Events (last 20)</div>'
          + '<table class="admin-table"><thead><tr><th>Time</th><th>Event</th><th>Symbol</th><th>Side</th><th>Price</th><th>Qty</th><th>Message</th></tr></thead><tbody>';
        data.recent_events.forEach(function (e) {
          html += '<tr>'
            + '<td class="muted">' + relTime(e.timestamp) + '</td>'
            + '<td>' + escapeHtml(e.event) + '</td>'
            + '<td>' + escapeHtml(e.symbol || '—') + '</td>'
            + '<td class="muted">' + escapeHtml(e.side || '—') + '</td>'
            + '<td class="muted">' + (e.price ? '$' + e.price.toFixed(2) : '—') + '</td>'
            + '<td class="muted">' + (e.qty || '—') + '</td>'
            + '<td class="muted">' + escapeHtml((e.message || '').substring(0, 60)) + '</td>'
            + '</tr>';
        });
        html += '</tbody></table>';
      }

      // Log tail
      if (data.log_tail && data.log_tail.length) {
        html += '<div class="admin-subheading">Log Tail (last 50 lines)</div>'
          + '<div class="admin-log-viewer">';
        data.log_tail.forEach(function (line) {
          var levelCls = '';
          if (line.indexOf('[ERROR]') !== -1 || line.indexOf('[CRITICAL]') !== -1) levelCls = 'level-ERROR';
          else if (line.indexOf('[WARNING]') !== -1) levelCls = 'level-WARNING';
          else if (line.indexOf('[INFO]') !== -1) levelCls = 'level-INFO';
          html += '<div class="admin-log-line' + (levelCls ? ' ' + levelCls : '') + '">' + escapeHtml(line) + '</div>';
        });
        html += '</div>';
      }

      content.innerHTML = html;
    });
  }

  // ─── Quick Stats (right panel polling) ──────
  function fetchQuickStats() {
    fetchJSON('/admin/api/system', function (err, data) {
      if (err) return;
      setText('qstat-users', data.total_users);
      setText('qstat-ai', data.ai_today);
      setText('qstat-waitlist', data.total_waitlist);
      setText('qstat-events', data.events_today);
    });

    fetchJSON('/admin/api/bot/health', function (err, data) {
      if (err) return;
      var dot = document.getElementById('qstat-bot-dot');
      var text = document.getElementById('qstat-bot-text');
      if (dot && text) {
        dot.className = 'admin-health-dot ' + (data.status === 'healthy' ? 'healthy' : data.status === 'warning' ? 'warning' : 'critical');
        text.textContent = data.status + ' — ' + data.status_note;
      }
    });
  }

  function setText(id, val) {
    var el = document.getElementById(id);
    if (el) el.textContent = val != null ? val : '—';
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
            var msg = 'Daily limit reached. You used ' + (data.usage || '') + ' of your queries.';
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

  // ─── Init ────────────────────────────────────
  quickStatInterval = setInterval(fetchQuickStats, 15000);
  fetchQuickStats();
})();
