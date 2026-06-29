# Secure-IT — Attack Module Dev Guide

This guide covers everything you need to build a full attack module.
Each module has 4 pages: **Informational → Easy Sim → Hard Sim → Quiz**.
The Quiz and Results pages are already built and shared — you don't touch them.

---

## Your Assignments

| Attack | ID to use in code | Assigned to |
|---|---|---|
| Phishing: Fake Website | `phishing_fake_website` | RICHARD |
| Keylogger | `keylogger` | RICHARD |
| Ransomware | `ransomware` | RICHARD |
| Spyware | `spyware` | RICHARD |
| Social Engineering | `social_engineering` | NEO |
| Man-in-the-Middle (MITM) | `mitm` | NEO |
| Adware / Malvertising | `adware_malvertising` | EVAN |
| Evil Twin / Rogue WiFi | `evil_twin` | EVAN |

> Already done by NEO: `phishing_fake_email`, `sql_injection`
> Use those as reference — copy the patterns, replace the content.

---

## File Overview

### Files you CREATE (per attack)

```
frontend/templates/simulations/
    <attack>_easy.html              Easy sim page
    <attack>_hard.html              Hard sim page

frontend/static/css/
    <attack>-easy.css               Easy sim styles
    <attack>-hard.css               Hard sim styles

frontend/static/js/
    <attack>-easy.js                Easy sim logic
    <attack>-hard.js                Hard sim logic

frontend/static/img/modules/<attack-folder>/
    image1_<attack>.jpg             Spotlight image — About tab
    image2_<attack>.png             Spotlight image — Origin tab
    image3_<attack>.jpg             Spotlight image — Real World tab
    video-poster.svg                Thumbnail for the video player
```

**Total per attack: 6 code files + 4 image files**

---

### Files you EDIT (shared — one section added per attack)

```
backend/simulation_data.py          Your attack's full data block
backend/simulation_missions.py      Your attack's workspace/hard sim config
backend/secure_it/routes/           Add your attack to EASY_SIMULATION_PAGES
    simulations.py
```

---

### Files you NEVER touch (already done, shared by all attacks)

```
frontend/templates/modules/attack_info.html     Informational page template
frontend/templates/simulation_quiz.html         Quiz page template
frontend/templates/simulation_results.html      Results page template
frontend/static/css/module-info.css
frontend/static/css/quiz.css
frontend/static/css/results.css
backend/secure_it/__init__.py
backend/database.py
```

---

## Step-by-Step

---

### Step 1 — Add your attack data in `simulation_data.py`

Find the `ATTACKS` dict. Your attack block is already there as a placeholder.
Replace it with full content following this structure:

```python
"your_attack_id": {
    "id": "your_attack_id",
    "name": "Attack Display Name",
    "icon": "🔒",                      # one emoji
    "image": "img/modules/your-folder/module_yourattack.jpg",
    "difficulty": "Beginner",          # Beginner / Intermediate / Advanced
    "short_description": "One sentence shown on cards.",
    "category": "malware_based",       # see categories below
    "category_label": "Malware-Based Attacks",

    "overview": {
        "explanation": "What this attack is in plain English.",
        "why_used": "Why attackers use this method.",
        "how_encountered": "Where/how a user typically encounters it.",
        "how_it_happens": [
            "Step 1 — attacker does X.",
            "Step 2 — victim does Y.",
            "Step 3 — attacker gains Z.",
        ],
        "warning_signs": [
            "Warning sign 1.",
            "Warning sign 2.",
        ],
        "prevention_tips": [
            "Prevention tip 1.",
            "Prevention tip 2.",
        ],
    },

    "easy_simulation": YOUR_ATTACK_EASY,   # defined separately, see Step 1b
    "hard_simulation": YOUR_ATTACK_HARD,   # defined separately, see Step 1b

    "quiz": YOUR_ATTACK_QUIZ,              # defined separately, see Step 1c

    "info_page": {
        "media": {
            "folder": "your-folder",           # matches img/modules/<your-folder>/
            "spotlight": [
                "image1_yourattack.jpg",        # About tab image
                "image2_yourattack.png",        # Origin tab image
                "image3_yourattack.jpg",        # Real World tab image
            ],
            "video_poster": "video-poster.svg",
        },
        "spotlight": [
            {
                "key": "about",
                "heading": "About",
                "text": "Paragraph explaining what this attack is.",
            },
            {
                "key": "origin",
                "heading": "Origin",
                "text": "Paragraph explaining how/why it developed.",
            },
            {
                "key": "real_world",
                "heading": "Example in Real World",
                "text": "A real-world scenario where this attack occurred.",
            },
        ],
        "real_world_examples": [
            "Example 1",
            "Example 2",
            "Example 3",
        ],
    },
},
```

