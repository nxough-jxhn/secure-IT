(function () {
  const dataElement = document.getElementById('sim-play-data');
  if (!dataElement) return;

  const data = JSON.parse(dataElement.textContent);
  const steps = data.steps || [];
  let currentStep = 0;
  let totalScore = 0;
  let maxScore = 0;
  const goodDecisions = [];
  const mistakes = [];
  const recommendations = new Set();

  const titleEl = document.getElementById('sim-step-title');
  const narrativeEl = document.getElementById('sim-step-narrative');
  const interfaceEl = document.getElementById('sim-interface-panel');
  const choicesEl = document.getElementById('sim-choices');
  const feedbackPanel = document.getElementById('sim-feedback-panel');
  const feedbackLabel = document.getElementById('sim-feedback-label');
  const feedbackOutcome = document.getElementById('sim-feedback-outcome');
  const feedbackExplanation = document.getElementById('sim-feedback-explanation');
  const nextBtn = document.getElementById('sim-next-btn');
  const progressFill = document.getElementById('sim-progress-fill');
  const progressLabel = document.getElementById('sim-progress-label');

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function renderInterface(step) {
    const ui = step.interface || {};
    const type = step.interface_type || 'generic';

    if (type === 'email') {
      return `
        <div class="sim-email-ui">
          <div class="sim-email-box">
            <div class="sim-email-header">From: ${escapeHtml(ui.from || 'unknown')}</div>
            <div class="mt-2 text-sm text-slate-300">Subject: ${escapeHtml(ui.subject || '')}</div>
            <pre class="mt-4 whitespace-pre-wrap text-sm leading-7 text-slate-200">${escapeHtml(ui.body || '')}</pre>
            ${ui.highlight ? `<div class="mt-4 rounded-xl border border-rose-400/30 bg-rose-400/10 px-3 py-2 sim-highlight-bad">${escapeHtml(ui.highlight)}</div>` : ''}
          </div>
        </div>`;
    }

    if (type === 'website') {
      const fields = (ui.fields || []).map((field) => `<div class="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm">${escapeHtml(field)}</div>`).join('');
      return `
        <div class="sim-website-ui">
          <div class="sim-website-box">
            <div class="sim-website-bar sim-highlight-bad">${escapeHtml(ui.url || '')}</div>
            <div class="mt-3 text-lg font-bold">${escapeHtml(ui.title || 'Login page')}</div>
            <div class="mt-4 grid gap-2">${fields}</div>
          </div>
        </div>`;
    }

    if (type === 'popup') {
      return `
        <div class="sim-popup-ui">
          <div class="sim-popup-box">
            <div class="sim-popup-title">${escapeHtml(ui.title || 'System Alert')}</div>
            <p class="mt-3 text-sm leading-7 text-slate-300">${escapeHtml(ui.message || '')}</p>
            <button type="button" class="sim-primary-btn mt-4">${escapeHtml(ui.button || 'Continue')}</button>
          </div>
        </div>`;
    }

    if (type === 'ransom') {
      const files = (ui.files || []).map((file) => `<li>${escapeHtml(file)}</li>`).join('');
      return `
        <div class="sim-ransom-box">
          <div class="sim-ransom-headline text-rose-200">${escapeHtml(ui.headline || 'FILES ENCRYPTED')}</div>
          <p class="mt-3 text-sm text-slate-300">${escapeHtml(ui.message || '')}</p>
          <ul class="mt-4 space-y-1 text-sm text-rose-100">${files}</ul>
        </div>`;
    }

    if (type === 'device') {
      const files = (ui.files || []).map((file) => `<li>${escapeHtml(file)}</li>`).join('');
      return `
        <div class="sim-device-ui">
          <div class="sim-device-box">
            <div class="font-bold">${escapeHtml(ui.label || 'External device')}</div>
            <ul class="mt-3 space-y-1 text-sm">${files}</ul>
            <p class="mt-3 text-xs text-amber-200">${escapeHtml(ui.autorun || '')}</p>
          </div>
        </div>`;
    }

    if (type === 'phone') {
      return `
        <div class="sim-phone-ui">
          <div class="sim-phone-box">
            <div class="text-sm text-slate-400">Incoming call</div>
            <div class="mt-2 text-xl font-bold">${escapeHtml(ui.caller || 'Unknown')}</div>
            <p class="mt-4 rounded-2xl border border-white/10 bg-white/5 p-4 text-sm leading-7">${escapeHtml(ui.script || '')}</p>
          </div>
        </div>`;
    }

    if (type === 'password') {
      return `
        <div class="sim-password-box">
          <div class="text-sm text-slate-400">Password attempt</div>
          <div class="mt-2 font-mono text-lg">${escapeHtml(ui.attempt || '')}</div>
          <div class="mt-3 text-rose-200">${escapeHtml(ui.strength || '')}</div>
          <p class="mt-3 text-sm text-amber-100">${escapeHtml(ui.warning || '')}</p>
        </div>`;
    }

    if (type === 'extension') {
      const permissions = (ui.permissions || []).map((item) => `<li>${escapeHtml(item)}</li>`).join('');
      return `
        <div class="sim-extension-box">
          <div class="font-bold">${escapeHtml(ui.name || 'Browser extension')}</div>
          <ul class="mt-3 space-y-1 text-sm text-amber-100">${permissions}</ul>
          <p class="mt-3 text-xs text-slate-400">${escapeHtml(ui.reviews || '')}</p>
        </div>`;
    }

    if (type === 'installer') {
      return `
        <div class="sim-installer-box">
          <div class="font-bold">${escapeHtml(ui.name || 'Setup.exe')}</div>
          <p class="mt-2 text-sm text-slate-300">Publisher: ${escapeHtml(ui.publisher || 'Unknown')}</p>
          <p class="mt-3 rounded-xl border border-amber-300/30 bg-amber-300/10 px-3 py-2 text-sm text-amber-100">${escapeHtml(ui.warning || '')}</p>
        </div>`;
    }

    if (type === 'status') {
      return `
        <div class="sim-status-box">
          <div class="font-bold">${escapeHtml(ui.service || 'Service status')}</div>
          <p class="mt-2 text-rose-200">${escapeHtml(ui.status || '')}</p>
          <p class="mt-3 text-sm text-slate-300">${escapeHtml(ui.chart || '')}</p>
        </div>`;
    }

    return `<div class="sim-generic-ui text-sm text-slate-300">${escapeHtml(step.narrative || '')}</div>`;
  }

  function updateProgress() {
    const percent = steps.length ? ((currentStep + 1) / steps.length) * 100 : 100;
    progressFill.style.width = `${percent}%`;
    progressLabel.textContent = `Step ${Math.min(currentStep + 1, steps.length)} / ${steps.length}`;
  }

  function renderStep() {
    const step = steps[currentStep];
    if (!step) return finishSimulation();

    feedbackPanel.classList.add('hidden');
    choicesEl.innerHTML = '';
    titleEl.textContent = step.title;
    narrativeEl.textContent = step.narrative;
    interfaceEl.innerHTML = renderInterface(step);
    updateProgress();

    maxScore += 100;

    step.choices.forEach((choice) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'sim-choice-btn';
      button.textContent = choice.label;
      button.addEventListener('click', () => handleChoice(step, choice, button));
      choicesEl.appendChild(button);
    });
  }

  function handleChoice(step, choice, button) {
    choicesEl.querySelectorAll('button').forEach((btn) => { btn.disabled = true; });
    totalScore += choice.score;

    if (choice.is_best || choice.score >= 100) {
      button.classList.add('selected-best');
      goodDecisions.push(`Step "${step.title}": ${choice.label}`);
      feedbackPanel.classList.add('is-success');
      feedbackPanel.classList.remove('is-warning', 'is-error');
      feedbackLabel.textContent = 'Strong security response';
    } else if (choice.score === 0) {
      button.classList.add('selected-bad');
      mistakes.push(`Step "${step.title}": ${choice.label}`);
      feedbackPanel.classList.add('is-error');
      feedbackPanel.classList.remove('is-success', 'is-warning');
      feedbackLabel.textContent = 'Risky decision';
    } else {
      mistakes.push(`Step "${step.title}": ${choice.label} — room for improvement`);
      feedbackPanel.classList.add('is-warning');
      feedbackPanel.classList.remove('is-success', 'is-error');
      feedbackLabel.textContent = 'Partially safe choice';
    }

    feedbackOutcome.textContent = choice.outcome;
    feedbackExplanation.textContent = choice.explanation;
    feedbackPanel.classList.remove('hidden');
    recommendations.add(choice.explanation);
  }

  nextBtn.addEventListener('click', () => {
    currentStep += 1;
    if (currentStep >= steps.length) {
      finishSimulation();
    } else {
      renderStep();
    }
  });

  async function finishSimulation() {
    const score = maxScore ? Math.round((totalScore / maxScore) * 100) : 0;
    nextBtn.disabled = true;
    titleEl.textContent = 'Submitting results...';

    try {
      const response = await fetch(data.complete_url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          score,
          good_decisions: goodDecisions,
          mistakes,
          recommendations: Array.from(recommendations),
        }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error('Simulation save failed');
      if (payload.redirect) {
        window.location.href = payload.redirect;
        return;
      }
      return;
    } catch (error) {
      alert('Could not save simulation results. Please try again.');
      nextBtn.disabled = false;
    }
  }

  renderStep();
})();
