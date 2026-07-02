"""TryHackMe-style mission workspace definitions for Secure-IT simulations."""

from __future__ import annotations

from typing import Any

from simulation_data import ATTACKS, get_attack


def _base_mission(attack_id: str) -> dict[str, Any]:
    attack = get_attack(attack_id)
    if not attack:
        return {}

    overview = attack.get("overview", {})
    return {
        "attack_id": attack_id,
        "name": attack["name"],
        "icon": attack["icon"],
        "difficulty": attack["difficulty"],
        "mission_title": f"{attack['name']} Investigation",
        "story": overview.get("explanation", attack.get("short_description", "")),
        "objectives": [
            "Review intelligence briefing and available tools",
            "Investigate indicators in the simulated environment",
            "Identify malicious activity and document findings",
            "Submit the correct incident response action",
        ],
        "tools": ["inbox", "terminal", "url_analyzer", "logs", "scanner", "notes"],
        "estimated_minutes": 12 if attack["difficulty"] == "Beginner" else 18,
        "skills_learned": [
            "Threat identification",
            "Security analysis",
            "Incident response",
        ],
    }


WORKSPACE_MISSIONS: dict[str, dict[str, Any]] = {
    "phishing_fake_email": {
        **_base_mission("phishing_fake_email"),
        "mission_title": "Hard Simulation — Suspicious Password Email",
        "story": (
            "You receive an email asking you to reset your password. It appears to come from your "
            "school portal. No hints are provided — identify suspicious signs on your own, use the "
            "URL analyzer if needed, and decide how to respond."
        ),
        "objectives": [
            "Review the password-reset email in the Gmail workspace",
            "Flag 3–5 suspicious signs hidden in the message",
            "Analyze the email link with the URL analyzer tool",
            "Avoid clicking unverified links and submit your incident report",
        ],
        "skills_learned": [
            "Phishing identification",
            "Sender verification",
            "URL threat assessment",
            "Incident reporting",
        ],
        "tools": ["gmail", "url_analyzer", "flag_tool"],
        "gmail_mode": True,
        "email": {
            "id": "phish-hard-1",
            "from_name": "UP Diliman Portal",
            "from_address": "noreply@up-portal-support.net",
            "subject": "ACTION REQUIRED: Your account will be suspended in 24 hours",
            "greeting": "Dear User,",
            "body": (
                "Our records show that your UP student portal password has not been updated recently. "
                "Please reset you're password immediately to avoid account suspension."
            ),
            "link_text": "upd.edu.ph/account-reset",
            "link_href": "https://up-portal-support.net/secure-login",
            "signoff": "Thank you,\nUP Diliman IT Services",
            "timestamp": "9:16 PM (1 hour ago)",
            "inbox_count": 1310,
        },
        "signs": [
            {
                "id": "sender_domain",
                "label": "Spoofed sender domain",
                "hint": "Legitimate UP mail uses @upd.edu.ph or @up.edu.ph — not up-portal-support.net.",
            },
            {
                "id": "urgent_language",
                "label": "Urgent threatening language",
                "hint": "Pressure to act within 24 hours is a common phishing tactic.",
            },
            {
                "id": "link_mismatch",
                "label": "Suspicious link URL",
                "hint": "The link text shows upd.edu.ph but hover/inspect reveals up-portal-support.net.",
            },
            {
                "id": "generic_greeting",
                "label": "Generic greeting",
                "hint": "Official mail usually addresses you by name, not “Dear User.”",
            },
            {
                "id": "grammar_error",
                "label": "Grammar or formatting error",
                "hint": "“Please reset you're password” misuses you're instead of your.",
            },
        ],
        "url_analysis": {
            "https://up-portal-support.net/secure-login": {
                "verdict": "PHISHING — HIGH RISK",
                "domain_age": "Registered 3 days ago",
                "ssl": "Valid but issuer unknown",
                "reputation": "Reported for credential harvesting",
                "similar_to": "Impersonates upd.edu.ph login portal",
                "recommendation": "Do not visit. Report to IT and block domain.",
            },
            "upd.edu.ph/account-reset": {
                "verdict": "DISPLAY TEXT ONLY",
                "note": "This is link text shown in the email, not the real destination. Analyze the hovered URL instead.",
            },
        },
        "inbox": {
            "emails": [
                {
                    "id": "phish-hard-1",
                    "from_display": "UP Diliman Portal",
                    "from_address": "noreply@up-portal-support.net",
                    "subject": "ACTION REQUIRED: Your account will be suspended in 24 hours",
                    "body": "",
                    "malicious": True,
                }
            ]
        },
        "logs": [
            {"time": "21:14:02", "level": "WARN", "message": "Inbound message from up-portal-support.net (external)"},
            {"time": "21:14:18", "level": "ALERT", "message": "Subject contains urgency keywords: suspended, 24 hours"},
            {"time": "21:15:44", "level": "INFO", "message": "URL analyzer available for analyst review"},
        ],
        "tasks": [
            {"id": "open_email", "objective_index": 0, "label": "Open the password-reset email", "action": "open_email"},
            {"id": "flag_three", "objective_index": 1, "label": "Flag at least 3 suspicious signs", "action": "flag_signs", "required": 3},
            {"id": "analyze_url", "objective_index": 2, "label": "Analyze the suspicious URL", "action": "analyze_url"},
            {"id": "submit_report", "objective_index": 3, "label": "Submit incident report without clicking the link", "action": "submit_report"},
        ],
        "decisions": [
            {
                "id": "final_action",
                "prompt": "Based on your investigation, what is the correct response?",
                "options": [
                    {"id": "click", "label": "Click the link and reset your password", "score": 0, "mistake": "Clicked unverified phishing link"},
                    {"id": "ignore", "label": "Ignore the email silently", "score": 40, "mistake": "Did not report the phishing attempt"},
                    {"id": "report_phishing", "label": "Report phishing and warn IT", "score": 100, "good": "Reported phishing and protected the organization"},
                ],
            }
        ],
    },
    "sql_injection": {
        **_base_mission("sql_injection"),
        "mission_title": "Hard Simulation — Vulnerable Admin Login",
        "story": (
            "You are testing a legacy UP Campus Portal admin login for security weaknesses. "
            "No hints are provided — observe the form on your own, flag vulnerability signs, "
            "and determine whether SQL injection can bypass authentication."
        ),
        "objectives": [
            "Review the admin login page and inspect how it handles input",
            "Flag 3–5 vulnerability signs you discover on your own",
            "Trigger and analyze suspicious database error responses",
            "Bypass the login with a crafted SQL injection payload",
            "Submit your incident report with the correct remediation action",
        ],
        "skills_learned": [
            "SQL injection identification",
            "Input validation assessment",
            "Authentication bypass analysis",
            "Secure development recommendations",
        ],
        "tools": ["login_lab", "flag_tool", "request_inspector"],
        "sqli_mode": True,
        "login_form": {
            "app_name": "UP Campus Portal — Admin",
            "url_bar": "portal.upd.edu.ph/admin/login?engine=mysql&query=1&legacy=1",
            "username_label": "Username",
            "password_label": "Password",
            "submit_label": "Sign in",
            "legacy_notice": "Legacy authentication module — CAPTCHA and input filtering disabled.",
            "footer_note": "Direct query mode enabled for this endpoint.",
            "error_message": (
                "SQL syntax error: You have an error in your SQL syntax; check the manual that "
                "corresponds to your MySQL server version for the right syntax to use near '''' at line 1"
            ),
            "accepted_payloads": [
                "' OR '1'='1' --",
                "' OR '1'='1'--",
                "admin' OR '1'='1' --",
                "' OR 1=1 --",
                "' OR '1'='1",
                "' OR 1=1--",
            ],
            "admin_dashboard": {
                "title": "Admin Dashboard",
                "welcome": "Welcome, administrator",
                "subtitle": "UP Campus Portal — elevated access granted",
                "stats": [
                    {"label": "Registered students", "value": "24,891"},
                    {"label": "Pending enrollments", "value": "312"},
                    {"label": "Last DB backup", "value": "Today, 02:00 AM"},
                ],
            },
        },
        "signs": [
            {
                "id": "no_sanitization",
                "label": "No input sanitization visible",
                "hint": "There is no CAPTCHA, rate limiting banner, or filtering notice — only a legacy auth warning.",
            },
            {
                "id": "url_hint",
                "label": "URL hints at direct database query usage",
                "hint": "Query parameters like engine=mysql, query=1, and legacy=1 suggest raw SQL-backed authentication.",
            },
            {
                "id": "special_chars",
                "label": "Form accepts special characters without filtering",
                "hint": "The username field accepts quotes, spaces, and SQL keywords with no client-side blocking.",
            },
            {
                "id": "no_input_limits",
                "label": "No input character limits enforced",
                "hint": "Neither field enforces maxlength or pattern restrictions — a common sign of missing validation.",
            },
            {
                "id": "sql_error_leak",
                "label": "SQL syntax error reveals database details",
                "hint": "Submitting a single quote triggers a MySQL syntax error — clear evidence of unsanitized SQL execution.",
            },
        ],
        "request_inspector": {
            "endpoint": "POST /admin/login?engine=mysql&query=1&legacy=1",
            "method": "POST",
            "content_type": "application/x-www-form-urlencoded",
            "backend_note": (
                "Legacy auth handler concatenates username/password directly into SQL. "
                "Raw query mode is enabled for this endpoint."
            ),
            "headers": [
                "X-Legacy-SQL: enabled",
                "X-Query-Builder: string_concat",
            ],
            "sample_body": "username={input}&password={input}",
        },
        "logs": [
            {"time": "14:02:11", "level": "INFO", "message": "Legacy login endpoint active: /admin/login?engine=mysql"},
            {"time": "14:02:44", "level": "WARN", "message": "No WAF rules matched for admin authentication route"},
            {"time": "14:03:02", "level": "INFO", "message": "Request inspector available for analyst review"},
        ],
        "tasks": [
            {"id": "review_form", "objective_index": 0, "label": "Review the admin login page", "action": "review_form"},
            {"id": "flag_three", "objective_index": 1, "label": "Flag at least 3 vulnerability signs", "action": "flag_signs", "required": 3},
            {"id": "trigger_error", "objective_index": 2, "label": "Trigger a SQL error with test input", "action": "trigger_error"},
            {"id": "bypass_login", "objective_index": 3, "label": "Bypass login with SQL injection", "action": "bypass_login"},
            {"id": "submit_report", "objective_index": 4, "label": "Submit incident report with remediation", "action": "submit_report"},
        ],
        "decisions": [
            {
                "id": "final_action",
                "prompt": "Based on your investigation, what is the correct remediation for this vulnerability?",
                "options": [
                    {
                        "id": "capcha_only",
                        "label": "Add CAPTCHA but keep string-built SQL queries",
                        "score": 20,
                        "mistake": "CAPTCHA alone does not fix SQL injection in query construction",
                    },
                    {
                        "id": "hide_errors",
                        "label": "Hide error messages but keep concatenated queries",
                        "score": 30,
                        "mistake": "Hiding errors reduces visibility but leaves the injection flaw exploitable",
                    },
                    {
                        "id": "parameterize",
                        "label": "Use parameterized queries and validate all input",
                        "score": 100,
                        "good": "Recommended fix: parameterized queries with proper input validation",
                    },
                ],
            }
        ],
    },
    "social_engineering": {
        **_base_mission("social_engineering"),
        "mission_title": "Hard Simulation — Suspicious IT Support Call",
        "story": (
            "You receive a phone call from someone claiming to be the UP IT Security Office. "
            "No hints are provided — listen carefully, flag suspicious tactics on your own, "
            "use the caller lookup tool if needed, and decide how to respond."
        ),
        "objectives": [
            "Answer the call and listen to the caller's requests",
            "Flag at least 3 suspicious social engineering tactics",
            "Use the caller lookup tool to verify the number",
            "End the call and decide the correct response",
            "Submit your incident report",
        ],
        "skills_learned": [
            "Social engineering identification",
            "Caller identity verification",
            "OTP security awareness",
            "Urgency tactic recognition",
        ],
        "tools": ["phone", "flag_tool", "caller_lookup"],
        "sim_template": "simulations/social_engineering_hard.html",
        "signs": [
            {
                "id": "spoofed_caller_id",
                "label": "Caller ID could be spoofed",
                "hint": "The display name 'TUP-T IT Helpdesk' can be set by anyone with a VoIP tool. Caller ID proves nothing.",
            },
            {
                "id": "urgency",
                "label": "Artificial urgency — 'right now'",
                "hint": "Legitimate TUP-T IT staff don't demand immediate action. Creating panic stops you from thinking critically.",
            },
            {
                "id": "personal_info_bait",
                "label": "Uses personal info to build false trust",
                "hint": "Knowing your student number doesn't make them IT. This information is easy to find online.",
            },
            {
                "id": "otp_request",
                "label": "Requests a verification code (OTP)",
                "hint": "Legitimate IT staff will never ask for an OTP over the phone. Full stop.",
            },
            {
                "id": "urgency_deadline",
                "label": "Countdown threat — '5 minutes'",
                "hint": "Fake deadlines create fear. Real security alerts give you time to verify.",
            },
            {
                "id": "authority_pressure",
                "label": "Pressure not to hang up",
                "hint": "Insisting you stay on the line is a manipulation tactic. Real IT will always let you call back.",
            },
        ],
        "logs": [
            {"time": "09:41:02", "level": "INFO",  "message": "Incoming call from +63 2 5310-0000 — caller ID: TUP-T IT Helpdesk"},
            {"time": "09:41:18", "level": "WARN",  "message": "Number not found in official TUP-T IT directory"},
            {"time": "09:41:44", "level": "ALERT", "message": "Call contains urgency keywords: suspended, 5 minutes"},
        ],
        "tasks": [
            {"id": "answer_call",   "objective_index": 0, "label": "Answer and listen to the call",        "action": "answer_call"},
            {"id": "flag_three",    "objective_index": 1, "label": "Flag at least 3 suspicious tactics",   "action": "flag_signs", "required": 3},
            {"id": "lookup_caller", "objective_index": 2, "label": "Look up the caller's number",          "action": "lookup_caller"},
            {"id": "end_call",      "objective_index": 3, "label": "End the call",                         "action": "end_call"},
            {"id": "review_call",   "objective_index": 0, "label": "Review all caller messages",           "action": "review_call"},
            {"id": "submit_report", "objective_index": 4, "label": "Submit incident report",               "action": "submit_report"},
        ],
        "decisions": [
            {
                "id": "final_action",
                "prompt": "Based on your investigation, what is the correct response to this call?",
                "options": [
                    {
                        "id": "read_otp",
                        "label": "Read the OTP to the caller to secure the account",
                        "score": 0,
                        "mistake": "Shared OTP with attacker — account credentials compromised",
                    },
                    {
                        "id": "partial_info",
                        "label": "Confirm student number but refuse to share the OTP",
                        "score": 35,
                        "mistake": "Shared personal details that help attackers refine further attacks",
                    },
                    {
                        "id": "hang_up_verify",
                        "label": "Hang up, find the official helpdesk number, and call back yourself",
                        "score": 100,
                        "good": "Correctly identified social engineering — verified through official channels",
                    },
                ],
            }
        ],
    },
    "ransomware": {
        **_base_mission("ransomware"),
        "mission_title": "Ransomware Incident Response",
        "story": "Multiple file extensions changed across shared drives. Lead the initial response as the on-call analyst.",
        "objectives": ["Identify encryption indicators", "Isolate affected systems", "Preserve evidence", "Activate recovery plan"],
        "logs": [
            {"time": "03:18:01", "level": "CRIT", "message": "Mass file rename detected: *.locked"},
            {"time": "03:18:22", "level": "ALERT", "message": "Ransom note dropped on DESKTOP-FIN-04"},
        ],
        "terminal_responses": {
            "help": "Commands: isolate host, snapshot-logs, status",
            "isolate host": "Host removed from network. Lateral movement blocked.",
            "snapshot-logs": "Forensic snapshot saved to secure vault.",
        },
        "tasks": [
            {"id": "logs", "objective_index": 0, "label": "Review ransomware alerts", "tool": "logs", "action": "review"},
            {"id": "isolate", "objective_index": 1, "label": "Isolate affected host", "tool": "terminal", "action": "command", "command": "isolate host"},
            {"id": "snapshot", "objective_index": 2, "label": "Capture forensic snapshot", "tool": "terminal", "action": "command", "command": "snapshot-logs"},
        ],
        "decisions": [
            {
                "id": "final_action",
                "prompt": "What is the correct IR action?",
                "options": [
                    {"id": "pay", "label": "Pay ransom immediately", "score": 0, "mistake": "Paid ransom without IR process"},
                    {"id": "isolate_recover", "label": "Isolate systems and restore from backups", "score": 100, "good": "Followed proper ransomware response"},
                    {"id": "wait", "label": "Wait and monitor", "score": 15, "mistake": "Delayed containment during active encryption"},
                ],
            }
        ],
    },
    "mitm": {
        **_base_mission("mitm"),
        "mission_title": "Hard Simulation — The Coffee Shop Transaction",
        "story": (
            "You are a student at a coffee shop who needs to pay tuition online. "
            "No hints are provided — every decision you make has a consequence. "
            "Navigate the scenario carefully: choose your network, verify the URL, "
            "respond to warnings, and review your transaction before confirming."
        ),
        "objectives": [
            "Select a safe network to connect to",
            "Verify the payment portal URL before logging in",
            "Respond correctly to the browser certificate warning",
            "Review the transaction summary before confirming",
        ],
        "skills_learned": [
            "Network security evaluation",
            "HTTPS and certificate awareness",
            "MITM attack recognition",
            "Secure transaction verification",
        ],
        "tools": ["browser", "wifi_selector"],
        "sim_template": "simulations/mitm_hard.html",
        "tasks": [
            {"id": "stage_1", "objective_index": 0, "label": "Choose a network", "action": "wifi_choice"},
            {"id": "stage_2", "objective_index": 1, "label": "Verify portal URL", "action": "url_choice"},
            {"id": "stage_3", "objective_index": 2, "label": "Handle certificate warning", "action": "cert_choice"},
            {"id": "stage_4", "objective_index": 3, "label": "Confirm or cancel transaction", "action": "transfer_choice"},
        ],
        "decisions": [],
    },
}