**Category values:**

| Label | Value to use |
|---|---|
| Social-Based Attacks | `social_based` |
| Malware-Based Attacks | `malware_based` |
| Network-Based Attacks | `network_based` |
| Injection-Based Attacks | `injection_based` |

---

#### Step 1b — Define the simulation steps

Add these before the `ATTACKS` dict (look at `PHISHING_EMAIL_STEPS` as a reference):

```python
YOUR_ATTACK_STEPS = [
    {
        "title": "Scenario Title",
        "narrative": "What the user sees happening in the scenario.",
        "interface_type": "email",   # email / website / file / terminal / phone / etc.
        "interface": {
            # fields depend on interface_type — copy from phishing or sql as reference
        },
        "choices": [
            _choice(
                "choice_id",
                "Button label the user sees",
                "What happens after they pick this",
                "Educational explanation shown in feedback",
                0,          # score: 0 = wrong, 100 = best answer
            ),
            _choice(
                "best_choice_id",
                "Correct button label",
                "What happens after correct choice",
                "Educational explanation",
                100,
                is_best=True,
            ),
        ],
    },
]

YOUR_ATTACK_EASY, YOUR_ATTACK_HARD = _simulation_block(
    YOUR_ATTACK_STEPS,
    indicators=[
        # Easy sim: guided hints shown to the user
        {
            "element": "element_id",
            "title": "What this indicator is",
            "description": "Explanation paragraph.",
            "wrong_label": "What the bad version looks like",
            "wrong": "The actual bad example text",
            "correct_label": "What the safe version looks like",
            "correct": "The actual safe example text",
            "tip": "Actionable tip for the user.",
        },
    ],
    signs=[
        # Hard sim: flags the user must find themselves (no hints)
        {"id": "sign_id_1", "label": "Sign label shown in the UI"},
        {"id": "sign_id_2", "label": "Another sign label"},
        {"id": "sign_id_3", "label": "Another sign label"},
        {"id": "sign_id_4", "label": "Another sign label"},
        {"id": "sign_id_5", "label": "Another sign label"},
    ],
)
```

---

#### Step 1c — Write the quiz

Add this before the `ATTACKS` dict too:

```python
YOUR_ATTACK_QUIZ = [
    {
        "question": "Scenario-based question — put the user in a situation.",
        "options": [
            "Option A",
            "Option B",   # ← index 1 = correct in this example
            "Option C",
            "Option D",
        ],
        "correct": 1,   # 0-indexed — which option is right
        "explanation": "Why that answer is correct. Teach the concept.",
    },
    # Write 5 questions total
]
```

**Quiz rules:**
- 5 questions minimum
- Questions must be scenario-based (put the user in a situation), not trivia
- `correct` is 0-indexed (0 = A, 1 = B, 2 = C, 3 = D)
- Explanation should teach, not just say "correct because correct"

---

### Step 2 — Add workspace config in `simulation_missions.py`

Find the `WORKSPACE_MISSIONS` dict and add your entry.
Copy the structure from `phishing_fake_email` or `ransomware` as a base.

