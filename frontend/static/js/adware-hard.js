(function () {
  const workspace = JSON.parse(document.getElementById('workspace-data')?.textContent || '{}');
  const eventFeed = document.getElementById('event-feed');
  const statusbarFlags = document.getElementById('statusbar-flags');
  const submitBtn = document.getElementById('submit-report-btn');
  const flagModeBtn = document.getElementById('flag-mode-btn');
  const popupCard = document.getElementById('popup-card');
  const taskLog = document.getElementById('task-log');
  let flagged = 0;
  let flagMode = false;

  function addEvent(message) {
    if (!eventFeed) return;
    const item = document.createElement('li');
    item.className = 'adware-hard-event';
    item.textContent = message;
    eventFeed.prepend(item);
  }

  function updateFlags() {
    if (statusbarFlags) {
      statusbarFlags.textContent = `${flagged} / ${workspace.signs?.length || 0} signs flagged`;
    }
    submitBtn.disabled = flagged < 2;
  }

  flagModeBtn?.addEventListener('click', () => {
    flagMode = !flagMode;
    flagModeBtn.textContent = flagMode ? '🗑 Cancel flag' : '🚩 Flag sign';
    addEvent(flagMode ? 'Flag mode enabled.' : 'Flag mode disabled.');
  });

  popupCard?.addEventListener('click', () => {
    if (!flagMode) return;
    flagged += 1;
    addEvent('Suspicious installer behavior flagged.');
    updateFlags();
  });

  submitBtn?.addEventListener('click', () => {
    if (flagged < 2) {
      alert('Flag at least 2 suspicious signs before submitting.');
      return;
    }
    alert('Incident report submitted. The popup appears to be adware-like and unsafe.');
  });

  updateFlags();
})();