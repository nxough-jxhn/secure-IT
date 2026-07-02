# Secure-IT — System Flowchart Guide

One complete flowchart that covers the entire system from start to finish.

---

## What a System Flowchart Is

A system flowchart shows **every major action a user or admin can take** in the system,
from the moment they open the site to the moment they finish their last task.
It is one connected diagram — not separate diagrams per feature.

---

## How to Structure It

### The four main swimlane columns (left to right)

A swimlane layout keeps it clean when multiple actors are involved.

| Swimlane | Who / What |
|---|---|
| **User** | Everything the student does in the browser |
| **System (Flask)** | Every route, check, and server-side process |
| **Database (MongoDB)** | Every read or write to the database |
| **External Services** | Firebase, Cloudinary, Gmail SMTP |

Draw horizontal dashed lines between the lanes. Every arrow that crosses a lane boundary represents a request or response.

---

## The Full Flow — What to Put, In Order

### SECTION 1 — Entry Point

```
START
  |
  v
User opens browser → visits /  (Landing Page)
  |
  v
[Is user logged in?]
  YES → skip to Dashboard
  NO  → show landing page with Get Started / Login buttons
```

---

### SECTION 2 — Registration

```
User clicks "Get Started"
  |
  v
Registration form shown (/login page, register panel)
Fields: Name, Gmail address, Password, Confirm password, Year level, Profile photo (optional)
  |
  v
[System] Validates all fields
  |
  [Gmail address? Password match? Fields not empty?]
  NO  → Return error message → back to form
  YES → continue
  |
  v
[External: Cloudinary] Upload profile photo (if provided) → returns image URL
  |
  v
[Database] create_pending_user() → store user as email_verified = False
  |
  v
[External: Gmail SMTP] send_verification_email() → sends link with token
  |
  v
User receives email → clicks /verify-email/<token>
  |
  v
[System] Checks token: exists in DB + not expired?
  NO  → Show error page (token invalid or expired)
  YES → update email_verified = True in MongoDB → redirect to /login
```

---

### SECTION 3 — Login

```
User at /login
  |
  v
[Choose login method]
  |
  |── Email + Password
  |     |
  |     v
  |   [System] authenticate_user()
  |   Checks: password hash match + email_verified = True
  |     |
  |   [Valid?]
  |   NO  → Show "Invalid email or password" error
  |   YES → Create Flask session (logged_in, user_email, role, display_name)
  |
  |── Google Sign-In button
        |
        v
      [External: Firebase JS SDK] → get ID token from Google
        |
        v
      POST /auth/firebase with token
        |
        v
      [External: Firebase Admin SDK] verify_firebase_id_token()
        |
      [Token valid?]
      NO  → Return 401 error
      YES → continue
        |
        v
      [Database] upsert_firebase_user() → create or update user in MongoDB
        |
        v
      Create Flask session
```

---

### SECTION 4 — Role Split After Login

```
After session created:
  |
  v
[System] Check session role
  |
  ADMIN → redirect /admin
  STUDENT → redirect /dashboard
```

---

### SECTION 5 — Student Path

#### 5A. Dashboard

```
/dashboard
Shows: Module progress cards, Recommended challenges,
       Recent activity, Profile KPIs, Weekly streak,
       Badges / Certificates / Namecards panel
  |
  v
User clicks a module card → /simulations/<attack_id>
  OR
User clicks "Cyber Range" → /simulations
```

#### 5B. Cyber Range

```
/simulations
Shows: 4 category pillars (Three.js), right-side attack carousel
  |
  v
User clicks a pillar → modal opens showing category attacks
  |
  v
User clicks an attack → /simulations/<attack_id>
```

#### 5C. Informational Page

```
/simulations/<attack_id>   (Informational Page)
Shows:
  - Spotlight carousel (About / Origin / Real World) with images
  - Educational video placeholder
  - Bottom carousel: How it Works / Warning Signs / Prevention / Real World
  - Two buttons: Easy Sim | Hard Sim (Hard Sim locked until Easy complete)
  |
  [System] update module_progress: info_viewed = True in MongoDB
  |
  v
User clicks "Easy Sim" → /simulations/<attack_id>/easy
```

#### 5D. Easy Simulation

