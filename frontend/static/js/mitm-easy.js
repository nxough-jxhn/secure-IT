(function () {
  'use strict';

  const config = window.MITM_EASY || {};

  /* ── DOM refs ── */
  const hotspots      = document.querySelectorAll('.mitm-hotspot[data-indicator]');
  const indicatorList = document.getElementById('mitm-indicator-list');
  const countEl       = document.getElementById('mitm-indicator-count');
  const completeBtn   = document.getElementById('mitm-complete-btn');
  const timerEl       = document.getElementById('mitm-timer');
  const clockEl       = document.getElementById('mitm-clock');

  const modal         = document.getElementById('mitm-modal');
  const modalClose    = document.getElementById('mitm-modal-close');
  const modalBackdrop = document.getElementById('mitm-modal-backdrop');
  const modalTitle    = document.getElementById('mitm-modal-title');
  const modalDesc     = document.getElementById('mitm-modal-desc');
  const modalWrong    = document.getElementById('mitm-modal-wrong');
  const modalCorrect  = document.getElementById('mitm-modal-correct');
  const modalTip      = document.getElementById('mitm-modal-tip');
  const modalTipText  = document.getElementById('mitm-modal-tip-text');

  const verdictSafe   = document.getElementById('verdict-safe');
  const verdictDanger = document.getElementById('verdict-danger');

  /* ── State ── */
  const indicatorMap = Object.fromEntries(
    (config.indicators || []).map((item) => [item.element, item])
  );
  const total = config.totalIndicators || hotspots.length;
  const acknowledged = new Set();
  const startTime = Date.now();

  /* ── Elapsed timer ── */
  setInterval(() => {
    const elapsed  = Math.floor((Date.now() - startTime) / 1000);
    const minutes  = Math.floor(elapsed / 60);
    const seconds  = elapsed % 60;
    if (timerEl) {
      timerEl.textContent =
        String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');
    }
  }, 1000);

  /* ── Taskbar clock ── */
  function updateClock() {
    if (!clockEl) return;
    const now = new Date();
    let h = now.getHours();
    const m = String(now.getMinutes()).padStart(2, '0');
    const ampm = h >= 12 ? 'PM' : 'AM';
    h = h % 12 || 12;
    clockEl.textContent = `${h}:${m} ${ampm}`;
  }
  updateClock();
  setInterval(updateClock, 10000);

  /* ── Build indicator sidebar ── */
  function populateIndicators() {
    if (!indicatorList) return;
    indicatorList.innerHTML = (config.indicators || []).map((ind, idx) => `
      <div class="mitm-indicator-item" data-indicator="${ind.element}">
        <div class="mitm-indicator-item__head">
          <span class="mitm-indicator-item__num">${idx + 1}</span>
          <span class="mitm-indicator-item__name">${ind.title || ind.element}</span>
        </div>
        <div class="mitm-indicator-item__status">Not reviewed yet</div>
      </div>
    `).join('');
  }

  /* ── Update progress state ── */
  function updateProgress() {
    if (countEl) countEl.textContent = `${acknowledged.size} / ${total} reviewed`;
    if (completeBtn) completeBtn.disabled = acknowledged.size < total;

    document.querySelectorAll('.mitm-indicator-item').forEach((card) => {
      const id = card.dataset.indicator;
      const reviewed = acknowledged.has(id);
      card.classList.toggle('is-reviewed', reviewed);
      const statusEl = card.querySelector('.mitm-indicator-item__status');
      if (statusEl) statusEl.textContent = reviewed ? '✓ Reviewed' : 'Not reviewed yet';
    });
  }

  /* ── Modal ── */
  function openModal(indicatorId) {
    const data = indicatorMap[indicatorId];
    if (!data || !modal) return;

    if (modalTitle)   modalTitle.textContent  = data.title || 'Red flag';
    if (modalDesc)    modalDesc.textContent   = data.description || '';
    if (modalWrong)   modalWrong.textContent  = data.wrong || '';
    if (modalCorrect) modalCorrect.textContent = data.correct || '';

    if (data.tip && modalTip && modalTipText) {
      modalTipText.innerHTML = data.tip;
      modalTip.hidden = false;
    } else if (modalTip) {
      modalTip.hidden = true;
    }

    modal.hidden = false;
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    if (!modal) return;
    modal.hidden = true;
    document.body.style.overflow = '';
  }

  /* ── Hotspot clicks ── */
  hotspots.forEach((node) => {
    node.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      const id = node.dataset.indicator;
      if (!id) return;
      if (!acknowledged.has(id)) {
        acknowledged.add(id);
        node.classList.add('is-reviewed');
        updateProgress();
      }
      openModal(id);
    });
  });

  /* ── Modal close handlers ── */
  modalClose?.addEventListener('click', (e) => { e.stopPropagation(); closeModal(); });
  modalBackdrop?.addEventListener('click', (e) => {
    if (e.target === modalBackdrop) { e.stopPropagation(); closeModal(); }
  });
  document.querySelector('.mitm-modal__dialog')?.addEventListener('click', (e) => e.stopPropagation());
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal && !modal.hidden) closeModal();
  });

  /* ── Verdict buttons ── */
  verdictSafe?.addEventListener('click', () => {
    alert('This connection is NOT safe! Review all the red flags to understand why — then complete the simulation.');
  });

  verdictDanger?.addEventListener('click', () => {
    if (acknowledged.size >= total) {
      alert('Correct — this connection is compromised. Click "Complete simulation" to finish.');
    } else {
      alert('Good instinct! Review all the red flags first before completing.');
    }
  });

  /* ── Complete button ── */
  completeBtn?.addEventListener('click', async () => {
    if (acknowledged.size < total) return;
    completeBtn.disabled   = true;
    completeBtn.textContent = 'Saving…';

    try {
      const res  = await fetch(config.completeUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || 'Could not save progress.');
      window.location.href = data.redirect || config.redirectUrl;
    } catch (err) {
      completeBtn.disabled   = false;
      completeBtn.textContent = 'Complete simulation';
      alert(err.message || 'Something went wrong — please try again.');
    }
  });

  /* ── Init ── */
  populateIndicators();
  updateProgress();
})();
