import * as THREE from 'three';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';

const PRIMARY = 0x00ff9f;

// Read category data from template
const raw = document.getElementById('cr-data');
if (!raw) throw new Error('Category data not found');
const categories = JSON.parse(raw.textContent);

// Modal elements
const overlay = document.getElementById('cr-overlay');
const modal = document.getElementById('cr-modal');
const closeBtn = document.getElementById('cr-close');
const miniNum = document.getElementById('cr-mini-num');
const miniName = document.getElementById('cr-mini-name');
const modalTitle = document.getElementById('cr-modal-title');
const modalDesc = document.getElementById('cr-modal-desc');
// const carouselTrack = document.getElementById('cr-carousel-track');
// const prevBtn = document.getElementById('cr-prev');
// const nextBtn = document.getElementById('cr-next');
const modalBadge   = document.getElementById('cr-modal-badge');
const modalCount   = document.getElementById('cr-modal-count');
// const missionList  = document.getElementById('cr-mission-list');
const sidebarPillar = document.getElementById('cr-sidebar-pillar');

const missionIcons = [
  `<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#4b5563" stroke-width="1.5"><rect x="3" y="4" width="18" height="14" rx="2"/><path d="M8 20h8M12 18v2"/></svg>`,
  `<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#4b5563" stroke-width="1.5"><path d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h18"/></svg>`,
  `<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#4b5563" stroke-width="1.5"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>`,
  `<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#4b5563" stroke-width="1.5"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>`,
];

const missionTrack  = document.getElementById('cr-mission-track');
const missionDots   = document.getElementById('cr-mission-dots');
const missionCounter = document.getElementById('cr-mission-counter');
const missionPrevBtn = document.getElementById('cr-mission-prev');
const missionNextBtn = document.getElementById('cr-mission-next');

const catPrevBtn = document.getElementById('cr-cat-prev');
const catNextBtn = document.getElementById('cr-cat-next');

catPrevBtn.addEventListener('click', () => {
  if (currentCategoryIndex > 0) switchCategory(currentCategoryIndex - 1, 'prev');
});
catNextBtn.addEventListener('click', () => {
  if (currentCategoryIndex < categories.length - 1) switchCategory(currentCategoryIndex + 1, 'next');
});







const nums = ['01', '02', '03', '04'];
const diffColors = {
  beginner: 'cr-card__diff--beginner',
  intermediate: 'cr-card__diff--intermediate',
  advanced: 'cr-card__diff--advanced',
};
const shortDesc = [
  'Social-based attacks exploit human psychology, trust, and behavior patterns to manipulate individuals into divulging confidential information or performing actions that compromise security. These attacks often involve impersonation, deception, and emotional manipulation rather than technical exploits.',
  'Malware-based attacks use malicious software designed to infiltrate, damage, or gain unauthorized access to computer systems. These attacks can steal sensitive data, disrupt operations, or provide remote access to attackers through various forms of harmful code.',
  'Network-based attacks target the infrastructure and protocols that enable communication between systems. These attacks exploit vulnerabilities in network services, configurations, and data transmission to intercept, modify, or disrupt network traffic and gain unauthorized access.',
  'Injection-based attacks exploit vulnerabilities in application input handling by inserting malicious code or commands. These attacks manipulate how applications process user input to execute unauthorized operations, access restricted data, or compromise system integrity.',
];

// Pillar configurations — very close spacing, bigger appearance
const PILLARS = [
  {
    num: '01',
    label: categories[0]?.label || 'Social-Based Attacks',
    categoryIndex: 0,
    x: -3.3,
    z: -0.5,
    rotY: 0.38,
    height: 3,
  },
  {
    num: '02',
    label: categories[1]?.label || 'Malware-Based Attacks',
    categoryIndex: 1,
    x: -1.1,
    z: -0.2,
    rotY: 0.18,
    height: 4,
  },
  {
    num: '03',
    label: categories[2]?.label || 'Network-Based Attacks',
    categoryIndex: 2,
    x: 1.1,
    z: -0.2,
    rotY: -0.18,
    height: 4,
  },
  {
    num: '04',
    label: categories[3]?.label || 'Injection-Based Attacks',
    categoryIndex: 3,
    x: 3.3,
    z: -0.5,
    rotY: -0.38,
    height: 3,
  },
];

