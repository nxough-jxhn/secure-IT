import * as THREE from 'three';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';

const PRIMARY = 0x00ff9f;

const DEFAULT_ROUTES = {
  modules: '/modules',
  social_based: '/modules/category/social_based',
  malware_based: '/modules/category/malware_based',
  network_based: '/modules/category/network_based',
  injection_based: '/modules/category/injection_based',
};

const PILLARS = [
  {
    num: '03',
    label: 'Social-Based Attacks',
    categoryKey: 'social_based',
    x: -5.95,
    z: -1.35,
    rotY: 0.58,
    height: 3.45,
  },
  {
    num: '04',
    label: 'Malware-Based Attacks',
    categoryKey: 'malware_based',
    x: -2.95,
    z: -0.55,
    rotY: 0.3,
    height: 3.75,
  },
  {
    num: '10',
    label: 'Cyberattack',
    categoryKey: 'modules',
    x: 0,
    z: 0,
    rotY: 0,
    height: 4.55,
    isCenter: true,
  },
  {
    num: '02',
    label: 'Network-Based Attacks',
    categoryKey: 'network_based',
    x: 2.95,
    z: -0.55,
    rotY: -0.3,
    height: 3.25,
  },
  {
    num: '01',
    label: 'Injection-Based Attacks',
    categoryKey: 'injection_based',
    x: 5.95,
    z: -1.35,
    rotY: -0.58,
    height: 2.95,
  },
];

function resolveRoutes(container) {
  const raw = container.dataset.routes;
  if (!raw) return DEFAULT_ROUTES;
  try {
    return { ...DEFAULT_ROUTES, ...JSON.parse(raw) };
  } catch {
    return DEFAULT_ROUTES;
  }
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
  const uniforms = {
    uTime: { value: 0 },
    uLine: { value: new THREE.Color(0x555555) },
    uGlow: { value: new THREE.Color(0x00ff9f) },
  };

  const material = new THREE.ShaderMaterial({
    transparent: true,
    depthWrite: false,
    uniforms,
    vertexShader: `
      varying vec2 vUv;
      void main() {
        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      varying vec2 vUv;
      uniform float uTime;
      uniform vec3 uLine;
      uniform vec3 uGlow;

      float gridLine(vec2 uv, float cells) {
        vec2 g = abs(fract(uv * cells - 0.5) - 0.5) / fwidth(uv * cells);
        return 1.0 - min(min(g.x, g.y), 1.0);
      }

      void main() {
        vec2 uv = vUv;
        float cells = 28.0;
        float line = gridLine(uv, cells);

        vec2 cellId = floor(uv * cells);
        float pick = mod(cellId.y + cellId.x * 0.31, 5.0);
        float selected = step(1.5, pick) * (1.0 - step(2.5, pick));
        selected += step(3.5, pick) * (1.0 - step(4.5, pick));

        float sweep = fract(uv.x * 2.2 - uTime * 0.12 + cellId.y * 0.07);
        float pulse = smoothstep(0.78, 0.98, sweep) * smoothstep(1.0, 0.82, sweep);
        float glow = line * selected * pulse * 1.4;

        vec3 color = uLine * line * 0.45;
        color += uGlow * glow;
        float alpha = line * 0.55 + glow * 0.75;
        gl_FragColor = vec4(color, alpha);
      }
    `,
  });

  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(52, 52), material);
  mesh.rotation.x = -Math.PI / 2;
  mesh.position.y = 0.008;
  mesh.userData.uniforms = uniforms;
  return mesh;
}

function createPillarGroup(config, route) {
  const group = new THREE.Group();
  const width = 1.08;
  const depth = 1.08;
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
  group.userData.route = route;
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

function initPillarScene(container) {
  const routes = resolveRoutes(container);
  const scene = new THREE.Scene();
  scene.fog = new THREE.Fog(0x0a0a0a, 18, 48);

  const camera = new THREE.PerspectiveCamera(42, container.clientWidth / container.clientHeight, 0.1, 120);
  camera.position.set(0, 4.6, 11.8);
  camera.lookAt(0, 1.55, 0);

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
    const route = routes[config.categoryKey] || DEFAULT_ROUTES[config.categoryKey];
    const group = createPillarGroup(config, route);
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
    if (target && target.userData.route) {
      window.location.href = target.userData.route;
    }
  });

  const clock = new THREE.Clock();
  let animationId = null;

  function animate() {
    const t = clock.getElapsedTime();
    animatedGrid.userData.uniforms.uTime.value = t;

    pillarGroups.forEach((group, index) => {
      const bob = Math.sin(t * 0.85 + group.userData.phase) * 0.02;
      group.position.y = group.userData.baseY + bob;

      const baseRot = PILLARS[index].rotY;
      const wobble = group.userData.hovered ? 0.006 : 0.01;
      group.rotation.y = baseRot + Math.sin(t * 0.45 + index) * wobble;

      group.userData.hoverT += (group.userData.targetHoverT - group.userData.hoverT) * 0.14;
      const hoverT = group.userData.hoverT;

      const textScale = 1 + hoverT * 0.55;
      const scaleKey = textScale.toFixed(3);
      if (group.userData.lastTextScale !== scaleKey) {
        refreshPillarTextures(group, hoverT > 0.2, textScale);
        group.userData.lastTextScale = scaleKey;
      }

      if (group.userData.numLabel) {
        const numScale = 1 + hoverT * 0.42;
        group.userData.numLabel.style.transform = `translate(-50%, -50%) scale(${numScale})`;
        group.userData.numLabel.classList.toggle('pillar-3d__num--active', hoverT > 0.2);
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
    disposeScene(scene);
    container.innerHTML = '';
  };
}

function disposeScene(object) {
  object.traverse((child) => {
    if (child.geometry) child.geometry.dispose();
    if (child.material) {
      const materials = Array.isArray(child.material) ? child.material : [child.material];
      materials.forEach((material) => {
        if (material.map) material.map.dispose();
        material.dispose();
      });
    }
  });
}

const host = document.getElementById('pillar-scene');
if (host) {
  initPillarScene(host);
}