```
/simulations/<attack_id>/easy
[System] Check: info_viewed = True? NO → redirect back to info page
  |
Simulation shown (type depends on attack):
  - Phishing Fake Email → Gmail inbox interface
  - SQL Injection → Login form interface
  - Social Engineering → Phone call interface
  |
User interacts: clicks red flag indicators, reviews explanations, gives verdict
  |
  v
User clicks "Complete simulation"
  |
  v
POST /simulations/<attack_id>/easy/complete
  |
  v
[Database] easy_complete = True saved to module_progress
  |
  v
Redirect back to /simulations/<attack_id>
Hard Sim button is now unlocked
```

#### 5E. Hard Simulation

```
User clicks "Hard Sim" → /simulations/<attack_id>/start
  |
  v
[System] Check: easy_complete = True? NO → redirect back to info page
  YES → set session: sim_started = True, record start timestamp
  |
  v
Redirect to /simulations/<attack_id>/play
  |
  v
Hard Simulation (no hints, fully unguided)
  - Phishing Hard: Gmail interface + flag mode + URL analyzer + event feed
  - SQL Injection Hard: login lab + request inspector + flag signs
  - Social Engineering Hard: phone call + flag mode + caller lookup + event feed
  |
User: flags suspicious signs, uses tools, submits incident report
Final decision modal → user picks response option
  |
  v
POST /simulations/<attack_id>/complete
with: score, flags_found, mistakes, good_decisions, time_spent_seconds
  |
  v
[System] Calculate score, points_earned
  |
  v
[Database]
  - Insert record to simulation_results collection
  - Update user: points += points_earned, level recalculated
  - Save flags, mistakes to module_progress
  |
  v
Redirect to /simulations/<attack_id>/results
```

#### 5F. Results Page

```
/simulations/<attack_id>/results
Shows:
  - Score % with SVG ring
  - Points earned
  - Correct actions list
  - Errors list
  - Skills developed tags
  - Flags found tags
  - Profile sidebar: rank change, level progress, points delta
  |
  v
User clicks "Continue to Quiz"
```

#### 5G. Quiz

```
/simulations/<attack_id>/quiz
Shows: 5 scenario-based questions, A/B/C/D options
Live counter: X correct / Y incorrect
Progress bar fills as questions answered
  |
  v
User answers all 5 questions
  |
  v
POST /simulations/<attack_id>/quiz/submit
  |
  v
[System] Calculate quiz_score (% correct), quiz_points = score // 3
  |
  v
[Database] record_simulation_completion()
  - Save quiz_score, quiz_points
  - If quiz_score >= 70% → module_complete = True
  |
  v
Quiz summary shown: score ring, per-question feedback
  |
  v
[quiz_score >= 70%?]
  YES → module_complete = True ✓ → Return to /simulations (Cyber Range)
  NO  → Module incomplete, user can retake hard sim (up to 2 retakes allowed)
```

#### 5H. Profile Page

```
/profile
User can:
  - Edit display name, year level
  - Upload or camera-capture profile photo → Cloudinary
  - View leaderboard ranking
  - Browse earned badges / namecards / titles
  - View community posts placeholder
  |
  v
POST /profile → [Database] update_user_by_email() → session refreshed
```

---

### SECTION 6 — Admin Path

```
/admin  (Admin Dashboard — Overview)
Shows:
  - 4 KPI cards: Total users, Active users 7d, Simulations done, Awareness score
  - Bar chart: avg simulation score per attack module
  - Donut chart: Awareness index breakdown
  - Tables: Most attempted modules, Most failed modules
  - Recent activity feed with user + scores + mistakes
  |
  v
/admin/users  (User Monitor)
Shows:
  - Left: user namecard grid (filterable: All / Active / Completed / No Activity)
  - Right: selected user detail panel (namecard hero, stats, attempt history)
  |
  v
Admin can review each user's:
  - Level, points, completed missions
  - Latest simulation score
  - Full attempt history with mistakes
```

---

### SECTION 7 — Logout

```
User submits logout form → POST /logout
  |
  v
[System] Clear Flask session (logged_in, user_email, role, etc.)
  |
  v
Redirect to / (Landing Page)
  |
  v
END
```

---

## Shape Reference (Standard Flowchart Symbols)

| Shape | Meaning | Use for |
|---|---|---|
| Oval | Start / End | BEGIN and END of the chart |
| Rectangle | Process | Every action, page load, system operation |
| Diamond | Decision | YES/NO questions (logged in? valid? score >= 70%?) |
| Parallelogram | Input / Output | Form submission, data display to user |
| Cylinder | Database | MongoDB read or write operations |
| Cloud | External Service | Firebase, Cloudinary, Gmail SMTP |
| Rounded rectangle | Swimlane label | Column headers |

