(function () {
  const dataEl = document.getElementById('workspace-data');
  if (!dataEl) return;

  const data = JSON.parse(dataEl.textContent);
  const tasks = data.tasks || [];
  const decisions = data.decisions || [];
  const logs = data.logs || [];
  const terminalResponses = data.terminal_responses || {};
  const inbox = data.inbox || {};

  const completedTasks = new Set();
  const completedObjectives = new Set();
  const actionsLog = [];
  const mistakes = [];
  const goodDecisions = [];
  const recommendations = [
    'Document indicators before taking action.',
    'Verify sender identity through official channels.',
    'Report suspicious activity to your security team.',
  ];

  let missionStartedAt = Date.now();
  let decisionMade = false;
  let finalScore = 0;
  let logsReviewed = false;
  const reviewLogsBtn = document.getElementById('review-logs-btn');
  const terminalForm = document.getElementById('terminal-form');
  const urlAnalyzeBtn = document.getElementById('url-analyze-btn');
  const submitReportBtn = document.getElementById('submit-report-btn');
  const terminalOutput = document.getElementById('terminal-output');
  const urlResult = document.getElementById('url-result');

  const progressFill = document.getElementById('mission-progress-fill');
  const progressPercent = document.getElementById('progress-percent');
  const progressCount = document.getElementById('progress-count');
  const objectiveList = document.getElementById('objective-list');
  const taskLog = document.getElementById('task-log');
  const eventFeed = document.getElementById('event-feed');
  const timerEl = document.getElementById('mission-timer');

  function normalizeCommand(value) {
    return String(value || '').trim().toLowerCase();
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

  function showEventModal(title, body, tone) {
    const modal = document.getElementById('event-modal');
    document.getElementById('event-modal-title').textContent = title;
    document.getElementById('event-modal-body').textContent = body;
    modal.classList.remove('hidden');
    pushEvent(title, tone);
  }

  document.getElementById('event-modal-close').addEventListener('click', () => {
    document.getElementById('event-modal').classList.add('hidden');
  });

  function switchTool(tool) {
    document.querySelectorAll('.workspace-tab').forEach((tab) => {
      tab.classList.toggle('is-active', tab.dataset.tool === tool);
    });
    document.querySelectorAll('.workspace-tool-panel').forEach((panel) => {
      panel.classList.toggle('is-active', panel.dataset.tool === tool);
    });
  }

  document.querySelectorAll('.workspace-tab').forEach((tab) => {
    tab.addEventListener('click', () => switchTool(tab.dataset.tool));
  });

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
    maybePromptDecision();
  }

  function updateProgress() {
    const total = tasks.length || 1;
    const done = completedTasks.size;
    const pct = Math.round((done / total) * 100);
    progressFill.style.width = `${pct}%`;
    progressPercent.textContent = `${pct}%`;
    progressCount.textContent = `${done} / ${total} tasks`;
  }

  function matchTask(tool, action, extra) {
    tasks.forEach((task) => {
      if (completedTasks.has(task.id)) return;
      if (task.tool !== tool || task.action !== action) return;

      if (action === 'command' && normalizeCommand(extra) !== normalizeCommand(task.command)) return;
      if (action === 'open' && task.email_id && task.email_id !== extra) return;
      if (action === 'headers' && task.email_id && task.email_id !== extra) return;
      if (action === 'analyze' && task.url && normalizeCommand(extra) !== normalizeCommand(task.url)) return;
      if (action === 'submit' && extra !== task.correct_response) return;

      completeTask(task.id);
    });
  }

  function renderInbox() {
    const list = document.getElementById('inbox-list');
    const detail = document.getElementById('inbox-detail');
    const emails = inbox.emails || [];
    if (!emails.length) {
      document.getElementById('panel-inbox')?.classList.remove('is-active');
      return;
    }

    list.innerHTML = '';
    emails.forEach((email) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'inbox-item';
      btn.innerHTML = `<div class="inbox-item-subject">${email.subject}</div><div class="inbox-item-from">${email.from_display}</div>`;
      btn.addEventListener('click', () => {
        document.querySelectorAll('.inbox-item').forEach((el) => el.classList.remove('is-active'));
        btn.classList.add('is-active');
        openEmail(email);
      });
      list.appendChild(btn);
    });

    function openEmail(email) {
      detail.innerHTML = `
        <div class="inbox-meta"><strong>From:</strong> ${email.from_display} &lt;${email.from_address}&gt;<br><strong>Subject:</strong> ${email.subject}<br><br>${email.body.replace(/\n/g, '<br>')}</div>
        <div class="inbox-actions">
          <button type="button" class="sim-secondary-btn text-sm" data-action="headers">View headers</button>
          ${email.suspicious_url ? `<button type="button" class="sim-secondary-btn text-sm" data-action="url">Inspect link</button>` : ''}
          <button type="button" class="sim-secondary-btn text-sm" data-action="report">Report email</button>
        </div>
        <div class="inbox-headers hidden" id="email-headers"></div>
      `;

      matchTask('inbox', 'open', email.id);
      logAction('open_email', email.subject);

      detail.querySelector('[data-action="headers"]').addEventListener('click', () => {
        const headers = document.getElementById('email-headers');
        headers.classList.remove('hidden');
        headers.textContent = Object.entries(email.headers || {})
          .map(([k, v]) => `${k}: ${v}`)
          .join('\n');
        matchTask('inbox', 'headers', email.id);
        logAction('view_headers', email.from_address);
      });

      const urlBtn = detail.querySelector('[data-action="url"]');
      if (urlBtn) {
        urlBtn.addEventListener('click', () => {
          switchTool('url_analyzer');
          document.getElementById('url-input').value = email.suspicious_url;
          analyzeUrl(email.suspicious_url);
        });
      }

      detail.querySelector('[data-action="report"]').addEventListener('click', () => {
        pushEvent('Email flagged for security review.', 'good');
        logAction('report_email', email.id);
      });
    }
  }

  function renderScanner() {
    const container = document.getElementById('scanner-content');
    const files = inbox.files || [];
    if (!files.length) return;

    container.innerHTML = '';
    files.forEach((file) => {
      const card = document.createElement('div');
      card.className = 'scanner-file-card';
      card.innerHTML = `
        <div class="font-bold text-white">${file.name}</div>
        <div class="mt-2 text-sm text-slate-400">${file.size} · hash ${file.hash}</div>
        <button type="button" class="sim-primary-btn mt-4 text-sm" data-scan="${file.name}">Scan file</button>
        <pre class="url-result mt-4 hidden" id="scan-result-${file.id}"></pre>
      `;
      card.querySelector('[data-scan]').addEventListener('click', () => {
        const result = document.getElementById(`scan-result-${file.id}`);
        result.classList.remove('hidden');
        result.textContent = file.malicious
          ? 'MALWARE DETECTED\nTrojan dropper behavior\nPersistence mechanism identified'
          : 'No threats detected.';
        logAction('scan_file', file.name);
        pushEvent(`Scanned ${file.name}`, file.malicious ? 'warn' : 'good');
        switchTool('terminal');
        document.getElementById('terminal-input').focus();
      });
      container.appendChild(card);
    });
  }

  function renderLogs() {
    const body = document.getElementById('logs-body');
    body.innerHTML = logs
      .map(
        (row) =>
          `<tr><td>${row.time}</td><td class="log-level-${row.level}">${row.level}</td><td>${row.message}</td></tr>`
      )
      .join('');
  }

  if (reviewLogsBtn) {
    reviewLogsBtn.addEventListener('click', () => {
      if (!logsReviewed) {
        logsReviewed = true;
        logAction('review_logs', 'Security logs reviewed');
        pushEvent('Security logs reviewed.', 'good');
      }
      matchTask('logs', 'review');
    });
  }

  function appendTerminal(text, tone) {
    if (!terminalOutput) return;
    const line = document.createElement('div');
    line.textContent = text;
    if (tone === 'error') line.style.color = '#fca5a5';
    terminalOutput.appendChild(line);
    terminalOutput.scrollTop = terminalOutput.scrollHeight;
  }

  if (terminalForm) {
    terminalForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const input = document.getElementById('terminal-input');
      const command = input.value.trim();
      if (!command) return;

      appendTerminal(`> ${command}`);
      logAction('terminal_command', command);

      const key = normalizeCommand(command);
      let response = terminalResponses[key];

      if (!response) {
        const matchKey = Object.keys(terminalResponses).find((k) => normalizeCommand(k) === key);
        response = matchKey ? terminalResponses[matchKey] : 'Unknown command. Type help for available commands.';
      }

      appendTerminal(response);
      matchTask('terminal', 'command', command);
      input.value = '';
    });
  }

  appendTerminal(data.terminal_help || 'Type help to begin.');

  function analyzeUrl(url) {
    if (!urlResult) return;
    const result = urlResult;
    const normalized = normalizeCommand(url);
    let output = 'No analysis available for this URL.';

    if (normalized.includes('secure-bank-verify.net') || normalized.includes('phish')) {
      output = 'PHISHING DETECTED\nDomain age: 2 days\nCloned login page\nCredential harvesting form';
    } else if (url) {
      output = `Analyzing ${url}\nReputation: suspicious\nRecommend blocking and reporting.`;
    }

    result.textContent = output;
    logAction('analyze_url', url);
    pushEvent(`URL analyzed: ${url}`, 'warn');
    matchTask('url_analyzer', 'analyze', url);
  }

  if (urlAnalyzeBtn) {
    urlAnalyzeBtn.addEventListener('click', () => {
      analyzeUrl(document.getElementById('url-input').value.trim());
    });
  }

  if (submitReportBtn) {
    submitReportBtn.addEventListener('click', () => {
      if (completedTasks.size < tasks.filter((t) => t.action !== 'submit').length) {
        showEventModal(
          'Investigation incomplete',
          'Complete the required investigation tasks before submitting your incident report.',
          'warn'
        );
        return;
      }
      openDecisionModal();
    });
  }

  function openDecisionModal() {
    const decision = decisions[0];
    if (!decision) {
      finishMission(80);
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
        modal.classList.add('hidden');
        applyDecision(option, decision);
      });
      optionsEl.appendChild(btn);
    });

    modal.classList.remove('hidden');
  }

  function applyDecision(option, decision) {
    decisionMade = true;
    logAction('final_decision', option.label);

    if (option.mistake) {
      mistakes.push(option.mistake);
      pushEvent(option.mistake, 'bad');
      if (option.id === 'click') {
        showEventModal(
          'Simulation event triggered',
          'Your credentials were captured by the attacker. This demonstrates how phishing attacks steal user information.',
          'bad'
        );
      }
    }

    if (option.good) {
      goodDecisions.push(option.good);
      pushEvent(option.good, 'good');
    }

    matchTask('notes', 'submit', option.id);

    const taskScore = Math.round((completedTasks.size / Math.max(tasks.length, 1)) * 60);
    finalScore = Math.min(100, taskScore + (option.score || 0) * 0.4);

    if (option.score >= 100) {
      finalScore = Math.max(finalScore, 85 + Math.min(15, completedTasks.size * 2));
    } else if (option.score <= 20) {
      finalScore = Math.min(finalScore, 35);
    }

    setTimeout(() => finishMission(Math.round(finalScore)), 600);
  }

  function maybePromptDecision() {
    if (decisionMade) return;
    const required = tasks.filter((t) => t.action !== 'submit');
    const allDone = required.every((t) => completedTasks.has(t.id));
    if (allDone) {
      pushEvent('All investigation tasks complete. Submit your incident report.', 'good');
      switchTool('notes');
    }
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
        }),
      });
      const payload = await response.json();
      if (payload.redirect) {
        window.location.href = payload.redirect;
      }
    } catch (error) {
      showEventModal('Submission error', 'Could not save mission results. Please try again.', 'bad');
    }
  }

  setInterval(() => {
    const elapsed = Math.floor((Date.now() - missionStartedAt) / 1000);
    const mins = String(Math.floor(elapsed / 60)).padStart(2, '0');
    const secs = String(elapsed % 60).padStart(2, '0');
    timerEl.textContent = `${mins}:${secs}`;
  }, 1000);

  renderInbox();
  renderScanner();
  renderLogs();
  updateProgress();
  progressCount.textContent = `0 / ${tasks.length} tasks`;

  const defaultTab = document.querySelector('.workspace-tab.is-active');
  if (defaultTab) switchTool(defaultTab.dataset.tool);
})();