function switchCategory(newIndex, direction) {
  const cat = categories[newIndex];
  if (!cat) return;

  currentCategoryIndex = newIndex;

  // Update arrow states
  catPrevBtn.style.opacity = newIndex === 0 ? '0.25' : '1';
  catPrevBtn.style.pointerEvents = newIndex === 0 ? 'none' : 'auto';
  catNextBtn.style.opacity = newIndex === categories.length - 1 ? '0.25' : '1';
  catNextBtn.style.pointerEvents = newIndex === categories.length - 1 ? 'none' : 'auto';

  const inner = document.getElementById('cr-modal').querySelector('.cr-modal__inner');

  // Slide out
  inner.style.transition = 'opacity 0.25s ease, transform 0.25s ease';
  inner.style.opacity = '0';
  inner.style.transform = direction === 'next' ? 'translateX(-40px)' : 'translateX(40px)';

  setTimeout(() => {
    // Update all content
    miniNum.textContent     = nums[newIndex];
    miniName.textContent    = cat.label;
    modalBadge.textContent  = `Category ${nums[newIndex]}`;
    modalTitle.textContent  = cat.label;
    modalDesc.textContent   = shortDesc[newIndex] || '';
    modalCount.textContent  = `${cat.missions.length} ATTACKS ——`;
    sidebarPillar.innerHTML = buildSidebarSVG(cat.label, newIndex);

    currentMissions = cat.missions.map(m => ({
      ...m,
      category_label: cat.label.toUpperCase()
    }));
    currentMissionIndex = 0;

    missionDots.innerHTML = currentMissions.map((_, i) =>
      `<span class="cr-modal__carousel-dot${i === 0 ? ' is-active' : ''}" data-i="${i}"></span>`
    ).join('');

    missionDots.querySelectorAll('.cr-modal__carousel-dot').forEach(dot => {
      dot.addEventListener('click', () => showMissionAtIndex(parseInt(dot.dataset.i)));
    });

    missionTrack.style.transition = 'none';
    missionTrack.style.opacity = '1';
    missionTrack.style.transform = 'translateX(0)';

    showMissionAtIndex(0);

    // Slide in from opposite side
    inner.style.transition = 'none';
    inner.style.transform = direction === 'next' ? 'translateX(40px)' : 'translateX(-40px)';
    inner.style.opacity = '0';

    requestAnimationFrame(() => {
      inner.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
      inner.style.opacity = '1';
      inner.style.transform = 'translateX(0)';
    });
  }, 250);
}


