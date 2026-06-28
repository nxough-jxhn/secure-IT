# Secure-IT: A Gamified Simulation-Based Platform for Cyber Threat Awareness and Online Safety

---

# PART 1 — SYSTEM FUNCTIONALITIES

---

## 🔷 General Functionalities
- The system is a web-based platform accessible through any modern browser without requiring installation
- The system supports role-based access control separating User and Admin accounts
- The system requires registration and login to access all features and track progress
- The system is fully responsive and accessible on both desktop and mobile browsers
- The system provides real-time feedback and updates across all modules without requiring page refresh
- All user passwords are stored encrypted using bcrypt hashing
- All user sessions are managed securely using JWT-based authentication
- The system maintains individual user progress, points, badges, namecards, and quiz history persistently across sessions

---

## 👤 User Functionalities

### Account Management
- Users can register using an email address and password
- Users can log in and log out securely
- Users can view and edit their profile information (display name, profile photo)
- Users can reset their password through email verification
- Users can set and display an active namecard on their profile

### Dashboard
- Users can view their personal dashboard showing total points, current level, progress bar to next level, number of completed modules, earned badges, and active namecard
- Users can view their per-module status: Locked, In Progress, or Completed
- Users can view their quiz score history and simulation score history per module
- Users can view and download all certificates they have earned
- Users can view their Namecard Gallery showing all namecards in the system — earned ones displayed in full, unearned ones shown as locked silhouettes

### Module Navigation
- Users can browse all 10 available attack modules grouped by category
- Users can see which modules are locked, in progress, or completed
- Users must complete the Informational Page before accessing the Easy Simulation
- Users must complete the Easy Simulation before accessing the Hard Simulation
- Users must complete or end the Hard Simulation before accessing the Quiz
- Users must pass the Quiz with a minimum score of 70% to unlock the next module
- Users can replay any previously completed Easy or Hard Simulation at any time for review
- Users have a maximum of 2 retakes on the Hard Simulation per module with no refresh or reset

### Leaderboard
- Users can view the global leaderboard showing all users ranked by total points in real time
- Users can see their own current rank on the leaderboard regardless of position

---

## 🧑‍💼 Admin Functionalities

### Account Management
- Admin can log in to a separate admin dashboard
- Admin can view, search, and manage all registered user accounts
- Admin can deactivate or reactivate user accounts
- Admin can reset a user's password

### Module and Content Management
- Admin can create, edit, and delete attack modules and categories
- Admin can create, edit, and delete quiz questions per module
- Admin can set the minimum passing score per quiz
- Admin can set module unlock order and prerequisites

### Analytics and Monitoring
- Admin can view system-wide analytics including total registered users, active users, and overall platform engagement
- Admin can view per-module analytics including average quiz scores, completion rates, most failed simulation, and most replayed simulation
- Admin can view individual user progress reports showing points, level, badges, namecards, and per-module scores
- Admin can view leaderboard standings and certificate issuance logs from the admin dashboard

---

# PART 2 — MODULE FUNCTIONALITIES

---

## 📋 Module Flow

Every module follows this exact sequential flow:

```
Choose Attack Module
        ↓
Informational Page [always accessible]
        ↓
Easy Simulation [unlocks after viewing Informational Page]
        ↓
Hard Simulation [unlocks after completing Easy Simulation]
        ↓
Quiz [unlocks after completing or ending Hard Simulation]
        ↓
Module Complete — Points, Badges, and Namecards Awarded
        ↓
Next Module Unlocked [if Quiz passed with minimum 70%]
```

---

## 📦 Module Structure Per Attack

Each module contains the following sections:

### 1. Informational Page
- Displays a structured overview of the attack type: what it is, how it works, and real-world examples
- Includes key warning signs and red flags users should watch for
- Displays an embedded educational video relevant to the attack type sourced from a curated internal resource — not a YouTube embed — to ensure reliability and availability during demo and defense
- Includes visual aids such as icons, diagrams, or annotated screenshots to support understanding
- Must be viewed before the Easy Simulation unlocks

### 2. Easy Simulation
- A guided, beginner-friendly version of the simulation
- Visual indicators and highlights are shown pointing to the red flags and suspicious signs within the scenario
- The user interacts with the scenario and identifies the highlighted signs
- No points are awarded for completing the Easy Simulation
- Completing the Easy Simulation unlocks the Hard Simulation
- Can be replayed at any time after completion

