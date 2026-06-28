# Secure-IT — Development Architecture & Build Plan

---

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────┐
│                  FRONTEND                    │
│         HTML + CSS + JavaScript              │
│   /templates  (Jinja2 rendered by Flask)     │
│   /static/css  /static/js                   │
└─────────────────┬───────────────────────────┘
                  │ HTTP Requests
┌─────────────────▼───────────────────────────┐
│                  BACKEND                     │
│              Flask (Python)                  │
│         /secure_it/routes/                   │
│              app.py                          │
└──────┬──────────┬──────────┬────────────────┘
       │          │          │
┌──────▼──┐ ┌────▼────┐ ┌───▼──────────────┐
│ MongoDB │ │Firebase │ │   Cloudinary      │
│ Atlas   │ │  Auth   │ │ (Profile Photos)  │
│(Primary │ │(Google  │ │                   │
│   DB)   │ │Sign-in) │ │                   │
└─────────┘ └─────────┘ └───────────────────┘
       │
┌──────▼──────────────────────────────────────┐
│            MongoDB Collections               │
│  users │ simulation_results │ badges         │
│  namecards │ certificates │ leaderboard      │
│  activity_logs │ metrics │ simulation_retakes│
└─────────────────────────────────────────────┘
```

---

## 🔧 Tech Stack


| Layer        | Technology              | Purpose                    |
| ------------ | ----------------------- | -------------------------- |
| Frontend     | HTML, CSS, JavaScript   | UI rendering               |
| Templating   | Jinja2 (Flask built-in) | Server-side HTML rendering |
| Backend      | Python + Flask          | Routes, logic, API         |
| Database     | MongoDB Atlas           | Primary data store         |
| Auth         | Firebase Auth           | Google Sign-in             |
| Auth (local) | bcrypt + JWT            | Email/password login       |
| Email        | Mailtrap (dev)          | Email verification         |
| File Storage | Cloudinary              | Profile photo uploads      |
| Env Config   | python-dotenv           | Environment variables      |


---

## 📁 Recommended Folder Structure

```
SECUR-IT/
│
├── secure_it/
│   ├── __init__.py
│   └── routes/
│       ├── auth.py          # login, register, verify email, google auth
│       ├── dashboard.py     # student dashboard, progress, leaderboard
│       ├── modules.py       # attack module list, category view
│       ├── simulation.py    # easy sim, hard sim, retake logic
│       ├── quiz.py          # quiz submission, scoring
│       ├── gamification.py  # badges, namecards, certificates, leaderboard
│       └── admin.py         # admin dashboard, user management, analytics
│
├── static/
│   ├── css/
│   │   ├── base.css
│   │   ├── dashboard.css
│   │   ├── simulation.css
│   │   └── gamification.css
│   ├── js/
│   │   ├── simulation.js    # simulation interactivity (click handlers, flagging signs)
│   │   ├── quiz.js          # quiz timer, answer selection, submission
│   │   └── leaderboard.js   # real-time leaderboard updates
│   └── uploads/
│       └── profiles/        # local profile photo fallback
│
├── templates/
│   ├── base.html            # base layout with nav
│   ├── auth/
│   │   ├── login.html
│   │   ├── register.html
│   │   └── verify.html
│   ├── dashboard/
│   │   ├── index.html       # student dashboard
│   │   └── profile.html     # profile + namecard gallery + certificates
│   ├── modules/
│   │   ├── index.html       # all modules grouped by category
│   │   ├── info.html        # informational page per attack
│   │   ├── easy_sim.html    # easy simulation with indicators
│   │   ├── hard_sim.html    # hard simulation no indicators
│   │   └── quiz.html        # quiz page
│   ├── gamification/
│   │   ├── leaderboard.html
│   │   ├── badges.html
│   │   └── namecards.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── users.html
│   │   └── analytics.html
│   └── certificates/
│       ├── performance.html
│       ├── completion.html
│       ├── perfect_score.html
│       └── leaderboard_cert.html
│
├── simulation_data.py       # all 10 attack definitions
├── simulation_missions.py   # workspace mission definitions
├── database.py              # all MongoDB functions
├── analytics.py             # admin analytics queries
├── firebase_auth.py         # Google auth handling
├── cloudinary_uploader.py   # profile photo upload
├── mailer.py                # email verification sending
├── seed_mongo.py            # initial DB seeding
├── app.py                   # Flask app entry point
├── .env                     # environment variables (never commit)
├── .env.example             # env template (safe to commit)
├── requirements.txt         # Python dependencies
└── README.md
```

---

## 🗓️ Development Build Plan

### 📋 Prerequisites (Already Done by Co-member)

- [x] Flask project structure initialized
- [x] MongoDB connection configured (`database.py`)
- [x] Firebase Auth configured (`firebase_auth.py`)
- [x] Cloudinary uploader configured
- [x] Mailtrap email configured
- [x] `.env` and `.env.example` set up
- [x] Basic `simulation_data.py` with some attacks
- [x] Basic `simulation_missions.py`
- [x] `seed_mongo.py` for initial data

---

### 🔴 Phase 1 — Foundation Fixes (Do This First)

*Fix existing code to match the final system design before building new features*

**1.1 — Update simulation_data.py**

- [x] Remove attacks not in final 10: `trojan`, `virus`, `dos`, `password_attack`
- [x] Rename `phishing` → `phishing_fake_email` for clarity
- [x] Add `category` and `category_label` field to all existing attacks
- [x] Add `easy_simulation` and `hard_simulation` keys to each attack
- [x] Add 6 missing attacks: `phishing_fake_website`, `keylogger`, `adware_malvertising`, `mitm`, `evil_twin`, `sql_injection`

**1.2 — Update database.py**

- [x] Fix `_level_for_points()` to use 5-level system (Rookie → Cyber Shield)
- [x] Update `DEFAULT_METRICS` — set `total_modules` to `10`
- [x] Add `module_progress` field structure to user documents
- [x] Update `record_simulation_completion()` to write to `module_progress`
- [x] Add `get_simulation_retakes()` function
- [x] Add `increment_simulation_retake()` function
- [x] Add `update_module_progress()` function

**1.3 — Update seed_mongo.py**

- [x] Update seeded metrics to reflect 10 modules
- [x] Add seed entries for new collections: badges, namecards, certificates, leaderboard

---

### 🟡 Phase 2 — Core Module Flow

*Build the main learning experience: info page → easy sim → hard sim → quiz*

**2.1 — Module List Page** (`/modules`)

- [x] Group and display all 10 attacks by category
- [x] Show locked/in progress/completed status per module
- [ ] Show category namecard progress (X/4 social-based complete, etc.)

**2.2 — Informational Page** (`/modules/<attack_id>/info`)

- [ ] Display attack overview, warning signs, prevention tips
- [ ] Embed curated educational video (internal, not YouTube)
- [ ] Show visual aids and annotated screenshots
- [ ] "Start Easy Simulation" button — only active after page is viewed
- [ ] Mark `info_page_viewed: True` in `module_progress` on first visit

**2.3 — Easy Simulation** (`/modules/<attack_id>/easy`)

- [ ] Render simulation interface (fake email, fake desktop, fake chat, etc.)
- [ ] Show visual indicators/highlights on red flag elements
- [ ] User clicks highlighted elements to acknowledge them
- [ ] On completion: mark `easy_sim_completed: True` in `module_progress`
- [ ] No points awarded — just unlocks hard simulation

**2.4 — Hard Simulation** (`/modules/<attack_id>/hard`)

- [ ] Render same simulation interface with NO indicators
- [ ] User must click/flag suspicious elements themselves
- [ ] Track which signs were found vs missed
- [ ] On partial completion: show choice modal — End or Retake
- [ ] On retake: check retake count — block if 2 retakes already used
- [ ] On end/full completion: award points, reveal answers, unlock quiz
- [ ] Mark `hard_sim_completed` or `hard_sim_ended_early` in `module_progress`
- [ ] Write to `simulation_retakes` collection

**2.5 — Quiz** (`/modules/<attack_id>/quiz`)

- [ ] Show 5–10 multiple choice questions with 4 options each
- [ ] On submission: score quiz, show per-question feedback
- [ ] If score >= 70%: mark `quiz_passed: True`, award points, unlock next module
- [ ] If score < 70%: show fail state, allow retry (no limit on quiz retries)
- [ ] Trigger badge check, namecard check, certificate generation after passing

---

### 🟢 Phase 3 — Gamification System

*Points, badges, namecards, leaderboard, certificates*

**3.1 — Badge System**

- [ ] Create `badges` collection in MongoDB
- [ ] Write `check_and_award_badges()` in `database.py`
- [ ] Award module completion badges on quiz pass
- [ ] Award milestone badges on condition met (first module, all modules, perfect score, etc.)
- [ ] Display badge wall on user profile

**3.2 — Namecard System**

- [ ] Create `namecards` collection in MongoDB
- [ ] Write `check_and_award_namecards()` in `database.py`
- [ ] Award category namecards when all modules in a category are complete
- [ ] Award leaderboard namecards dynamically based on rank (update on every leaderboard refresh)
- [ ] Award ultimate namecard when all 10 modules done + max points reached
- [ ] Build Namecard Gallery page showing all earned and locked namecards
- [ ] Allow user to set active namecard from their gallery

**3.3 — Leaderboard**

- [ ] Create `leaderboard` collection in MongoDB
- [ ] Write `refresh_leaderboard()` in `database.py`
- [ ] Call `refresh_leaderboard()` after every point change
- [ ] Build leaderboard page — top 3 highlighted gold/silver/bronze
- [ ] Show user's own rank even if outside top 10
- [ ] Display rank title next to username

**3.4 — Certificate System**

- [ ] Create `certificates` collection in MongoDB
- [ ] Write `generate_certificate()` in `database.py`
- [ ] Performance Certificate: auto-generate on registration, auto-update on every point change
- [ ] Completion Certificate: generate on completing all 10 modules
- [ ] Perfect Score Certificate: generate on reaching max 1,500 pts
- [ ] Leaderboard Certificate: generate/update when user enters/updates top 10 rank
- [ ] Build PDF generation for all 4 certificate types (use `reportlab` or `weasyprint` Python library)
- [ ] Show downloadable certificate buttons on profile/dashboard

---

### 🔵 Phase 4 — Dashboard & Profile

*User-facing progress overview*

**4.1 — Student Dashboard** (`/dashboard`)

- [ ] Show total points, current level, progress bar to next level
- [ ] Show modules completed out of 10
- [ ] Show active namecard
- [ ] Show recent activity (last 3–5 module completions)
- [ ] Show earned badges (last 3 earned prominently)
- [ ] Show current leaderboard rank

**4.2 — Profile Page** (`/profile`)

- [ ] Show all earned badges in badge wall
- [ ] Show Namecard Gallery — earned full, unearned silhouette
- [ ] Show all 4 certificate types with download buttons
- [ ] Allow profile photo upload via Cloudinary
- [ ] Allow display name edit

---

### ⚫ Phase 5 — Admin Dashboard

*Backend monitoring — not a main surface-level role*

**5.1 — Admin Dashboard** (`/admin`)

- [ ] Total registered users count
- [ ] Active users (logged in last 7 days)
- [ ] Per-module completion rates chart
- [ ] Average quiz scores per module
- [ ] Most failed simulation
- [ ] Most replayed simulation

**5.2 — User Management** (`/admin/users`)

- [ ] List all users with search
- [ ] View individual user progress report
- [ ] Deactivate/reactivate accounts
- [ ] Reset user password

---

### 🏁 Phase 6 — Polish & Testing

*Before final demo*

- [ ] Mobile responsiveness check on all pages
- [ ] Test full module flow end-to-end (info → easy → hard → quiz → rewards)
- [ ] Test retake limit enforcement (max 2, no reset)
- [ ] Test module unlock chain (can't skip modules)
- [ ] Test badge and namecard award triggers
- [ ] Test certificate PDF generation and download
- [ ] Test leaderboard real-time update after point change
- [ ] Test Google Sign-in flow
- [ ] Test email verification flow
- [ ] Seed demo users for defense presentation

---

## ⚠️ Important Notes

**Build Order Matters:**
Phase 1 must be done before Phase 2. Phase 2 must be done before Phase 3. Do not start gamification before the core module flow works end-to-end.

**Simulation Rendering:**
Each attack's simulation interface (fake email, fake desktop, fake chat, fake WiFi selector) is built as a custom HTML/CSS component per attack type — not a generic template. This is the most time-consuming frontend work. Prioritize it early in Phase 2.

**Certificate PDF Generation:**
Use `weasyprint` (Python) to convert HTML certificate templates to PDF. Install via:

```
pip install weasyprint
```

Design certificates as HTML templates first, then render to PDF on download request.

**Real-time Leaderboard:**
For simplicity, "real-time" can mean the leaderboard refreshes on page load and after every point-earning action — full WebSocket implementation is not required for the project scope.

**SQL Injection Module:**
This is the only module where the user plays as the attacker. The fake vulnerable login form should only accept the specific SQL injection strings defined in your `simulation_data.py` — it should not be a real SQL query executor.