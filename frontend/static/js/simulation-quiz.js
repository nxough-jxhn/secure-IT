(function () {
  const dataElement = document.getElementById('sim-quiz-data');
  if (!dataElement) return;

  const data = JSON.parse(dataElement.textContent);
  const questions = data.questions || [];
  let currentQuestion = 0;
  let correctCount = 0;
  let incorrectCount = 0;
  const answers = [];

  // DOM refs
  const questionText    = document.getElementById('quiz-question-text');
  const stepLabel       = document.getElementById('quiz-step-label');
  const optionsEl       = document.getElementById('quiz-options');
  const feedbackPanel   = document.getElementById('quiz-feedback-panel');
  const feedbackLabel   = document.getElementById('quiz-feedback-label');
  const feedbackText    = document.getElementById('quiz-feedback-text');
  const nextBtn         = document.getElementById('quiz-next-btn');
  const progressFill    = document.getElementById('quiz-progress-fill');
  const progressLabel   = document.getElementById('quiz-progress-label');
  const correctCountEl  = document.getElementById('quiz-correct-count');
  const incorrectCountEl= document.getElementById('quiz-incorrect-count');
  const questionPanel   = document.getElementById('quiz-question-panel');
  const summaryPanel    = document.getElementById('quiz-summary-panel');
  const finalScore      = document.getElementById('quiz-final-score');
  const pointsValue     = document.getElementById('quiz-points-value');
  const scoreArc        = document.getElementById('quiz-score-arc');
  const ptsArc          = document.getElementById('quiz-pts-arc');
  const pointsEarned    = document.getElementById('quiz-points-earned');
  const summaryFeedback = document.getElementById('quiz-summary-feedback');

  // SVG icons per option index (A=clock, B=shield-check, C=lock, D=send)
  const OPTION_ICONS = [
    // A – clock
    `<svg viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67V7z" fill="currentColor"/></svg>`,
    // B – shield check
    `<svg viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-2 16l-4-4 1.41-1.41L10 14.17l6.59-6.59L18 9l-8 8z" fill="currentColor"/></svg>`,
    // C – lock
    `<svg viewBox="0 0 24 24"><path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z" fill="currentColor"/></svg>`,
    // D – send / paper plane
    `<svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" fill="currentColor"/></svg>`,
  ];

  function updateProgress() {
    const total = questions.length || 1;
    const shown = Math.min(currentQuestion + 1, total);
    const pct = (shown / total) * 100;
    progressFill.style.width = `${pct}%`;
    progressLabel.textContent = `${shown} / ${total}`;
    stepLabel.textContent = `Question ${shown} of ${total}`;
  }

  function updateCounters() {
    if (correctCountEl)   correctCountEl.textContent   = correctCount;
    if (incorrectCountEl) incorrectCountEl.textContent = incorrectCount;
  }

  function renderQuestion() {
    if (currentQuestion >= questions.length) {
      currentQuestion = Math.max(questions.length - 1, 0);
    }

    const question = questions[currentQuestion];
    if (!question) return;

    feedbackPanel.classList.add('hidden');
    feedbackPanel.classList.remove('is-success', 'is-error');
    optionsEl.innerHTML = '';
    questionText.textContent = question.question;
    nextBtn.disabled = true;
    updateProgress();

    question.options.forEach((option, index) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'qz-option';
      button.innerHTML = `
        <span class="qz-option__letter">${String.fromCharCode(65 + index)}</span>
        <span class="qz-option__icon">${OPTION_ICONS[index] || OPTION_ICONS[0]}</span>
        <span class="qz-option__text">${option}</span>
      `;
      button.addEventListener('click', () => handleAnswer(question, index, button));
      optionsEl.appendChild(button);
    });
  }

  function handleAnswer(question, selectedIndex, button) {
    // Disable all options
    Array.from(optionsEl.querySelectorAll('button')).forEach(btn => { btn.disabled = true; });
    answers[currentQuestion] = selectedIndex;

    const isCorrect = selectedIndex === question.correct;

    if (isCorrect) {
      correctCount++;
      button.classList.add('correct');
      feedbackLabel.textContent = 'Correct';
      feedbackPanel.classList.add('is-success');
    } else {
      incorrectCount++;
      button.classList.add('incorrect');
      const correctBtn = optionsEl.children[question.correct];
      if (correctBtn) correctBtn.classList.add('correct');
      feedbackLabel.textContent = 'Incorrect';
      feedbackPanel.classList.add('is-error');
    }

    feedbackText.textContent = question.explanation;
    feedbackPanel.classList.remove('hidden');
    nextBtn.disabled = false;
    updateCounters();
  }

  nextBtn.addEventListener('click', () => {
    currentQuestion += 1;
    if (currentQuestion >= questions.length) {
      submitQuiz();
    } else {
      renderQuestion();
    }
  });

  async function submitQuiz() {
    nextBtn.disabled = true;
    questionText.textContent = 'Submitting…';

    try {
      const response = await fetch(data.submit_url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error('Quiz submit failed');
      showSummary(payload);
    } catch (err) {
      alert('Could not submit quiz. Please try again.');
      nextBtn.disabled = false;
      currentQuestion = Math.max(questions.length - 1, 0);
      renderQuestion();
    }
  }

  function setArc(el, pct) {
    if (!el) return;
    const circumference = 2 * Math.PI * 52; // r=52 → ~326.7
    const drawn = (pct / 100) * circumference;
    el.setAttribute('stroke-dasharray', `${drawn} ${circumference}`);
  }

  function showSummary(payload) {
    questionPanel.classList.add('hidden');
    summaryPanel.classList.remove('hidden');

    const score = payload.score || 0;
    const pts   = payload.points_earned || 0;
    const maxQPts = 33;

    finalScore.textContent  = `${score}%`;
    pointsValue.textContent = `+${pts}`;
    if (pointsEarned) pointsEarned.textContent = `+${pts} bonus points added to your profile`;

    // Animate arcs after a brief delay so the element is visible
    requestAnimationFrame(() => {
      setArc(scoreArc, score);
      setArc(ptsArc, Math.round((pts / maxQPts) * 100));
    });

    summaryFeedback.innerHTML = '';
    (payload.feedback || []).forEach((item, index) => {
      const card = document.createElement('div');
      card.className = `qz-sum-item ${item.correct ? 'is-correct' : 'is-wrong'}`;
      card.innerHTML = `
        <span class="qz-sum-item__badge">Question ${index + 1} — ${item.correct ? 'Correct' : 'Incorrect'}</span>
        <p class="qz-sum-item__q">${item.question}</p>
        <p class="qz-sum-item__exp">${item.explanation}</p>
      `;
      summaryFeedback.appendChild(card);
    });
  }

  renderQuestion();
})();