### 3. Hard Simulation
- A realistic, fullscreen, interactive simulation with no indicators or highlights — the user must identify signs on their own
- The simulation places the user as the target and presents a realistic scenario interface (fake email client, fake desktop, fake chat, fake WiFi selector, fake login page, fake browser, etc.)
- The user must identify all required signs during the simulation to earn full points
- Each simulation contains 3–5 hidden signs the user must find and flag
- Simulation questions are embedded within the simulation itself — the user answers them as they interact with the scenario
- Points are awarded based on how many signs were correctly identified and how many attempts were used

**Hard Simulation — Attempt and Retake Rules:**
- Users have a maximum of 2 retakes per module — no refresh or reset ever
- **First attempt — all signs found:** Full points awarded, answers revealed, proceeds to Quiz
- **First attempt — partial signs found:** User is given a choice:
  - **End Simulation:** Partial points awarded, answers revealed, Quiz unlocks
  - **Retake:** No answers revealed, simulation resets, user tries again (retake 1 of 2)
- **Second attempt — all signs found:** Full points awarded, answers revealed, proceeds to Quiz
- **Second attempt — partial signs found:** Same choice presented (End or Retake 1 more time)
- **Third attempt (final) — regardless of result:** Points awarded based on score, answers revealed, Quiz unlocks
- If the user ends the simulation early at any point, partial points are awarded and answers are revealed

### 4. Quiz
- Unlocks only after the Hard Simulation is completed or ended
- Contains 5–10 multiple choice questions with 4 choices each
- Questions are general and scenario-based — they do not directly reference the simulation but test broader understanding and application of the attack concept
- Users must score a minimum of 70% to pass and unlock the next module
- Immediate feedback is shown after submission — correct and incorrect answers with explanations per question
- Points are awarded based on the score achieved

---

## 🗂️ Attack Categories and Modules

---

### 🎣 Category 1 — Social-Based Attacks
*Attacks that exploit human behavior, trust, and psychology*

---

#### Module 1 — Phishing: Fake Email

**Informational Page:**
- What phishing is and how fake emails are used to steal credentials
- How attackers spoof sender domains to look legitimate
- Common red flags: urgent language, mismatched sender address, suspicious links, generic greetings
- Real-world examples of phishing emails targeting students and banking users
- Visual: annotated screenshot of a real phishing email with red flags labeled

**Easy Simulation:**
- User is shown a fake email inside a simulated email client interface
- Visual indicators highlight: the spoofed sender domain, the urgent subject line, the suspicious link URL, and the generic greeting
- User clicks each highlighted indicator to acknowledge it
- Completion unlocks Hard Simulation

**Hard Simulation:**
- User is shown the same fake email with no indicators or highlights
- The email appears to come from a legitimate source (e.g. school portal, bank, government agency)
- Signs the user must find and flag (3–5):
  - Sender domain is slightly off (e.g. `school-portal.net` instead of `school.edu.ph`)
  - Urgent language pressuring immediate action (e.g. "Your account will be suspended in 24 hours")
  - Hovering over the link reveals a mismatched or suspicious URL
  - Generic greeting used instead of the user's name (e.g. "Dear User")
  - Email contains subtle grammar or formatting errors
- Consequence reveal: if user clicked the link without verifying, a popup shows credentials were submitted to an unknown server

**Quiz Covers (5–8 questions):**
- How to identify a spoofed sender domain
- What urgent language in an email typically signals
- How to safely verify a link before clicking
- What to do when you receive a suspicious email
- Why generic greetings are a red flag in official communications

---

#### Module 2 — Phishing: Fake Website

**Informational Page:**
- How attackers clone legitimate websites to steal login credentials
- What to look for in a URL bar: HTTPS, correct domain spelling, suspicious subdomains
- How fake websites are distributed (through phishing emails, fake ads, shortened links)
- Visual: side-by-side comparison of a real vs. fake login page with red flags labeled

**Easy Simulation:**
- User is shown a fake login page that looks like their school portal or a popular platform
- Visual indicators highlight: the wrong URL in the address bar, missing HTTPS padlock, slightly off logo, and a suspicious input form
- User clicks each indicator to acknowledge it
- Completion unlocks Hard Simulation