function createSideGradientTexture(active) {
  const canvas = document.createElement('canvas');
  canvas.width = 64;
  canvas.height = 256;
  const ctx = canvas.getContext('2d');
  const grad = ctx.createLinearGradient(0, 0, 0, 256);

  if (active) {
    grad.addColorStop(0, '#b8ffe0');
    grad.addColorStop(0.12, '#3dffc0');
    grad.addColorStop(0.35, '#1a4034');
    grad.addColorStop(1, '#050505');
  } else {
    grad.addColorStop(0, '#ffffff');
    grad.addColorStop(0.06, '#f5f5f5');
    grad.addColorStop(0.18, '#cccccc');
    grad.addColorStop(0.38, '#5a5a5a');
    grad.addColorStop(0.62, '#222222');
    grad.addColorStop(1, '#050505');
  }

  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 64, 256);

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function createFrontFaceTexture(label, active, textScale = 1) {
  const canvas = document.createElement('canvas');
  canvas.width = 256;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');

  const grad = ctx.createLinearGradient(0, 0, 0, 512);
  if (active) {
    grad.addColorStop(0, '#d4ffe8');
    grad.addColorStop(0.15, '#1f4035');
    grad.addColorStop(1, '#050505');
  } else {
    grad.addColorStop(0, '#ffffff');
    grad.addColorStop(0.12, '#8a8a8a');
    grad.addColorStop(0.45, '#2a2a2a');
    grad.addColorStop(1, '#050505');
  }
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 256, 512);

  ctx.save();
  ctx.translate(128, 256);
  ctx.rotate(-Math.PI / 2);
  ctx.fillStyle = active ? '#00ff9f' : '#f5f5f5';
  ctx.font = `700 ${Math.round(24 * textScale)}px Manrope, Arial, sans-serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.shadowColor = active ? 'rgba(0,255,159,0.6)' : 'rgba(0,0,0,0.85)';
  ctx.shadowBlur = active ? 14 : 8;
  ctx.fillText(label.toUpperCase(), 0, 0);
  ctx.restore();

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function createTopFaceTexture(active) {
  const canvas = document.createElement('canvas');
  canvas.width = 256;
  canvas.height = 256;
  const ctx = canvas.getContext('2d');

  const grad = ctx.createRadialGradient(128, 128, 16, 128, 128, 150);
  grad.addColorStop(0, active ? '#ffffff' : '#f5f5f5');
  grad.addColorStop(0.55, active ? '#d8ffe8' : '#c8c8c8');
  grad.addColorStop(1, active ? '#8ae8c0' : '#9a9a9a');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 256, 256);

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function createAnimatedGrid() {
  // Grid removed per user request - return empty mesh
  const mesh = new THREE.Mesh(
    new THREE.PlaneGeometry(1, 1),
    new THREE.MeshBasicMaterial({ transparent: true, opacity: 0 })
  );
  mesh.rotation.x = -Math.PI / 2;
  mesh.position.y = 0.008;
  return mesh;
}

function createPillarGroup(config) {
  const group = new THREE.Group();
  const width = 0.9;
  const depth = 0.9;
  const { height, rotY } = config;

  const sideTexture = createSideGradientTexture(false);
  const sideMaterial = new THREE.MeshStandardMaterial({
    map: sideTexture,
    metalness: 0.48,
    roughness: 0.5,
  });

  const frontTexture = createFrontFaceTexture(config.label, false, 1);
  const frontMaterial = new THREE.MeshStandardMaterial({
    map: frontTexture,
    metalness: 0.35,
    roughness: 0.48,
  });

  const topTexture = createTopFaceTexture(false);
  const topMaterial = new THREE.MeshStandardMaterial({
    map: topTexture,
    metalness: 0.2,
    roughness: 0.22,
    emissive: 0x444444,
    emissiveIntensity: 0.42,
  });

  const bottomMaterial = new THREE.MeshStandardMaterial({ color: 0x030303 });

  const geometry = new THREE.BoxGeometry(width, height, depth);
  const mesh = new THREE.Mesh(geometry, [
    sideMaterial,
    sideMaterial,
    topMaterial,
    bottomMaterial,
    frontMaterial,
    sideMaterial,
  ]);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  mesh.position.y = height / 2;
  group.add(mesh);

  const edgeGeometry = new THREE.EdgesGeometry(geometry);
  const edgeMaterial = new THREE.LineBasicMaterial({
    color: PRIMARY,
    transparent: true,
    opacity: 0,
  });
  const edges = new THREE.LineSegments(edgeGeometry, edgeMaterial);
  edges.position.y = height / 2;
  group.add(edges);

  const glowGeometry = new THREE.CylinderGeometry(0.62, 1.05, 0.06, 32);
  const glowMaterial = new THREE.MeshBasicMaterial({
    color: PRIMARY,
    transparent: true,
    opacity: 0,
  });
  const baseGlow = new THREE.Mesh(glowGeometry, glowMaterial);
  baseGlow.position.y = 0.03;
  group.add(baseGlow);

  const topGlowGeometry = new THREE.PlaneGeometry(width * 1.15, depth * 1.15);
  const topGlowMaterial = new THREE.MeshBasicMaterial({
    color: PRIMARY,
    transparent: true,
    opacity: 0,
    side: THREE.DoubleSide,
  });
  const topGlow = new THREE.Mesh(topGlowGeometry, topGlowMaterial);
  topGlow.rotation.x = -Math.PI / 2;
  topGlow.position.y = height + 0.02;
  group.add(topGlow);

  group.rotation.y = rotY;
  group.userData.config = config;
  group.userData.mesh = mesh;
  group.userData.sideMaterial = sideMaterial;
  group.userData.sideTexture = sideTexture;
  group.userData.frontMaterial = frontMaterial;
  group.userData.frontTexture = frontTexture;
  group.userData.topMaterial = topMaterial;
  group.userData.topTexture = topTexture;
  group.userData.edges = edges;
  group.userData.baseGlow = baseGlow;
  group.userData.topGlow = topGlow;
  group.userData.baseY = 0;
  group.userData.phase = Math.random() * Math.PI * 2;
  group.userData.hovered = false;
  group.userData.hoverT = 0;
  group.userData.targetHoverT = 0;
  group.userData.baseScale = 1;

  const numLabel = document.createElement('div');
  numLabel.className = 'pillar-3d__num';
  numLabel.textContent = config.num;
  const numObj = new CSS2DObject(numLabel);
  numObj.position.set(0, height + 0.42, 0);
  group.add(numObj);
  group.userData.numLabel = numLabel;

  return group;
}

function refreshPillarTextures(group, active, textScale) {
  const { config, sideMaterial, frontMaterial, topMaterial } = group.userData;

  group.userData.sideTexture.dispose();
  group.userData.frontTexture.dispose();
  group.userData.topTexture.dispose();

  const sideTexture = createSideGradientTexture(active);
  const frontTexture = createFrontFaceTexture(config.label, active, textScale);
  const topTexture = createTopFaceTexture(active);

  sideMaterial.map = sideTexture;
  sideMaterial.emissive = new THREE.Color(active ? 0x004422 : 0x000000);
  sideMaterial.emissiveIntensity = active ? 0.45 : 0;
  sideMaterial.needsUpdate = true;

  frontMaterial.map = frontTexture;
  frontMaterial.needsUpdate = true;

  topMaterial.map = topTexture;
  topMaterial.emissive = new THREE.Color(active ? 0x00ff9f : 0x555555);
  topMaterial.emissiveIntensity = active ? 0.55 : 0.42;
  topMaterial.needsUpdate = true;

  group.userData.sideTexture = sideTexture;
  group.userData.frontTexture = frontTexture;
  group.userData.topTexture = topTexture;
}

function setPillarHover(group, active) {
  if (!group || group.userData.hovered === active) return;
  group.userData.hovered = active;
  group.userData.targetHoverT = active ? 1 : 0;

  const { edges, baseGlow, topGlow } = group.userData;
  edges.material.opacity = active ? 0.95 : 0;
  baseGlow.material.opacity = active ? 0.38 : 0;
  topGlow.material.opacity = active ? 0.22 : 0;
}

// Modal functions
// function renderMissionCard(mission, categoryLabel) {
//   const isCompleted = mission.state === 'completed';
//   const card = document.createElement('a');
//   card.href = `/simulations/${mission.id}`;
//   card.className = 'cr-mission-card-portrait' + (isCompleted ? ' cr-mission-card-portrait--done' : '');
  
//   card.innerHTML = `
//     <div class="cr-card__portrait">
//       <span class="cr-card__portrait-placeholder">🎯</span>
//     </div>
//     <div class="cr-card__content">
//       <span class="cr-card__category">${categoryLabel}</span>
//       <h3 class="cr-card__name">${mission.name}</h3>
//       <p class="cr-card__description">${mission.short_description || 'Interactive simulation exercise'}</p>
//       <span class="cr-card__status ${isCompleted ? 'cr-card__status--done' : ''}">${isCompleted ? '[completed]' : '[not started]'}</span>
//       <div class="cr-card__footer">
//         <div class="cr-card__objectives">
//           <span class="cr-card__label">objectives</span>
//           <span class="cr-card__value">${mission.objectives_count || 0}</span>
//         </div>
//         <div class="cr-card__time">
//           <span class="cr-card__label">time</span>
//           <span class="cr-card__value">${mission.estimated_minutes || 0}m</span>
//         </div>
//       </div>
//     </div>
//   `;
  
