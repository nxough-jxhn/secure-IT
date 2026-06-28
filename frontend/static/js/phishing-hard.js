(function () {
  const dataEl = document.getElementById('workspace-data');
  if (!dataEl) return;

  const data = JSON.parse(dataEl.textContent);
  const email     = data.email || {};
  const signs     = data.signs || [];
  const tasks     = data.tasks || [];
  const decisions = data.decisions || [];
  const urlAnalysis = data.url_analysis || {};

  const flaggedSigns   = new Set();
  const completedTasks = new Set();
  const actionsLog     = [];
  const mistakes       = [];
  const goodDecisions  = [];
  const recommendations = [
    'Verify sender domains against official institution addresses.',
    'Inspect link destinations before clicking.',
    'Report phishing instead of ignoring suspicious mail.',
  ];

  let missionStartedAt = Date.now();
  let decisionMade = false;
  let flagMode     = false;
  let emailOpened  = false;
  let linkClicked  = false;
  let urlAnalyzed  = false;

  // DOM refs
  const app            = document.getElementById('phish-hard-app');
  const progressFill   = document.getElementById('mission-progress-fill');
  const progressPct    = document.getElementById('progress-percent');
  const progressCount  = document.getElementById('progress-count');
  const flagsMeta      = document.getElementById('flags-meta');
  const statusbarFlags = document.getElementById('statusbar-flags');
  const objectiveList  = document.getElementById('objective-list');
  const taskLog        = document.getElementById('task-log');
  const eventFeed      = document.getElementById('event-feed');
  const timerEl        = document.getElementById('mission-timer');
  const statusbarTimer = document.getElementById('statusbar-timer');
  const submitBtn      = document.getElementById('submit-report-btn');
  const completSimBtn  = document.getElementById('complete-sim-btn');
  const flagModeBtn    = document.getElementById('flag-mode-btn');

  const inboxView = document.getElementById('gmail-inbox-view');
  const readView  = document.getElementById('gmail-read-view');
  const emailList = document.getElementById('email-list');
  const readPane  = document.getElementById('email-read-pane');
  const backBtn   = document.getElementById('gmail-back-btn');

  const signMap = Object.fromEntries(signs.map(s => [s.id, s]));

  // ── Helpers ──────────────────────────────────────────────
  function escapeHtml(v) {
    return String(v)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;')
      .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }
  function formatMultiline(v) {
    return String(v||'').split('\n').map(escapeHtml).join('<br>');
  }
  function logAction(action, detail) {
    actionsLog.push({ action, detail, at: new Date().toISOString() });
  }
  function pushEvent(message, tone) {
    const li = document.createElement('li');
    li.className = `ph-event${tone ? ' ph-event--'+tone : ''}`;
    li.textContent = message;
    eventFeed.prepend(li);
    // remove placeholder text
    const empty = eventFeed.querySelector('.ph-event--info:only-child');
    if (empty && eventFeed.children.length > 1) empty.remove();
  }

  // ── Progress ─────────────────────────────────────────────
  function updateProgress() {
    const total = tasks.length || 1;
    const done  = completedTasks.size;
    const pct   = Math.round((done / total) * 100);
    progressFill.style.width = `${pct}%`;
    progressPct.textContent  = `${pct}%`;
    progressCount.textContent = `${done} / ${total} tasks`;
    const flagText = `${flaggedSigns.size} / ${signs.length} signs flagged`;
    if (flagsMeta)      flagsMeta.textContent = flagText;
    if (statusbarFlags) statusbarFlags.textContent = flagText;
  }

  function maybeEnableSubmit() {
    const done = ['open_email','flag_three','analyze_url'].every(id => completedTasks.has(id));
    if (submitBtn)    submitBtn.disabled    = !done || decisionMade;
    if (completSimBtn) completSimBtn.disabled = !done;
  }

  // ── Tasks / Objectives ────────────────────────────────────
  function completeTask(taskId) {
    if (completedTasks.has(taskId)) return;
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;

    completedTasks.add(taskId);

    if (typeof task.objective_index === 'number') {
      const obj = objectiveList?.querySelector(`[data-objective-index="${task.objective_index}"]`);
      if (obj) {
        obj.classList.add('is-done');
        const chk = obj.querySelector('.ph-objective__check');
        if (chk) chk.textContent = '✓';
      }
    }

    // Task log
    const empty = taskLog?.querySelector('.ph-task-log__empty');
    if (empty) empty.remove();
    const li = document.createElement('li');
    li.className = 'is-done';
    li.textContent = `✓ ${task.label}`;
    taskLog?.appendChild(li);

    logAction('task_complete', task.label);
    pushEvent(`Task: ${task.label}`, 'good');
    updateProgress();
    maybeEnableSubmit();
  }

  function checkFlagTask() {
    const task = tasks.find(t => t.action === 'flag_signs');
    if (!task) return;
    if (flaggedSigns.size >= (task.required || 3)) completeTask(task.id);
  }

  // ── Gmail inbox ───────────────────────────────────────────
  function renderInboxList() {
    emailList.innerHTML = '';
    const row = document.createElement('button');
    row.type = 'button';
    row.className = 'ph-gmail__email-row is-unread';
    row.innerHTML = `
      <span>☆</span>
      <span class="ph-gmail__row-from">${escapeHtml(email.from_name||'')}</span>
      <span class="ph-gmail__row-subject">
        ${escapeHtml(email.subject||'')}
        <span class="ph-gmail__row-snippet"> — ${escapeHtml((email.body||'').slice(0,48))}…</span>
      </span>
      <span class="ph-gmail__row-time">${escapeHtml(email.timestamp||'')}</span>
    `;
    row.addEventListener('click', openEmail);
    emailList.appendChild(row);
  }

  function openEmail() {
    emailOpened = true;
    inboxView.classList.add('ph-hidden');
    readView.classList.remove('ph-hidden');
    if (backBtn) backBtn.hidden = false;

    readPane.innerHTML = `
      <div class="ph-read__subject-row">
        <h1 class="ph-read__subject">
          <span data-sign="urgent_language">
            ${escapeHtml(email.subject||'')}
          </span>
        </h1>
        <div class="ph-read__tags">
          <span class="ph-read__inbox-tag">Inbox</span>
          <span class="ph-read__icon">⭐</span>
          <span class="ph-read__icon">↩</span>
          <span class="ph-read__icon">⋮</span>
        </div>
      </div>

      <div class="ph-read__sender">
        <div class="ph-read__sender-left">
          <span class="ph-read__avatar">U</span>
          <div>
            <div class="ph-read__from-name">${escapeHtml(email.from_name||'')}</div>
            <div class="ph-read__from-email" data-sign="sender_domain">
              &lt;${escapeHtml(email.from_address||'')}&gt;
            </div>
            <div class="ph-read__to-me">to me ▾</div>
          </div>
        </div>
        <div class="ph-read__time">${escapeHtml(email.timestamp||'')}</div>
      </div>

      <div class="ph-read__body">
        <div class="ph-read__body-line" data-sign="generic_greeting">
          ${escapeHtml(email.greeting||'')}
        </div>
        <div class="ph-read__body-line" data-sign="grammar_error">${escapeHtml(email.body||'')}</div>
        <div class="ph-read__body-line">
          <button type="button" class="ph-read__link" data-sign="link_mismatch"
            data-href="${escapeHtml(email.link_href||'')}" id="email-link">
            ${escapeHtml(email.link_text||'')}
          </button>
        </div>
        <div class="ph-read__body-line">${formatMultiline(email.signoff)}</div>
      </div>
    `;

    // Attach sign interaction listeners
    readPane.querySelectorAll('[data-sign]').forEach(node => {
      node.addEventListener('click', e => handleSignInteraction(e, node));
    });
    document.getElementById('email-link')?.addEventListener('click', handleLinkClick);

    completeTask('open_email');
    logAction('open_email', email.subject);
    pushEvent('Opened suspicious password-reset email.', 'warn');
  }

  function handleSignInteraction(event, node) {
    if (!flagMode) return;
    event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation();
    const signId = node.dataset.sign;
    if (signId) flagSign(signId, node);
  }

  function handleLinkClick(event) {
    if (flagMode) {
      handleSignInteraction(event, event.currentTarget);
      return;
    }
    event.preventDefault();
    linkClicked = true;
    mistakes.push('Clicked unverified phishing link');
    logAction('click_link', email.link_href);
    pushEvent('You clicked the suspicious link without verifying it.', 'bad');
    openPhishModal('consequence-modal');
  }

  function flagSign(signId, node) {
    const signInfo = signMap[signId];
    if (flaggedSigns.has(signId)) {
      showFlagModal(signInfo?.label||'Already flagged', signInfo?.hint||'');
      return;
    }
    flaggedSigns.add(signId);
    node.classList.add('is-flagged');
    logAction('flag_sign', signId);
    pushEvent(`Flagged: ${signInfo?.label||signId}`, 'good');
    checkFlagTask();
    updateProgress();
    showFlagModal(signInfo?.label||'Sign flagged', signInfo?.hint||'');
    // exit flag mode after each flag
    flagMode = false;
    app?.classList.remove('is-flag-mode');
    flagModeBtn?.classList.remove('is-active');
  }

  // ── Modals ────────────────────────────────────────────────
  function openPhishModal(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.hidden = false;
    document.body.style.overflow = 'hidden';
  }

  function closePhishModal(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.hidden = true;
    document.body.style.overflow = '';
  }

  function showFlagModal(title, body) {
    document.getElementById('flag-modal-title').textContent = title;
    document.getElementById('flag-modal-body').textContent  = body;
    openPhishModal('flag-modal');
  }

  // Backdrop clicks close their respective modals
  ['flag-modal','consequence-modal','decision-modal'].forEach(id => {
    const backdrop = document.getElementById(id)?.querySelector('.phish-modal__backdrop');
    backdrop?.addEventListener('click', e => {
      if (e.target === backdrop) closePhishModal(id);
    });
    const dialog = document.getElementById(id)?.querySelector('.phish-modal__dialog');
    dialog?.addEventListener('click', e => e.stopPropagation());
  });

  document.getElementById('flag-modal-close')?.addEventListener('click', () => closePhishModal('flag-modal'));
  document.getElementById('consequence-close')?.addEventListener('click', () => closePhishModal('consequence-modal'));

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      ['flag-modal','consequence-modal','decision-modal'].forEach(id => {
        const el = document.getElementById(id);
        if (el && !el.hidden) closePhishModal(id);
      });
    }
  });

  // ── URL analyzer ──────────────────────────────────────────
  function analyzeUrl(rawUrl) {
    const url = String(rawUrl||'').trim();
    const resultEl = document.getElementById('url-result');
    if (!url) { resultEl.textContent = 'Enter a URL to analyze.'; return; }

    const normalized = url.toLowerCase();
    let output = null;
    Object.entries(urlAnalysis).forEach(([key, info]) => {
      if (normalized.includes(key.toLowerCase()) || key.toLowerCase().includes(normalized.replace(/^https?:\/\//,''))) {
        output = formatAnalysis(info);
      }
    });
    if (!output) output = `Analyzing: ${url}\n\nVerdict: UNKNOWN\nRecommendation: Treat as suspicious until verified.`;

    resultEl.textContent = output;
    urlAnalyzed = true;
    logAction('analyze_url', url);
    pushEvent(`URL analyzed: ${url}`, 'warn');
    completeTask('analyze_url');
    maybeEnableSubmit();
  }

  function formatAnalysis(info) {
    const lines = [];
    if (info.verdict)     lines.push(`Verdict: ${info.verdict}`);
    if (info.domain_age)  lines.push(`Domain age: ${info.domain_age}`);
    if (info.ssl)         lines.push(`SSL: ${info.ssl}`);
    if (info.reputation)  lines.push(`Reputation: ${info.reputation}`);
    if (info.similar_to)  lines.push(`Similar to: ${info.similar_to}`);
    if (info.note)        lines.push(info.note);
    if (info.recommendation) lines.push(`\nRecommendation: ${info.recommendation}`);
    return lines.join('\n');
  }

  // ── Decision / finish ─────────────────────────────────────
  function openDecisionModal() {
    const decision = decisions[0];
    if (!decision) { finishMission(calculateScore(100)); return; }

    document.getElementById('decision-prompt').textContent = decision.prompt;
    const opts = document.getElementById('decision-options');
    opts.innerHTML = '';
    decision.options.forEach(option => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'decision-option';
      btn.textContent = option.label;
      btn.addEventListener('click', () => {
        closePhishModal('decision-modal');
        applyDecision(option);
      });
      opts.appendChild(btn);
    });
    openPhishModal('decision-modal');
  }

  function calculateScore(decisionScore) {
    const flagScore   = Math.round((flaggedSigns.size / Math.max(signs.length,1)) * 50);
    const toolScore   = urlAnalyzed ? 15 : 0;
    const clickPenalty = linkClicked ? 35 : 0;
    const decPart     = Math.round((decisionScore||0) * 0.35);
    return Math.max(0, Math.min(100, flagScore + toolScore + decPart - clickPenalty));
  }

  function applyDecision(option) {
    decisionMade = true;
    if (submitBtn) submitBtn.disabled = true;
    logAction('final_decision', option.label);
    if (option.mistake)  { mistakes.push(option.mistake);       pushEvent(option.mistake,  'bad'); }
    if (option.good)     { goodDecisions.push(option.good);     pushEvent(option.good,     'good'); }
    completeTask('submit_report');
    setTimeout(() => finishMission(calculateScore(option.score||0)), 500);
  }

  async function finishMission(score) {
    const timeSpentSeconds = Math.round((Date.now() - missionStartedAt) / 1000);
    try {
      const res = await fetch(data.complete_url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          score, mistakes, good_decisions: goodDecisions, recommendations,
          actions_log: actionsLog, time_spent_seconds: timeSpentSeconds,
          skills_developed: data.skills_learned||[], flags_found: Array.from(flaggedSigns),
        }),
      });
      const payload = await res.json();
      if (payload.redirect) window.location.href = payload.redirect;
    } catch {
      pushEvent('Could not save mission results. Please try again.', 'bad');
    }
  }

  // ── Event wiring ──────────────────────────────────────────
  flagModeBtn?.addEventListener('click', () => {
    if (!emailOpened) { pushEvent('Open the email before flagging signs.', 'warn'); return; }
    flagMode = !flagMode;
    app?.classList.toggle('is-flag-mode', flagMode);
    flagModeBtn.classList.toggle('is-active', flagMode);
    pushEvent(flagMode ? 'Flag mode on — click a suspicious element.' : 'Flag mode off.', 'info');
  });

  document.getElementById('open-analyzer-btn')?.addEventListener('click', () => {
    document.getElementById('url-drawer').hidden = false;
  });
  document.getElementById('url-drawer-close')?.addEventListener('click', () => {
    document.getElementById('url-drawer').hidden = true;
  });
  document.getElementById('url-drawer-backdrop')?.addEventListener('click', () => {
    document.getElementById('url-drawer').hidden = true;
  });
  document.getElementById('url-analyze-btn')?.addEventListener('click', () => {
    analyzeUrl(document.getElementById('url-input').value);
  });
  document.getElementById('paste-email-link')?.addEventListener('click', () => {
    const val = email.link_href||'';
    document.getElementById('url-input').value = val;
    analyzeUrl(val);
  });

  submitBtn?.addEventListener('click', openDecisionModal);
  completSimBtn?.addEventListener('click', openDecisionModal);

  backBtn?.addEventListener('click', () => {
    readView.classList.add('ph-hidden');
    inboxView.classList.remove('ph-hidden');
    backBtn.hidden = true;
  });

  // ── Timer ─────────────────────────────────────────────────
  setInterval(() => {
    const elapsed = Math.floor((Date.now() - missionStartedAt) / 1000);
    const mm = String(Math.floor(elapsed/60)).padStart(2,'0');
    const ss = String(elapsed%60).padStart(2,'0');
    const display = `${mm}:${ss}`;
    if (timerEl)        timerEl.textContent        = display;
    if (statusbarTimer) statusbarTimer.textContent  = display;
  }, 1000);

  // ── Init ──────────────────────────────────────────────────
  renderInboxList();
  updateProgress();
  progressCount.textContent = `0 / ${tasks.length} tasks`;
})();