```python
"your_attack_id": {
    **_base_mission("your_attack_id"),    # pulls name/icon/difficulty automatically

    "mission_title": "Hard Simulation — Short descriptive title",
    "story": (
        "What the player's role is. Set the scene. "
        "No hints — they must figure it out themselves."
    ),
    "objectives": [
        "Objective 1 — what they need to do first",
        "Objective 2 — flag suspicious signs",
        "Objective 3 — use a tool",
        "Objective 4 — submit the incident report",
    ],
    "skills_learned": [
        "Skill 1",
        "Skill 2",
        "Skill 3",
    ],

    # ↓ This tells the router which HTML template to use for the hard sim
    "sim_template": "simulations/your_attack_hard.html",

    "signs": [
        {
            "id": "sign_id_1",
            "label": "Sign label",
            "hint": "Hint shown when they hover/click the sign.",
        },
        # match the sign IDs from simulation_data.py
    ],

    "logs": [
        {"time": "10:00:01", "level": "INFO",  "message": "Scenario initialized."},
        {"time": "10:00:22", "level": "WARN",  "message": "Anomaly detected."},
        {"time": "10:00:45", "level": "ALERT", "message": "Suspicious activity confirmed."},
    ],

    "tasks": [
        {
            "id": "task_1",
            "objective_index": 0,
            "label": "Task label shown in the task log",
            "action": "review_form",   # your JS will call completeTask("task_1") when done
        },
        {
            "id": "flag_three",
            "objective_index": 1,
            "label": "Flag at least 3 suspicious signs",
            "action": "flag_signs",
            "required": 3,
        },
        {
            "id": "submit_report",
            "objective_index": 3,
            "label": "Submit incident report",
            "action": "submit_report",
        },
    ],

    "decisions": [
        {
            "id": "final_action",
            "prompt": "Based on your investigation, what is the correct response?",
            "options": [
                {
                    "id": "wrong_choice",
                    "label": "A wrong thing to do",
                    "score": 0,
                    "mistake": "Short label for the mistake (shown in results)",
                },
                {
                    "id": "correct_choice",
                    "label": "The correct response",
                    "score": 100,
                    "good": "Short label for the good action (shown in results)",
                },
            ],
        }
    ],
},
```

---

### Step 3 — Register the easy sim in `simulations.py`

Open `backend/secure_it/routes/simulations.py`.
Find `EASY_SIMULATION_PAGES` and add your attack:

```python
EASY_SIMULATION_PAGES: dict[str, dict[str, str]] = {
    "phishing_fake_email": {
        "template": "simulations/phishing_easy.html",
        "interface_key": "email_data",
    },
    "sql_injection": {
        "template": "simulations/sql_injection_easy.html",
        "interface_key": "form_data",
    },
    # ↓ Add yours here
    "your_attack_id": {
        "template": "simulations/your_attack_easy.html",
        "interface_key": "interface_data",   # can be anything, matches what you use in the template
    },
}
```

The `interface_key` is the variable name available in your easy sim template
(e.g. `{{ interface_data.field_name }}`).

The hard sim routing is already handled — as long as you set `"sim_template"` in
`simulation_missions.py` (Step 2), it routes automatically. No other change needed.

---

### Step 4 — Build the Easy Sim HTML/CSS/JS

The easy sim is a **guided, hinted** version. The user sees the attack scenario and
is shown indicators (the panel on the right) that point out what's suspicious.

**Reference files to copy from:**
```
frontend/templates/simulations/phishing_easy.html
frontend/static/css/phishing-easy.css
frontend/static/js/phishing-easy.js
```

**Layout structure (3 columns):**
```
[Left sidebar]          [Center — the attack UI]         [Right sidebar]
Sim info                Your attack's interface           Indicators panel
Objectives              (email / form / file / etc.)      Flag buttons
Timer                                                      Verdict buttons
Task list
```

**What the JS needs to do:**
- Let the user interact with the attack interface
- Track which indicators they've found/flagged
- Show feedback when they flag something
- Call `POST {{ complete_url }}` with the result JSON when done:

```javascript
fetch(completeUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        score: 85,
        good_decisions: ["Identified spoofed domain"],
        mistakes: [],
        recommendations: ["Always verify sender domain"],
        time_spent_seconds: 120,
        skills_developed: ["Threat identification"],
        flags_found: ["sender_domain", "urgent_language"],
    })
});
```

---

### Step 5 — Build the Hard Sim HTML/CSS/JS

The hard sim is **no hints** — the user must find the signs themselves.

**Reference files to copy from:**
```
frontend/templates/simulations/phishing_hard.html
frontend/static/css/phishing-hard.css
frontend/static/js/phishing-hard.js
```

**Layout structure (3 columns):**
```
[Left sidebar]          [Center — attack interface]      [Right sidebar]
Sim info                Your attack's interface           Event feed
Objectives              with no hint overlays
Timer
Progress
Task log
```