//   return card;
// }

// function showMission(index) {
//   if (index < 0 || index >= currentMissions.length) return;
//   currentIndex = index;
  
//   const mission = currentMissions[index];
//   const cat = categories.find(c => c.missions.some(m => m.id === mission.id));
//   const categoryLabel = cat ? cat.label.toUpperCase() : '';
  
//   carouselTrack.innerHTML = '';
//   const card = renderMissionCard(mission, categoryLabel);
//   carouselTrack.appendChild(card);
  
//   // Update nav button states
//   prevBtn.style.opacity = index === 0 ? '0.3' : '1';
//   prevBtn.style.pointerEvents = index === 0 ? 'none' : 'auto';
//   nextBtn.style.opacity = index === currentMissions.length - 1 ? '0.3' : '1';
//   nextBtn.style.pointerEvents = index === currentMissions.length - 1 ? 'none' : 'auto';
// }

function renderMissionRow(mission, categoryLabel, rowIndex) {
  const done = mission.state === 'completed';
  const num  = String(rowIndex + 1).padStart(2, '0');
  const icon = missionIcons[rowIndex % missionIcons.length];
  const iconColored = done ? icon.replace('#4b5563', '#00ff9f') : icon;
  const imgHtml = mission.image
    ? `<img src="/static/${mission.image}" alt="${mission.name}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center;border-radius:inherit;">`
    : iconColored;

  const row = document.createElement('a');
  row.href = `/simulations/${mission.id}`;
  row.className = 'cr-mission-row' + (done ? ' cr-mission-row--done' : '');
  row.style.animationDelay = `${0.28 + rowIndex * 0.07}s`;
  row.style.animation = 'crRowIn 0.35s ease both';

  row.innerHTML = `
    <div class="cr-mission-row__img" style="position:relative;overflow:hidden;">
      <div class="cr-mission-row__img-grid"></div>
      ${imgHtml}
    </div>
    <span class="cr-mission-row__num">${num}</span>
    <div class="cr-mission-row__info">
      <div class="cr-mission-row__cat">${categoryLabel}</div>
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
  `;
  return row;
}

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
    <!-- Side face — darker, more solid -->
    <polygon points="70,8 90,18 90,210 70,200" fill="url(#spS${index})"/>
    <!-- Front face -->
    <rect x="0" y="8" width="70" height="192" fill="url(#spF${index})"/>
    <!-- Top face -->
    <polygon points="0,8 70,8 90,18 20,18" fill="url(#spT${index})"/>
    <!-- Inner shadow on front left edge -->
    <line x1="1" y1="9" x2="1" y2="199" stroke="#000" stroke-width="2" opacity="0.4"/>
    <!-- Green edge highlight -->
    <line x1="0" y1="8" x2="0" y2="200" stroke="#00ff9f" stroke-width="1.5" opacity="0.7"/>
    <line x1="0" y1="8" x2="70" y2="8" stroke="#00ff9f" stroke-width="1" opacity="0.45"/>
    <!-- Label -->
    <text x="35" y="104" text-anchor="middle"
      font-family="Manrope,sans-serif" font-size="7" font-weight="700"
      letter-spacing="3" fill="#ffffff" opacity="0.9"
      transform="rotate(-90,35,104)">${label.toUpperCase().slice(0, 22)}</text>
    <!-- Base glow -->
    <ellipse cx="40" cy="208" rx="38" ry="6" fill="#00ff9f" opacity="0.22" filter="url(#spG${index})"/>
    <ellipse cx="40" cy="210" rx="28" ry="4" fill="#00ff9f" opacity="0.32"/>
  </svg>`;
}


function showMissionAtIndex(index) {
  if (!currentMissions.length) return;
  currentMissionIndex = Math.max(0, Math.min(index, currentMissions.length - 1));
  const mission = currentMissions[currentMissionIndex];
  const num = String(currentMissionIndex + 1).padStart(2, '0');
  const icon = missionIcons[currentMissionIndex % missionIcons.length];

  // Animate out then in
  missionTrack.style.opacity = '0';
  missionTrack.style.transform = 'translateX(20px)';

  setTimeout(() => {
    const done = mission.state === 'completed';
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
      </a>
    `;

    missionTrack.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    missionTrack.style.opacity = '1';
    missionTrack.style.transform = 'translateX(0)';
  }, 120);

  // Update dots
  missionDots.querySelectorAll('.cr-modal__carousel-dot').forEach((dot, i) => {
    dot.classList.toggle('is-active', i === currentMissionIndex);
  });

  // Update counter
  missionCounter.textContent = `${currentMissionIndex + 1} / ${currentMissions.length}`;

  // Update nav buttons
  missionPrevBtn.disabled = currentMissionIndex === 0;
  missionNextBtn.disabled = currentMissionIndex === currentMissions.length - 1;
}




