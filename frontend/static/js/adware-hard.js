/* ═══════════════════════════════════════════
   Adware Hard Simulation — Workspace JS
═══════════════════════════════════════════ */
(function () {
  const workspace = JSON.parse(document.getElementById('workspace-data')?.textContent || '{}');
  const signs      = workspace.signs     || [];
  const tasks      = workspace.tasks     || [];
  const decisions  = workspace.decisions || [];

  /* ── DOM refs ── */
  const eventFeed     = document.getElementById('event-feed');
  const flagModeBtn   = document.getElementById('flag-mode-btn');
  const submitBtn     = document.getElementById('submit-report-btn');
  const statusFlags   = document.getElementById('statusbar-flags');
  const taskLog       = document.getElementById('task-log');
  const progressFill  = document.getElementById('mission-progress-fill');
  const progressPct   = document.getElementById('progress-percent');
  const progressCount = document.getElementById('progress-count');
  const missionTimer  = document.getElementById('mission-timer');
  const objectiveList = document.getElementById('objective-list');
  const popupCard     = document.getElementById('popup-card');

  /* ── State ── */
  let flagMode   = false;
  let flagged    = new Set();
  let tasksComplete = new Set();
  let startTime  = Date.now();
  let timerInterval;

  /* ── Timer ── */
  function updateTimer() {
    const e = Math.floor((Date.now() - startTime) / 1000);
    const m = String(Math.floor(e / 60)).padStart(2, '0');
    const s = String(e % 60).padStart(2, '0');
    if (missionTimer) missionTimer.textContent = `${m}:${s}`;
  }
  timerInterval = setInterval(updateTimer, 1000);

  /* ── Event feed ── */
  function addEvent(msg, type) {
    if (!eventFeed) return;
    const li = document.createElement('li');
    li.className = 'adware-hard-event' + (type ? ` adware-hard-event--${type}` : '');
    li.textContent = msg;
    eventFeed.prepend(li);
  }

  /* ── Task log ── */
  function logTask(label) {
    if (!taskLog) return;
    const empty = taskLog.querySelector('.adware-hard-task-log__empty');
    if (empty) empty.remove();
    const li = document.createElement('li');
    li.className = 'adware-hard-task-log__item';
    li.textContent = label;
    taskLog.prepend(li);
  }

  /* ── Progress ── */
  function updateProgress() {
    const done  = tasksComplete.size;
    const total = Math.max(tasks.length, 1);
    const pct   = Math.round((done / total) * 100);
    if (progressFill)  progressFill.style.width  = pct + '%';
    if (progressPct)   progressPct.textContent   = pct + '%';
    if (progressCount) progressCount.textContent  = `${done} / ${total} tasks`;

    // Update objectives
    if (objectiveList) {
      objectiveList.querySelectorAll('.adware-hard-objective').forEach((el, i) => {
        if (i < done) {
          el.classList.add('is-done');
          el.querySelector('.adware-hard-objective__check').textContent = '✓';
        }
      });
    }
  }

  function completeTask(taskId) {
    if (tasksComplete.has(taskId)) return;
    tasksComplete.add(taskId);
    const task = tasks.find(t => t.id === taskId);
    if (task) {
      logTask('✓ ' + task.label);
      addEvent(task.label + ' completed.', 'good');
    }
    updateProgress();
    checkSubmitReady();
  }

  function checkSubmitReady() {
    const minFlags = tasks.find(t => t.action === 'flag_signs')?.required || 2;
    if (submitBtn) submitBtn.disabled = flagged.size < minFlags;
  }

  /* ── Flag mode ── */
  flagModeBtn?.addEventListener('click', () => {
    flagMode = !flagMode;
    flagModeBtn.textContent = flagMode ? '🗑 Cancel flag' : '🚩 Flag sign';
    flagModeBtn.classList.toggle('is-active', flagMode);
    document.body.style.cursor = flagMode ? 'crosshair' : '';
    addEvent(flagMode ? 'Flag mode enabled. Click suspicious popup elements.' : 'Flag mode disabled.', '');
  });

  /* ── Popup interaction — flag signs by clicking popup parts ── */
  const POPUP_SIGN_MAP = {
    'popup-title':    'scare_language',
    'popup-body':     'urgent_install',
    'popup-meta':     'unknown_publisher',
    'popup-cta':      'urgent_install',
    'popup-url':      'scare_language',
  };

  if (popupCard) {
    popupCard.querySelectorAll('[id]').forEach(el => {
      el.style.cursor = 'pointer';
      el.addEventListener('click', e => {
        if (!flagMode) return;
        e.stopPropagation();
        const signId = POPUP_SIGN_MAP[el.id] || signs[flagged.size % signs.length]?.id;
        if (!signId || flagged.has(signId)) return;
        flagged.add(signId);
        el.style.outline = '2px solid #ffb84d';
        updateFlagCount();
        completeTask('flag_signs');
        const sign = signs.find(s => s.id === signId);
        addEvent(`Flagged: ${sign ? sign.label : signId}`, 'warn');
        showFlagModal(sign);
      });
    });

    // Also allow clicking the whole popup card
    popupCard.addEventListener('click', () => {
      if (!flagMode) return;
      // Pick next unflagged sign
      const next = signs.find(s => !flagged.has(s.id));
      if (!next) return;
      flagged.add(next.id);
      updateFlagCount();
      completeTask('flag_signs');
      addEvent(`Flagged: ${next.label}`, 'warn');
      showFlagModal(next);
    });
  }

  function updateFlagCount() {
    if (statusFlags) statusFlags.textContent = `${flagged.size} / ${signs.length} signs flagged`;
    checkSubmitReady();
  }

  /* ── Inspect popup task (just opening/viewing it) ── */
  completeTask('inspect_popup');

  /* ── Flag modal ── */
  const flagModal      = document.getElementById('flag-modal');
  const flagModalClose = document.getElementById('flag-modal-close');
  const flagModalBd    = document.getElementById('flag-modal-backdrop');
  const flagModalTitle = document.getElementById('flag-modal-title');
  const flagModalBody  = document.getElementById('flag-modal-body');

  function showFlagModal(sign) {
    if (!flagModal || !sign) return;
    if (flagModalTitle) flagModalTitle.textContent = sign.label || 'Sign flagged';
    if (flagModalBody)  flagModalBody.textContent  = sign.hint  || '';
    flagModal.hidden = false;
    document.body.style.overflow = 'hidden';
  }

  flagModalClose?.addEventListener('click', () => { flagModal.hidden = true; document.body.style.overflow = ''; });
  flagModalBd?.addEventListener('click',    () => { flagModal.hidden = true; document.body.style.overflow = ''; });

  /* ── Submit → decision modal ── */
  const decisionModal   = document.getElementById('decision-modal');
  const decisionBd      = document.getElementById('decision-modal-backdrop');
  const decisionPrompt  = document.getElementById('decision-prompt');
  const decisionOptions = document.getElementById('decision-options');

  submitBtn?.addEventListener('click', () => {
    const minFlags = tasks.find(t => t.action === 'flag_signs')?.required || 2;
    if (flagged.size < minFlags) {
      addEvent(`Flag at least ${minFlags} signs before submitting.`, 'alert');
      return;
    }
    completeTask('submit_report');
    showDecisionModal();
  });

  function showDecisionModal() {
    if (!decisionModal || !decisions.length) { submitReport(100, [], []); return; }
    const d = decisions[0];
    if (decisionPrompt) decisionPrompt.textContent = d.prompt || 'What is the correct response?';
    if (decisionOptions) {
      decisionOptions.innerHTML = '';
      (d.options || []).forEach(opt => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'adware-hard-decision-btn';
        btn.innerHTML = `<span class="adware-hard-decision-btn__label">${opt.label}</span>`;
        btn.addEventListener('click', () => {
          decisionModal.hidden = true;
          document.body.style.overflow = '';
          const mistakes = opt.mistake ? [opt.mistake] : [];
          const good     = opt.good    ? [opt.good]    : [];
          submitReport(opt.score || 0, mistakes, good);
        });
        decisionOptions.appendChild(btn);
      });
    }
    decisionModal.hidden = false;
    document.body.style.overflow = 'hidden';
  }

  decisionBd?.addEventListener('click', () => { decisionModal.hidden = true; document.body.style.overflow = ''; });

  /* ── Final submission ── */
  async function submitReport(score, mistakes, goodActions) {
    clearInterval(timerInterval);
    const timeSpent = Math.floor((Date.now() - startTime) / 1000);
    addEvent('Submitting incident report…', '');

    const payload = {
      score,
      mistakes,
      good_decisions: goodActions,
      recommendations: ['Use a trusted security tool to scan your system'],
      actions_log: Array.from(flagged).map(id => `Flagged: ${id}`),
      skills_developed: workspace.skills_learned || [],
      time_spent_seconds: timeSpent,
      flags_found: Array.from(flagged),
    };

    try {
      const res  = await fetch(workspace.complete_url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok && data.redirect) {
        window.location.href = data.redirect;
      } else {
        addEvent('Could not save result. Please try again.', 'alert');
      }
    } catch {
      addEvent('Network error. Please try again.', 'alert');
    }
  }

  /* ── Init ── */
  updateFlagCount();
  updateProgress();
  addEvent('Suspicious installer popup detected. Investigate the content.', 'warn');
})();
