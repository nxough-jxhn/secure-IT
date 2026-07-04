/* ═══════════════════════════════════════════
   Evil Twin Hard Simulation — Workspace JS
═══════════════════════════════════════════ */
(function () {
  const workspace = JSON.parse(document.getElementById('workspace-data')?.textContent || '{}');
  const signs      = workspace.signs       || [];
  const tasks      = workspace.tasks       || [];
  const decisions  = workspace.decisions   || [];
  const networks   = workspace.wifi_options?.networks || [];

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
  const networkList   = document.getElementById('network-list');

  /* ── State ── */
  let flagMode      = false;
  let flagged       = new Set();
  let tasksComplete = new Set();
  let startTime     = Date.now();
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
    li.className = 'evil-twin-hard-event' + (type ? ` evil-twin-hard-event--${type}` : '');
    li.textContent = msg;
    eventFeed.prepend(li);
  }

  /* ── Task log ── */
  function logTask(label) {
    if (!taskLog) return;
    const empty = taskLog.querySelector('.evil-twin-hard-task-log__empty');
    if (empty) empty.remove();
    const li = document.createElement('li');
    li.className = 'evil-twin-hard-task-log__item';
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
    if (objectiveList) {
      objectiveList.querySelectorAll('.evil-twin-hard-objective').forEach((el, i) => {
        if (i < done) {
          el.classList.add('is-done');
          el.querySelector('.evil-twin-hard-objective__check').textContent = '✓';
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

  /* ── Build network list ── */
  function buildNetworkList() {
    if (!networkList) return;
    networkList.innerHTML = '';
    networks.forEach((net, i) => {
      const card = document.createElement('div');
      card.className = 'evil-twin-hard-network' + (net.official ? '' : ' evil-twin-hard-network--suspicious');
      card.dataset.idx = i;
      card.dataset.official = net.official ? 'true' : 'false';

      const secBadge = net.security === 'Open'
        ? `<span class="evil-twin-hard-network__badge">Open ⚠</span>`
        : `<span class="evil-twin-hard-network__badge">${net.security}</span>`;

      card.innerHTML = `
        <div class="evil-twin-hard-network__top">
          <span class="evil-twin-hard-network__name">📶 ${net.name}</span>
          <span class="evil-twin-hard-network__signal">${net.signal}</span>
        </div>
        <div class="evil-twin-hard-network__meta">
          ${secBadge}
          <span>${net.official ? '✓ Official' : 'Unknown source'}</span>
        </div>`;

      networkList.appendChild(card);
    });

    completeTask('inspect_networks');
    addEvent('Network list loaded. Inspect each hotspot carefully.', '');
  }

  buildNetworkList();

  /* ── Flag mode ── */
  flagModeBtn?.addEventListener('click', () => {
    flagMode = !flagMode;
    flagModeBtn.textContent = flagMode ? '🗑 Cancel flag' : '🚩 Flag sign';
    flagModeBtn.classList.toggle('is-active', flagMode);
    document.body.style.cursor = flagMode ? 'crosshair' : '';
    addEvent(flagMode ? 'Flag mode enabled. Click suspicious networks.' : 'Flag mode disabled.', '');
  });

  /* ── Network click — flag suspicious ones ── */
  networkList?.addEventListener('click', e => {
    const card = e.target.closest('.evil-twin-hard-network');
    if (!card) return;

    const idx = parseInt(card.dataset.idx);
    const net = networks[idx];
    if (!net) return;

    if (!flagMode) {
      // Just inspecting — show info event
      addEvent(`Inspecting: ${net.name} (${net.security}, ${net.signal})`, '');
      return;
    }

    // Flagging
    const signId = net.official ? 'official_network' : (signs[flagged.size % signs.length]?.id || 'rogue_name');
    if (flagged.has(signId + '_' + idx)) return;

    flagged.add(signId + '_' + idx);
    card.classList.add('is-flagged');
    updateFlagCount();
    completeTask('flag_signs');

    const sign = signs.find(s => s.id === signId) || { label: net.official ? 'Official network' : 'Suspicious hotspot', hint: '' };
    addEvent(`Flagged: ${sign.label}`, net.official ? '' : 'warn');
    showFlagModal(sign, net.official);
  });

  function updateFlagCount() {
    if (statusFlags) statusFlags.textContent = `${flagged.size} / ${signs.length} signs flagged`;
    checkSubmitReady();
  }

  /* ── Flag modal ── */
  const flagModal      = document.getElementById('flag-modal');
  const flagModalClose = document.getElementById('flag-modal-close');
  const flagModalBd    = document.getElementById('flag-modal-backdrop');
  const flagModalTitle = document.getElementById('flag-modal-title');
  const flagModalBody  = document.getElementById('flag-modal-body');

  function showFlagModal(sign, isOfficial) {
    if (!flagModal) return;
    if (flagModalTitle) flagModalTitle.textContent = sign.label || 'Sign flagged';
    if (flagModalBody)  flagModalBody.textContent  = isOfficial
      ? 'This is the legitimate campus network. Connect to this one.'
      : (sign.hint || '');
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
        btn.className = 'evil-twin-hard-decision-btn';
        btn.innerHTML = `<span class="evil-twin-hard-decision-btn__label">${opt.label}</span>`;
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
      good_decisions:   goodActions,
      recommendations:  ['Always verify the official SSID with staff before connecting'],
      actions_log:      Array.from(flagged).map(id => `Flagged: ${id}`),
      skills_developed: workspace.skills_learned || [],
      time_spent_seconds: timeSpent,
      flags_found:      Array.from(flagged),
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
  addEvent('Multiple hotspots detected. Identify the rogue access point.', 'warn');
})();