function openCategory(index) {
  const cat = categories[index];
  if (!cat) return;

  currentCategoryIndex = index;

  // Update arrow visibility
  catPrevBtn.style.opacity = index === 0 ? '0.25' : '1';
  catPrevBtn.style.pointerEvents = index === 0 ? 'none' : 'auto';
  catNextBtn.style.opacity = index === categories.length - 1 ? '0.25' : '1';
  catNextBtn.style.pointerEvents = index === categories.length - 1 ? 'none' : 'auto';

  // Populate header
  miniNum.textContent     = nums[index];
  miniName.textContent    = cat.label;
  modalBadge.textContent  = `Category ${nums[index]}`;
  modalTitle.textContent  = cat.label;
  modalDesc.textContent   = shortDesc[index] || '';
  modalCount.textContent  = `${cat.missions.length} ATTACKS ——`;
  sidebarPillar.innerHTML = buildSidebarSVG(cat.label, index);

  // Tag each mission with its category label for display
  currentMissions = cat.missions.map(m => ({
    ...m,
    category_label: cat.label.toUpperCase()
  }));
  currentMissionIndex = 0;

  // Build dots
  missionDots.innerHTML = currentMissions.map((_, i) =>
    `<span class="cr-modal__carousel-dot${i === 0 ? ' is-active' : ''}" data-i="${i}"></span>`
  ).join('');

  // Dot click
  missionDots.querySelectorAll('.cr-modal__carousel-dot').forEach(dot => {
    dot.addEventListener('click', () => showMissionAtIndex(parseInt(dot.dataset.i)));
  });

  // Reset track state
  missionTrack.style.transition = 'none';
  missionTrack.style.opacity = '1';
  missionTrack.style.transform = 'translateX(0)';

  showMissionAtIndex(0);

  overlay.classList.add('is-open');
  requestAnimationFrame(() => overlay.classList.add('is-active'));
}

missionPrevBtn.addEventListener('click', () => showMissionAtIndex(currentMissionIndex - 1));
missionNextBtn.addEventListener('click', () => showMissionAtIndex(currentMissionIndex + 1));



function closeModal() {
  overlay.classList.remove('is-active');
  setTimeout(() => {
    overlay.classList.remove('is-open');
    missionTrack.innerHTML = '';
    missionDots.innerHTML = '';
  }, 380);
}


// prevBtn.addEventListener('click', () => showMission(currentIndex - 1));
// nextBtn.addEventListener('click', () => showMission(currentIndex + 1));
closeBtn.addEventListener('click', closeModal);
overlay.addEventListener('click', (e) => {
  if (e.target === overlay) closeModal();
});
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeModal();
  if (!overlay.classList.contains('is-active')) return;
  if (e.key === 'ArrowLeft' && currentCategoryIndex > 0) switchCategory(currentCategoryIndex - 1, 'prev');
  if (e.key === 'ArrowRight' && currentCategoryIndex < categories.length - 1) switchCategory(currentCategoryIndex + 1, 'next');
});

