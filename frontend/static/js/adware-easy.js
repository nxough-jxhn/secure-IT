(function () {
  const config = window.ADWARE_EASY || {};
  const hotspots = document.querySelectorAll('.adware-hotspot[data-indicator]');
  const indicatorCount = document.getElementById('indicator-count');
  const indicatorList = document.getElementById('indicator-list');
  const completeBtn = document.getElementById('complete-easy');
  const verdictSafe = document.getElementById('verdict-safe');
  const verdictDanger = document.getElementById('verdict-danger');
  const timer = document.getElementById('timer');

  const modal = document.getElementById('adware-modal');
  const modalClose = document.getElementById('adware-modal-close');
  const modalBackdrop = document.getElementById('adware-modal-backdrop');
  const modalTitle = document.getElementById('adware-modal-title');
  const modalDesc = document.getElementById('adware-modal-desc');
  const modalWrong = document.getElementById('adware-modal-wrong');
  const modalCorrect = document.getElementById('adware-modal-correct');

  const indicatorMap = Object.fromEntries((config.indicators || []).map((item) => [item.element, item]));
  const total = config.totalIndicators || hotspots.length;
  const acknowledged = new Set();
  let startTime = Date.now();

  function updateTimer() {
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    if (timer) {
      timer.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }
  }

  setInterval(updateTimer, 1000);

  function populateIndicators() {
    if (!indicatorList) return;
    const indicators = config.indicators || [];
    indicatorList.innerHTML = indicators.map((ind, idx) => `
      <div class="adware-indicator" data-indicator="${ind.element}">
        <span class="adware-indicator__number">${idx + 1}</span>
        <div class="adware-indicator__content">
          <div class="adware-indicator__title">${ind.title || ind.element}</div>
          <div class="adware-indicator__desc">${ind.description || ''}</div>
        </div>
      </div>
    `).join('');
  }

  function updateProgress() {
    if (indicatorCount) {
      indicatorCount.textContent = `${acknowledged.size} / ${total} reviewed`;
    }
    if (completeBtn) {
      completeBtn.disabled = acknowledged.size < total;
    }
    document.querySelectorAll('.adware-indicator').forEach((card) => {
      if (acknowledged.has(card.dataset.indicator)) {
        card.classList.add('is-reviewed');
      }
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
      if (!acknowledged.has(id)) {
        acknowledged.add(id);
        node.classList.add('is-reviewed');
        updateProgress();
      }
      openModal(id);
    });
  });

  modalClose?.addEventListener('click', closeModal);
  modalBackdrop?.addEventListener('click', (event) => {
    if (event.target === modalBackdrop) {
      closeModal();
    }
  });
  document.getElementById('adware-modal-dialog')?.addEventListener('click', (event) => event.stopPropagation());

  verdictSafe?.addEventListener('click', () => {
    alert('This is actually an adware-style installer. Review the warning signs before proceeding.');
  });

  verdictDanger?.addEventListener('click', () => {
    if (acknowledged.size >= total) {
      alert('Correct! This looks like adware. Click complete to finish.');
    } else {
      alert('Good instinct. Review the remaining indicators first.');
    }
  });

  completeBtn?.addEventListener('click', async () => {
    if (acknowledged.size < total) return;
    completeBtn.disabled = true;
    completeBtn.textContent = 'Saving...';
    try {
      const response = await fetch(config.completeUrl, {method: 'POST', headers: {'Content-Type': 'application/json'}});
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