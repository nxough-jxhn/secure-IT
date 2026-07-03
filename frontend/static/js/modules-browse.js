/**
 * modules-browse.js
 * Wires the "View all →" buttons on the modules page to the
 * shared cr-overlay modal system (same HTML/CSS as simulations page).
 * Does NOT require Three.js.
 */

// ── Data ────────────────────────────────────────────────────
const raw = document.getElementById('cr-data');
if (!raw) { console.error('modules-browse: #cr-data not found'); }
const categories = raw ? JSON.parse(raw.textContent) : [];

// ── Modal elements ──────────────────────────────────────────
const overlay       = document.getElementById('cr-overlay');
const modalBadge    = document.getElementById('cr-modal-badge');
const modalTitle    = document.getElementById('cr-modal-title');
const modalCount    = document.getElementById('cr-modal-count');
const modalDesc     = document.getElementById('cr-modal-desc');
const miniNum       = document.getElementById('cr-mini-num');
const miniName      = document.getElementById('cr-mini-name');
const sidebarPillar = document.getElementById('cr-sidebar-pillar');
const missionTrack  = document.getElementById('cr-mission-track');
const missionDots   = document.getElementById('cr-mission-dots');
const missionCounter = document.getElementById('cr-mission-counter');
const missionPrevBtn = document.getElementById('cr-mission-prev');
const missionNextBtn = document.getElementById('cr-mission-next');
const closeBtn      = document.getElementById('cr-close');
const catPrevBtn    = document.getElementById('cr-cat-prev');
const catNextBtn    = document.getElementById('cr-cat-next');

// ── State ───────────────────────────────────────────────────
let currentCategoryIndex = 0;
let currentMissions      = [];
let currentMissionIndex  = 0;

// ── Short category descriptions (same as range-grid.js) ─────
const shortDesc = [
  'Social-based attacks exploit human psychology, trust, and behavior patterns to manipulate individuals into divulging confidential information or performing actions that compromise security.',
  'Malware-based attacks use malicious software designed to infiltrate, damage, or gain unauthorized access to computer systems through various forms of harmful code.',
  'Network-based attacks target the infrastructure and protocols that enable communication between systems, exploiting vulnerabilities in network services and configurations.',
  'Injection-based attacks exploit vulnerabilities in application input handling by inserting malicious code or commands to access restricted data or compromise system integrity.',
];

const nums = ['01', '02', '03', '04'];

const missionIcons = [
  `<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#4b5563" stroke-width="1.5"><rect x="3" y="4" width="18" height="14" rx="2"/><path d="M8 20h8M12 18v2"/></svg>`,
  `<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#4b5563" stroke-width="1.5"><path d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h18"/></svg>`,
  `<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#4b5563" stroke-width="1.5"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>`,
  `<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#4b5563" stroke-width="1.5"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>`,
];

// ── Sidebar SVG (identical to range-grid.js) ────────────────
function buildSidebarSVG(label, index) {
  return `
  <svg width="90" height="220" viewBox="0 0 90 220" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="spF${index}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#e8e8e8"/>
        <stop offset="8%" stop-color="#aaaaaa"/>
        <stop offset="30%" stop-color="#444444"/>
        <stop offset="65%" stop-color="#1c1c1c"/>
        <stop offset="100%" stop-color="#080808"/>
      </linearGradient>
      <linearGradient id="spS${index}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#cccccc"/>
        <stop offset="8%" stop-color="#888888"/>
        <stop offset="30%" stop-color="#333333"/>
        <stop offset="65%" stop-color="#141414"/>
        <stop offset="100%" stop-color="#060606"/>
      </linearGradient>
      <linearGradient id="spT${index}" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#ffffff"/>
        <stop offset="40%" stop-color="#d8d8d8"/>
        <stop offset="100%" stop-color="#aaaaaa"/>
      </linearGradient>
      <filter id="spG${index}" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="3" result="blur"/>
        <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
    </defs>
    <polygon points="70,8 90,18 90,210 70,200" fill="url(#spS${index})"/>
    <rect x="0" y="8" width="70" height="192" fill="url(#spF${index})"/>
    <polygon points="0,8 70,8 90,18 20,18" fill="url(#spT${index})"/>
    <line x1="1" y1="9" x2="1" y2="199" stroke="#000" stroke-width="2" opacity="0.4"/>
    <line x1="0" y1="8" x2="0" y2="200" stroke="#00ff9f" stroke-width="1.5" opacity="0.7"/>
    <line x1="0" y1="8" x2="70" y2="8" stroke="#00ff9f" stroke-width="1" opacity="0.45"/>
    <text x="35" y="104" text-anchor="middle"
      font-family="Manrope,sans-serif" font-size="7" font-weight="700"
      letter-spacing="3" fill="#ffffff" opacity="0.9"
      transform="rotate(-90,35,104)">${label.toUpperCase().slice(0, 22)}</text>
    <ellipse cx="40" cy="208" rx="38" ry="6" fill="#00ff9f" opacity="0.22" filter="url(#spG${index})"/>
    <ellipse cx="40" cy="210" rx="28" ry="4" fill="#00ff9f" opacity="0.32"/>
  </svg>`;
}