// ══════════════════════════════════════════
// Attack Carousel (right side)
// ══════════════════════════════════════════

const attackSlide = document.getElementById('cr-attack-slide');
const attackNextBtn = document.getElementById('cr-attack-next');

let carouselAttacks = [];
let carouselIndex = 0;
let carouselTimer = null;
let currentMissions = [];
let currentMissionIndex = 0;
let currentCategoryIndex = 0;


function renderAttackCard(mission, categoryLabel) {
  const card = document.createElement('a');
  card.href = `/simulations/${mission.id}`;
  card.className = 'cr-attack-card';
  
  const skills = mission.skills_learned || [];
  const skillTags = skills.slice(0, 2).map(s => `<span class="cr-attack-tag">${s}</span>`).join('');
  
  card.innerHTML = `
    <div class="cr-attack-card__category">${categoryLabel} / ${String(carouselIndex + 1).padStart(2, '0')}</div>
    <h2 class="cr-attack-card__title">${mission.name}</h2>
    <p class="cr-attack-card__description">${mission.short_description || 'Learn to identify fake emails and cloned login pages before entering your credentials.'}</p>
    ${skillTags ? `<div class="cr-attack-card__tags">${skillTags}</div>` : ''}
    <div class="cr-attack-card__footer">
      <span class="cr-attack-card__link">Start Mission →</span>
      <div class="cr-attack-card__meta">
        <span class="cr-attack-card__meta-item">${mission.objectives_count || 0} objectives</span>
        <span class="cr-attack-card__meta-item">${mission.estimated_minutes || 0} min</span>
      </div>
    </div>
  `;
  
  return card;
}

function showAttackSlide(index, direction = 'next') {
  if (categories.length === 0) return;
  
  carouselIndex = (index + categories.length) % categories.length;
  const cat = categories[carouselIndex];
  
  attackSlide.innerHTML = '';
  
  // Flat invisible click layer that sits over the tilted visual
  const clickLayer = document.createElement('div');
  clickLayer.style.cssText = `
    position: absolute;
    inset: 0;
    z-index: 100;
    cursor: pointer;
  `;
  clickLayer.addEventListener('click', (e) => {
    // check if next button was clicked
    if (e.target.closest('#cr-attack-next')) return;
    openCategory(carouselIndex);
  });
  attackSlide.appendChild(clickLayer);

  const card = document.createElement('div');
  card.className = 'cr-attack-card';

  const num = String(carouselIndex + 1).padStart(2, '0');
  
  card.innerHTML = `
    <div class="cr-attack-card__category">CATEGORY ${num}</div>
    <h2 class="cr-attack-card__title">${cat.label}</h2>
    <p class="cr-attack-card__description">${getCategoryDesc(carouselIndex)}</p>
    <div class="cr-attack-card__tags">
      ${cat.missions.slice(0, 3).map(m => `<span class="cr-attack-tag">${m.name}</span>`).join('')}
    </div>
    <div class="cr-attack-card__footer">
      <span class="cr-attack-card__link">View Attacks →</span>
      <div class="cr-attack-card__meta">
        <span class="cr-attack-card__meta-item">${cat.missions.length} missions</span>
        <span class="cr-attack-card__meta-item">${cat.unlocked_count} unlocked</span>
      </div>
    </div>
  `;

  card.style.transform = direction === 'next' ? 'translateX(100%)' : 'translateX(-100%)';
  card.style.opacity = '0';
  attackSlide.appendChild(card);
  
  card.getBoundingClientRect();
  
  card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
  card.style.transform = 'translateX(0)';
  card.style.opacity = '1';
  card.style.position = 'relative';
  
  clearTimeout(carouselTimer);
  carouselTimer = setTimeout(() => {
    showAttackSlide(carouselIndex + 1, 'next');
  }, 5000);
}

function getCategoryDesc(index) {
  const descs = [
    'Social-based attacks exploit human psychology, trust, and behavior to manipulate individuals into divulging confidential information. Through impersonation, deception, and emotional manipulation, attackers bypass technical defenses entirely — making awareness your strongest shield against phishing, pretexting, and social engineering.',
    'Malware-based attacks deploy malicious software to infiltrate, damage, or silently take control of computer systems. From keyloggers that capture every keystroke to ransomware that locks your files for payment — understanding how these threats operate is the first step to stopping them before they cause irreversible damage.',
    'Network-based attacks target the infrastructure connecting systems, exploiting vulnerabilities in protocols and configurations to intercept, redirect, or disrupt communications. Man-in-the-middle attacks, rogue access points, and traffic sniffing can expose sensitive data without the victim ever knowing they were compromised.',
    'Injection-based attacks manipulate how applications handle user input — inserting malicious code or commands to hijack execution, bypass authentication, or extract restricted data. SQL injection, command injection, and XSS are among the most prevalent and damaging vulnerabilities found in web applications today.',
  ];
  return descs[index] || '';
}

