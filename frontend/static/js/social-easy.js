(function () {
  const cfg = window.SE_EASY;
  if (!cfg) return;

  const indicators   = cfg.indicators || [];
  const completeUrl  = cfg.completeUrl;
  let reviewedCount  = 0;
  let verdictChosen  = null;
  const reviewed     = new Set();

  // DOM refs
  const indicatorList  = document.getElementById('se-indicator-list');
  const countEl        = document.getElementById('se-indicator-count');
  const completeBtn    = document.getElementById('se-complete-btn');
  const endCallBtn     = document.getElementById('se-end-call-btn');
  const verdictLegit   = document.getElementById('verdict-legit');
  const verdictAttack  = document.getElementById('verdict-attack');
  const timerEl        = document.getElementById('se-timer');
  const callTimerEl    = document.getElementById('se-call-timer');

  // ── Timer ──────────────────────────────────────────
  let elapsed = 0;
  let callElapsed = 0;

  setInterval(() => {
    elapsed++;
    callElapsed++;
    const m = String(Math.floor(elapsed / 60)).padStart(2, '0');
    const s = String(elapsed % 60).padStart(2, '0');
    if (timerEl) timerEl.textContent = `${m}:${s}`;
    if (callTimerEl) {
      const cm = Math.floor(callElapsed / 60);
      const cs = String(callElapsed % 60).padStart(2, '0');
      callTimerEl.textContent = `${cm}:${cs}`;
    }
  }, 1000);

  // ── Build indicator list ────────────────────────────
  const indicatorMap = {};
  indicators.forEach((ind, i) => {
    indicatorMap[ind.element] = ind;

    const item = document.createElement('div');
    item.className = 'se-indicator-item';
    item.dataset.element = ind.element;
    item.innerHTML = `
      <div class="se-indicator-item__head">
        <span class="se-indicator-item__num">${i + 1}</span>
        <span class="se-indicator-item__name">${ind.title}</span>
      </div>
      <span class="se-indicator-item__status">Click flag ${i + 1} in the call to review</span>
    `;
    item.addEventListener('click', () => openModal(ind.element));
    indicatorList.appendChild(item);
  });

  // ── Hotspot clicks ─────────────────────────────────
  document.querySelectorAll('.se-hotspot').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.indicator;
      if (id) openModal(id);
    });
  });

  // ── Modal ───────────────────────────────────────────
  const modal       = document.getElementById('se-modal');
  const modalTitle  = document.getElementById('se-modal-title');
  const modalDesc   = document.getElementById('se-modal-desc');
  const modalWrong  = document.getElementById('se-modal-wrong');
  const modalRight  = document.getElementById('se-modal-correct');
  const modalTip    = document.getElementById('se-modal-tip');
  const modalTipTxt = document.getElementById('se-modal-tip-text');
  const modalClose  = document.getElementById('se-modal-close');
  const modalBd     = document.getElementById('se-modal-backdrop');

  function openModal(elementId) {
    const ind = indicatorMap[elementId];
    if (!ind) return;

    modalTitle.textContent  = ind.title;
    modalDesc.textContent   = ind.description;
    modalWrong.textContent  = ind.wrong || '';
    modalRight.textContent  = ind.correct || '';

    if (ind.tip) {
      modalTipTxt.innerHTML = ind.tip;
      modalTip.hidden = false;
    } else {
      modalTip.hidden = true;
    }

    modal.hidden = false;
    markReviewed(elementId);
  }

  function closeModal() { modal.hidden = true; }

  modalClose?.addEventListener('click', closeModal);
  modalBd?.addEventListener('click', closeModal);
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && !modal.hidden) closeModal();
  });

  // ── Mark reviewed ───────────────────────────────────
  function markReviewed(elementId) {
    if (reviewed.has(elementId)) return;
    reviewed.add(elementId);
    reviewedCount++;

    // Mark hotspot buttons
    document.querySelectorAll(`.se-hotspot[data-indicator="${elementId}"]`).forEach(btn => {
      btn.classList.add('is-reviewed');
    });

    // Mark indicator list item
    const item = indicatorList.querySelector(`[data-element="${elementId}"]`);
    if (item) {
      item.classList.add('is-reviewed');
      item.querySelector('.se-indicator-item__status').textContent = 'Reviewed ✓';
    }

    // Update count
    if (countEl) countEl.textContent = `${reviewedCount} / ${indicators.length} reviewed`;

    // Enable end call button once all reviewed
    if (reviewedCount >= indicators.length) {
      if (endCallBtn) endCallBtn.disabled = false;
    }

    checkReady();
  }

  // ── Verdict ─────────────────────────────────────────
  verdictLegit?.addEventListener('click', () => setVerdict('legit'));
  verdictAttack?.addEventListener('click', () => setVerdict('attack'));

  function setVerdict(v) {
    verdictChosen = v;
    verdictLegit?.classList.toggle('is-active', v === 'legit');
    verdictAttack?.classList.toggle('is-active', v === 'attack');
    checkReady();
  }

  function checkReady() {
    if (reviewedCount >= indicators.length && verdictChosen) {
      if (completeBtn) completeBtn.disabled = false;
    }
  }

  // ── End call button (just visual — disables after click) ─
  endCallBtn?.addEventListener('click', () => {
    endCallBtn.disabled = true;
    endCallBtn.innerHTML = '<span>✓</span><span>Call ended</span>';
  });

  // ── Complete ─────────────────────────────────────────
  completeBtn?.addEventListener('click', async () => {
    completeBtn.disabled = true;
    completeBtn.textContent = 'Submitting…';

    const score = verdictChosen === 'attack' ? 100 : 0;
    const flags = Array.from(reviewed);

    try {
      const res = await fetch(completeUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          score,
          flags_found: flags,
          good_decisions: verdictChosen === 'attack'
            ? ['Correctly identified social engineering attack', 'Chose to hang up and verify independently']
            : [],
          mistakes: verdictChosen !== 'attack'
            ? ['Trusted the caller without independent verification']
            : [],
          recommendations: [
            'Never share OTPs or verification codes over the phone',
            'Always hang up and call back through an official number you find yourself',
            'Urgency on the phone is a manipulation tactic — slow down and verify',
          ],
          time_spent_seconds: elapsed,
          skills_developed: ['Social engineering detection', 'Caller verification', 'OTP security awareness'],
        }),
      });
      const data = await res.json();
      if (data.redirect) window.location.href = data.redirect;
    } catch {
      completeBtn.disabled = false;
      completeBtn.textContent = 'Complete simulation';
      alert('Could not submit. Please try again.');
    }
  });
})();
