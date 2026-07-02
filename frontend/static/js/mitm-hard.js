(function () {
  'use strict';

  const dataEl = document.getElementById('workspace-data');
  if (!dataEl) return;
  const data = JSON.parse(dataEl.textContent);

  /* ── Scoring ── */
  const MAX_SCORE = 50;
  const EARN = { good_wifi: 15, https_login: 20, correct_receiver: 15 };
  const DEDUCT = { bad_wifi: 0, http_login: 0, wrong_receiver: 0 }; // kept for mistake logging
  let score = 0; // starts at 0, earned per correct action
  const mistakes = [], goodDecisions = [], actionsLog = [];
  const recommendations = [
    'Always connect to WPA3-Enterprise or WPA2-Enterprise networks for sensitive tasks.',
    'Check the URL protocol — HTTPS encrypts your connection; HTTP does not.',
    'Verify all payment details, especially the receiver email, before confirming.',
  ];

  /* ── WiFi data — no obvious hints ── */
  const NETWORKS = [
    {
      id: 'evil',
      name: 'TUPT_Canteen_Wifi',
      bars: 4,
      locked: false,
      details: {
        'Security':    'Open (None)',
        'Band':        '2.4 GHz',
        'Channel':     '6',
        'Signal':      '-42 dBm (Excellent)',
        'Network Type':'Public',
        'IP Range':    '192.168.10.0/24',
        'Gateway':     '192.168.10.1',
        'DNS':         '8.8.8.8',
      },
    },
    {
      id: 'evil2',
      name: '2nd_Floor_Network',
      bars: 3,
      locked: true,
      details: {
        'Security':    'WPA2-Personal',
        'Band':        '5 GHz',
        'Channel':     '36',
        'Signal':      '-58 dBm (Good)',
        'Network Type':'Private',
        'IP Range':    '10.0.2.0/24',
        'Gateway':     '10.0.2.1',
        'DNS':         '10.0.2.1',
      },
    },
    {
      id: 'safe',
      name: 'TUPT_Faculty_Secure',
      bars: 3,
      locked: true,
      details: {
        'Security':    'WPA3-Enterprise (802.1X)',
        'Band':        '5 GHz',
        'Channel':     '149',
        'Signal':      '-61 dBm (Good)',
        'Network Type':'Enterprise',
        'IP Range':    '172.16.5.0/24',
        'Gateway':     '172.16.5.1',
        'DNS':         '172.16.5.2 (Internal)',
        'Certificate': 'tupt.edu.ph — Issued by DigiCert',
      },
    },
    {
      id: 'evil3',
      name: 'Library_Public_Wifi',
      bars: 2,
      locked: false,
      details: {
        'Security':    'WPA2-Personal',
        'Band':        '2.4 GHz',
        'Channel':     '11',
        'Signal':      '-70 dBm (Fair)',
        'Network Type':'Public',
        'IP Range':    '192.168.50.0/24',
        'Gateway':     '192.168.50.1',
        'DNS':         '8.8.8.8',
      },
    },
    {
      id: 'evil4',
      name: 'TUPT_Student_Portal',
      bars: 4,
      locked: false,
      details: {
        'Security':    'Open (None)',
        'Band':        '2.4 GHz',
        'Channel':     '1',
        'Signal':      '-39 dBm (Excellent)',
        'Network Type':'Public',
        'IP Range':    '192.168.99.0/24',
        'Gateway':     '192.168.99.1',
        'DNS':         '8.8.8.8',
      },
    },
  ];

  /* ── Stage tracking ── */
  let currentStep = 0;
  let missionStart = null;
  let timerHandle = null;
  let selectedNetwork = null;

  /* ── DOM refs ── */
  const timerEl      = document.getElementById('mh-timer');
  const progFill     = document.getElementById('mh-progress-fill');
  const progPct      = document.getElementById('mh-progress-pct');
  const progCount    = document.getElementById('mh-progress-count');
  const stepItems    = document.querySelectorAll('.mh-step');
  const eventFeed    = document.getElementById('mh-event-feed');
  const logEl        = document.getElementById('mh-log');
  const wifiTrayBtn  = document.getElementById('mh-wifi-tray-btn');
  const wifiPanel    = document.getElementById('mh-wifi-panel');
  const wifiList     = document.getElementById('mh-wifi-list');
  const wifiDetail   = document.getElementById('mh-wifi-detail');
  const wifiDetailBd = document.getElementById('mh-wifi-detail-bd');
  const wifiDetailContent = document.getElementById('mh-wifi-detail-content');
  const wifiConnectBtn    = document.getElementById('mh-wifi-connect-btn');
  const wifiDetailCancel  = document.getElementById('mh-wifi-detail-cancel');
  const wifiDetailClose   = document.getElementById('mh-wifi-detail-close');
  const chromeWindow = document.getElementById('mh-chrome-window');
  const chromeBtnTB  = document.getElementById('mh-chrome-taskbar-btn');
  const urlBar       = document.getElementById('mh-url-bar');
  const urlGoBtn     = document.getElementById('mh-url-go');
  const secIcon      = document.getElementById('mh-security-icon');
  const notSecLabel  = document.getElementById('mh-not-secure-label');
  const loginPage    = document.getElementById('mh-page-login');
  const payPage      = document.getElementById('mh-page-payment');
  const loginBtn     = document.getElementById('mh-login-btn');
  const payBtn       = document.getElementById('mh-pay-btn');
  const receiverField = document.getElementById('mh-receiver-field');
  const portalUser   = document.getElementById('mh-portal-user');
  const payId        = document.getElementById('mh-pay-id');
  const revealOverlay = document.getElementById('mh-reveal-overlay');
  const revealContent = document.getElementById('mh-reveal-content');

  let pendingNetwork = null; // network object being viewed in detail drawer

  /* ── Helpers ── */
  function log(action, detail) { actionsLog.push({ action, detail, at: new Date().toISOString() }); }

  function pushFeed(msg, tone) {
    const li = document.createElement('li');
    li.className = `mh-event${tone ? ' mh-event--' + tone : ''}`;
    li.textContent = msg;
    eventFeed.prepend(li);
    if (eventFeed.children.length > 1) {
      const ph = eventFeed.querySelector('.mh-event--info:last-child');
      if (ph && ph.textContent.includes('Waiting')) ph.remove();
    }
  }

  function pushLog(msg, cls) {
    const empty = logEl.querySelector('.mh-log__empty');
    if (empty) empty.remove();
    const li = document.createElement('li');
    if (cls) li.className = cls;
    li.textContent = msg;
    logEl.appendChild(li);
  }

  function deduct(key, label) {
    // Wrong action — no points earned for this stage, just log it
    mistakes.push(label);
    log('mistake', label);
    pushFeed(`Mistake: ${label}`, 'bad');
    pushLog(`✗ ${label}`, 'bad');
  }

  function goodCall(label, earnKey) {
    score = Math.min(MAX_SCORE, score + (EARN[earnKey] || 0));
    goodDecisions.push(label);
    log('good', label);
    pushFeed(`Good: ${label}`, 'good');
    pushLog(`✓ ${label}`, 'good');
  }

  function setStep(n) {
    currentStep = n;
    const pct = Math.round((n / 3) * 100);
    progFill.style.width = `${pct}%`;
    progPct.textContent  = `${pct}%`;
    progCount.textContent = `Step ${Math.min(n + 1, 3)} of 3`;
    stepItems.forEach((el, i) => {
      el.classList.remove('mh-step--active', 'mh-step--done');
      if (i < n) el.classList.add('mh-step--done');
      else if (i === n) el.classList.add('mh-step--active');
    });
  }

  /* ── Briefing → start ── */
  document.getElementById('mh-briefing-start').addEventListener('click', () => {
    document.getElementById('mh-briefing').style.display = 'none';
    missionStart = Date.now();
    timerHandle = setInterval(() => {
      const e = Math.floor((Date.now() - missionStart) / 1000);
      timerEl.textContent =
        String(Math.floor(e / 60)).padStart(2, '0') + ':' + String(e % 60).padStart(2, '0');
    }, 1000);
    pushFeed('Simulation started. Click the WiFi icon in the taskbar.', 'info');
    setStep(0);
    updateClock();
  });

  /* ── End Simulation button ── */
  document.getElementById('mh-end-sim-btn').addEventListener('click', () => {
    if (!missionStart) {
      // Sim hasn't started yet — just go back
      window.location.href = data.briefing_url || '/simulations/mitm';
      return;
    }
    if (!confirm('End the simulation now? You will keep the points you have earned so far and the quiz will unlock.')) return;
    mistakes.push('Ended simulation early');
    log('end_early', `score at end: ${score}`);
    pushFeed('Simulation ended early.', 'warn');
    showReveal();
  });  /* ── Clock ── */
  function updateClock() {
    const now = new Date();
    let h = now.getHours(), m = String(now.getMinutes()).padStart(2, '0');
    const ap = h >= 12 ? 'PM' : 'AM';
    h = h % 12 || 12;
    const clockEl = document.getElementById('mh-clock');
    const dateEl  = document.getElementById('mh-date');
    if (clockEl) clockEl.textContent = `${h}:${m} ${ap}`;
    if (dateEl) {
      const days = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
      const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
      dateEl.textContent = `${days[now.getDay()]}, ${months[now.getMonth()]} ${now.getDate()}`;
    }
    setTimeout(updateClock, 10000);
  }

  /* ══ STAGE 1 — WiFi Panel ══ */

  function buildSignalBars(count, connected) {
    let html = '';
    for (let i = 1; i <= 4; i++) {
      const lit = i <= count ? (connected ? 'mh-wifi-bar--lit-blue' : 'mh-wifi-bar--lit') : '';
      html += `<span class="mh-wifi-bar ${lit}"></span>`;
    }
    return html;
  }

  function renderWifiList() {
    wifiList.innerHTML = '';
    NETWORKS.forEach(net => {
      const isConnected = selectedNetwork && selectedNetwork.id === net.id;
      const row = document.createElement('div');
      row.className = `mh-wifi-row${isConnected ? ' mh-wifi-row--connected' : ''}`;
      row.dataset.id = net.id;
      row.innerHTML = `
        <div class="mh-wifi-row__signal">${buildSignalBars(net.bars, isConnected)}</div>
        ${net.locked ? '<span class="mh-wifi-row__lock">🔒</span>' : ''}
        <div class="mh-wifi-row__info">
          <span class="mh-wifi-row__name">${net.name}</span>
          <span class="mh-wifi-row__status">${isConnected ? 'Connected, secured' : (net.locked ? 'Secured' : 'Open')}</span>
        </div>
        <button type="button" class="mh-wifi-row__info-btn" data-id="${net.id}" title="Network details">ⓘ</button>
      `;
      // Clicking the row body opens detail (just like clicking the name in real Windows)
      row.addEventListener('click', (e) => {
        if (e.target.closest('.mh-wifi-row__info-btn')) return;
        openWifiDetail(net);
      });
      row.querySelector('.mh-wifi-row__info-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        openWifiDetail(net);
      });
      wifiList.appendChild(row);
    });
  }

  wifiTrayBtn.addEventListener('click', () => {
    if (wifiPanel.hidden) {
      renderWifiList();
      wifiPanel.hidden = false;
    } else {
      wifiPanel.hidden = true;
    }
  });

  // Close panel when clicking outside
  document.addEventListener('click', (e) => {
    if (!wifiPanel.hidden && !wifiPanel.contains(e.target) && !wifiTrayBtn.contains(e.target)) {
      wifiPanel.hidden = true;
    }
  });

  function openWifiDetail(net) {
    pendingNetwork = net;
    wifiPanel.hidden = true;

    let rows = `<div class="mh-wifi-detail__name">${net.name}</div><div class="mh-wifi-detail__table">`;
    Object.entries(net.details).forEach(([k, v]) => {
      rows += `<div class="mh-wifi-detail__row">
        <span class="mh-wifi-detail__key">${k}</span>
        <span class="mh-wifi-detail__val">${v}</span>
      </div>`;
    });
    rows += '</div>';
    wifiDetailContent.innerHTML = rows;

    // If already connected to this network, change button to "Disconnect"
    const isConnected = selectedNetwork && selectedNetwork.id === net.id;
    wifiConnectBtn.textContent = isConnected ? 'Disconnect' : 'Connect';
    wifiDetail.hidden = false;
  }

  function closeWifiDetail() {
    wifiDetail.hidden = true;
    pendingNetwork = null;
  }

  wifiDetailClose.addEventListener('click', closeWifiDetail);
  wifiDetailCancel.addEventListener('click', closeWifiDetail);
  wifiDetailBd.addEventListener('click', closeWifiDetail);

  wifiConnectBtn.addEventListener('click', () => {
    if (!pendingNetwork) return;
    const net = pendingNetwork;
    closeWifiDetail();

    // Evaluate choice silently — no feedback pop-up
    selectedNetwork = net;
    log('wifi_selected', net.id);

    if (net.id === 'safe') {
      goodCall('Connected to WPA3-Enterprise network', 'good_wifi');
    } else {
      deduct('bad_wifi', `Connected to untrusted network: ${net.name}`);
    }

    // Update taskbar WiFi icon to show connected
    document.getElementById('mh-wifi-tray-icon').textContent = net.id === 'safe' ? '📶' : '📶';
    pushFeed(`Connected to ${net.name}. Chrome is opening…`, 'info');
    renderWifiList(); // refresh to show connected state

    // Small delay then open Chrome
    setTimeout(() => openChrome(), 800);
  });

  /* ══ STAGE 2 — Chrome / Login ══ */

  function openChrome() {
    setStep(1);
    chromeWindow.classList.remove('mh-window--hidden');
    chromeBtnTB.disabled = false;
    chromeBtnTB.classList.add('is-open');
    pushFeed('Browser opened. Check the address bar before logging in.', 'warn');
  }

  // URL bar — user can edit http → https
  urlBar.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') { e.preventDefault(); applyUrl(); }
  });
  urlGoBtn.addEventListener('click', applyUrl);

  function applyUrl() {
    const val = (urlBar.textContent || '').trim();
    if (val.startsWith('https://')) {
      secIcon.textContent = '🔒';
      secIcon.classList.add('secure');
      notSecLabel.classList.add('hidden-label');
    } else {
      secIcon.textContent = '⚠';
      secIcon.classList.remove('secure');
      notSecLabel.classList.remove('hidden-label');
    }
    pushFeed(`URL updated: ${val}`, 'info');
    log('url_changed', val);
  }

  loginBtn.addEventListener('click', () => {
    const idVal  = (document.getElementById('mh-student-id').value || '').trim();
    const pwVal  = (document.getElementById('mh-password').value || '').trim();
    const currentUrl = (urlBar.textContent || '').trim();

    // Validate student ID format TUPT-XX-XXXX
    const idPattern = /^TUPT-\d{2}-\d{4}$/;
    if (!idPattern.test(idVal)) {
      pushFeed('Invalid Student ID format. Use TUPT-XX-XXXX.', 'warn');
      return;
    }
    if (!pwVal) {
      pushFeed('Enter your password.', 'warn');
      return;
    }

    // Evaluate silently — no success/fail message
    const isHttps = currentUrl.startsWith('https://');
    if (!isHttps) {
      deduct('http_login', 'Logged in over HTTP (unencrypted connection)');
    } else {
      goodCall('Logged in over HTTPS (encrypted connection)', 'https_login');
    }

    log('login', idVal);
    pushFeed('Logging in… redirecting to payment portal.', 'info');

    // Show payment page
    setTimeout(() => {
      loginPage.classList.add('mh-page-hidden');
      payPage.classList.remove('mh-page-hidden');
      if (portalUser) portalUser.textContent = idVal;
      if (payId) payId.textContent = idVal;
      setStep(2);
      pushFeed('Payment page loaded. Review all details before confirming.', 'warn');
    }, 600);
  });

  /* ══ STAGE 3 — Payment ══ */

  payBtn.addEventListener('click', () => {
    const receiver = (receiverField.textContent || '').trim();
    const correctReceiver = 'payment@tupt.edu.ph';
    const alteredReceiver = 'payrnent@tupt.edu.ph'; // rn looks like m

    if (receiver === correctReceiver) {
      goodCall('Corrected the payment receiver email', 'correct_receiver');
    } else if (receiver === alteredReceiver) {
      deduct('wrong_receiver', 'Confirmed payment with tampered receiver email');
    } else if (receiver !== correctReceiver) {
      deduct('wrong_receiver', 'Confirmed payment with incorrect receiver email');
    }

    log('payment_confirmed', receiver);
    pushFeed('Payment submitted. Simulation complete.', 'info');

    setTimeout(() => showReveal(), 700);
  });

  /* ══ REVEAL SCREEN ══ */

  const STEP_META = [
    {
      label: 'Step 1 — WiFi Selection',
      good:    { label: 'Connected to WPA3-Enterprise network', detail: 'WPA3-Enterprise uses 802.1X authentication, meaning each device gets an individual encrypted session. An attacker on the same network cannot intercept other users\' traffic.' },
      mistake: { label: 'Connected to an untrusted or open network', detail: 'Open or WPA2-Personal networks allow any device nearby to intercept traffic using ARP spoofing or by acting as a rogue access point. All data sent over this connection was visible to the attacker.' },
    },
    {
      label: 'Step 2 — URL Verification',
      good:    { label: 'Accessed the portal over HTTPS', detail: 'HTTPS encrypts the connection between your browser and the server using TLS. Even if an attacker intercepts the packets, the data is unreadable without the private key.' },
      mistake: { label: 'Logged in over HTTP (no encryption)', detail: 'HTTP transmits data in plain text. The attacker on your network captured your Student ID and password as they travelled through the network — no decryption required.' },
    },
    {
      label: 'Step 3 — Payment Receiver',
      good:    { label: 'Corrected the tampered receiver email', detail: 'The MITM attacker altered the payment receiver from payment@tupt.edu.ph to payrnent@tupt.edu.ph. Catching this prevented the payment from being redirected to the attacker\'s account.' },
      mistake: { label: 'Confirmed payment with a tampered receiver email', detail: 'The MITM attacker changed "payment" to "payrnent" — a single character swap that looks nearly identical. Your ₱7,800 was redirected to an account controlled by the attacker.' },
    },
  ];

  function showReveal() {
    if (timerHandle) clearInterval(timerHandle);
    setStep(3);

    const isSafe   = (key) => !mistakes.some(m => m.toLowerCase().includes(key));
    const stepChecks = [
      !mistakes.some(m => m.includes('untrusted network') || m.includes('Connected to')),
      !mistakes.some(m => m.includes('HTTP')),
      !mistakes.some(m => m.includes('receiver')),
    ];

    const timeSpent = missionStart ? Math.round((Date.now() - missionStart) / 1000) : 0;
    const mistakeCount = mistakes.length;

    const itemsHtml = STEP_META.map((meta, i) => {
      const wasGood = stepChecks[i];
      const info    = wasGood ? meta.good : meta.mistake;
      return `
        <div class="mh-reveal-item ${wasGood ? 'mh-reveal-item--good' : 'mh-reveal-item--mistake'}">
          <span class="mh-reveal-item__icon">${wasGood ? '✓' : '✗'}</span>
          <div class="mh-reveal-item__body">
            <span class="mh-reveal-item__step">${meta.label}</span>
            <span class="mh-reveal-item__label">${info.label}</span>
            <span class="mh-reveal-item__detail">${info.detail}</span>
          </div>
        </div>`;
    }).join('');

    const scoreClass = score >= 35 ? '' : 'low';
    const mins = Math.floor(timeSpent / 60), secs = String(timeSpent % 60).padStart(2, '0');

    revealContent.innerHTML = `
      <span class="mh-reveal__badge">Simulation Complete</span>
      <h2 class="mh-reveal__title">The School Canteen — What Happened</h2>
      <p class="mh-reveal__sub">
        ${mistakeCount === 0
          ? 'Perfect run. You made no mistakes — the attacker collected nothing.'
          : `You made ${mistakeCount} mistake${mistakeCount > 1 ? 's' : ''}. Here is what the attacker was able to intercept and why.`
        }
      </p>
      <div>
        <div class="mh-reveal__section-label">Decision Breakdown</div>
        <div class="mh-reveal__items">${itemsHtml}</div>
      </div>
      <div class="mh-reveal__score-row">
        <span class="mh-reveal__score-label">Final Score &nbsp;·&nbsp; Time: ${mins}m ${secs}s</span>
        <span class="mh-reveal__score-value ${scoreClass}">${score} / ${MAX_SCORE} pts</span>
      </div>
      <div class="mh-reveal__actions">
        <button type="button" class="mh-reveal__btn mh-reveal__btn--ghost" id="mh-btn-exit">← Cyber Range</button>
        <button type="button" class="mh-reveal__btn mh-reveal__btn--primary" id="mh-btn-finish">Save &amp; Continue →</button>
      </div>
    `;

    revealOverlay.hidden = false;

    document.getElementById('mh-btn-exit').addEventListener('click', () => {
      window.location.href = data.briefing_url || '/simulations/mitm';
    });
    document.getElementById('mh-btn-finish').addEventListener('click', finishMission);
  }

  /* ══ FINISH — POST to backend ══ */
  async function finishMission() {
    const btn = document.getElementById('mh-btn-finish');
    if (btn) { btn.disabled = true; btn.textContent = 'Saving…'; }

    const timeSpent = missionStart ? Math.round((Date.now() - missionStart) / 1000) : 0;
    const normalised = Math.round((score / MAX_SCORE) * 100);

    try {
      const res = await fetch(data.complete_url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          score: normalised,
          mistakes,
          good_decisions: goodDecisions,
          recommendations,
          actions_log: actionsLog,
          time_spent_seconds: timeSpent,
          skills_developed: data.skills_learned || [],
          flags_found: [],
        }),
      });
      const payload = await res.json().catch(() => ({}));
      if (payload.redirect) window.location.href = payload.redirect;
    } catch {
      if (btn) { btn.disabled = false; btn.textContent = 'Save & Continue →'; }
      pushFeed('Could not save results. Please try again.', 'bad');
    }
  }

})();