**Hard Simulation:**
- User receives a message with a link and lands on a convincing fake login page
- No indicators shown — user must examine the page carefully
- Signs the user must find and flag (3–5):
  - URL in the fake address bar is slightly misspelled (e.g. `faceb00k.com` or `g00gle.com`)
  - No HTTPS padlock or shows "Not Secure" warning
  - Logo or page layout has subtle visual differences from the real site
  - Input fields behave unusually (e.g. password field shows typed characters instead of dots)
  - Page footer contains incorrect copyright year or missing legal links
- Consequence reveal: user logged in and their credentials were silently captured and sent to an attacker's server

**Quiz Covers (5–8 questions):**
- How to verify a website's URL before entering credentials
- What HTTPS means and why its absence is a red flag
- How attackers distribute fake website links
- What to do if you accidentally entered credentials on a suspicious site
- How to distinguish a real site from a cloned one

---

#### Module 3 — Social Engineering

**Informational Page:**
- What social engineering is and how it exploits trust and human psychology
- Common tactics: pretexting, impersonation, building rapport to extract information
- What types of information seem innocent but can be weaponized
- Real-world examples: fake IT support calls, impersonating classmates or professors
- Visual: diagram showing how innocent pieces of information build a complete profile

**Easy Simulation:**
- User receives a scripted chat from a "friendly stranger"
- Visual indicators highlight each question that is extracting sensitive information
- After each highlighted question the user is shown a tooltip explaining why that question is dangerous
- Completion unlocks Hard Simulation

**Hard Simulation:**
- User receives a natural-feeling chat from a "friendly stranger" or someone posing as a classmate or school staff
- No indicators — the conversation feels genuinely casual
- The stranger asks seemingly innocent questions over the course of the chat:
  - What school do you go to?
  - What is your student ID format?
  - What is your pet's name?
  - What year were you born?
  - Who is your favorite teacher?
- Signs the user must find and flag (3–5):
  - Questions gradually escalate from general to personal
  - Stranger avoids answering questions about themselves when asked
  - Stranger steers the conversation back to personal topics repeatedly
  - Stranger uses flattery or urgency to keep the user engaged
  - Stranger asks for information that would typically be used in account recovery
- Consequence reveal: a profile card assembles showing exactly what the attacker now knows and how each answer maps to a common security question or account recovery method

**Quiz Covers (5–8 questions):**
- What information should never be shared with strangers online
- How attackers use innocent-sounding questions to build a profile
- What pretexting is and how to recognize it
- How to respond when someone online asks personal questions
- What makes social engineering different from other cyber attacks

---

### 🦠 Category 2 — Malware-Based Attacks
*Attacks that use malicious software to compromise a device or steal data*

---

#### Module 4 — Keylogger

**Informational Page:**
- What a keylogger is and how it silently records keystrokes
- How keyloggers are installed: through malicious downloads, infected USB drives, or compromised extensions
- Warning signs: unfamiliar browser extensions, slow device performance, unknown background processes
- Why public or shared devices are especially risky
- Visual: annotated fake taskbar showing a suspicious extension icon

**Easy Simulation:**
- User is shown a fake desktop with a taskbar
- Visual indicators highlight the suspicious browser extension icon in the taskbar
- User is guided to type into a fake login form and shown how keystrokes are being captured in real time by the highlighted extension
- Completion unlocks Hard Simulation

**Hard Simulation:**
- User is shown a fake desktop with a taskbar containing a subtle suspicious browser extension icon among several normal-looking ones
- No indicators — user must examine the taskbar and environment carefully before typing
- User is prompted to log in to a fake school portal
- Signs the user must find and flag (3–5):
  - An unrecognized extension icon is present in the taskbar
  - The device performance indicator shows unusual background activity
  - The extension has a generic or misspelled name when hovered
  - A subtle network activity indicator shows data being sent while typing
  - The login page loads slightly slower than expected due to the fake keylogger process
- After the user types their password and submits: a system alert reveals their exact keystrokes were captured
- Consequence reveal: the unrecognized extension was the keylogger — it captured everything typed on the device

**Quiz Covers (5–8 questions):**
- What a keylogger is and how it works
- What signs to check before typing passwords on any device
- Why shared or public devices are high-risk for keylogging
- How to manage and audit browser extensions
- What to do if you suspect a keylogger is installed