**What the JS needs to do:**
- Render the attack interface (same scenario as easy but no guided indicators)
- Track flags the user marks themselves
- Handle the final decision modal
- Submit results to `POST {{ workspace_data.complete_url }}` with the same JSON shape as easy sim above

**The `workspace_data` variable is available in your template as JSON:**
```html
<script id="workspace-data" type="application/json">
    {{ workspace_data | tojson }}
</script>
```

Parse it in JS:
```javascript
const data = JSON.parse(document.getElementById('workspace-data').textContent);
// data.signs          ← array of signs to flag
// data.tasks          ← task list
// data.decisions      ← final decision options
// data.complete_url   ← where to POST results
// data.logs           ← security log entries
```

---

### Step 6 — Drop in the images

Put your 4 images in the correct folder:

```
frontend/static/img/modules/<your-folder>/
    image1_<attack>.jpg     (used on the About tab of the informational page)
    image2_<attack>.png     (used on the Origin tab)
    image3_<attack>.jpg     (used on the Real World tab)
    video-poster.svg        (thumbnail shown on the video player)
```

The image folder name must match what you set in `simulation_data.py`:
```python
"media": {
    "folder": "your-folder",   # ← must match the folder name exactly
    ...
}
```

---

## Quick Reference — Folder Names

| Attack ID | Image folder name |
|---|---|
| `phishing_fake_email` | `phishing` ✓ done |
| `phishing_fake_website` | `phishing-website` ✓ image exists |
| `social_engineering` | `social-engineering` ✓ image exists |
| `keylogger` | `keylogger` ✓ image exists |
| `ransomware` | `ransomware` ✓ image exists |
| `spyware` | `spyware` ✓ image exists |
| `adware_malvertising` | `adware` ✓ image exists |
| `mitm` | `mitm` ✓ image exists |
| `evil_twin` | `evil-twin` ✓ image exists |
| `sql_injection` | `sql-injection` ✓ done |

The `module_<attack>.jpg/png` card images are already there.
You still need to add the 3 spotlight images + `video-poster.svg` for each.

---

## Checklist (per attack)

```
Data
  [ ] ATTACKS["your_attack_id"] filled in simulation_data.py
        [ ] overview (explanation, why_used, how_encountered, steps, warnings, tips)
        [ ] info_page (media folder + spotlight 3 tabs + real_world_examples)
        [ ] easy_simulation (steps + indicators)
        [ ] hard_simulation (steps + signs)
        [ ] quiz (5 questions with correct index + explanation)

  [ ] WORKSPACE_MISSIONS["your_attack_id"] filled in simulation_missions.py
        [ ] sim_template set to "simulations/your_attack_hard.html"
        [ ] objectives (4–5 items)
        [ ] signs (matching IDs from simulation_data.py)
        [ ] tasks (matching action IDs your JS will complete)
        [ ] decisions (options with score/good/mistake)
        [ ] logs (3–5 log entries)

  [ ] Attack added to EASY_SIMULATION_PAGES in simulations.py

Frontend
  [ ] your_attack_easy.html created
  [ ] your_attack_hard.html created
  [ ] your_attack-easy.css created
  [ ] your_attack-hard.css created
  [ ] your_attack-easy.js created
  [ ] your_attack-hard.js created

Images
  [ ] image1_<attack>.jpg (About tab)
  [ ] image2_<attack>.png (Origin tab)
  [ ] image3_<attack>.jpg (Real World tab)
  [ ] video-poster.svg
```

---

## Testing Your Attack

Once all files are in place, run the server and navigate to:

```
/simulations/<your_attack_id>          Informational page
/simulations/<your_attack_id>/easy     Easy sim
/simulations/<your_attack_id>/play     Hard sim (requires completing easy first)
/simulations/<your_attack_id>/quiz     Quiz (requires completing hard sim first)
/simulations/<your_attack_id>/results  Results page
```

If the informational page shows a 404 or blank, check that your `ATTACKS` block has
`"info_page"` with content.

If the easy sim 404s, check that your attack ID is in `EASY_SIMULATION_PAGES`.

If the hard sim goes to the wrong template, check that `"sim_template"` is set in
`WORKSPACE_MISSIONS`.
