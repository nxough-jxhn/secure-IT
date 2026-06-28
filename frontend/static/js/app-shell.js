(function () {
  const sidebar = document.getElementById('profile-sidebar');
  if (!sidebar) return;

  const toggles = [
    document.getElementById('header-progress-toggle'),
    document.getElementById('header-progress-toggle-mobile'),
  ].filter(Boolean);

  if (!toggles.length) return;

  const storageKey = 'secure-it-profile-sidebar-open';

  function readStorage() {
    try {
      return localStorage.getItem(storageKey);
    } catch (error) {
      return null;
    }
  }

  function writeStorage(open) {
    try {
      localStorage.setItem(storageKey, open ? '1' : '0');
    } catch (error) {
      // Ignore storage-restricted browsers.
    }
  }

  function setOpen(open) {
    sidebar.classList.toggle('is-open', open);
    document.body.classList.toggle('profile-sidebar-open', open);

    toggles.forEach((toggle) => {
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.classList.toggle('is-active', open);
    });

    writeStorage(open);
  }

  toggles.forEach((toggle) => {
    toggle.addEventListener('click', () => {
      setOpen(!sidebar.classList.contains('is-open'));
    });
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && sidebar.classList.contains('is-open')) {
      setOpen(false);
    }
  });

  if (readStorage() === '1') {
    setOpen(true);
  }
})();
