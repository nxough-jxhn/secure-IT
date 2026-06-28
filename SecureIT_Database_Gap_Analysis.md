# Secure-IT — Database & Codebase Gap Analysis
*Cross-checked against Final Functional Requirements*

---

## 📌 Summary

The current codebase has a working foundation — authentication, simulation flow, quiz, and basic progress tracking are partially in place. However, significant structural gaps exist because the current code was built around a simpler system before the full gamification design, two-simulation structure, namecard system, certificate system, and updated attack modules were finalized.

---

## ✅ What Already Exists (Keep These)

### Collections in MongoDB
| Collection | Status | Notes |
|---|---|---|
| `users` | ✅ Exists | Has name, email, password_hash, role, points, level, simulations_completed |
| `simulation_results` | ✅ Exists | Has email, attack_id, simulation_score, quiz_score, points_earned, mistakes, good_actions |
| `profiles` | ✅ Exists | Basic profile data — needs expansion |
| `metrics` | ✅ Exists | Admin-level stats |
| `attempts` | ✅ Exists | Intrusion attempt logs |
| `activity_logs` | ✅ Exists | User action logging |

### simulation_data.py — Current Attacks
| Attack ID | Status | Notes |
|---|---|---|
| `phishing` | ✅ Exists | Covers fake email scenario |
| `malware` | ✅ Exists | Generic malware — maps to Adware/Ransomware |
| `ransomware` | ✅ Exists | Exists but needs two-sim structure |
| `trojan` | ✅ Exists | Not in final 10 — can be removed or repurposed |
| `virus` | ✅ Exists | Not in final 10 — can be removed or repurposed |
| `spyware` | ✅ Exists | ✅ In final 10 — needs expansion |
| `dos` | ✅ Exists | Not in final 10 — can be removed |
| `social_engineering` | ✅ Exists | ✅ In final 10 — needs expansion |
| `password_attack` | ✅ Exists | Not in final 10 — can be removed |

---

## ❌ What is Missing (Must Add)

### 1. Missing Attack Modules in simulation_data.py

| Attack ID Needed | Status |
|---|---|
| `phishing_fake_website` | ❌ Missing — only fake email exists |
| `keylogger` | ❌ Missing entirely |
| `adware_malvertising` | ❌ Missing — current `malware` is too generic |
| `mitm` | ❌ Missing entirely |
| `evil_twin` | ❌ Missing entirely |
| `sql_injection` | ❌ Missing entirely |

**Action:** Add 6 new attack entries to `simulation_data.py` following the existing structure. Each needs `id`, `name`, `icon`, `difficulty`, `overview`, `steps`, and `quiz`.

---

### 2. Missing: Two-Simulation Structure Per Module

**Current behavior:**
- One simulation per attack (the hard version only)
- No easy/guided simulation with visual indicators

**What needs to be added:**
Each attack entry in `simulation_data.py` needs a second simulation object:

```python
"phishing": {
    ...
    "easy_simulation": {
        "steps": [...],          # same scenario but with indicators/highlights
        "indicators": [          # list of red flags to highlight for the user
            {"element": "sender_domain", "hint": "This domain is not the real bank"},
            {"element": "link_url", "hint": "Hover to check this URL"},
        ]
    },
    "hard_simulation": {
        "steps": [...],          # same as current "steps" — no indicators
        "signs": [               # the hidden signs user must find and flag
            {"id": "sender_domain", "label": "Spoofed sender domain"},
            {"id": "urgent_language", "label": "Urgent threatening language"},
        ]
    },
    ...
}
```

**Action:** Refactor all 10 attack entries to separate `easy_simulation` and `hard_simulation` keys.

---

### 3. Missing: Retake Tracking Per Module

**Current behavior:**
`simulation_results` records completions but does not track retake count per user per attack.

**What needs to be added to `users` collection:**
```python
"simulation_retakes": {
    "phishing": 0,          # number of retakes used (max 2)
    "keylogger": 1,
    ...
}
```

Or as a separate collection:

```python
# simulation_retakes collection
{
    "email": "user@example.com",
    "attack_id": "phishing",
    "retakes_used": 1,          # 0, 1, or 2 — never exceeds 2
    "hard_sim_completed": True,
    "hard_sim_ended_early": False,
    "updated_at": datetime
}
```

**Action:** Add `simulation_retakes` collection or embed retake tracking inside `users`.

---

### 4. Missing: Easy Simulation Completion Tracking

**Current behavior:**
`simulations_completed` in `users` only tracks if a simulation was done — no distinction between easy and hard.

**What needs to be added:**
```python
# Inside users collection
"module_progress": {
    "phishing": {
        "info_page_viewed": True,
        "easy_sim_completed": True,
        "hard_sim_completed": False,
        "hard_sim_ended_early": False,
        "quiz_passed": False,
        "quiz_score": None,
        "module_complete": False
    },
    ...
}
```

**Action:** Add `module_progress` field to `users` collection and update `record_simulation_completion()` in `database.py` to write to it.

---

### 5. Missing: Gamification — Updated Points & Level System

**Current behavior in `database.py`:**
```python
def _level_for_points(points: int) -> str:
    if points >= 2500:
        return "Advanced"
    if points >= 1000:
        return "Intermediate"
    return "Beginner"
```
This uses the old 3-level system with wrong thresholds.

**What it should be (5 levels):**
```python
def _level_for_points(points: int) -> str:
    if points >= 1300:
        return "Cyber Shield"
    if points >= 1000:
        return "Guardian"
    if points >= 600:
        return "Defender"
    if points >= 300:
        return "Aware"
    return "Rookie"
```

**Action:** Update `_level_for_points()` in `database.py`.

---

### 6. Missing: Badge System Collection

**Current behavior:**
Badges are hardcoded in `get_user_dashboard_data()` based on point thresholds only — not tied to module completion or milestones.

```python
# Current — wrong and incomplete
if progress["points"] >= 500:
    badges.append("Mission Operator")
```

**What needs to be added:**

```python
# badges collection
{
    "email": "user@example.com",
    "badges_earned": [
        {
            "badge_id": "phishing_spotter",
            "badge_name": "Phishing Spotter",
            "badge_type": "module",       # "module" or "milestone"
            "earned_at": datetime
        },
        {
            "badge_id": "first_step",
            "badge_name": "First Step",
            "badge_type": "milestone",
            "earned_at": datetime
        }
    ],
    "updated_at": datetime
}
```

A `check_and_award_badges()` function needs to be written in `database.py` that runs after every module completion and checks all badge conditions.

**Action:** Create `badges` collection and `check_and_award_badges()` function.

---

### 7. Missing: Namecard System Collection

**No namecard system exists at all.**

**What needs to be added:**

```python
# namecards collection
{
    "email": "user@example.com",
    "namecards_earned": [
        {
            "namecard_id": "social_sentinel",
            "namecard_name": "Social Sentinel",
            "namecard_type": "category",      # "category", "leaderboard", "ultimate"
            "earned_at": datetime
        }
    ],
    "active_namecard": "social_sentinel",     # currently displayed namecard
    "updated_at": datetime
}
```

A `check_and_award_namecards()` function needs to be written that runs after module completion and leaderboard rank updates.

**Action:** Create `namecards` collection and `check_and_award_namecards()` function.

---

### 8. Missing: Certificate System Collection

**No certificate system exists at all.**

**What needs to be added:**

```python
# certificates collection
{
    "email": "user@example.com",
    "certificates": [
        {
            "cert_id": "performance",
            "cert_type": "performance",       # "performance", "completion", "perfect_score", "leaderboard"
            "issued_at": datetime,
            "data": {                          # dynamic data embedded in the cert
                "points": 860,
                "level": "Defender",
                "modules_completed": 6,
                "generated_at": datetime
            }
        },
        {
            "cert_id": "completion",
            "cert_type": "completion",
            "issued_at": datetime,
            "data": {
                "completion_date": datetime,
                "badges_earned": [...],
            }
        }
    ],
    "updated_at": datetime
}
```

