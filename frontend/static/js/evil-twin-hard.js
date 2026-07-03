(function () {
  const eventFeed = document.getElementById('event-feed');
  const flagModeBtn = document.getElementById('flag-mode-btn');
  const submitBtn = document.getElementById('submit-report-btn');
  const networkList = document.getElementById('network-list');
  let flagMode = false;
  let flagged = 0;

  function addEvent(message) {
    if (!eventFeed) return;
    const item = document.createElement('li');
    item.className = 'evil-twin-hard-event';
    item.textContent = message;
    eventFeed.prepend(item);
  }

  flagModeBtn?.addEventListener('click', () => {
    flagMode = !flagMode;
    flagModeBtn.textContent = flagMode ? '🗑 Cancel flag' : '🚩 Flag sign';
    addEvent(flagMode ? 'Flag mode enabled.' : 'Flag mode disabled.');
  });

  networkList?.addEventListener('click', (event) => {
    const card = event.target.closest('.evil-twin-hard-network');
    if (!card || !flagMode) return;
    flagged += 1;
    card.classList.add('is-flagged');
    addEvent('Suspicious hotspot flagged.');
  });

  submitBtn?.addEventListener('click', () => {
    if (flagged < 2) {
      alert('Flag at least 2 suspicious signs before submitting.');
      return;
    }
    alert('Incident report submitted. The suspicious hotspot appears to be a rogue access point.');
  });
})();