// ── Show a mission card in the modal ────────────────────────
function showMissionAtIndex(index) {
  if (!currentMissions.length) return;
  currentMissionIndex = Math.max(0, Math.min(index, currentMissions.length - 1));
  const mission = currentMissions[currentMissionIndex];
  const num  = String(currentMissionIndex + 1).padStart(2, '0');
  const icon = missionIcons[currentMissionIndex % missionIcons.length];

  missionTrack.style.opacity = '0';
  missionTrack.style.transform = 'translateX(20px)';

  setTimeout(() => {
    const done   = mission.state === 'completed';
    const imgHtml = mission.image
      ? `<img src="/static/${mission.image}" alt="${mission.name}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center;border-radius:inherit;">`
      : (done ? icon.replace('stroke="#4b5563"', 'stroke="#00ff9f"') : icon);

    missionTrack.innerHTML = `
      <a href="/simulations/${mission.id}" class="cr-mission-row${done ? ' cr-mission-row--done' : ''}">
        <div class="cr-mission-row__img" style="position:relative;overflow:hidden;">
          <div class="cr-mission-row__img-grid"></div>
          ${imgHtml}
        </div>
        <span class="cr-mission-row__num">${num}</span>
        <div class="cr-mission-row__info">
          <div class="cr-mission-row__cat">${mission.category_label || ''}</div>
          <div class="cr-mission-row__name">${mission.name}</div>
          <div class="cr-mission-row__desc">${mission.short_description || 'Interactive simulation exercise'}</div>
          <div class="cr-mission-row__status${done ? ' cr-mission-row__status--done' : ''}">${done ? '[completed]' : '[not started]'}</div>
        </div>
        <div class="cr-mission-row__meta">
          <div class="cr-mission-row__stat">
            <span class="cr-mission-row__stat-label">objectives</span>
            <span class="cr-mission-row__stat-val">${mission.objectives_count || 0}</span>
          </div>
          <div class="cr-mission-row__stat">
            <span class="cr-mission-row__stat-label">time</span>
            <span class="cr-mission-row__stat-val">${mission.estimated_minutes || 0}m</span>
          </div>
          <div class="cr-mission-row__arrow">→</div>
        </div>
      </a>`;

    missionTrack.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    missionTrack.style.opacity    = '1';
    missionTrack.style.transform  = 'translateX(0)';
  }, 120);

  // Dots
  missionDots.querySelectorAll('.cr-modal__carousel-dot').forEach((dot, i) => {
    dot.classList.toggle('is-active', i === currentMissionIndex);
  });

  missionCounter.textContent = `${currentMissionIndex + 1} / ${currentMissions.length}`;
  missionPrevBtn.disabled = currentMissionIndex === 0;
  missionNextBtn.disabled = currentMissionIndex === currentMissions.length - 1;
}

// ── Open the modal for a category index ─────────────────────
function openCategory(index) {
  const cat = categories[index];
  if (!cat) return;

  currentCategoryIndex = index;

  // Arrow visibility
  catPrevBtn.style.opacity       = index === 0 ? '0.25' : '1';
  catPrevBtn.style.pointerEvents = index === 0 ? 'none' : 'auto';
  catNextBtn.style.opacity       = index === categories.length - 1 ? '0.25' : '1';
  catNextBtn.style.pointerEvents = index === categories.length - 1 ? 'none' : 'auto';

  // Populate header
  miniNum.textContent     = nums[index] || String(index + 1).padStart(2, '0');
  miniName.textContent    = cat.label;
  modalBadge.textContent  = `Category ${nums[index] || index + 1}`;
  modalTitle.textContent  = cat.label;
  modalDesc.textContent   = shortDesc[index] || '';
  modalCount.textContent  = `${cat.missions.length} ATTACKS ——`;
  sidebarPillar.innerHTML = buildSidebarSVG(cat.label, index);

  // Tag missions with their category label
  currentMissions = cat.missions.map(m => ({
    ...m,
    category_label: cat.label.toUpperCase(),
  }));
  currentMissionIndex = 0;

  // Build dots
  missionDots.innerHTML = currentMissions
    .map((_, i) => `<span class="cr-modal__carousel-dot${i === 0 ? ' is-active' : ''}" data-i="${i}"></span>`)
    .join('');

  missionDots.querySelectorAll('.cr-modal__carousel-dot').forEach(dot => {
    dot.addEventListener('click', () => showMissionAtIndex(parseInt(dot.dataset.i)));
  });

  // Reset track state
  missionTrack.style.transition = 'none';
  missionTrack.style.opacity    = '1';
  missionTrack.style.transform  = 'translateX(0)';

  showMissionAtIndex(0);
  overlay.classList.add('is-open');
  requestAnimationFrame(() => overlay.classList.add('is-active'));
}

// ── Close the modal ──────────────────────────────────────────
function closeModal() {
  overlay.classList.remove('is-active');
  setTimeout(() => {
    overlay.classList.remove('is-open');
    missionTrack.innerHTML = '';
    missionDots.innerHTML  = '';
  }, 320);
}

// ── Event listeners ──────────────────────────────────────────
closeBtn?.addEventListener('click', closeModal);
overlay?.addEventListener('click', e => {
  if (e.target === overlay) closeModal();
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && overlay?.classList.contains('is-open')) closeModal();
});

missionPrevBtn?.addEventListener('click', () => showMissionAtIndex(currentMissionIndex - 1));
missionNextBtn?.addEventListener('click', () => showMissionAtIndex(currentMissionIndex + 1));

catPrevBtn?.addEventListener('click', () => {
  if (currentCategoryIndex > 0) openCategory(currentCategoryIndex - 1);
});
catNextBtn?.addEventListener('click', () => {
  if (currentCategoryIndex < categories.length - 1) openCategory(currentCategoryIndex + 1);
});

// ── Wire each "View all →" button to its category index ──────
document.querySelectorAll('.mb-cat__view-all').forEach(btn => {
  const idx = parseInt(btn.dataset.catIndex, 10);
  btn.addEventListener('click', () => openCategory(idx));
});