def _generic_mission(attack_id: str) -> dict[str, Any]:
    attack = get_attack(attack_id)
    if not attack:
        return {}

    base = _base_mission(attack_id)
    hard_simulation = attack.get("hard_simulation", {})
    steps = hard_simulation.get("steps") or attack.get("steps", [])
    first = steps[0] if steps else {}
    iface = first.get("interface", {})

    base["story"] = attack.get("overview", {}).get("explanation", base["story"])
    base["mission_title"] = f"{attack['name']} Security Lab"
    base["logs"] = [
        {"time": "10:00:01", "level": "INFO", "message": f"Simulation environment ready: {attack_id}"},
        {"time": "10:00:15", "level": "WARN", "message": "Anomaly detected in training scenario"},
    ]
    base["terminal_responses"] = {
        "help": "Commands: analyze, scan, report",
        "analyze": "Analysis complete. Review indicators in logs panel.",
        "scan": "Scan complete. Suspicious activity confirmed in scenario.",
        "report": "Incident report submitted to SOC queue.",
    }
    base["inbox"] = {
        "emails": [
            {
                "id": f"{attack_id}-1",
                "from_display": "Training Scenario",
                "from_address": f"lab@{attack_id}.secure-it.local",
                "subject": first.get("title", attack["name"]),
                "body": first.get("narrative", attack["short_description"]),
                "headers": {"SPF": "PASS", "Scenario": attack["name"]},
                "suspicious_url": iface.get("highlight") or iface.get("url", ""),
                "malicious": True,
            }
        ]
    }
    base["tasks"] = [
        {"id": "investigate", "objective_index": 1, "label": "Investigate scenario indicators", "tool": "logs", "action": "review"},
        {"id": "analyze", "objective_index": 2, "label": "Run analyze in terminal", "tool": "terminal", "action": "command", "command": "analyze"},
        {"id": "report", "objective_index": 3, "label": "Submit incident report", "tool": "terminal", "action": "command", "command": "report"},
    ]
    best_choice = next((c for step in steps for c in step.get("choices", []) if c.get("is_best")), None)
    base["decisions"] = [
        {
            "id": "final_action",
            "prompt": first.get("narrative", "Choose the best security response."),
            "options": [
                {
                    "id": c["id"],
                    "label": c["label"],
                    "score": c.get("score", 0),
                    "good": c["label"] if c.get("is_best") or c.get("score", 0) >= 100 else None,
                    "mistake": c["label"] if c.get("score", 0) < 70 else None,
                }
                for step in steps[:1]
                for c in step.get("choices", [])
            ]
            or [
                {"id": "secure", "label": "Apply secure response", "score": 100, "good": "Selected secure response"},
                {"id": "risky", "label": "Take risky shortcut", "score": 0, "mistake": "Unsafe decision"},
            ],
        }
    ]
    if best_choice:
        base["decisions"][0]["options"] = sorted(
            base["decisions"][0]["options"],
            key=lambda o: o.get("score", 0),
            reverse=True,
        )
    return base


def get_workspace_mission(attack_id: str) -> dict[str, Any] | None:
    if attack_id in WORKSPACE_MISSIONS:
        mission = dict(WORKSPACE_MISSIONS[attack_id])
    else:
        mission = _generic_mission(attack_id)

    if not mission:
        return None

    attack = get_attack(attack_id)
    if attack:
        mission["quiz"] = attack.get("quiz", [])
        mission["short_description"] = attack.get("short_description", "")
    return mission


def list_mission_summaries() -> list[dict[str, Any]]:
    summaries = []
    for attack_id in ATTACKS:
        mission = get_workspace_mission(attack_id)
        if not mission:
            continue
        attack = get_attack(attack_id)
        summaries.append(
            {
                "id": attack_id,
                "name": mission["name"],
                "icon": mission["icon"],
                "image": attack.get("image", "") if attack else "",
                "difficulty": mission["difficulty"],
                "short_description": mission.get("short_description", ""),
                "mission_title": mission["mission_title"],
                "estimated_minutes": mission["estimated_minutes"],
                "objectives_count": len(mission.get("objectives", [])),
                "skills_learned": mission.get("skills_learned", []),
                "tools": mission.get("tools", []),
            }
        )
    return summaries