---

#### Module 5 — Ransomware

**Informational Page:**
- What ransomware is and how it encrypts files and demands payment
- How ransomware is delivered: malicious downloads, email attachments, infected links
- Why paying the ransom is not recommended
- What to do if ransomware is triggered: disconnect, report, do not pay
- Visual: screenshot of a realistic ransomware lockscreen with explanation of each element

**Easy Simulation:**
- User is shown a fake desktop with a suspicious downloadable file
- Visual indicators highlight the untrusted file source, suspicious file name, and the absence of a verified publisher warning
- User is guided through what happens when an untrusted file is executed
- Completion unlocks Hard Simulation

**Hard Simulation:**
- User is on a fake desktop environment browsing a fake file manager or download page
- A tempting file is available for download (e.g. "Free_Adobe_Crack.exe" or "Exam_Reviewer_2026.zip")
- Signs the user must find and flag (3–5):
  - File source is unverified or from an untrusted website
  - File has an executable extension disguised as a document (.exe, .bat)
  - No digital signature or publisher verification shown
  - Download site has excessive ads and redirect prompts
  - File size is suspiciously small for what it claims to be
- If user downloads and opens the file: files on the fake desktop begin visually greying out one by one, then a fullscreen lockscreen appears: *"Your files have been encrypted. Send payment to recover them."*
- Consequence reveal: the downloaded file was ransomware — the user's fake files are now encrypted

**Quiz Covers (5–8 questions):**
- What ransomware is and how it spreads
- How to identify untrusted or suspicious files before downloading
- Why you should never pay a ransomware demand
- What to do immediately after a ransomware attack
- How to protect files against ransomware (backups, verified sources)

---

#### Module 6 — Spyware

**Informational Page:**
- What spyware is and how it silently monitors device activity
- How spyware is installed: bundled with free software, fake app updates, malicious links
- What spyware collects: browsing history, screenshots, location, personal files
- Warning signs: slow device, unusual battery drain, unexpected data usage, unfamiliar background processes
- Visual: diagram showing spyware silently sending data to an attacker's server

**Easy Simulation:**
- User is shown a fake desktop
- Visual indicators highlight background processes running silently: a fake spyware process in the task manager, unusual network activity, and a data usage spike indicator
- User is guided through identifying each sign
- Completion unlocks Hard Simulation

**Hard Simulation:**
- User is on a fake desktop environment going through normal activity (opening files, browsing)
- Signs the user must find and flag (3–5):
  - An unknown process is running in the fake task manager consuming resources
  - Network activity indicator shows data being sent even when the user is not actively browsing
  - A recently installed unknown application appears in the fake installed apps list
  - Device performance slows noticeably during normal use
  - Screenshots of the fake desktop are being silently saved to an unknown folder
- Consequence reveal: a spyware program installed alongside a free download has been silently collecting browsing history and screenshots and sending them to an external server

**Quiz Covers (5–8 questions):**
- What spyware is and how it differs from other malware
- How spyware is typically installed without the user's knowledge
- What warning signs indicate spyware may be present on a device
- How to check running processes for suspicious activity
- What to do if spyware is suspected or confirmed

---

#### Module 7 — Adware / Malvertising

**Informational Page:**
- What adware is and how malvertising works
- How malicious ads redirect users to harmful sites or trigger automatic downloads
- Why free streaming and download sites are high-risk environments
- Warning signs: excessive popups, unexpected redirects, browser homepage changes, slow browsing
- Visual: annotated screenshot of a malvertising-heavy webpage with red flags labeled

**Easy Simulation:**
- User is shown a fake webpage with excessive ads and popups
- Visual indicators highlight the fake prize popup, the suspicious redirect banner, the auto-download prompt, and the browser homepage change notification
- User clicks each indicator to acknowledge it
- Completion unlocks Hard Simulation

**Hard Simulation:**
- User is browsing a fake free streaming or download website
- No indicators — the page looks like a normal (if cluttered) website
- Signs the user must find and flag (3–5):
  - A popup claims the user won a prize and asks them to click to claim it
  - An ad banner mimics a system alert (e.g. "Your device has a virus — click to clean")
  - Clicking anywhere on the page triggers an unexpected redirect to another site
  - A download starts automatically without the user initiating it
  - The browser address bar changes to a different URL after a few seconds
