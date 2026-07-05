(function () {
  'use strict';

  const dataEl = document.getElementById('workspace-data');
  if (!dataEl) return;
  const data = JSON.parse(dataEl.textContent);

  /* ══ Conversation definitions ══
     Order is randomized on load so users can't assume which is first = real.
     LEGIT = Conversation A or B depending on flip.
     All scoring tracked silently.
  ══════════════════════════════ */

  // Randomize which slot is legit
  const legitFirst = Math.random() < 0.5;

  const LEGIT_SENDER = {
    id: 'legit',
    name: 'Ma\'am Reyes — TUP-T Registrar',
    initials: 'MR',
    color: '#0a7c4d',
    verified: true,
  };

  const FAKE_SENDER = {
    id: 'fake',
    name: 'TUP-T Enrollment Assistance',
    initials: 'EA',
    color: '#1877f2',
    verified: false,
  };

  /* LEGIT conversation script
     Only asks for: name, student ID, school email.
     Confirms data from her end. Short and closes cleanly.
  */
  const LEGIT_SCRIPT = [
    {
      type: 'received',
      text: 'Good afternoon po. This is Ma\'am Reyes from the TUP-T Registrar\'s Office. We\'re doing final verification for re-enrollment confirmations this semester. May I confirm your full name as registered in our system?',
      delay: 1200,
      waitForReply: true,
      replyKey: 'name',
    },
    {
      type: 'received',
      text: 'Thank you. And your student ID number please? Format is TUPT-XX-XXXX.',
      delay: 1000,
      waitForReply: true,
      replyKey: 'student_id',
    },
    {
      type: 'received',
      text: 'Got it. And lastly, your TUP-T school email address, for our records.',
      delay: 1000,
      waitForReply: true,
      replyKey: 'school_email',
    },
    {
      type: 'received',
      text: 'Perfect — your details match what we have on file. Your section is confirmed as BSIT 2-1 with 21 enrolled units. Re-enrollment is finalized. You\'ll receive an SMS confirmation to your registered number within 24 hours. Thank you and good luck this semester!',
      delay: 1200,
      waitForReply: false,
      final: true,
    },
  ];

  /* FAKE conversation script
     Starts identically to legit — name and ID.
     Then escalates: asks for course/year (has it), mobile number, sends fake image,
     asks for SHS name framed as "updating transfer records",
     asks for parent/guardian name framed as "confirming contact on file".
     Closes warmly. No password request — purely profile harvesting.
  */
  const FAKE_SCRIPT = [
    {
      type: 'received',
      text: 'Hi! Good afternoon po. We\'re from the TUP-T Enrollment Assistance Team helping students finalize their re-enrollment records this semester. Just a quick verification — can I get your complete name?',
      delay: 1200,
      waitForReply: true,
      replyKey: 'name',
    },
    {
      type: 'received',
      text: 'Thanks! And your student ID?',
      delay: 900,
      waitForReply: true,
      replyKey: 'student_id',
    },
    {
      type: 'received',
      text: 'Got it! Just to make sure we have your updated info — what\'s your current course and year level?',
      delay: 1000,
      waitForReply: true,
      replyKey: 'course_year',
      scoreKey: 'gave_course',
      deduct: 5,
    },
    {
      type: 'received',
      text: 'Okay! And just to confirm the right contact details on our end — what\'s the mobile number registered on your account?',
      delay: 1000,
      waitForReply: true,
      replyKey: 'mobile',
      scoreKey: 'gave_mobile',
      deduct: 8,
    },
    {
      type: 'image',
      delay: 1400,
      waitForReply: false,
      imageLabel: 'Enrollment Confirmation Preview',
    },
    {
      type: 'received',
      text: 'Here\'s a preview of your confirmation slip! We just need to verify one more detail to release this — for our transfer records update, what was the name of your senior high school?',
      delay: 800,
      waitForReply: true,
      replyKey: 'shs_name',
      scoreKey: 'gave_shs',
      deduct: 8,
    },
    {
      type: 'received',
      text: 'Perfect! Last thing lang po — we have two contact persons on file for emergency purposes. Who\'s your primary contact person? Just confirming the name.',
      delay: 1100,
      waitForReply: true,
      replyKey: 'guardian_name',
      scoreKey: 'gave_guardian',
      deduct: 8,
    },
    {
      type: 'received',
      text: 'Thank you so much po! Your re-enrollment is now confirmed. You should receive a confirmation within 24 hours. Good luck this sem! 😊',
      delay: 1000,
      waitForReply: false,
      final: true,
    },
  ];

  /* Ordered by randomization */
  const CONVERSATIONS = legitFirst
    ? [
        { label: 'A', sender: LEGIT_SENDER, script: LEGIT_SCRIPT, isLegit: true },
        { label: 'B', sender: FAKE_SENDER,  script: FAKE_SCRIPT,  isLegit: false },
      ]
    : [
        { label: 'A', sender: FAKE_SENDER,  script: FAKE_SCRIPT,  isLegit: false },
        { label: 'B', sender: LEGIT_SENDER, script: LEGIT_SCRIPT, isLegit: true },
      ];

  const CORRECT_ANSWER = CONVERSATIONS.find(c => c.isLegit).label;

  const REFUSAL_PROMPTS = {
    legit_name: {
      prompt: (val) => `To continue verification, we need your full name. Your reply '${val}' does not match the name saved in our database. Please provide your registered full name.`,
      exit: "Since you cannot verify your name, we cannot proceed with re-enrollment. Terminating verification."
    },
    legit_student_id: {
      prompt: (val) => `Verification requires your student ID. Your reply '${val}' does not match the ID format in our database. Please provide your correct student ID (e.g. TUPT-21-4892).`,
      exit: "We cannot verify your record without a student ID. Ending verification."
    },
    legit_school_email: {
      prompt: (val) => `To finalize enrollment, we need your registered school email. Your reply '${val}' is incorrect. Please provide your official school email.`,
      exit: "Without a verified school email, we cannot complete re-enrollment. Goodbye."
    },
    fake_name: {
      prompt: (val) => `To continue with your enrollment assistance, we need your full name. Your reply '${val}' does not match our records. Please verify your complete name.`,
      exit: "We cannot assist you without your registered name. Terminating assistance."
    },
    fake_student_id: {
      prompt: (val) => `We need your correct student ID to check your files. Your reply '${val}' is invalid. Please share your student ID.`,
      exit: "Sorry, we cannot continue without your student ID. Goodbye."
    },
    fake_course_year: {
      prompt: (val) => `To update your file, we need your current course and year. Your reply '${val}' is invalid. Please share it.`,
      exit: "We cannot complete the update without your course details. Terminating chat."
    },
    fake_mobile: {
      prompt: (val) => `Please provide your correct mobile number so we can send your verification PIN. Your reply '${val}' is not a valid contact number.`,
      exit: "We cannot proceed without a verified contact number. Terminating chat."
    },
    fake_shs_name: {
      prompt: (val) => `Your senior high school name is required to verify your transcript records. Your reply '${val}' does not match. Please provide it.`,
      exit: "We cannot release the slip without this record. Goodbye."
    },
    fake_guardian_name: {
      prompt: (val) => `We need your primary emergency contact's name for database confirmation. Your reply '${val}' is invalid. Please share it.`,
      exit: "Emergency contact is required to finalize. Ending conversation."
    }
  };

  /* ══ State ══ */
  let score = 0;
  const MAX_SCORE = 50;
  const FINAL_ID_POINTS = 15;
  const mistakes = [], goodDecisions = [], actionsLog = [];
  const sharedData = {}; // tracks what user typed per replyKey per convo
  let missionStart = null;
  let timerHandle = null;
  let currentConvIndex = 0;
  let currentStepIndex = 0;
  let waitingForReply = false;
  let convDone = [false, false];
  let hasRefusedCurrentStep = false;

  /* Predefined student identity used in scoring */
  const STUDENT_ID = {
    name:     'Juan Dela Cruz',
    student_id: 'TUPT-21-4892',
    school_email: 'juan.delacruz@tup.edu.ph',
    course:   'BSIT 2nd Year',
    section:  'BSIT 2-1',
    mobile:   '09171234567',
    shs_name: 'Taguig National High School',
    guardian_name: 'Maria Dela Cruz',
  };

  const recommendations = [
    'Legitimate school registrars only ask for name, student ID, and school email for re-enrollment — they already have everything else.',
    'Be suspicious of any contact that asks for information the institution should already have in their database.',
    'Social engineering attacks often start with normal-sounding questions before escalating to sensitive data.',
    'Compare the tone, length, and types of questions between two contacts — patterns reveal intent.',
  ];

  /* ══ DOM ══ */
  const timerEl       = document.getElementById('se-timer');
  const progFill      = document.getElementById('se-progress-fill');
  const progLabel     = document.getElementById('se-progress-label');
  const logEl         = document.getElementById('se-log');
  const eventFeed     = document.getElementById('se-event-feed');
  const convLabel     = document.getElementById('se-conv-label');
  const convStatus    = document.getElementById('se-conv-status');
  const senderAvatar  = document.getElementById('se-sender-avatar');
  const senderName    = document.getElementById('se-sender-name');
  const senderStatus  = document.getElementById('se-sender-status');
  const chat          = document.getElementById('se-chat');
  const replyInput    = document.getElementById('se-reply-input');
  const sendBtn       = document.getElementById('se-send-btn');
  const phoneTime     = document.getElementById('se-phone-time');
  const finalModal    = document.getElementById('se-final-modal');
  const revealOverlay = document.getElementById('se-reveal-overlay');
  const revealContent = document.getElementById('se-reveal-content');
  const transitionModal = document.getElementById('se-transition-modal');
  const transitionTitle = document.getElementById('se-trans-title');
  const transitionDesc  = document.getElementById('se-trans-desc');
  const transitionBtn   = document.getElementById('se-trans-btn');

  /* ══ Helpers ══ */
  function logAction(a, d) { actionsLog.push({ action: a, detail: d, at: new Date().toISOString() }); }
  function pushFeed(msg, tone) {
    const li = document.createElement('li');
    li.className = `se-event${tone ? ' se-event--' + tone : ''}`;
    li.textContent = msg;
    eventFeed.prepend(li);
    if (eventFeed.children.length > 1) {
      const ph = eventFeed.querySelector(':last-child');
      if (ph && ph.textContent.includes('Waiting')) ph.remove();
    }
  }
  function pushLog(msg, cls) {
    const empty = logEl.querySelector('.se-log__empty');
    if (empty) empty.remove();
    const li = document.createElement('li');
    if (cls) li.className = cls;
    li.textContent = msg;
    logEl.appendChild(li);
  }
  function scrollChat() {
    chat.scrollTop = chat.scrollHeight;
  }
  function updateClock() {
    const now = new Date();
    let h = now.getHours(), m = String(now.getMinutes()).padStart(2, '0');
    const ap = h >= 12 ? 'PM' : 'AM'; h = h % 12 || 12;
    if (phoneTime) phoneTime.textContent = `${h}:${m}`;
    setTimeout(updateClock, 30000);
  }

  /* ══ Briefing start ══ */
  document.getElementById('se-briefing-start').addEventListener('click', () => {
    document.getElementById('se-briefing').style.display = 'none';
    missionStart = Date.now();
    timerHandle = setInterval(() => {
      const e = Math.floor((Date.now() - missionStart) / 1000);
      if (timerEl) timerEl.textContent =
        String(Math.floor(e / 60)).padStart(2, '0') + ':' + String(e % 60).padStart(2, '0');
    }, 1000);
    updateClock();
    startConversation(0);
  });

  /* ══ End Simulation button ══ */
  document.getElementById('se-end-btn').addEventListener('click', () => {
    if (!missionStart) { window.location.href = data.briefing_url || '/simulations/social_engineering'; return; }
    if (!confirm('End the simulation now? You will keep the points earned so far.')) return;
    mistakes.push('Ended simulation early');
    logAction('end_early', score);
    showFinalQuestion();
  });

  /* ══ Load conversation UI ══ */
  function startConversation(idx) {
    currentConvIndex = idx;
    currentStepIndex = 0;
    waitingForReply = false;
    hasRefusedCurrentStep = false;
    const conv = CONVERSATIONS[idx];

    // Update sidebar progress
    const pct = idx === 0 ? 0 : 50;
    if (progFill) progFill.style.width = `${pct}%`;
    if (progLabel) progLabel.textContent = `Conversation ${idx + 1} of 2`;

    // Update topbar
    if (convLabel) convLabel.textContent = `Conversation ${conv.label}`;
    if (convStatus) convStatus.textContent = 'Active';

    // Update phone messenger header
    if (senderAvatar) {
      senderAvatar.textContent = conv.sender.initials;
      senderAvatar.style.background = conv.sender.color;
    }
    if (senderName) senderName.textContent = conv.sender.name;
    if (senderStatus) senderStatus.textContent = 'Active now';

    // Clear chat
    chat.innerHTML = '';
    const dateDiv = document.createElement('div');
    dateDiv.className = 'se-chat-date';
    dateDiv.textContent = 'Today';
    chat.appendChild(dateDiv);

    // Enable input
    replyInput.disabled = false;
    replyInput.value = '';
    sendBtn.disabled = true;

    pushFeed(`Conversation ${conv.label} started.`, 'info');
    pushLog(`Started Conversation ${conv.label}`, '');

    // Begin script
    runStep();
  }

  /* ══ Script runner ══ */
  function runStep() {
    const conv = CONVERSATIONS[currentConvIndex];
    const step = conv.script[currentStepIndex];
    if (!step) return;

    if (step.type === 'received' || step.type === 'image') {
      // Show typing indicator
      const typingEl = document.createElement('div');
      typingEl.className = 'se-typing';
      typingEl.innerHTML = `
        <span class="se-typing__dot"></span>
        <span class="se-typing__dot"></span>
        <span class="se-typing__dot"></span>`;
      chat.appendChild(typingEl);
      scrollChat();

      setTimeout(() => {
        typingEl.remove();

        if (step.type === 'image') {
          appendFakeImage(conv.sender);
        } else {
          appendReceivedBubble(step.text, conv.sender);
        }
        scrollChat();

        if (step.waitForReply) {
          waitingForReply = true;
          replyInput.disabled = false;
          replyInput.focus();
        } else {
          currentStepIndex++;
          if (step.final) {
            convDone[currentConvIndex] = true;
            onConversationEnd();
          } else {
            setTimeout(runStep, 600);
          }
        }
      }, step.delay || 1000);
    }
  }

  function appendReceivedBubble(text, sender) {
    const wrap = document.createElement('div');
    wrap.className = 'se-bubble-received';
    wrap.innerHTML = `
      <div class="se-bubble-received__avatar" style="background:${sender.color}">${sender.initials}</div>
      <div class="se-bubble-received__text">${text}</div>`;
    chat.appendChild(wrap);
  }

  function appendFakeImage(sender) {
    const wrap = document.createElement('div');
    wrap.className = 'se-bubble-received';
    wrap.innerHTML = `
      <div class="se-bubble-received__avatar" style="background:${sender.color}">${sender.initials}</div>
      <div class="se-fake-img">
        <div class="se-fake-img__header">
          <span class="se-fake-img__logo">🎓</span>
          <span class="se-fake-img__title">TUP-T RE-ENROLLMENT CONFIRMATION</span>
        </div>
        <div class="se-fake-img__row"><span>Student Name</span><span>________________</span></div>
        <div class="se-fake-img__row"><span>Student ID</span><span>________________</span></div>
        <div class="se-fake-img__row"><span>Course / Year</span><span>________________</span></div>
        <div class="se-fake-img__row"><span>Semester</span><span>1st Sem AY 2025-2026</span></div>
        <div class="se-fake-img__row"><span>Status</span><span>PENDING VERIFICATION</span></div>
        <div class="se-fake-img__footer">Official TUP-T Registrar's Office • For verification purposes only</div>
      </div>`;
    chat.appendChild(wrap);
  }

  function appendSentBubble(text) {
    const div = document.createElement('div');
    div.className = 'se-bubble-sent';
    div.textContent = text;
    chat.appendChild(div);
    scrollChat();
  }

  /* ══ Reply handling ══ */
  replyInput.addEventListener('input', () => {
    sendBtn.disabled = replyInput.value.trim().length === 0;
  });
  replyInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !sendBtn.disabled) { e.preventDefault(); handleSend(); }
  });
  sendBtn.addEventListener('click', handleSend);

  function verifyDetail(key, text) {
    if (!text) return false;
    const t = text.toLowerCase().trim();
    switch (key) {
      case 'name':
        return t.includes('juan') || t.includes('dela') || t.includes('cruz');
      case 'student_id':
        return t.includes('4892') || t.includes('21-4892');
      case 'school_email':
        return t.includes('juan') && (t.includes('tup') || t.includes('delacruz'));
      case 'course_year':
        return t.includes('bsit') || t.includes('2nd') || t.includes('second');
      case 'mobile':
        return t.includes('0917') || t.includes('1234567') || t.includes('4567');
      case 'shs_name':
        return t.includes('taguig') || t.includes('national');
      case 'guardian_name':
        return t.includes('maria');
      default:
        return true;
    }
  }

  function handleSend() {
    if (!waitingForReply) return;
    const text = replyInput.value.trim();
    if (!text) return;

    waitingForReply = false;
    replyInput.disabled = true;
    sendBtn.disabled = true;
    replyInput.value = '';

    appendSentBubble(text);

    const conv = CONVERSATIONS[currentConvIndex];
    const step = conv.script[currentStepIndex];

    if (step.replyKey) {
      const isValid = verifyDetail(step.replyKey, text);
      const key = `${conv.sender.id}_${step.replyKey}`;
      const refusalMeta = REFUSAL_PROMPTS[key];

      if (!isValid) {
        // Verification failed (explicit refusal, short response, or incorrect/fake data)
        const displayReply = text.length > 25 ? text.substring(0, 25) + '...' : text;
        
        if (!hasRefusedCurrentStep && refusalMeta) {
          // First refusal: show follow-up prompt, do NOT advance step index
          hasRefusedCurrentStep = true;
          logAction('refusal_first', { conv: conv.label, key: step.replyKey, value: text });
          pushLog(`Refused: ${step.replyKey}`, '');

          setTimeout(() => {
            const typingEl = document.createElement('div');
            typingEl.className = 'se-typing';
            typingEl.innerHTML = `
              <span class="se-typing__dot"></span>
              <span class="se-typing__dot"></span>
              <span class="se-typing__dot"></span>`;
            chat.appendChild(typingEl);
            scrollChat();

            setTimeout(() => {
              typingEl.remove();
              appendReceivedBubble(refusalMeta.prompt(displayReply), conv.sender);
              scrollChat();

              waitingForReply = true;
              replyInput.disabled = false;
              replyInput.focus();
            }, 1000);
          }, 600);
          return;
        } else {
          // Second refusal/failure: exit/end conversation immediately
          logAction('refusal_second', { conv: conv.label, key: step.replyKey, value: text });
          pushLog(`Refused: ${step.replyKey}`, '');

          // Attaker flow: award refusal bonus points on second refusal
          if (!conv.isLegit && step.deduct) {
            score += 5;
            goodDecisions.push(`Refused unnecessary question: ${step.replyKey}`);
          }

          setTimeout(() => {
            const typingEl = document.createElement('div');
            typingEl.className = 'se-typing';
            typingEl.innerHTML = `
              <span class="se-typing__dot"></span>
              <span class="se-typing__dot"></span>
              <span class="se-typing__dot"></span>`;
            chat.appendChild(typingEl);
            scrollChat();

            setTimeout(() => {
              typingEl.remove();
              appendReceivedBubble(refusalMeta ? refusalMeta.exit : "Ending conversation.", conv.sender);
              scrollChat();

              convDone[currentConvIndex] = true;
              onConversationEnd();
            }, 1000);
          }, 600);
          return;
        }
      } else {
        // Correct details provided!
        hasRefusedCurrentStep = false;
        sharedData[`${conv.id}_${step.replyKey}`] = text;
        logAction('reply', { conv: conv.label, key: step.replyKey, value: text });

        if (!conv.isLegit && step.deduct) {
          // Shared unnecessary data with attacker
          score = Math.max(0, score - step.deduct);
          mistakes.push(`Shared ${step.replyKey} with attacker`);
          pushLog(`Shared: ${step.replyKey}`, '');
        } else if (conv.isLegit) {
          // Provided to legit registrar
          const earns = { name: 5, student_id: 8, school_email: 7 };
          const earned = earns[step.replyKey] || 0;
          if (earned > 0) {
            score = Math.min(MAX_SCORE - FINAL_ID_POINTS, score + earned);
            goodDecisions.push(`Provided ${step.replyKey} to legitimate staff`);
            pushLog(`Shared: ${step.replyKey}`, '');
          }
        } else {
          // name / student_id given to fake convo = not penalized
          pushLog(`Shared: ${step.replyKey}`, '');
        }
      }
    }

    currentStepIndex++;
    setTimeout(runStep, 600);
  }

  /* ══ Conversation end ══ */
  function onConversationEnd() {
    const conv = CONVERSATIONS[currentConvIndex];
    pushFeed(`Conversation ${conv.label} complete.`, 'info');
    pushLog(`Conversation ${conv.label} ended`, '');

    replyInput.disabled = true;
    sendBtn.disabled = true;

    if (currentConvIndex === 0) {
      if (progFill) progFill.style.width = '50%';
      
      // Update transition modal labels dynamically
      if (transitionTitle) transitionTitle.textContent = `Conversation ${conv.label} Ended`;
      if (transitionDesc) transitionDesc.textContent = `You have completed Conversation ${conv.label}. Ready to proceed to Conversation ${CONVERSATIONS[1].label}?`;
      if (transitionBtn) {
        transitionBtn.textContent = `Proceed to Convo ${CONVERSATIONS[1].label}`;
        
        // Remove old listeners by cloning the button
        const newBtn = transitionBtn.cloneNode(true);
        transitionBtn.parentNode.replaceChild(newBtn, transitionBtn);
        newBtn.addEventListener('click', () => {
          transitionModal.hidden = true;
          
          // Clear chat area for clean transition
          chat.innerHTML = '';
          const note = document.createElement('div');
          note.className = 'se-chat-date';
          note.textContent = `Starting Conversation ${CONVERSATIONS[1].label}…`;
          chat.appendChild(note);
          
          setTimeout(() => startConversation(1), 1000);
        }, { once: true });
      }
      
      // Show transition modal
      setTimeout(() => {
        transitionModal.hidden = false;
      }, 4500);
    } else {
      // Both done — show final question
      if (progFill) progFill.style.width = '80%';
      setTimeout(showFinalQuestion, 1000);
    }
  }

  /* ══ Final identification question ══ */
  function showFinalQuestion() {
    if (timerHandle) clearInterval(timerHandle);
    finalModal.hidden = false;
    document.body.style.overflow = 'hidden';

    document.getElementById('se-final-a').addEventListener('click', () => handleFinalAnswer('A'), { once: true });
    document.getElementById('se-final-b').addEventListener('click', () => handleFinalAnswer('B'), { once: true });
  }

  function handleFinalAnswer(answer) {
    finalModal.hidden = true;
    document.body.style.overflow = '';
    const correct = answer === CORRECT_ANSWER;
    if (correct) {
      score = Math.min(MAX_SCORE, score + FINAL_ID_POINTS);
      goodDecisions.push('Correctly identified the legitimate conversation');
      pushFeed('Correct identification! +15 pts', 'good');
    } else {
      score = Math.max(0, score - 10);
      mistakes.push('Misidentified the attacker conversation as legitimate');
      pushFeed('Wrong identification. −10 pts', 'bad');
    }
    logAction('final_answer', { answer, correct });
    if (progFill) progFill.style.width = '100%';
    setTimeout(() => showReveal(answer, correct), 400);
  }

  /* ══ Reveal screen ══ */
  function showReveal(userAnswer, identCorrect) {
    const legitConv = CONVERSATIONS.find(c => c.isLegit);
    const fakeConv  = CONVERSATIONS.find(c => !c.isLegit);
    const timeSpent = missionStart ? Math.round((Date.now() - missionStart) / 1000) : 0;
    const mins = Math.floor(timeSpent / 60), secs = String(timeSpent % 60).padStart(2, '0');
    const scoreClass = score >= 35 ? '' : 'low';

    const dataSharedRows = [];
    if (sharedData['fake_course_year'] && !/refuse|no|why/i.test(sharedData['fake_course_year'] || '')) {
      dataSharedRows.push({ icon: '⚠', label: 'Course & Year Level', detail: 'The registrar already has this for re-enrollment. Asking is a red flag.', cls: 'warn' });
    }
    if (sharedData['fake_mobile'] && !/refuse|no|why/i.test(sharedData['fake_mobile'] || '')) {
      dataSharedRows.push({ icon: '⚠', label: 'Mobile Number', detail: 'Not needed to confirm re-enrollment — used as an account recovery / contact harvesting vector.', cls: 'warn' });
    }
    if (sharedData['fake_shs_name'] && !/refuse|no|why/i.test(sharedData['fake_shs_name'] || '')) {
      dataSharedRows.push({ icon: '⚠', label: 'Senior High School Name', detail: 'Framed as "updating transfer records" — but SHS name is a common security question answer.', cls: 'warn' });
    }
    if (sharedData['fake_guardian_name'] && !/refuse|no|why/i.test(sharedData['fake_guardian_name'] || '')) {
      dataSharedRows.push({ icon: '⚠', label: 'Guardian / Contact Name', detail: 'Framed as "confirming existing contact" — another account recovery field.', cls: 'warn' });
    }
    if (dataSharedRows.length === 0) {
      dataSharedRows.push({ icon: '✓', label: 'You did not share unnecessary data with the attacker.', detail: '', cls: 'ok' });
    }

    const dataRowsHtml = dataSharedRows.map(r => `
      <div class="se-reveal__data-row se-reveal__data-row--${r.cls}">
        <span class="se-reveal__data-icon">${r.icon}</span>
        <div class="se-reveal__data-body">
          <span class="se-reveal__data-label">${r.label}</span>
          ${r.detail ? `<span class="se-reveal__data-detail">${r.detail}</span>` : ''}
        </div>
      </div>`).join('');

    revealContent.innerHTML = `
      <span class="se-reveal__badge">Simulation Complete</span>
      <h2 class="se-reveal__title">Re-Enrollment Season — What Really Happened</h2>
      <p class="se-reveal__sub">
        ${identCorrect
          ? 'You correctly identified which conversation was legitimate. Here is the breakdown of what set them apart.'
          : `You identified Conversation ${userAnswer} as legitimate — that was actually the ${userAnswer === CORRECT_ANSWER ? 'real registrar' : 'attacker'}. Here is what you missed.`
        }
      </p>

      <div>
        <div class="se-reveal__section-label">Conversation Breakdown</div>
        <div class="se-reveal__convos">
          <div class="se-reveal-conv se-reveal-conv--legit">
            <div class="se-reveal-conv__header">
              <span class="se-reveal-conv__verdict">✓ Legitimate</span>
              <span class="se-reveal-conv__name">Conversation ${legitConv.label} — ${LEGIT_SENDER.name}</span>
            </div>
            <div class="se-reveal-conv__body">
              <div class="se-reveal-tag se-reveal-tag--safe"><span class="se-reveal-tag__icon">✓</span>Only asked for name, student ID, and school email</div>
              <div class="se-reveal-tag se-reveal-tag--safe"><span class="se-reveal-tag__icon">✓</span>Confirmed your section and units from her records — proving she has the database</div>
              <div class="se-reveal-tag se-reveal-tag--safe"><span class="se-reveal-tag__icon">✓</span>Formal, efficient tone — no excessive friendliness</div>
              <div class="se-reveal-tag se-reveal-tag--safe"><span class="se-reveal-tag__icon">✓</span>Closed with a specific official method (SMS to registered number)</div>
            </div>
          </div>
          <div class="se-reveal-conv se-reveal-conv--attack">
            <div class="se-reveal-conv__header">
              <span class="se-reveal-conv__verdict">✗ Attacker</span>
              <span class="se-reveal-conv__name">Conversation ${fakeConv.label} — ${FAKE_SENDER.name}</span>
            </div>
            <div class="se-reveal-conv__body">
              <div class="se-reveal-tag se-reveal-tag--technique"><span class="se-reveal-tag__icon">⚠</span><b>Foot-in-the-door:</b> started with normal questions before escalating</div>
              <div class="se-reveal-tag se-reveal-tag--technique"><span class="se-reveal-tag__icon">⚠</span><b>Unnecessary data:</b> asked for course/year the registrar already has</div>
              <div class="se-reveal-tag se-reveal-tag--technique"><span class="se-reveal-tag__icon">⚠</span><b>Reciprocity:</b> sent a fake official document to build trust before asking more</div>
              <div class="se-reveal-tag se-reveal-tag--technique"><span class="se-reveal-tag__icon">⚠</span><b>Reframing:</b> harvested security question answers by calling them "transfer records"</div>
              <div class="se-reveal-tag se-reveal-tag--technique"><span class="se-reveal-tag__icon">⚠</span>Warmer, friendlier tone — less formal than a real registrar would be</div>
              <div class="se-reveal-tag se-reveal-tag--technique"><span class="se-reveal-tag__icon">⚠</span>Sender name: "Enrollment Assistance" not "Registrar's Office"</div>
            </div>
          </div>
        </div>
      </div>

      <div>
        <div class="se-reveal__section-label">Data You Shared With the Attacker</div>
        ${dataRowsHtml}
      </div>

      <div class="se-reveal__score-row">
        <span class="se-reveal__score-label">Final Score &nbsp;·&nbsp; Time: ${mins}m ${secs}s</span>
        <span class="se-reveal__score-value ${scoreClass}">${score} / ${MAX_SCORE} pts</span>
      </div>

      <div class="se-reveal__actions">
        <button type="button" class="se-reveal__btn se-reveal__btn--ghost" id="se-btn-exit">← Cyber Range</button>
        <button type="button" class="se-reveal__btn se-reveal__btn--primary" id="se-btn-finish">Save &amp; Continue →</button>
      </div>
    `;

    revealOverlay.hidden = false;

    document.getElementById('se-btn-exit').addEventListener('click', () => {
      window.location.href = data.briefing_url || '/simulations/social_engineering';
    });
    document.getElementById('se-btn-finish').addEventListener('click', finishMission);
  }

  /* ══ POST results ══ */
  async function finishMission() {
    const btn = document.getElementById('se-btn-finish');
    if (btn) { btn.disabled = true; btn.textContent = 'Saving…'; }
    const timeSpent = missionStart ? Math.round((Date.now() - missionStart) / 1000) : 0;
    const normalised = Math.round((score / MAX_SCORE) * 100);
    try {
      const res = await fetch(data.complete_url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          score: normalised, mistakes, good_decisions: goodDecisions,
          recommendations, actions_log: actionsLog,
          time_spent_seconds: timeSpent,
          skills_developed: data.skills_learned || [],
          flags_found: [],
        }),
      });
      const payload = await res.json().catch(() => ({}));
      if (payload.redirect) window.location.href = payload.redirect;
    } catch {
      if (btn) { btn.disabled = false; btn.textContent = 'Save & Continue →'; }
      pushFeed('Could not save results. Try again.', 'bad');
    }
  }

})();
