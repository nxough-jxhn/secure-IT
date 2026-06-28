(function () {
  const config = window.SQLI_EASY || {};
  const hotspots = document.querySelectorAll('.sqli-hotspot[data-indicator]');
  const progressEl = document.getElementById('indicator-progress');
  const completeBtn = document.getElementById('complete-easy');
  const modal = document.getElementById('phish-modal');
  const modalClose = document.getElementById('phish-modal-close');
  const modalBackdrop = document.getElementById('phish-modal-backdrop');
  const modalTitle = document.getElementById('phish-modal-title');
  const modalDesc = document.getElementById('phish-modal-desc');
  const modalWrongLabel = document.getElementById('phish-modal-wrong-label');
  const modalWrong = document.getElementById('phish-modal-wrong');
  const modalCorrectLabel = document.getElementById('phish-modal-correct-label');
  const modalCorrect = document.getElementById('phish-modal-correct');
  const modalTip = document.getElementById('phish-modal-tip');
  const modalTipText = document.getElementById('phish-modal-tip-text');
  const modalCompare = document.getElementById('phish-modal-compare');
  const revealItems = modal?.querySelectorAll('.phish-modal__reveal') || [];

  const usernameInput = document.getElementById('username-input');
  const passwordInput = document.getElementById('password-input');
  const queryPreview = document.getElementById('query-preview');
  const loginForm = document.getElementById('login-form');
  const loginError = document.getElementById('login-error');
  const loginStage = document.getElementById('login-stage');
  const adminDashboard = document.getElementById('admin-dashboard');
  const insertFullBtn = document.getElementById('insert-full-payload');
  const labHint = document.getElementById('lab-hint');

  const OPEN_MS = 480;
  const CLOSE_MS = 200;
  const indicatorMap = Object.fromEntries(
    (config.indicators || []).map((item) => [item.element, item])
  );
  const total = config.totalIndicators || hotspots.length;
  const acknowledged = new Set();
  let bypassAchieved = false;
  let lastFocused = null;
  let isAnimating = false;
  let openTimer = null;
  let closeTimer = null;

  function normalizePayload(value) {
    return String(value || '').trim().toLowerCase().replace(/\s+/g, ' ');
  }

  function isValidPayload(value) {
    const normalized = normalizePayload(value);
    return (
      normalized.includes("'") &&
      normalized.includes('or') &&
      (normalized.includes("'1'='1") || normalized.includes('1=1'))
    );
  }

  function renderQueryPreview() {
    if (!queryPreview) return;
    const username = usernameInput?.value || '';
    const password = passwordInput?.value || '';
    const query = (config.queryTemplate || '')
      .replace('{username}', username || '…')
      .replace('{password}', password || '…');
    queryPreview.textContent = query;
  }

  function updateProgress() {
    if (progressEl) {
      progressEl.textContent = `${acknowledged.size} / ${total} indicators reviewed`;
    }
    updateCompleteState();
  }

  function updateCompleteState() {
    if (!completeBtn) return;
    completeBtn.disabled = acknowledged.size < total || !bypassAchieved;
  }

  function resetRevealAnimation() {
    revealItems.forEach((el) => {
      el.style.setProperty('--stagger', el.dataset.stagger || '0');
      el.style.animation = 'none';
      el.style.opacity = '0';
      el.style.transform = 'translateY(10px)';
    });
  }

  function playRevealAnimation() {
    requestAnimationFrame(() => {
      revealItems.forEach((el) => {
        el.style.animation = '';
        el.style.opacity = '';
        el.style.transform = '';
      });
    });
  }

  function populateModal(data) {
    modalTitle.textContent = data.title || 'Vulnerability';
    modalDesc.textContent = data.description || '';
    modalWrongLabel.textContent = data.wrong_label || 'What you see';
    modalWrong.textContent = data.wrong || '';
    modalCorrectLabel.textContent = data.correct_label || 'What you should expect';
    modalCorrect.textContent = data.correct || '';

    if (data.tip) {
      modalTipText.innerHTML = data.tip;
      modalTip.hidden = false;
    } else {
      modalTipText.innerHTML = '';
      modalTip.hidden = true;
    }

    if (modalCompare) modalCompare.hidden = false;
  }

  function finishOpen() {
    if (!modal) return;
    modal.classList.add('is-open');
    modal.classList.remove('is-opening');
    isAnimating = false;
    playRevealAnimation();
    modalClose?.focus();
  }

  function showModalShell() {
    if (!modal) return;

    window.clearTimeout(openTimer);
    window.clearTimeout(closeTimer);
    isAnimating = true;

    modal.hidden = false;
    modal.classList.remove('is-closing', 'is-open', 'is-opening');
    resetRevealAnimation();
    document.body.classList.add('phish-modal-open');

    requestAnimationFrame(() => {
      modal.classList.add('is-opening');
      openTimer = window.setTimeout(finishOpen, OPEN_MS);
    });
  }

  function openModal(indicatorId) {
    const data = indicatorMap[indicatorId];
    if (!data || !modal) return;

    populateModal(data);

    if (modal.hidden) {
      showModalShell();
      return;
    }

    if (isAnimating) return;

    modal.classList.remove('is-open');
    resetRevealAnimation();
    requestAnimationFrame(() => {
      modal.classList.add('is-open');
      playRevealAnimation();
    });
  }

  function openErrorModal(message) {
    if (!modal) return;

    modalTitle.textContent = 'Could not save progress';
    modalDesc.textContent = message || 'Please try again.';
    modalWrongLabel.textContent = '';
    modalWrong.textContent = '';
    modalCorrectLabel.textContent = '';
    modalCorrect.textContent = '';
    modalTip.hidden = true;
    if (modalCompare) modalCompare.hidden = true;

    if (modal.hidden) {
      showModalShell();
      return;
    }

    if (isAnimating) return;

    modal.classList.remove('is-open');
    resetRevealAnimation();
    requestAnimationFrame(() => {
      modal.classList.add('is-open');
      playRevealAnimation();
    });
  }

  function closeModal() {
    if (!modal || modal.hidden || isAnimating) return;
    if (!modal.classList.contains('is-open')) return;

    isAnimating = true;
    modal.classList.remove('is-open', 'is-opening');
    modal.classList.add('is-closing');

    window.clearTimeout(closeTimer);
    closeTimer = window.setTimeout(() => {
      modal.hidden = true;
      modal.classList.remove('is-closing', 'is-opening');
      document.body.classList.remove('phish-modal-open');
      isAnimating = false;
      lastFocused?.focus();
    }, CLOSE_MS);
  }

  function acknowledgeIndicator(id) {
    if (!id || acknowledged.has(id)) return;
    acknowledged.add(id);
    document.querySelectorAll(`.sqli-hotspot[data-indicator="${id}"]`).forEach((node) => {
      node.classList.remove('is-pending');
      node.classList.add('is-reviewed');
    });
    updateProgress();
  }

  function handleHotspotClick(node, event) {
    event.preventDefault();
    event.stopPropagation();

    const id = node.dataset.indicator;
    if (!id) return;

    lastFocused = node;
    acknowledgeIndicator(id);
    openModal(id);
  }

  hotspots.forEach((node) => {
    node.classList.add('is-pending');
    node.addEventListener('click', (event) => handleHotspotClick(node, event));
  });

  document.querySelectorAll('.sqli-payload__chip[data-part]').forEach((chip) => {
    chip.addEventListener('click', (event) => {
      const part = chip.dataset.part || '';
      if (usernameInput) {
        usernameInput.value += part;
        usernameInput.dispatchEvent(new Event('input', { bubbles: true }));
      }

      if (chip.dataset.indicator) {
        handleHotspotClick(chip, event);
      }
    });
  });

  insertFullBtn?.addEventListener('click', () => {
    if (usernameInput) {
      usernameInput.value = config.validPayload || "' OR '1'='1' --";
      usernameInput.dispatchEvent(new Event('input', { bubbles: true }));
    }
  });

  usernameInput?.addEventListener('input', renderQueryPreview);
  passwordInput?.addEventListener('input', renderQueryPreview);

  loginForm?.addEventListener('submit', (event) => {
    event.preventDefault();
    if (loginError) loginError.hidden = true;

    const username = usernameInput?.value || '';
    if (!isValidPayload(username)) {
      if (loginError) {
        loginError.hidden = false;
        loginError.textContent =
          'Login failed. Try closing the username string with a quote, adding OR \'1\'=\'1, then commenting out the password check with --.';
      }
      return;
    }

    bypassAchieved = true;
    if (loginStage) loginStage.hidden = true;
    if (adminDashboard) adminDashboard.hidden = false;
    if (labHint) {
      labHint.innerHTML =
        'Authentication bypassed. Review the simulated admin dashboard, then complete the easy simulation.';
    }
    updateCompleteState();
  });

  modalClose?.addEventListener('click', (event) => {
    event.stopPropagation();
    closeModal();
  });

  modalBackdrop?.addEventListener('click', (event) => {
    if (event.target !== modalBackdrop) return;
    closeModal();
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && modal && !modal.hidden && !isAnimating) {
      closeModal();
    }
  });

  completeBtn?.addEventListener('click', async () => {
    if (acknowledged.size < total || !bypassAchieved) return;
    completeBtn.disabled = true;
    try {
      const response = await fetch(config.completeUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.error || 'Could not save progress.');
      window.location.href = data.redirect || config.redirectUrl;
    } catch (error) {
      completeBtn.disabled = false;
      openErrorModal(error.message || 'Please try again.');
    }
  });

  renderQueryPreview();
  updateProgress();
})();