- If user clicks the fake prize popup or the fake system alert: a fake malware install sequence triggers
- Consequence reveal: the ad was malvertising — clicking it silently installed adware that will now bombard the device with more ads and may have installed additional malware

**Quiz Covers (5–8 questions):**
- What adware and malvertising are and how they differ
- Why free streaming and download sites are high-risk for malvertising
- How to recognize a fake system alert disguised as an ad
- What to do when a download starts automatically without your action
- How ad blockers and safe browsing practices reduce malvertising risk

---

### 🌐 Category 3 — Network-Based Attacks
*Attacks that exploit network connections and traffic*

---

#### Module 8 — Man-in-the-Middle (MITM)

**Informational Page:**
- What a MITM attack is and how attackers intercept and alter network traffic
- How MITM happens: through unsecured public WiFi, ARP spoofing, SSL stripping
- Why HTTPS matters and what it protects against
- Warning signs: unexpected session timeouts, altered transaction details, certificate warnings
- Visual: diagram showing attacker sitting between user and server intercepting communications

**Easy Simulation:**
- User is shown a fake network connection screen
- Visual indicators highlight the missing HTTPS padlock, the public WiFi warning, and the duplicate network name
- User is guided through how each ignored warning enabled the MITM attack
- Completion unlocks Hard Simulation

**Hard Simulation:**
- User is already connected to a public WiFi (they selected it from a list earlier)
- User sends a message or transaction to their "bank" through a fake banking interface
- Signs the user must find and flag (3–5):
  - The banking site URL shows HTTP not HTTPS
  - The WiFi network connected to has no password protection
  - A subtle certificate warning appeared briefly during page load and was dismissible
  - The transaction confirmation shows a slightly different amount than what was entered
  - Session timeout occurs unexpectedly mid-transaction
- Consequence reveal: the transaction details were silently altered by the attacker sitting between the user and the bank — the amount sent was different from what the user intended

**Quiz Covers (5–8 questions):**
- What a MITM attack is and how it works
- Why HTTPS is critical for protecting data in transit
- What risks come with using unsecured public WiFi
- How to identify signs of a MITM attack during a transaction
- What to do if you suspect your connection has been intercepted

---

#### Module 9 — Evil Twin / Rogue WiFi

**Informational Page:**
- What an Evil Twin attack is and how rogue WiFi networks work
- How attackers set up networks with identical names to legitimate ones in public places
- Real-world context: free WiFi in malls, cafes, airports, and public transport hubs in the Philippines
- Warning signs: two networks with identical or near-identical names, unusually strong signal from an unknown network, no password on a network that should have one
- Visual: side-by-side comparison of a legitimate vs. rogue WiFi network in a device's WiFi selector

**Easy Simulation:**
- User is shown a fake WiFi selector screen with two identical-looking networks
- Visual indicators highlight the differences between the legitimate and rogue network: signal strength, security type, and network name subtle differences
- User is guided to select the correct network
- Completion unlocks Hard Simulation

**Hard Simulation:**
- User is in a simulated public place scenario (e.g. SM Mall, coffee shop, airport)
- User opens a fake WiFi selector showing multiple available networks including two that look nearly identical
- Signs the user must find and flag (3–5):
  - Two networks share the same name (e.g. both named `SM_FreeWifi`)
  - One network has an unusually stronger signal than the other despite same location
  - One network shows no security lock icon despite being in a commercial establishment
  - Network details show different MAC addresses for the two identical-named networks
  - One network does not require any agreement or registration page upon connection (unlike the legitimate one)
- If user connects to the rogue network: their fake browsing session is shown being silently monitored
- Consequence reveal: the network they chose was a rogue access point set up by an attacker — all their browsing data was intercepted

**Quiz Covers (5–8 questions):**
- What an Evil Twin attack is and how it is set up
- How to identify a rogue WiFi network among legitimate ones
- Why free public WiFi without passwords is high-risk
- What to check before connecting to any public network
- What a VPN does and how it helps on public WiFi

---

### 💉 Category 4 — Injection-Based Attacks
*Attacks that exploit system and code vulnerabilities through malicious input*

---

#### Module 10 — SQL Injection

**Informational Page:**
- What SQL injection is and how it exploits vulnerable input fields
- How attackers use SQL commands to bypass login forms or extract database contents
- Why this matters to developers and end users alike
- Real-world examples: login bypass, data extraction, database manipulation
- Visual: diagram showing how a normal login query differs from an injected one