A `generate_certificate()` function needs to be written that creates/updates the relevant certificate type.

**Action:** Create `certificates` collection and `generate_certificate()` function.

---

### 9. Missing: Category Grouping in simulation_data.py

**Current behavior:**
Attacks have no category field — they're just a flat dictionary.

**What needs to be added to each attack entry:**
```python
"phishing": {
    "id": "phishing",
    "category": "social_based",        # ADD THIS
    "category_label": "Social-Based Attacks",
    ...
}
```

**Categories:**
| category value | Attacks |
|---|---|
| `social_based` | phishing, phishing_fake_website, social_engineering |
| `malware_based` | keylogger, ransomware, spyware, adware_malvertising |
| `network_based` | mitm, evil_twin |
| `injection_based` | sql_injection |

**Action:** Add `category` and `category_label` fields to all 10 attack entries.

---

### 10. Missing: Leaderboard Collection

**Current behavior:**
No dedicated leaderboard — rankings would have to be computed live from `users` every time which is slow.

**What needs to be added:**

```python
# leaderboard collection — updated after every point change
{
    "email": "user@example.com",
    "username": "JohnNeo",
    "points": 1200,
    "level": "Guardian",
    "badges_count": 8,
    "active_namecard": "social_sentinel",
    "rank": 1,
    "rank_title": "Top Defender",
    "updated_at": datetime
}
```

A `refresh_leaderboard()` function that re-ranks all users and updates rank titles and leaderboard namecards after every point change.

**Action:** Create `leaderboard` collection and `refresh_leaderboard()` function.

---

### 11. Missing: total_modules Reference Update

**Current behavior in `database.py`:**
```python
# This pulls from simulation_data.ATTACKS which currently has 9 entries
completion = round((len(progress["simulations_completed"]) / max(len(list_attack_ids()), 1)) * 100)
```

Once the final 10 attacks are in `simulation_data.py`, this will auto-correct. But `DEFAULT_METRICS` also hardcodes:
```python
DEFAULT_METRICS = {
    "total_modules": 6,   # ❌ Should be 10
    ...
}
```

**Action:** Update `total_modules` to `10` in `DEFAULT_METRICS`.

---

## 🗂️ Final Collections Summary

| Collection | Status | Action |
|---|---|---|
| `users` | ✅ Exists | Add `module_progress`, `simulation_retakes` fields |
| `simulation_results` | ✅ Exists | Keep as is |
| `profiles` | ✅ Exists | Keep or merge into `users` |
| `metrics` | ✅ Exists | Update `total_modules` to 10 |
| `attempts` | ✅ Exists | Keep as is |
| `activity_logs` | ✅ Exists | Keep as is |
| `badges` | ❌ Missing | Create new collection |
| `namecards` | ❌ Missing | Create new collection |
| `certificates` | ❌ Missing | Create new collection |
| `leaderboard` | ❌ Missing | Create new collection |
| `simulation_retakes` | ❌ Missing | Create new collection or embed in `users` |

---

## 🔧 Functions to Update in database.py

| Function | Action |
|---|---|
| `_level_for_points()` | Update to 5-level system with correct thresholds |
| `record_simulation_completion()` | Add `module_progress` update, badge check, namecard check, leaderboard refresh, certificate generation |
| `get_user_dashboard_data()` | Remove hardcoded badge logic — pull from `badges` collection instead |
| `get_user_progress()` | Add `module_progress`, `badges`, `namecards`, `active_namecard` to return data |

## 🔧 New Functions to Add in database.py

| Function | Purpose |
|---|---|
| `check_and_award_badges()` | Check all badge conditions after module completion and award missing ones |
| `check_and_award_namecards()` | Check all namecard conditions and award missing ones |
| `generate_certificate()` | Create or update a certificate for a given type |
| `refresh_leaderboard()` | Re-rank all users and update rank titles and leaderboard namecards |
| `get_simulation_retakes()` | Get retake count for a user per attack |
| `increment_simulation_retake()` | Add 1 to retake count for a user per attack |
| `update_module_progress()` | Update the module_progress field for a user per attack |
