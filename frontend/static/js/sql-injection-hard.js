(function () {
  const dataEl = document.getElementById('workspace-data');
  if (!dataEl) return;

  const data = JSON.parse(dataEl.textContent);
  const form = data.login_form || {};
  const signs = data.signs || [];
  const tasks = data.tasks || [];
  const decisions = data.decisions || [];
  const inspector = data.request_inspector || {};
  const acceptedPayloads = (form.accepted_payloads || []).map(normalizePayload);

  const flaggedSigns = new Set();
  const completedTasks = new Set();
  const completedObjectives = new Set();
  const actionsLog = [];
  const mistakes = [];
  const goodDecisions = [];
  const recommendations = [
    'Replace string-concatenated SQL with parameterized queries.',
    'Validate and allow-list input instead of blacklisting characters.',
    'Never expose raw database errors to end users.',
  ];

  let missionStartedAt = Date.now();
  let decisionMade = false;
  let flagMode = false;
  let errorTriggered = false;
  let bypassAchieved = false;
  let inspectorOpened = false;
  let finalScore = 0;

  const app = document.getElementById('sqli-hard-app');
  const progressFill = document.getElementById('mission-progress-fill');
  const progressPercent = document.getElementById('progress-percent');
  const progressCount = document.getElementById('progress-count');
  const flagsMeta = document.getElementById('flags-meta');
  const objectiveList = document.getElementById('objective-list');
  const taskLog = document.getElementById('task-log');
  const eventFeed = document.getElementById('event-feed');
  const timerEl = document.getElementById('mission-timer');
  const submitBtn = document.getElementById('submit-report-btn');

  const loginStage = document.getElementById('login-stage');
  const adminDashboard = document.getElementById('admin-dashboard');
  const loginForm = document.getElementById('login-form');
  const usernameInput = document.getElementById('username-input');
  const passwordInput = document.getElementById('password-input');
  const sqlErrorEl = document.getElementById('sql-error');
  const loginErrorEl = document.getElementById('login-error');

  const signMap = Object.fromEntries(signs.map((s) => [s.id, s]));

  function normalizePayload(value) {
    return String(value || '').trim().toLowerCase().replace(/\s+/g, ' ');
  }

  function isAcceptedPayload(value) {
    const normalized = normalizePayload(value);
    if (acceptedPayloads.includes(normalized)) return true;
    return (
      normalized.includes("'") &&
      normalized.includes('or') &&
      (normalized.includes("'1'='1") || normalized.includes('1=1'))
    );
  }

  function triggersSqlError(value) {
    const trimmed = String(value || '').trim();
    return trimmed === "'" || trimmed === "''" || /^'+$/.test(trimmed);
  }

  function logAction(action, detail) {
    actionsLog.push({ action, detail, at: new Date().toISOString() });
  }

  function pushEvent(message, tone) {
    const item = document.createElement('li');
    item.textContent = message;
    if (tone) item.classList.add(`event-${tone}`);
    eventFeed.prepend(item);
  }

  function completeTask(taskId) {
    if (completedTasks.has(taskId)) return;
    const task = tasks.find((t) => t.id === taskId);
    if (!task) return;

    completedTasks.add(taskId);
    if (typeof task.objective_index === 'number') {
      completedObjectives.add(task.objective_index);
      const obj = objectiveList.querySelector(`[data-objective-index="${task.objective_index}"]`);
      if (obj) {
        obj.classList.add('is-done');
        obj.querySelector('.obj-icon').textContent = '✓';
      }
    }

    const li = document.createElement('li');
    li.className = 'is-done';
    li.textContent = `✓ ${task.label}`;
    if (taskLog.querySelector('.text-slate-500')) {
      taskLog.innerHTML = '';
    }
    taskLog.appendChild(li);

    logAction('task_complete', task.label);
    pushEvent(`Task complete: ${task.label}`, 'good');
    updateProgress();
    maybeEnableSubmit();
  }

  function updateProgress() {
    const total = tasks.length || 1;
    const done = completedTasks.size;
    const pct = Math.round((done / total) * 100);
    progressFill.style.width = `${pct}%`;
    progressPercent.textContent = `${pct}%`;
    progressCount.textContent = `${done} / ${total} tasks`;
    flagsMeta.textContent = `${flaggedSigns.size} / ${signs.length} signs flagged`;
  }

  function maybeEnableSubmit() {
    const requiredDone = ['flag_three', 'trigger_error', 'bypass_login'].every((id) =>
      completedTasks.has(id)
    );
    submitBtn.disabled = !requiredDone || decisionMade;
  }

  function checkFlagTask() {
    const task = tasks.find((t) => t.action === 'flag_signs');
    if (!task) return;
    const required = task.required || 3;
    if (flaggedSigns.size >= required) {
      completeTask(task.id);
    }
  }

  function renderForm() {
    document.getElementById('url-bar-text').textContent = form.url_bar || '';
    document.getElementById('form-title').textContent = form.app_name || 'Admin Login';
    document.getElementById('legacy-notice').textContent = form.legacy_notice || '';
    document.getElementById('username-label').textContent = form.username_label || 'Username';
    document.getElementById('password-label').textContent = form.password_label || 'Password';
    document.getElementById('submit-btn').textContent = form.submit_label || 'Sign in';
    document.getElementById('form-footer').textContent = form.footer_note || '';

    if (sqlErrorEl) {
      sqlErrorEl.textContent = form.error_message || 'SQL syntax error near unexpected input.';
    }

    document.querySelectorAll('[data-sign]').forEach((node) => {
      node.addEventListener('click', (event) => handleSignInteraction(event, node));
    });

    completeTask('review_form');
    logAction('review_form', form.url_bar);
    pushEvent('Reviewing legacy admin login endpoint.', 'info');
  }

  function renderDashboard() {
    const dash = form.admin_dashboard || {};
    document.getElementById('dash-subtitle').textContent = dash.subtitle || '';
    document.getElementById('dash-title').textContent = dash.title || 'Admin Dashboard';
    document.getElementById('dash-welcome').textContent = dash.welcome || '';

    const statsEl = document.getElementById('dash-stats');
    statsEl.innerHTML = '';
    (dash.stats || []).forEach((stat) => {
      const article = document.createElement('article');
      article.className = 'sqli-hard-dashboard__stat';
      article.innerHTML = `
        <span class="sqli-hard-dashboard__stat-label">${escapeHtml(stat.label || '')}</span>
        <strong class="sqli-hard-dashboard__stat-value">${escapeHtml(stat.value || '')}</strong>
      `;
      statsEl.appendChild(article);
    });
  }

  function handleSignInteraction(event, node) {
    const signId = node.dataset.sign;
    if (!signId) return;

    if (signId === 'sql_error_leak' && !errorTriggered) {
      if (flagMode) {
        event.preventDefault();
        event.stopPropagation();
        pushEvent('Trigger a SQL error first — try submitting a single quote in the username field.', 'warn');
      }
      return;
    }

    if (flagMode) {
      event.preventDefault();
      event.stopPropagation();
      flagSign(signId, node);
    }
  }

  function showSqlError() {
    if (errorTriggered) return;
    errorTriggered = true;

    if (sqlErrorEl) {
      sqlErrorEl.hidden = false;
      sqlErrorEl.classList.add('is-revealed');
    }

    logAction('trigger_sql_error', usernameInput?.value || "'");
    pushEvent('SQL syntax error returned — database query details leaked.', 'bad');
    completeTask('trigger_error');
  }

  function handleBypass() {
    bypassAchieved = true;
    if (loginStage) loginStage.hidden = true;
    if (adminDashboard) adminDashboard.hidden = false;
    renderDashboard();

    logAction('bypass_login', usernameInput?.value || '');
    pushEvent('Authentication bypassed with SQL injection payload.', 'bad');
    completeTask('bypass_login');
    maybeEnableSubmit();

    openPhishModal('consequence-modal');
  }

  function flagSign(signId, node) {
    if (signId === 'sql_error_leak' && !errorTriggered) {
      pushEvent('Submit a single quote first to reveal the SQL error message.', 'warn');
      return;
    }

    if (flaggedSigns.has(signId)) {
      showFlagModal(signMap[signId]?.label || 'Sign already flagged', signMap[signId]?.hint || '');
      return;
    }

    flaggedSigns.add(signId);
    node.classList.add('is-flagged');
    logAction('flag_sign', signId);
    pushEvent(`Flagged: ${signMap[signId]?.label || signId}`, 'good');
    checkFlagTask();
    updateProgress();
    showFlagModal(signMap[signId]?.label || 'Sign flagged', signMap[signId]?.hint || '');
    flagMode = false;
    app?.classList.remove('is-flag-mode');
    document.getElementById('flag-mode-btn')?.classList.remove('is-active');
  }

  function showFlagModal(title, body) {
    document.getElementById('flag-modal-title').textContent = title;
    document.getElementById('flag-modal-body').textContent = body;
    openPhishModal('flag-modal');
  }

  function openPhishModal(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.hidden = false;
    el.classList.remove('is-closing');
    el.classList.add('is-opening');
    document.body.classList.add('phish-modal-open');
    requestAnimationFrame(() => {
      el.classList.add('is-open');
      el.classList.remove('is-opening');
    });
  }

  function closePhishModal(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.add('is-closing');
    el.classList.remove('is-open');
    setTimeout(() => {
      el.hidden = true;
      el.classList.remove('is-closing');
      document.body.classList.remove('phish-modal-open');
    }, 200);
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function formatInspector() {
    const lines = [];
    if (inspector.endpoint) lines.push(`Endpoint: ${inspector.endpoint}`);
    if (inspector.method) lines.push(`Method: ${inspector.method}`);
    if (inspector.content_type) lines.push(`Content-Type: ${inspector.content_type}`);
    if (inspector.backend_note) lines.push(`\nBackend note:\n${inspector.backend_note}`);
    if (inspector.headers?.length) {
      lines.push('\nHeaders:');
      inspector.headers.forEach((header) => lines.push(`  ${header}`));
    }
    if (inspector.sample_body) lines.push(`\nSample body:\n  ${inspector.sample_body}`);
    return lines.join('\n');
  }

  function openInspectorDrawer() {
    document.getElementById('inspector-drawer').hidden = false;
    document.getElementById('inspector-result').textContent = formatInspector();
    if (!inspectorOpened) {
      inspectorOpened = true;
      logAction('open_inspector', inspector.endpoint);
      pushEvent('Request inspector opened — legacy SQL mode confirmed.', 'warn');
    }
  }

  function closeInspectorDrawer() {
    document.getElementById('inspector-drawer').hidden = true;
  }

  function openDecisionModal() {
    const decision = decisions[0];
    if (!decision) {
      finishMission(calculateScore(100));
      return;
    }

    const modal = document.getElementById('decision-modal');
    document.getElementById('decision-prompt').textContent = decision.prompt;
    const optionsEl = document.getElementById('decision-options');
    optionsEl.innerHTML = '';

    decision.options.forEach((option) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'decision-option';
      btn.textContent = option.label;
      btn.addEventListener('click', () => {
        closePhishModal('decision-modal');
        applyDecision(option);
      });
      optionsEl.appendChild(btn);
    });

    openPhishModal('decision-modal');
  }

  function calculateScore(decisionScore) {
    const flagScore = Math.round((flaggedSigns.size / Math.max(signs.length, 1)) * 40);
    const toolScore = inspectorOpened ? 10 : 0;
    const bypassScore = bypassAchieved ? 25 : 0;
    const errorScore = errorTriggered ? 10 : 0;
    const decisionPart = Math.round((decisionScore || 0) * 0.15);
    return Math.max(0, Math.min(100, flagScore + toolScore + bypassScore + errorScore + decisionPart));
  }

  function applyDecision(option) {
    decisionMade = true;
    submitBtn.disabled = true;
    logAction('final_decision', option.label);

    if (option.mistake) {
      mistakes.push(option.mistake);
      pushEvent(option.mistake, 'bad');
    }
    if (option.good) {
      goodDecisions.push(option.good);
      pushEvent(option.good, 'good');
    }

    completeTask('submit_report');
    finalScore = calculateScore(option.score || 0);
    setTimeout(() => finishMission(finalScore), 500);
  }

  async function finishMission(score) {
    const timeSpentSeconds = Math.round((Date.now() - missionStartedAt) / 1000);

    try {
      const response = await fetch(data.complete_url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          score,
          mistakes,
          good_decisions: goodDecisions,
          recommendations,
          actions_log: actionsLog,
          time_spent_seconds: timeSpentSeconds,
          skills_developed: data.skills_learned || [],
          flags_found: Array.from(flaggedSigns),
        }),
      });
      const payload = await response.json();
      if (payload.redirect) {
        window.location.href = payload.redirect;
      }
    } catch (error) {
      pushEvent('Could not save mission results. Please try again.', 'bad');
    }
  }

  loginForm?.addEventListener('submit', (event) => {
    event.preventDefault();
    if (loginErrorEl) loginErrorEl.hidden = true;

    const username = usernameInput?.value || '';

    if (isAcceptedPayload(username)) {
      handleBypass();
      return;
    }

    if (triggersSqlError(username)) {
      showSqlError();
      if (loginErrorEl) {
        loginErrorEl.hidden = false;
        loginErrorEl.textContent = 'Login failed. Inspect the database error message above.';
      }
      return;
    }

    if (loginErrorEl) {
      loginErrorEl.hidden = false;
      loginErrorEl.textContent = 'Invalid credentials. Keep investigating the form for injection opportunities.';
    }
    logAction('login_attempt', username);
    pushEvent('Login attempt rejected.', 'info');
  });

  document.getElementById('flag-mode-btn')?.addEventListener('click', () => {
    flagMode = !flagMode;
    app?.classList.toggle('is-flag-mode', flagMode);
    document.getElementById('flag-mode-btn')?.classList.toggle('is-active', flagMode);
    pushEvent(
      flagMode
        ? 'Flag mode enabled — click a vulnerability sign on the login page.'
        : 'Flag mode disabled.',
      'info'
    );
  });

  document.getElementById('open-inspector-btn')?.addEventListener('click', openInspectorDrawer);
  document.getElementById('inspector-drawer-close')?.addEventListener('click', closeInspectorDrawer);
  document.getElementById('inspector-drawer-backdrop')?.addEventListener('click', closeInspectorDrawer);

  document.getElementById('consequence-close')?.addEventListener('click', () => {
    closePhishModal('consequence-modal');
  });

  document.getElementById('flag-modal-close')?.addEventListener('click', () => {
    closePhishModal('flag-modal');
  });

  submitBtn?.addEventListener('click', () => {
    if (!bypassAchieved) {
      pushEvent('Bypass the login with SQL injection before submitting your report.', 'warn');
      return;
    }
    openDecisionModal();
  });

  setInterval(() => {
    const elapsed = Math.floor((Date.now() - missionStartedAt) / 1000);
    const mins = String(Math.floor(elapsed / 60)).padStart(2, '0');
    const secs = String(elapsed % 60).padStart(2, '0');
    timerEl.textContent = `${mins}:${secs}`;
  }, 1000);

  renderForm();
  updateProgress();
  progressCount.textContent = `0 / ${tasks.length} tasks`;
})();