**Easy Simulation:**
- User plays as the attacker for the first time
- A fake vulnerable login form is shown with visual indicators highlighting where the SQL injection input goes and why the form is vulnerable
- User is guided through entering a basic SQL injection string (e.g. `' OR '1'='1`) with tooltips explaining what each part of the input does
- The form is bypassed and the user sees the fake admin dashboard they gained access to
- Completion unlocks Hard Simulation

**Hard Simulation:**
- User is presented with a fake vulnerable login form with no indicators or guidance
- User must figure out the correct SQL injection input on their own to bypass the login
- Signs and observations the user must make (3–5):
  - The login form has no input sanitization visible (no CAPTCHA, no input character limits)
  - Error messages reveal database information when wrong input is entered
  - The URL structure hints at direct database query usage
  - The form accepts special characters without filtering
  - Entering a single quote `'` causes an unusual error message revealing SQL syntax
- User attempts SQL injection inputs to bypass the form
- Consequence reveal: the form was successfully bypassed — this demonstrates how vulnerable unsanitized input fields are and why developers must always validate and sanitize user input

**Quiz Covers (5–8 questions):**
- What SQL injection is and how it works
- What makes a login form vulnerable to SQL injection
- How input sanitization and parameterized queries prevent SQL injection
- What an attacker can do after a successful SQL injection
- How to recognize signs of a SQL-vulnerable form as a user or developer

---

# PART 3 — GAMIFICATION SYSTEM

---

## 🎯 Points System

### Points Per Activity

| Activity | Points |
|---|---|
| Completing Easy Simulation | 0 pts (no points — tutorial only) |
| Hard Simulation — all signs found on 1st try | 50 pts |
| Hard Simulation — all signs found on 2nd try | 35 pts |
| Hard Simulation — all signs found on 3rd try | 20 pts |
| Hard Simulation — ended early / partial score | 10 pts |
| Simulation Questions — per correct answer (3–5 questions) | 5 pts each |
| Quiz — 70%–89% score | 30 pts |
| Quiz — 90%–99% score | 45 pts |
| Quiz — 100% score | 60 pts |
| First time completing a module (bonus) | +10 pts |
| Completing all 10 modules (bonus) | +50 pts |

### Maximum Points Per Module

| Activity | Max Points |
|---|---|
| Hard Simulation (1st try perfect) | 50 pts |
| Simulation Questions (5 x 5 pts) | 25 pts |
| Quiz (100% score) | 60 pts |
| First Module Completion Bonus | 10 pts |
| **Total per module** | **145 pts** |

**Maximum Possible Points (all 10 modules + completion bonus):**
> (145 pts × 10 modules) + 50 bonus = **1,500 pts**

---

## 🎮 Level System

| Level | Points Required | Title |
|---|---|---|
| Level 1 | 0 – 299 pts | Rookie |
| Level 2 | 300 – 599 pts | Aware |
| Level 3 | 600 – 999 pts | Defender |
| Level 4 | 1,000 – 1,299 pts | Guardian |
| Level 5 | 1,300 – 1,500 pts | Cyber Shield |

- Current level and title are displayed prominently on the user's profile and dashboard
- Leveling up triggers a visual celebration animation on screen
- Progress bar to the next level is always visible on the dashboard

---

## 🔓 Module Unlock System

- All modules are locked by default except Module 1
- Module 1 — Phishing: Fake Email is accessible immediately upon registration
- Each module unlocks sequentially after passing the previous module's Quiz with a minimum score of 70%
- Within each module the unlock chain is: Informational Page → Easy Simulation → Hard Simulation → Quiz
- The Hard Simulation has a maximum of 2 retakes per module with no refresh or reset ever
- Completed modules and Easy Simulations remain accessible for replay at any time
- If a user ends the Hard Simulation early, partial points are awarded and the Quiz still unlocks

---

## 🏅 Badge System

### Module Completion Badges
*Awarded upon fully completing a module (Easy Sim + Hard Sim + Quiz passed)*