---

## Arrow Labels to Always Include

- Every diamond branch: **YES** or **NO**
- Every redirect: **"Redirect →"**
- Every POST: **"POST /route"**
- Every database action: **"Save to DB"** or **"Read from DB"**
- Every external call: the service name (e.g. **"Firebase verify"**)

---

## Layout Recommendations

- **Direction**: Top to bottom (portrait orientation — A3 or larger paper / export)
- **Happy path**: straight vertical column down the center
- **Error paths**: branch left (dead ends with an error state terminal)
- **Admin path**: branch right at the "role check" diamond
- **External services**: on the far right lane
- **Database**: second from right lane

### Column order (left → right):

```
[User / Browser] | [Flask System] | [MongoDB] | [External Services]
```

---

## AI Prompt — Ready to Paste

Paste this into ChatGPT, Claude, or any AI to generate a Mermaid.js version of the flowchart:

```
Create a single complete system flowchart for a web app called Secure-IT
— a gamified cybersecurity training platform for students.

The flowchart must cover the ENTIRE system end-to-end in one diagram,
organized in 4 swimlane columns: User | Flask System | MongoDB | External Services.

Include every section in this order:

SECTION 1 — Entry
User opens the site (/) → check if logged in → yes: go to dashboard / no: show landing page

SECTION 2 — Registration
User fills registration form (name, Gmail, password, year level, optional photo)
→ validate fields → upload photo to Cloudinary → create user in MongoDB (unverified)
→ send verification email via Gmail SMTP with token
→ user clicks /verify-email/<token> → check token valid and not expired
→ mark email_verified = True → redirect to login

SECTION 3 — Login
Two paths:
  Path A: Email + password → authenticate_user() → check valid + verified → create Flask session
  Path B: Google button → Firebase JS SDK gets token → POST /auth/firebase
       → Firebase Admin SDK verifies token → upsert_firebase_user() in MongoDB → create Flask session

SECTION 4 — Role check after login
  Admin → /admin dashboard
  Student → /dashboard

SECTION 5 — Student learning path
  5A: /dashboard — module progress, recommended challenges, KPIs, badges
  5B: /simulations (Cyber Range) — 4 category pillars, attack carousel → click module
  5C: /simulations/<id> (Informational Page) — spotlights, carousel tabs, Easy/Hard buttons
      → system saves info_viewed = True in MongoDB
  5D: /simulations/<id>/easy (Easy Sim) — guided simulation with hints
      Types: Gmail interface (phishing), login form (SQL injection), phone call (social engineering)
      → user flags red flags, gives verdict
      → POST /easy/complete → easy_complete = True in MongoDB
  5E: /simulations/<id>/play (Hard Sim) — unguided, no hints
      → user flags signs, uses analysis tools, submits incident report decision modal
      → POST /complete with score + flags + mistakes
      → save to simulation_results in MongoDB, update user points and level
  5F: /simulations/<id>/results — score, correct actions, errors, profile delta
  5G: /simulations/<id>/quiz — 5 scenario questions A/B/C/D
      → POST /quiz/submit → calculate quiz_score
      → quiz_score >= 70%? YES: module_complete = True / NO: can retake hard sim
  5H: /profile — edit name/photo, view leaderboard, badges, namecards, community posts

SECTION 6 — Admin path
  /admin — KPI cards, bar chart (sim scores per module), donut (awareness index), recent activity table
  /admin/users — user namecard grid + selected user detail panel with attempt history

SECTION 7 — Logout
  POST /logout → clear Flask session → redirect to /

Style: use standard flowchart shapes (oval=start/end, rectangle=process, diamond=decision,
cylinder=database, cloud=external service). Label all YES/NO branches. Label all arrows.
Make the happy path go straight down the center. Error paths branch left. Admin path branches right.
```

---

## Tools to Draw It

| Tool | Why use it | Link |
|---|---|---|
| **draw.io** | Free, full control, swimlanes built in, exports PNG/PDF | app.diagrams.net |
| **Lucidchart** | Drag and drop, easy swimlanes | lucidchart.com |
| **Mermaid Live** | Paste the AI output directly, see it rendered instantly | mermaid.live |
| **Figma FigJam** | If you prefer a visual canvas | figma.com |

The easiest workflow:
1. Paste the AI prompt above into ChatGPT
2. Ask it to output **Mermaid.js flowchart code**
3. Paste the code into **mermaid.live** to preview
4. Export as SVG or PNG for your document
