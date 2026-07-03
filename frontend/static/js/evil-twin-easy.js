(function () {
  const config = window.EVIL_TWIN_EASY || {};
  const hotspots = document.querySelectorAll('.evil-twin-hotspot[data-indicator]');
  const indicatorCount = document.getElementById('indicator-count');
  const indicatorList = document.getElementById('indicator-list');
  const completeBtn = document.getElementById('complete-easy');
  const timer = document.getElementById('evil-twin-timer');
  const verdictSafe = document.getElementById('verdict-safe');
  const verdictDanger = document.getElementById('verdict-danger');
  const modal = document.getElementById('evil-twin-modal');
  const modalClose = document.getElementById('evil-twin-modal-close');
  const modalBackdrop = document.getElementById('evil-twin-modal-backdrop');
  const modalTitle = document.getElementById('evil-twin-modal-title');
  const modalDesc = document.getElementById('evil-twin-modal-desc');
  const modalWrong = document.getElementById('evil-twin-modal-wrong');
  const modalCorrect = document.getElementById('evil-twin-modal-correct');

  const indicatorMap = Object.fromEntries((config.indicators || []).map((item) => [item.element, item]));
  const total = Math.max(config.totalIndicators || 0, hotspots.length);
  const reviewedNodes = new Set();
  const reviewedIndicators = new Set();
  let startTime = Date.now();

  function updateTimer() {
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    if (timer) timer.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  }

  setInterval(updateTimer, 1000);

  function populateIndicators() {
    if (!indicatorList) return;
    indicatorList.innerHTML = (config.indicators || []).map((ind, idx) => `
      <div class="evil-twin-indicator" data-indicator="${ind.element}">
        <span class="evil-twin-indicator__number">${idx + 1}</span>
        <div class="evil-twin-indicator__content">
          <div class="evil-twin-indicator__title">${ind.title || ind.element}</div>
          <div class="evil-twin-indicator__desc">${ind.description || ''}</div>
        </div>
      </div>
    `).join('');
  }

  function updateProgress() {
    const reviewedCount = reviewedNodes.size;
    if (indicatorCount) indicatorCount.textContent = `${reviewedCount} / ${total} reviewed`;
    if (completeBtn) completeBtn.disabled = reviewedCount < total;
    document.querySelectorAll('.evil-twin-indicator').forEach((card) => {
      if (reviewedIndicators.has(card.dataset.indicator)) card.classList.add('is-reviewed');
    });
  }

  function openModal(indicatorId) {
    const data = indicatorMap[indicatorId];
    if (!data || !modal) return;
    modalTitle.textContent = data.title || 'Red flag';
    modalDesc.textContent = data.description || '';
    modalWrong.textContent = data.wrong || '';
    modalCorrect.textContent = data.correct || '';
    modal.hidden = false;
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    if (!modal) return;
    modal.hidden = true;
    document.body.style.overflow = '';
  }

  hotspots.forEach((node) => {
    node.addEventListener('click', (event) => {
      event.preventDefault();
      event.stopPropagation();
      const id = node.dataset.indicator;
      if (!id) return;
      if (!reviewedNodes.has(node)) {
        reviewedNodes.add(node);
        if (id) reviewedIndicators.add(id);
        node.classList.add('is-reviewed');
        updateProgress();
      }
      openModal(id);
    });
  });

  modalClose?.addEventListener('click', closeModal);
  modalBackdrop?.addEventListener('click', (event) => {
    if (event.target === modalBackdrop) closeModal();
  });
  document.getElementById('evil-twin-modal-dialog')?.addEventListener('click', (event) => event.stopPropagation());

  verdictSafe?.addEventListener('click', () => {
    alert('The suspicious hotspot is not safe. Review the indicators before proceeding.');
  });

  verdictDanger?.addEventListener('click', () => {
    if (reviewedNodes.size >= total) {
      alert('Correct — the suspicious network is an evil twin or rogue hotspot.');
    } else {
      alert('Good instinct. Review the remaining risk indicators first.');
    }
  });

  completeBtn?.addEventListener('click', async () => {
    if (reviewedNodes.size < total) return;
    completeBtn.disabled = true;
    completeBtn.textContent = 'Saving...';
    try {
      const response = await fetch(config.completeUrl, { method: 'POST', headers: { 'Content-Type': 'application/json' } });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.error || 'Could not save progress.');
      window.location.href = data.redirect || config.redirectUrl;
    } catch (error) {
      completeBtn.disabled = false;
      completeBtn.textContent = 'Complete simulation';
      alert(error.message || 'Please try again.');
    }
  });

  populateIndicators();
  updateProgress();
})();