| Badge Name | Module |
|---|---|
| Phishing Spotter | Phishing — Fake Email |
| Web Defender | Phishing — Fake Website |
| Mind Shield | Social Engineering |
| Key Defender | Keylogger |
| Ransomware Survivor | Ransomware |
| Spy Catcher | Spyware |
| Ad Blocker | Adware / Malvertising |
| MITM Detector | Man-in-the-Middle |
| Signal Guardian | Evil Twin / Rogue WiFi |
| Code Breaker | SQL Injection |

### Milestone Badges
*Awarded upon reaching broader achievements — kept minimal and meaningful*

| Badge Name | Condition |
|---|---|
| First Step | Complete your first module |
| Full Shield | Complete all 10 modules |
| Perfect Strike | Get 100% on any quiz |
| Flawless | Get 100% on all 10 quizzes |
| Persistent | Use both retakes and still finish a Hard Simulation |
| Unstoppable | Complete all 10 Hard Simulations on the first try |

---

## 🏆 Leaderboard and Ranking System

- Global leaderboard ranks all users by total accumulated points in real time
- Leaderboard displays: Rank Number, Rank Title, Username, Level Title, Total Points, Number of Badges
- Top 3 users are visually highlighted with gold, silver, and bronze distinction
- Users can see their own current rank regardless of position

### Rank Titles

| Position | Rank Title |
|---|---|
| 🥇 1st Place | Top Defender |
| 🥈 2nd Place | Elite Guard |
| 🥉 3rd Place | Cyber Ace |
| 4th – 10th Place | Honor Shield |
| 11th and beyond | Active Learner |

---

## 🃏 Namecard System

Namecards are collectible visual profile cards inspired by collectible card systems. Users can set one active namecard to display on their profile and the leaderboard. All namecards in the system are visible in the user's Namecard Gallery — earned ones displayed in full, unearned ones shown as locked silhouettes.

### Type 1 — Category Namecards
*Awarded after completing ALL modules under a category*

| Namecard | Condition | Visual Theme |
|---|---|---|
| Social Sentinel | Complete all Social-Based modules | Dark blue, chat and message motifs |
| Malware Hunter | Complete all Malware-Based modules | Red, virus and bug motifs |
| Network Warden | Complete all Network-Based modules | Teal, network and signal motifs |
| Code Guardian | Complete the SQL Injection module | Green, code and terminal motifs |

### Type 2 — Leaderboard Namecards
*Awarded to current top 3 on the leaderboard — updates dynamically with rank changes*

| Namecard | Condition | Visual Theme |
|---|---|---|
| ⚡ Cyber Throne | 1st place on leaderboard | Gold, animated border, crown motif |
| 🛡️ Iron Vanguard | 2nd place on leaderboard | Silver, shield motif |
| 🔰 Bronze Bastion | 3rd place on leaderboard | Bronze, fortress motif |

### Type 3 — Ultimate Namecard
*The rarest namecard in the system — awarded only to users who achieve everything*

| Namecard | Condition | Visual Theme |
|---|---|---|
| 👑 Secure-IT Elite | Complete all 10 modules AND achieve maximum points (1,500 pts) | Gold animated, crown and shield motif, exclusive design distinct from all others |

---

## 📜 Certificate System

All certificates are downloadable as PDF from the user's dashboard.

### Certificate 1 — Performance Certificate
- Awarded to all users at any stage
- Updates dynamically every time the user's points change
- Displays: username, current total points, current level title, number of modules completed, and date generated
- Can be downloaded and regenerated at any time

### Certificate 2 — Completion Certificate
- Awarded when the user completes all 10 modules (Easy Sim + Hard Sim + Quiz passed for all)
- One-time permanent certificate — does not update after issuance
- Displays: username, completion date, all 10 module badges earned, and a formal completion statement
- Official-looking layout suitable for sharing or portfolio use

### Certificate 3 — Perfect Score Certificate
- Awarded only when the user achieves the maximum possible points in the system (1,500 pts)
- Visually distinct from all other certificates — gold design, premium layout
- Displays: username, date achieved, total points, and a statement confirming maximum achievement
- Rare — very few users will ever earn this certificate

### Certificate 4 — Leaderboard Certificate
- Awarded to users currently ranked in the Top 10 of the global leaderboard
- Updates dynamically — if the user drops out of the top 10 the certificate reflects their last top 10 standing
- Top 3 receive a visually distinct version with gold, silver, or bronze design based on their rank
- Displays: username, current rank, rank title, total points, and date of ranking

