(function () {
  const config = window.PHISHING_EASY || {};
  const hotspots = document.querySelectorAll('.phish-hotspot[data-indicator]');
  const indicatorCount = document.getElementById('indicator-count');
  const indicatorList = document.getElementById('indicator-list');
  const completeBtn = document.getElementById('complete-easy');
  const verdictLegit = document.getElementById('verdict-legit');
  const verdictPhish = document.getElementById('verdict-phish');
  const timer = document.getElementById('timer');
  
  const modal = document.getElementById('phish-modal');
  const modalClose = document.getElementById('phish-modal-close');
  const modalBackdrop = document.getElementById('phish-modal-backdrop');
  const modalTitle = document.getElementById('phish-modal-title');
  const modalDesc = document.getElementById('phish-modal-desc');
  const modalWrong = document.getElementById('phish-modal-wrong');
  const modalCorrect = document.getElementById('phish-modal-correct');
  const modalTip = document.getElementById('phish-modal-tip');
  const modalTipText = document.getElementById('phish-modal-tip-text');

  const indicatorMap = Object.fromEntries(
    (config.indicators || []).map((item) => [item.element, item])
  );
  const total = config.totalIndicators || hotspots.length;
  const acknowledged = new Set();
  let startTime = Date.now();
  let timerInterval = null;

  // Timer
  function updateTimer() {
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    if (timer) {
      timer.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }
  }

  timerInterval = setInterval(updateTimer, 1000);

  // Populate indicator sidebar from config data
  function populateIndicators() {
    if (!indicatorList) return;
    
    const indicators = config.indicators || [];
    indicatorList.innerHTML = indicators.map((ind, idx) => `
      <div class="phish-indicator" data-indicator="${ind.element}">
        <span class="phish-indicator__number">${idx + 1}</span>
        <div class="phish-indicator__content">
          <div class="phish-indicator__title">${ind.title || ind.element}</div>
          <div class="phish-indicator__desc">${ind.description || ''}</div>
        </div>
        <span class="phish-indicator__icon">⚠</span>
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

    // Update indicator sidebar
    document.querySelectorAll('.phish-indicator').forEach(card => {
      const id = card.dataset.indicator;
      if (acknowledged.has(id)) {
        card.classList.add('is-reviewed');
      }
    });
  }

  let modalOpen = false;

  function openModal(indicatorId) {
    const data = indicatorMap[indicatorId];
    if (!data || !modal) return;

    modalTitle.textContent = data.title || 'Red flag';
    modalDesc.textContent = data.description || '';
    modalWrong.textContent = data.wrong || '';
    modalCorrect.textContent = data.correct || '';

    if (data.tip) {
      modalTipText.innerHTML = data.tip;
      modalTip.hidden = false;
    } else {
      modalTip.hidden = true;
    }

    modalOpen = true;
    modal.hidden = false;
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    if (!modal) return;
    modalOpen = false;
    modal.hidden = true;
    document.body.style.overflow = '';
  }

  // Hotspot clicks
  hotspots.forEach((node) => {
    node.addEventListener('click', (event) => {
      // Prevent the click from reaching the backdrop or body
      event.preventDefault();
      event.stopPropagation();
      event.stopImmediatePropagation();

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

  // Modal close — only respond to direct button/backdrop clicks
  modalClose?.addEventListener('click', (event) => {
    event.stopPropagation();
    closeModal();
  });

  modalBackdrop?.addEventListener('click', (event) => {
    // Only close when clicking the semi-transparent backdrop itself
    if (event.target === modalBackdrop) {
      event.stopPropagation();
      closeModal();
    }
  });

  // Prevent clicks inside the dialog from closing it
  document.getElementById('phish-modal-dialog')?.addEventListener('click', (event) => {
    event.stopPropagation();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && modal && !modal.hidden) {
      closeModal();
    }
  });

  // Verdict buttons
  verdictLegit?.addEventListener('click', () => {
    alert('This is actually a phishing email! Review the red flags to understand why.');
  });

  verdictPhish?.addEventListener('click', () => {
    if (acknowledged.size >= total) {
      alert('Correct! This is a phishing email. Click "Complete simulation" to finish.');
    } else {
      alert('Good instinct! Review all the red flags first before completing.');
    }
  });

  // Complete button
  completeBtn?.addEventListener('click', async () => {
    if (acknowledged.size < total) return;
    completeBtn.disabled = true;
    completeBtn.textContent = 'Saving...';
    
    try {
      const response = await fetch(config.completeUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.error || 'Could not save progress.');
      
      clearInterval(timerInterval);
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