function initAttackCarousel() {
  if (categories.length > 0) {
    carouselAttacks = categories[0].missions; // keep this for compatibility
    showAttackSlide(0);
  }
}

if (attackNextBtn) {
  attackNextBtn.addEventListener('click', () => {
    showAttackSlide(carouselIndex + 1, 'next');
  });
}

setTimeout(() => initAttackCarousel(), 100);


// Initialize scene
function initPillarScene(container) {
  const scene = new THREE.Scene();
  scene.fog = new THREE.Fog(0x0a0a0a, 18, 48);

  const camera = new THREE.PerspectiveCamera(42, container.clientWidth / container.clientHeight, 0.1, 120);
  camera.position.set(0, 3.8, 9.5);
  camera.lookAt(0, 1.8, 0);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.setClearColor(0x000000, 0);
  container.appendChild(renderer.domElement);
  renderer.domElement.classList.add('pillar-scene__canvas');
  renderer.domElement.style.cursor = 'default';

  const labelRenderer = new CSS2DRenderer();
  labelRenderer.setSize(container.clientWidth, container.clientHeight);
  labelRenderer.domElement.classList.add('pillar-scene__labels');
  container.appendChild(labelRenderer.domElement);

  scene.add(new THREE.AmbientLight(0xffffff, 0.32));

  const keyLight = new THREE.DirectionalLight(0xffffff, 1.15);
  keyLight.position.set(2, 12, 10);
  keyLight.castShadow = true;
  scene.add(keyLight);

  const rimLight = new THREE.DirectionalLight(0xffffff, 0.4);
  rimLight.position.set(0, 4, -10);
  scene.add(rimLight);

  const animatedGrid = createAnimatedGrid();
  scene.add(animatedGrid);

  const floor = new THREE.Mesh(
    new THREE.PlaneGeometry(52, 52),
    new THREE.MeshStandardMaterial({
      color: 0x040404,
      metalness: 0.05,
      roughness: 1,
      transparent: true,
      opacity: 0.85,
    }),
  );
  floor.rotation.x = -Math.PI / 2;
  floor.receiveShadow = true;
  scene.add(floor);




  const pillarGroups = PILLARS.map((config) => {
    const group = createPillarGroup(config);
    group.position.set(config.x, 0, config.z);
    scene.add(group);
    return group;
  });

  const hoverLight = new THREE.PointLight(PRIMARY, 0, 7);
  hoverLight.position.set(0, 0.4, 0);
  scene.add(hoverLight);

  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  let hoveredGroup = null;

  function pickPillar(clientX, clientY) {
    const rect = renderer.domElement.getBoundingClientRect();
    pointer.x = ((clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = -((clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(pointer, camera);
    const hits = raycaster.intersectObjects(
      pillarGroups.map((g) => g.userData.mesh),
      false,
    );
    return hits.length ? hits[0].object.parent : null;
  }

  function updateHover(clientX, clientY) {
    const next = pickPillar(clientX, clientY);
    if (next !== hoveredGroup) {
      if (hoveredGroup) setPillarHover(hoveredGroup, false);
      hoveredGroup = next;
      if (hoveredGroup) {
        setPillarHover(hoveredGroup, true);
        hoverLight.intensity = 2.8;
        hoverLight.position.set(hoveredGroup.position.x, 0.5, hoveredGroup.position.z);
        renderer.domElement.style.cursor = 'pointer';
      } else {
        hoverLight.intensity = 0;
        renderer.domElement.style.cursor = 'default';
      }
    }
  }

  renderer.domElement.addEventListener('pointermove', (event) => {
    updateHover(event.clientX, event.clientY);
  });

  renderer.domElement.addEventListener('pointerleave', () => {
    if (hoveredGroup) setPillarHover(hoveredGroup, false);
    hoveredGroup = null;
    hoverLight.intensity = 0;
    renderer.domElement.style.cursor = 'default';
  });

  renderer.domElement.addEventListener('click', (event) => {
    const target = pickPillar(event.clientX, event.clientY);
    if (target && target.userData.config) {
      openCategory(target.userData.config.categoryIndex);
    }
  });

  const clock = new THREE.Clock();
  let animationId = null;

  // Sequential pillar glow animation (like button pulse)
  function getPillarGlow(t, pillarIndex) {
    const cycleTime = 3.5; // seconds per pillar
    const totalCycle = cycleTime * PILLARS.length;
    const currentPhase = (t % totalCycle) / cycleTime;
    const activePillarFloat = currentPhase;
    const activePillar = Math.floor(activePillarFloat);
    
    if (activePillar !== pillarIndex) return 0;
    
    const progress = activePillarFloat - activePillar;
    // Pulse: fade in, hold, fade out
    if (progress < 0.3) return progress / 0.3;
    if (progress < 0.7) return 1;
    return 1 - (progress - 0.7) / 0.3;
  }

  function animate() {
    const t = clock.getElapsedTime();
    // Grid animation removed

    pillarGroups.forEach((group, index) => {
      const bob = Math.sin(t * 0.85 + group.userData.phase) * 0.02;
      group.position.y = group.userData.baseY + bob;

      const baseRot = PILLARS[index].rotY;
      const wobble = group.userData.hovered ? 0.006 : 0.01;
      group.rotation.y = baseRot + Math.sin(t * 0.45 + index) * wobble;

      // Combine hover + sequential glow
      const sequentialGlow = group.userData.hovered ? 0 : getPillarGlow(t, index);
      const combinedGlow = Math.max(group.userData.hoverT, sequentialGlow);

      group.userData.hoverT += (group.userData.targetHoverT - group.userData.hoverT) * 0.14;

      const textScale = 1 + combinedGlow * 0.55;
      const scaleKey = textScale.toFixed(3);
      if (group.userData.lastTextScale !== scaleKey) {
        refreshPillarTextures(group, combinedGlow > 0.2, textScale);
        group.userData.lastTextScale = scaleKey;
      }

      if (group.userData.numLabel) {
        const numScale = 1 + combinedGlow * 0.42;
        group.userData.numLabel.style.transform = `translate(-50%, -50%) scale(${numScale})`;
        group.userData.numLabel.classList.toggle('pillar-3d__num--active', combinedGlow > 0.2);
      }

      // Apply sequential glow to edges and base
      const { edges, baseGlow, topGlow } = group.userData;
      if (!group.userData.hovered && sequentialGlow > 0) {
        edges.material.opacity = sequentialGlow * 0.75;
        baseGlow.material.opacity = sequentialGlow * 0.28;
        topGlow.material.opacity = sequentialGlow * 0.18;
      }
    });

    if (hoveredGroup) {
      hoverLight.intensity = 2.2 + Math.sin(t * 2.2) * 0.35;
    }

    renderer.render(scene, camera);
    labelRenderer.render(scene, camera);
    animationId = requestAnimationFrame(animate);
  }

  animate();

  function onResize() {
    const w = container.clientWidth;
    const h = container.clientHeight;
    if (w === 0 || h === 0) return;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
    labelRenderer.setSize(w, h);
  }

  const resizeObserver = new ResizeObserver(onResize);
  resizeObserver.observe(container);

  return () => {
    cancelAnimationFrame(animationId);
    resizeObserver.disconnect();
    renderer.dispose();
    container.innerHTML = '';
  };
}

const host = document.getElementById('cr-scene');
if (host) {
  initPillarScene(host);
}

// ── Module strip: category tabs + "View all →" ──────────────
(function () {
  const scroll    = document.getElementById('cr-strip-scroll');
  const viewAllBtn = document.getElementById('cr-strip-viewall');
  const tabs      = document.querySelectorAll('.cr-strip-tab');
  if (!scroll || !tabs.length) return;

  let activeCatId    = tabs[0]?.dataset.catId || '';
  let activeCatIndex = 0;

  function activate(tab) {
    tabs.forEach(t => {
      t.classList.remove('is-active');
      t.setAttribute('aria-selected', 'false');
    });
    tab.classList.add('is-active');
    tab.setAttribute('aria-selected', 'true');
    activeCatId    = tab.dataset.catId;
    activeCatIndex = parseInt(tab.dataset.catIndex, 10);

    // Update "View all" to open the right category modal
    if (viewAllBtn) viewAllBtn.dataset.catIndex = activeCatIndex;

    // Scroll the strip to the first card of that category
    const firstCard = scroll.querySelector(`.cr-strip-card[data-cat-id="${activeCatId}"]`);
    if (firstCard) {
      firstCard.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'start' });
    }
  }

  tabs.forEach(tab => {
    tab.addEventListener('click', () => activate(tab));
  });

  // "View all →" opens the modal for the currently active category
  viewAllBtn?.addEventListener('click', () => openCategory(activeCatIndex));

  // Update active tab when user scrolls manually
  const cardEls = scroll.querySelectorAll('.cr-strip-card[data-cat-id]');
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.dataset.catId;
        const matchTab = document.querySelector(`.cr-strip-tab[data-cat-id="${id}"]`);
        if (matchTab && id !== activeCatId) activate(matchTab);
      }
    });
  }, { root: scroll, threshold: 0.6 });

  // Only observe the first card of each category to avoid over-triggering
  const seen = new Set();
  cardEls.forEach(card => {
    const id = card.dataset.catId;
    if (!seen.has(id)) { observer.observe(card); seen.add(id); }
  });
})();
