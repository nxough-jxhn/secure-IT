"""Cybersecurity attack simulation content for Secure-IT."""

from __future__ import annotations

from typing import Any


def _choice(
    choice_id: str,
    label: str,
    outcome: str,
    explanation: str,
    score: int,
    is_best: bool = False,
) -> dict[str, Any]:
    return {
        "id": choice_id,
        "label": label,
        "outcome": outcome,
        "explanation": explanation,
        "score": score,
        "is_best": is_best,
    }


def _placeholder_overview(topic: str) -> dict[str, Any]:
    return {
        "explanation": f"Placeholder overview for {topic}. Full content will be added in a later pass.",
        "why_used": "Placeholder — attacker motivation will be documented here.",
        "how_encountered": "Placeholder — common encounter scenarios will be documented here.",
        "how_it_happens": [
            "Placeholder step 1.",
            "Placeholder step 2.",
            "Placeholder step 3.",
        ],
        "warning_signs": [
            "Placeholder warning sign 1.",
            "Placeholder warning sign 2.",
        ],
        "prevention_tips": [
            "Placeholder prevention tip 1.",
            "Placeholder prevention tip 2.",
        ],
    }


def _placeholder_quiz(topic: str) -> list[dict[str, Any]]:
    return [
        {
            "question": f"Placeholder quiz question about {topic}?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct": 0,
            "explanation": "Placeholder explanation — full quiz content coming soon.",
        },
    ]


def _simulation_block(
    steps: list[dict[str, Any]],
    indicators: list[dict[str, str]] | None = None,
    signs: list[dict[str, str]] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    easy = {"steps": steps, "indicators": indicators or []}
    hard = {"steps": steps, "signs": signs or []}
    return easy, hard


PHISHING_EMAIL_STEPS = [
    {
        "title": "Suspicious University Email",
        "narrative": "You receive an email claiming to be from the University of the Philippines saying your network password will expire unless you update it within one day.",
        "interface_type": "email",
        "interface": {
            "from_name": "University of the philippines",
            "from": "it-support@univeristy.up-edu.ph",
            "subject": "Important: Your Password will expire in 1 day(s)",
            "greeting": "Dear network user,",
            "body": (
                "This email is meant to inform you that your University of the Philippines network password "
                "will expire in 24 hours. Please follow the link below to update your password."
            ),
            "signoff": "Thank you,\nUP Diliman Network Security Staff",
            "highlight": "upd.edu.ph/password-renewal",
            "link_actual": "up-edu.philippines-renewal.net/login",
            "footer_label": "UNIVERSITY OF THE PHILIPPINES",
        },
        "choices": [
            _choice(
                "click",
                "Click the verification link",
                "You entered credentials on a fake site. The attacker captured your username and password.",
                "The link domain does not match your university portal. Phishing sites mimic legitimate login pages to steal credentials.",
                0,
            ),
            _choice(
                "report",
                "Report the email to IT or the university helpdesk",
                "You flagged a phishing attempt. Security teams can warn others and block the malicious domain.",
                "Reporting suspicious messages is the best response. It protects you and helps your organization respond quickly.",
                100,
                is_best=True,
            ),
            _choice(
                "ignore",
                "Ignore the message",
                "You avoided the trap, but the phishing email remains unreported and may target others.",
                "Ignoring is safer than clicking, but reporting helps stop the attack from spreading.",
                60,
            ),
        ],
    },
    {
        "title": "Follow-up Login Page",
        "narrative": "You opened the link in a sandbox browser. A login page appears asking for your university username and password.",
        "interface_type": "website",
        "interface": {
            "url": "http://secure-up-verify.net/login",
            "title": "University Portal — Account Verification",
            "fields": ["University username", "Password"],
        },
        "choices": [
            _choice(
                "enter",
                "Enter your credentials to verify",
                "Credentials were sent to the attacker. Your account is now compromised.",
                "Legitimate university services do not ask for full credentials on pages reached through urgent email links.",
                0,
            ),
            _choice(
                "close",
                "Close the page and report the URL",
                "You stopped the attack and provided valuable intelligence to your security team.",
                "Closing suspicious pages and reporting URLs prevents credential theft.",
                100,
                is_best=True,
            ),
            _choice(
                "bookmark",
                "Bookmark the page to check later",
                "You preserved a dangerous link that could be clicked accidentally later.",
                "Never bookmark unverified login pages. Delete the email and report it instead.",
                20,
            ),
        ],
    },
]

PHISHING_EMAIL_QUIZ = [
    {
        "question": "You receive a password-reset email from noreply@up-portal-support.net. What is the safest first step?",
        "options": [
            "Click the link immediately before the 24-hour deadline",
            "Verify the sender through official UP channels and inspect the URL before acting",
            "Reply with your password to prove you own the account",
            "Forward the email to classmates to ask if it looks real",
        ],
        "correct": 1,
        "explanation": "Legitimate universities do not pressure you through unofficial domains. Verify through official portals or IT helpdesk contacts you already trust.",
    },
    {
        "question": "A link displays upd.edu.ph/account-reset, but hovering shows up-portal-support.net. What does this mean?",
        "options": [
            "The link is safe because the visible text looks official",
            "Gmail always shows the real destination in hover text",
            "The attacker is disguising a malicious URL behind familiar-looking link text",
            "UP uses multiple domains for the same login page",
        ],
        "correct": 2,
        "explanation": "Phishers often show a trusted domain in the link text while sending victims to a completely different site.",
    },
    {
        "question": "Before opening a suspicious URL from an email, which approach is best?",
        "options": [
            "Open it in a private window so it cannot harm your main browser",
            "Paste the URL into a scanner like VirusTotal to check reputation first",
            "Shorten the URL so it is easier to share with friends",
            "Bookmark it to check later when you have more time",
        ],
        "correct": 1,
        "explanation": "URL reputation scanners help identify phishing and malware hosts before you visit them.",
    },
    {
        "question": "Which detail most strongly suggests the hard-simulation email was a mass phishing attempt?",
        "options": [
            "The email includes an official-looking logo",
            "The greeting says “Dear User” instead of your name",
            "The message was received during business hours",
            "The email uses plain formatting without images",
        ],
        "correct": 1,
        "explanation": "Generic greetings are common when attackers send the same message to thousands of recipients.",
    },
    {
        "question": "After confirming a phishing email, what is the best response?",
        "options": [
            "Click the link once to see if the page loads",
            "Report it to IT/security and avoid interacting with the link",
            "Reply and ask the sender to confirm they are legitimate",
            "Delete it silently without telling anyone",
        ],
        "correct": 1,
        "explanation": "Reporting protects others and lets security teams block malicious domains. Deleting after reporting reduces accidental clicks.",
    },
]

PHISHING_EMAIL_EASY, PHISHING_EMAIL_HARD = _simulation_block(
    PHISHING_EMAIL_STEPS,
    indicators=[
        {
            "element": "sender_domain",
            "title": "Misspelled sender email address",
            "description": (
                "The display name looks official, but the actual email address contains a typo. "
                "Attackers hope you only glance at the name and miss small spelling mistakes in the address."
            ),
            "wrong_label": "What you see in this email",
            "wrong": "it-support@univeristy.up-edu.ph",
            "correct_label": "What a legitimate UP IT email looks like",
            "correct": (
                "Official messages use verified @up.edu.ph or @upd.edu.ph addresses with correct spelling — "
                "for example, helpdesk@upd.edu.ph — not misspelled domains like “univeristy.”"
            ),
            "tip": (
                "Also notice the sender name says “University of the philippines” with a lowercase “p.” "
                "Real institutions capitalize proper nouns consistently."
            ),
        },
        {
            "element": "urgent_subject",
            "title": "Urgent, pressure-filled subject line",
            "description": (
                "Phishing emails often create panic so you act before verifying. "
                "A countdown like “expire in 1 day(s)” pushes you to click without thinking."
            ),
            "wrong_label": "Suspicious subject in this email",
            "wrong": "Important: Your Password will expire in 1 day(s)",
            "correct_label": "How legitimate IT notices usually read",
            "correct": (
                "Real password reminders come through official portals or clearly branded messages "
                "without threatening immediate lockout. They rarely pressure you with same-day deadlines in email alone."
            ),
            "tip": "If a subject feels urgent, pause and verify through your university’s official website or IT helpdesk — not the email link.",
        },
        {
            "element": "generic_greeting",
            "title": "Generic greeting instead of your name",
            "description": (
                "Mass phishing campaigns send thousands of emails at once, so they use vague greetings "
                "instead of addressing you personally."
            ),
            "wrong_label": "What this email says",
            "wrong": "Dear network user,",
            "correct_label": "What you should expect",
            "correct": (
                "Official university IT mail usually addresses you by name or your assigned UP email username — "
                "for example, “Dear Juan Dela Cruz,” or “Dear jdela_cruz@up.edu.ph.”"
            ),
            "tip": "A generic greeting combined with other red flags is a strong sign the message was not meant specifically for you.",
        },
        {
            "element": "link_url",
            "title": "Suspicious link disguised as official",
            "description": (
                "The link text looks like a real UP domain, but the actual destination can be completely different. "
                "Never trust displayed link text alone — always inspect where it really leads."
            ),
            "wrong_label": "Link shown in this email",
            "wrong": "upd.edu.ph/password-renewal  →  actually goes to up-edu.philippines-renewal.net/login",
            "correct_label": "Safer way to update your password",
            "correct": (
                "Open your browser and type the official UP portal URL yourself (e.g. accounts.upd.edu.ph), "
                "or use a bookmark you saved earlier — never follow password links from unexpected emails."
            ),
            "tip": (
                "Before opening any suspicious URL, paste it into "
                "<a href=\"https://www.virustotal.com/gui/home/url\" target=\"_blank\" rel=\"noopener noreferrer\">VirusTotal</a> "
                "to scan the link for malware, phishing, and other threats — free and trusted by security teams worldwide."
            ),
        },
    ],
    signs=[
        {"id": "sender_domain", "label": "Spoofed sender domain"},
        {"id": "urgent_language", "label": "Urgent threatening language"},
        {"id": "link_url", "label": "Suspicious link URL"},
        {"id": "generic_greeting", "label": "Generic greeting instead of your name"},
        {"id": "grammar_error", "label": "Grammar or formatting error"},
    ],
)

RANSOMWARE_STEPS = [
    {
        "title": "Encrypted Files Alert",
        "narrative": "Your project folder files now have a strange extension. A note demands payment in Bitcoin within 48 hours.",
        "interface_type": "ransom",
        "interface": {
            "headline": "YOUR FILES HAVE BEEN ENCRYPTED",
            "message": "Pay 0.5 BTC to recover your documents. Timer: 47:59:12 remaining.",
            "files": ["report.docx.locked", "presentation.pptx.locked", "notes.pdf.locked"],
        },
        "choices": [
            _choice(
                "pay",
                "Pay the ransom immediately",
                "Payment was sent but files were not restored. Attackers often re-target paying victims.",
                "Paying encourages criminals and rarely guarantees full recovery.",
                0,
            ),
            _choice(
                "isolate",
                "Disconnect from the network and contact IT",
                "IT isolated the device, restored from backups, and blocked further spread.",
                "Isolation and professional response limit damage and preserve recoverable backups.",
                100,
                is_best=True,
            ),
            _choice(
                "wait",
                "Wait to see if files fix themselves",
                "Ransomware spread to shared drives while you waited.",
                "Delay allows ransomware to encrypt more systems. Act immediately.",
                10,
            ),
        ],
    },
]

RANSOMWARE_EASY, RANSOMWARE_HARD = _simulation_block(
    RANSOMWARE_STEPS,
    indicators=[
        {"element": "untrusted_source", "hint": "The file came from an unverified source."},
        {"element": "suspicious_extension", "hint": "Executable extensions disguised as documents are risky."},
        {"element": "no_publisher", "hint": "No verified publisher or digital signature was shown."},
    ],
    signs=[
        {"id": "untrusted_source", "label": "File from an unverified website"},
        {"id": "executable_disguise", "label": "Executable extension disguised as a document"},
        {"id": "no_signature", "label": "Missing digital signature or publisher verification"},
        {"id": "redirect_ads", "label": "Excessive ads and redirect prompts on download site"},
    ],
)

SPYWARE_STEPS = [
    {
        "title": "Free Screen Recorder Extension",
        "narrative": "A browser extension promises free HD screen recording but asks for access to all website data and clipboard content.",
        "interface_type": "extension",
        "interface": {
            "name": "UltraCapture Free",
            "permissions": ["Read all data on all websites", "Access clipboard", "Manage downloads"],
            "reviews": "Mixed — some users report account theft",
        },
        "choices": [
            _choice(
                "add",
                "Add extension with full permissions",
                "Spyware began logging passwords and session tokens from banking sites.",
                "Excessive permissions are a major spyware red flag.",
                0,
            ),
            _choice(
                "decline",
                "Decline and use a trusted official tool instead",
                "You avoided spyware and used a verified screen recorder from the official store.",
                "Minimal permissions and trusted publishers reduce spyware risk.",
                100,
                is_best=True,
            ),
            _choice(
                "limited",
                "Add it but never visit banking sites",
                "Spyware still captured credentials from email and school accounts.",
                "Spyware monitors broadly—not just banking sessions.",
                35,
            ),
        ],
    },
]

SPYWARE_EASY, SPYWARE_HARD = _simulation_block(
    SPYWARE_STEPS,
    indicators=[
        {"element": "background_process", "hint": "An unknown process is consuming resources."},
        {"element": "network_activity", "hint": "Data is being sent even when you are not browsing."},
        {"element": "unknown_app", "hint": "A recently installed unknown application appeared."},
    ],
    signs=[
        {"id": "unknown_process", "label": "Unknown process in task manager"},
        {"id": "network_activity", "label": "Background network activity while idle"},
        {"id": "unknown_app", "label": "Recently installed unknown application"},
        {"id": "performance_drop", "label": "Noticeable device slowdown during normal use"},
    ],
)

SOCIAL_ENGINEERING_STEPS = [
    {
        "title": "Urgent IT Support Call",
        "narrative": "Someone calling from an unknown number claims to be IT support. They say your account will be deleted in 10 minutes unless you read them your verification code.",
        "interface_type": "phone",
        "interface": {
            "caller": "Unknown Number",
            "script": "Hi, this is IT. We detected a breach on your account. Read me the 6-digit code we just sent you so we can secure it.",
        },
        "choices": [
            _choice(
                "code",
                "Read the verification code aloud",
                "The attacker used your code to reset your password and access your account.",
                "MFA codes should never be shared—legitimate IT will never ask for them.",
                0,
            ),
            _choice(
                "verify",
                "Hang up and call IT through the official helpdesk number",
                "Real IT confirmed there was no breach. The social engineering attempt was logged.",
                "Independent verification defeats impersonation attacks.",
                100,
                is_best=True,
            ),
            _choice(
                "partial",
                "Give them your username but not the code",
                "They used your username to trigger more targeted phishing against you.",
                "Even partial information helps attackers refine their approach.",
                40,
            ),
        ],
    },
]

SOCIAL_ENGINEERING_EASY, SOCIAL_ENGINEERING_HARD = _simulation_block(
    SOCIAL_ENGINEERING_STEPS,
    indicators=[
        {"element": "escalating_questions", "hint": "Questions are moving from general to personal."},
        {"element": "deflection", "hint": "The stranger avoids answering questions about themselves."},
        {"element": "recovery_info", "hint": "They are asking for information used in account recovery."},
    ],
    signs=[
        {"id": "escalating_questions", "label": "Questions escalating from general to personal"},
        {"id": "deflection", "label": "Stranger avoids answering personal questions"},
        {"id": "topic_steering", "label": "Conversation steered back to personal topics"},
        {"id": "recovery_info", "label": "Requests for account recovery information"},
    ],
)


SQL_INJECTION_STEPS = [
    {
        "title": "Admin Login Bypass",
        "narrative": (
            "You discovered a legacy admin login page for the UP Campus Portal. "
            "The form looks ordinary, but the backend may build SQL queries by stitching user input directly into the string."
        ),
        "interface_type": "login_form",
        "interface": {
            "app_name": "UP Campus Portal — Admin",
            "url_bar": "portal.upd.edu.ph/admin/login",
            "username_label": "Username",
            "password_label": "Password",
            "submit_label": "Sign in",
            "footer_note": "Restricted to authorized UP IT personnel only.",
            "vulnerable_query": (
                "SELECT * FROM users WHERE username = '{username}' "
                "AND password = '{password}' LIMIT 1"
            ),
            "valid_payload": "' OR '1'='1' --",
            "admin_dashboard": {
                "title": "Admin Dashboard",
                "welcome": "Welcome, administrator",
                "subtitle": "UP Campus Portal — elevated access granted",
                "stats": [
                    {"label": "Registered students", "value": "24,891"},
                    {"label": "Pending enrollments", "value": "312"},
                    {"label": "Last DB backup", "value": "Today, 02:00 AM"},
                ],
                "alert": (
                    "This dashboard is simulated. In a real breach, an attacker with admin access "
                    "could modify records, export data, or create backdoor accounts."
                ),
            },
        },
        "choices": [
            _choice(
                "bypass",
                "Bypass login with a crafted SQL payload",
                "Authentication was bypassed. You reached the admin dashboard without valid credentials.",
                "Unsanitized input let you close the username string and append OR '1'='1, making the WHERE clause always true.",
                100,
                is_best=True,
            ),
            _choice(
                "guess",
                "Keep guessing usernames and passwords",
                "Brute force is slow and may trigger lockouts without exploiting the underlying flaw.",
                "The vulnerability is in how input is handled, not weak passwords alone.",
                20,
            ),
        ],
    },
]

SQL_INJECTION_QUIZ = [
    {
        "question": "In the simulation, submitting a single quote into the username field caused a MySQL syntax error to appear. What does this tell you about the application?",
        "options": [
            "The server uses a strong password policy",
            "User input is being concatenated directly into a SQL query without sanitization",
            "The database is running in read-only mode",
            "The login form uses multi-factor authentication",
        ],
        "correct": 1,
        "explanation": "A SQL syntax error in response to a single quote is a clear sign that user input is being stitched directly into the query string. This allows an attacker to break out of the intended SQL structure.",
    },
    {
        "question": "The simulation's URL bar contained parameters like `engine=mysql&query=1&legacy=1`. Why is this a red flag for SQL injection risk?",
        "options": [
            "It confirms HTTPS is disabled on the page",
            "It reveals that the login page was built recently",
            "It suggests the backend uses raw SQL query construction with no abstraction layer",
            "It means the server is running an outdated operating system",
        ],
        "correct": 2,
        "explanation": "Parameters like engine=mysql and legacy=1 hint that SQL is being built directly from user input rather than through a safe ORM or prepared statement layer — a strong indicator of injection risk.",
    },
    {
        "question": "You used `' OR '1'='1' --` to bypass the login. Why did the double dash (--) at the end matter?",
        "options": [
            "It signals the end of an HTML comment in the page",
            "It tells the browser to stop loading the page",
            "It starts a SQL comment, discarding the password check that follows",
            "It triggers an automatic database backup",
        ],
        "correct": 2,
        "explanation": "-- is a SQL comment delimiter. Everything after it is ignored by the database engine, including the password validation clause — so the query succeeds with any or no password.",
    },
    {
        "question": "The login form in the simulation had a legacy notice stating CAPTCHA and input filtering were disabled. Which fix would actually prevent SQL injection?",
        "options": [
            "Re-enabling CAPTCHA on the login page",
            "Hiding the SQL error messages from users",
            "Replacing string-concatenated queries with parameterized queries and bound parameters",
            "Adding a rate limiter that blocks more than 5 login attempts",
        ],
        "correct": 2,
        "explanation": "CAPTCHA, rate limiting, and hiding errors reduce visibility and brute force risk but do not fix the root cause. Parameterized queries — which bind user input as data, never as executable SQL — are the correct fix.",
    },
    {
        "question": "After bypassing the admin login in the simulation, an admin dashboard was revealed with student records and enrollment data. As a developer, what is the most important lesson here?",
        "options": [
            "Admin dashboards should always display a warning banner",
            "Student records should be stored in a separate country",
            "Any unsanitized input field that feeds into a SQL query can become an entry point to the entire database",
            "Login pages should require a username of at least 12 characters",
        ],
        "correct": 2,
        "explanation": "SQL injection can expose far more than one user's data. A single vulnerable input field can give an attacker access to the whole database — including records, credentials, and admin functions they were never authorized to see.",
    },
]

SQL_INJECTION_EASY, SQL_INJECTION_HARD = _simulation_block(
    SQL_INJECTION_STEPS,
    indicators=[
        {
            "element": "unsanitized_input",
            "title": "No input sanitization on username",
            "description": (
                "The username field accepts quotes, spaces, and SQL keywords without filtering. "
                "That means your input may be copied directly into a database query instead of being treated as plain text."
            ),
            "wrong_label": "What this vulnerable form allows",
            "wrong": "Username accepts: ' OR '1'='1' -- with no warnings or blocks",
            "correct_label": "What secure applications do",
            "correct": (
                "Inputs are validated, escaped, or passed through parameterized queries so special characters "
                "cannot alter the SQL statement structure."
            ),
            "tip": "As a user, you cannot fix this — but recognizing unsanitized fields helps you report risky apps to developers.",
        },
        {
            "element": "string_concat",
            "title": "Query built by string concatenation",
            "description": (
                "The preview below shows how the server likely builds the login query: your username and password "
                "are inserted inside single quotes in the SQL string. Any quote you type can break out of that string."
            ),
            "wrong_label": "Vulnerable query pattern",
            "wrong": "SELECT * FROM users WHERE username = '{your input}' AND password = '{password}'",
            "correct_label": "Safer pattern",
            "correct": (
                "SELECT * FROM users WHERE username = ? AND password = ? "
                "with bound parameters so user input never becomes executable SQL."
            ),
            "tip": "If you ever see error messages mentioning SELECT, syntax near quotes, or table names, treat the form as high risk.",
        },
        {
            "element": "or_always_true",
            "title": "OR '1'='1 makes the check always pass",
            "description": (
                "After closing the username string with a quote, adding OR '1'='1 creates a condition that is "
                "always true. The database returns rows even when your password is wrong."
            ),
            "wrong_label": "Injected logic",
            "wrong": "... WHERE username = '' OR '1'='1' AND password = 'anything'",
            "correct_label": "Why it works",
            "correct": (
                "Because '1'='1' is always true, the WHERE clause succeeds and the application thinks "
                "a valid user was found."
            ),
            "tip": "Click the guided payload chips below to assemble this segment, or type it yourself in the username field.",
        },
        {
            "element": "sql_comment",
            "title": "SQL comment (--) disables the rest of the query",
            "description": (
                "Two dashes start a SQL comment. Everything after them — including the password check — "
                "is ignored by the database engine."
            ),
            "wrong_label": "With comment at the end",
            "wrong": "... OR '1'='1' -- AND password = 'wrong'",
            "correct_label": "What the database executes",
            "correct": "... OR '1'='1'   (password portion commented out and never evaluated)",
            "tip": "Different databases use different comment syntax; -- is common in MySQL, PostgreSQL, and others.",
        },
    ],
    signs=[
        {"id": "no_sanitization", "label": "No visible input sanitization or character limits"},
        {"id": "error_leak", "label": "Single quote triggers SQL syntax error messages"},
        {"id": "url_hint", "label": "URL structure hints at direct database query usage"},
        {"id": "special_chars", "label": "Form accepts special characters without filtering"},
        {"id": "bypass_success", "label": "Successful authentication bypass via crafted input"},
    ],
)


def _placeholder_module(
    attack_id: str,
    name: str,
    icon: str,
    difficulty: str,
    short_description: str,
    category: str,
    category_label: str,
    image: str = "",
) -> dict[str, Any]:
    overview = _placeholder_overview(name)
    steps = [
        {
            "title": f"{name} scenario",
            "narrative": f"Placeholder {name} simulation scenario.",
            "interface_type": "generic",
            "interface": {"label": attack_id},
            "choices": [
                _choice(
                    "secure",
                    "Apply the secure response",
                    "Placeholder secure outcome.",
                    "Placeholder secure explanation.",
                    100,
                    is_best=True,
                ),
                _choice(
                    "risky",
                    "Take the risky action",
                    "Placeholder risky outcome.",
                    "Placeholder risky explanation.",
                    0,
                ),
            ],
        },
    ]
    easy, hard = _simulation_block(
        steps,
        indicators=[{"element": "placeholder_indicator", "hint": "Placeholder guided hint."}],
        signs=[{"id": "placeholder_sign", "label": "Placeholder sign to identify."}],
    )
    return {
        "id": attack_id,
        "name": name,
        "icon": icon,
        "image": image,
        "difficulty": difficulty,
        "short_description": short_description,
        "category": category,
        "category_label": category_label,
        "overview": overview,
        "easy_simulation": easy,
        "hard_simulation": hard,
        "quiz": _placeholder_quiz(name),
    }


ATTACKS: dict[str, dict[str, Any]] = {
    "phishing_fake_email": {
        "id": "phishing_fake_email",
        "name": "Phishing: Fake Email",
        "icon": "🎣",
        "image": "img/modules/phishing/module_phishing.jpg",
        "difficulty": "Beginner",
        "short_description": "Learn to spot fake emails and messages designed to steal your credentials.",
        "category": "social_based",
        "category_label": "Social-Based Attacks",
        "overview": {
            "explanation": (
                "Phishing is a cyber attack where attackers impersonate trusted organizations or individuals "
                "to trick users into revealing sensitive information such as passwords, financial details, or personal data."
            ),
            "why_used": "Attackers use phishing because it is cheap, scalable, and exploits human trust rather than technical flaws.",
            "how_encountered": "You may encounter phishing through email, SMS, social media messages, or fake login pages.",
            "how_it_happens": [
                "Attacker creates a fake message or email that looks legitimate.",
                "Victim receives the suspicious communication.",
                "Victim clicks a malicious link or provides sensitive information.",
                "Attacker gains access to accounts, money, or personal data.",
            ],
            "warning_signs": [
                "Suspicious or shortened links",
                "Urgent language demanding immediate action",
                "Unknown or spoofed senders",
                "Requests for passwords or personal information",
                "Fake websites with slightly wrong URLs",
            ],
            "prevention_tips": [
                "Verify links before clicking by hovering or checking the domain",
                "Enable multi-factor authentication on important accounts",
                "Never share passwords through email or chat",
                "Check sender identity through official channels",
            ],
        },
        "easy_simulation": PHISHING_EMAIL_EASY,
        "hard_simulation": PHISHING_EMAIL_HARD,
        "quiz": PHISHING_EMAIL_QUIZ,
        "info_page": {
            "spotlight": [
                {
                    "key": "about",
                    "heading": "About",
                    "text": (
                        "Phishing is a cyber attack where attackers impersonate trusted organizations or individuals "
                        "to trick users into revealing sensitive information such as passwords, financial details, or personal data."
                    ),
                },
                {
                    "key": "origin",
                    "heading": "Origin",
                    "text": (
                        "Attackers use phishing because it is cheap, scalable, and exploits human trust rather than technical flaws. "
                        "It often starts with a forged message, followed by a fake login page designed to harvest credentials."
                    ),
                },
                {
                    "key": "real_world",
                    "heading": "Example in Real World",
                    "text": (
                        "You may encounter phishing through email, SMS, social media messages, or fake login pages. "
                        "A common scenario is an urgent bank alert email that pushes you to verify your account through a suspicious link."
                    ),
                },
            ],
            "real_world_examples": [
                "Fake bank security alerts demanding immediate verification",
                "HR payroll messages with malicious attachment links",
                "Shipping notifications with look-alike tracking URLs",
            ],
        },
    },
    "phishing_fake_website": _placeholder_module(
        "phishing_fake_website",
        "Phishing: Fake Website",
        "🌐",
        "Beginner",
        "Learn to identify cloned login pages and suspicious URLs before entering credentials.",
        "social_based",
        "Social-Based Attacks",
        image="img/modules/phishing-website/module_phishing_website.jpg",
    ),
    "social_engineering": {
        "id": "social_engineering",
        "name": "Social Engineering",
        "icon": "🎭",
        "image": "img/modules/social-engineering/module_social.jpg",
        "difficulty": "Intermediate",
        "short_description": "Practice responding to manipulative tactics that exploit trust and urgency.",
        "category": "social_based",
        "category_label": "Social-Based Attacks",
        "overview": {
            "explanation": "Social engineering manipulates people into revealing information or taking unsafe actions through psychology rather than hacking alone.",
            "why_used": "Humans are often the weakest link—urgency, authority, and fear bypass technical controls.",
            "how_encountered": "Phone calls, impersonation, tailgating, fake IT support, and urgent messages.",
            "how_it_happens": [
                "Attacker researches the target or organization.",
                "They impersonate someone trusted.",
                "They create urgency or fear to rush decisions.",
                "Victim shares credentials or access.",
            ],
            "warning_signs": [
                "Unusual urgency or secrecy requests",
                "Callers refusing to verify identity",
                "Requests to bypass normal procedures",
                "Pressure to share OTP codes",
            ],
            "prevention_tips": [
                "Verify identity through official channels",
                "Follow established security procedures",
                "Never share MFA codes with anyone",
                "Report suspicious contact attempts",
            ],
        },
        "easy_simulation": SOCIAL_ENGINEERING_EASY,
        "hard_simulation": SOCIAL_ENGINEERING_HARD,
        "quiz": [
            {
                "question": "Social engineering primarily targets:",
                "options": ["Hardware cooling systems", "Human psychology and trust", "Fiber optic cables", "Power supply units"],
                "correct": 1,
                "explanation": "Social engineering exploits human behavior rather than software bugs alone.",
            },
        ],
    },
    "keylogger": _placeholder_module(
        "keylogger",
        "Keylogger",
        "⌨️",
        "Intermediate",
        "Understand how keyloggers capture keystrokes and how to spot them before typing sensitive data.",
        "malware_based",
        "Malware-Based Attacks",
        image="img/modules/keylogger/module_keylogger.jpg",
    ),
    "ransomware": {
        "id": "ransomware",
        "name": "Ransomware",
        "icon": "🔒",
        "image": "img/modules/ransomware/module_ransomware.jpg",
        "difficulty": "Intermediate",
        "short_description": "Experience how attackers encrypt files and demand payment to restore access.",
        "category": "malware_based",
        "category_label": "Malware-Based Attacks",
        "overview": {
            "explanation": "Ransomware encrypts your files or locks your system, then demands payment—often in cryptocurrency—to restore access.",
            "why_used": "Attackers profit directly by extorting victims who need their files back urgently.",
            "how_encountered": "Ransomware spreads through phishing emails, exposed remote access, or unpatched software.",
            "how_it_happens": [
                "Malware gains access to the system.",
                "It encrypts files across drives and network shares.",
                "A ransom note appears with payment instructions.",
                "Victims face data loss if backups are unavailable.",
            ],
            "warning_signs": [
                "Unexpected file extension changes",
                "Ransom notes on desktop or in folders",
                "Inability to open documents",
                "Mass antivirus alerts",
                "Demands for cryptocurrency payment",
            ],
            "prevention_tips": [
                "Maintain regular offline backups",
                "Patch systems promptly",
                "Limit user permissions",
                "Never pay ransoms without consulting IT—payment does not guarantee recovery",
            ],
        },
        "easy_simulation": RANSOMWARE_EASY,
        "hard_simulation": RANSOMWARE_HARD,
        "quiz": [
            {
                "question": "What does ransomware primarily do?",
                "options": ["Speeds up your computer", "Encrypts files and demands payment", "Improves file compression", "Updates your antivirus"],
                "correct": 1,
                "explanation": "Ransomware holds data hostage by encryption until a ransom is paid.",
            },
            {
                "question": "Best defense against ransomware data loss?",
                "options": ["Regular tested backups", "Stronger passwords only", "Disabling firewalls", "Paying quickly every time"],
                "correct": 0,
                "explanation": "Reliable backups let organizations recover without paying criminals.",
            },
        ],
    },
    "spyware": {
        "id": "spyware",
        "name": "Spyware",
        "icon": "👁️",
        "image": "img/modules/spyware/module_spyware.jpg",
        "difficulty": "Intermediate",
        "short_description": "See how hidden software monitors activity and steals private information.",
        "category": "malware_based",
        "category_label": "Malware-Based Attacks",
        "overview": {
            "explanation": "Spyware secretly monitors user activity, capturing keystrokes, screenshots, browsing history, and credentials.",
            "why_used": "Attackers harvest personal and financial data for fraud or resale.",
            "how_encountered": "Bundled with free software, malicious browser extensions, or compromised downloads.",
            "how_it_happens": [
                "Spyware installs alongside another program.",
                "It runs silently in the background.",
                "It logs sensitive input and sends data to attackers.",
                "Victims discover fraud or privacy breaches later.",
            ],
            "warning_signs": [
                "Battery drain or sluggish performance",
                "Unknown browser extensions",
                "Unexpected webcam or microphone activity",
                "Unexplained account logins from new locations",
            ],
            "prevention_tips": [
                "Review installed browser extensions regularly",
                "Use reputable security software",
                "Cover cameras when not in use and audit app permissions",
                "Avoid suspicious free toolbars and utilities",
            ],
        },
        "easy_simulation": SPYWARE_EASY,
        "hard_simulation": SPYWARE_HARD,
        "quiz": [
            {
                "question": "What is spyware designed to do?",
                "options": ["Improve graphics performance", "Secretly monitor and collect user data", "Encrypt files for backup", "Block all internet ads"],
                "correct": 1,
                "explanation": "Spyware operates covertly to capture sensitive information.",
            },
        ],
    },
    "adware_malvertising": _placeholder_module(
        "adware_malvertising",
        "Adware / Malvertising",
        "📢",
        "Beginner",
        "Recognize malicious ads, fake prize popups, and automatic downloads on risky websites.",
        "malware_based",
        "Malware-Based Attacks",
        image="img/modules/adware/module_adware.jpg",
    ),
    "mitm": _placeholder_module(
        "mitm",
        "Man-in-the-Middle (MITM)",
        "🔀",
        "Advanced",
        "Learn how attackers intercept network traffic on unsecured connections.",
        "network_based",
        "Network-Based Attacks",
        image="img/modules/mitm/module_mitm.jpg",
    ),
    "evil_twin": _placeholder_module(
        "evil_twin",
        "Evil Twin / Rogue WiFi",
        "📶",
        "Intermediate",
        "Identify rogue WiFi networks that mimic legitimate public hotspots.",
        "network_based",
        "Network-Based Attacks",
        image="img/modules/evil-twin/module_eviltwin.png",
    ),
    "sql_injection": {
        "id": "sql_injection",
        "name": "SQL Injection",
        "icon": "💉",
        "image": "img/modules/sql-injection/module_sql-injection.jpg",
        "difficulty": "Advanced",
        "short_description": "Understand how unsanitized input fields can be exploited to bypass authentication.",
        "category": "injection_based",
        "category_label": "Injection-Based Attacks",
        "overview": {
            "explanation": (
                "SQL injection is an attack where malicious SQL code is inserted into input fields "
                "that an application sends to a database. If the app builds queries by concatenating "
                "user input, attackers can alter the query logic."
            ),
            "why_used": (
                "Login bypass and data theft through SQL injection remain common because many legacy "
                "applications still trust user input instead of using parameterized queries."
            ),
            "how_encountered": (
                "You may encounter SQL injection risks in login forms, search boxes, URL parameters, "
                "and any field that appears to query a database behind the scenes."
            ),
            "how_it_happens": [
                "Application builds a SQL query using raw user input.",
                "Attacker submits crafted input containing quotes and SQL keywords.",
                "The modified query executes in the database.",
                "Attacker bypasses authentication or extracts sensitive data.",
            ],
            "warning_signs": [
                "Login forms that accept quotes and SQL-like text without errors",
                "Database error messages shown to users",
                "URLs with query parameters that change page content",
                "Search boxes returning unexpected database records",
            ],
            "prevention_tips": [
                "Developers should use parameterized queries and ORM bindings",
                "Validate and allow-list expected input formats",
                "Never expose raw database errors to end users",
                "Apply least-privilege database accounts for application connections",
            ],
        },
        "easy_simulation": SQL_INJECTION_EASY,
        "hard_simulation": SQL_INJECTION_HARD,
        "quiz": SQL_INJECTION_QUIZ,
        "info_page": {
            "media": {
                "folder": "sql-injection",
                "spotlight": [
                    "image1_sql.png",
                    "image2_sql.png",
                    "image3_sql.jpg",
                ],
                "video_poster": "video-poster.svg",
            },
            "spotlight": [
                {
                    "key": "about",
                    "heading": "About",
                    "text": (
                        "SQL injection exploits applications that pass user input directly into database queries. "
                        "Instead of typing a normal username, an attacker inserts SQL fragments that change what the query does."
                    ),
                },
                {
                    "key": "query",
                    "heading": "Normal vs injected query",
                    "text": (
                        "A safe login might run: SELECT * FROM users WHERE username = ? AND password = ?. "
                        "A vulnerable app might stitch input into quotes — letting an attacker close the string "
                        "and append OR '1'='1 to bypass the password check."
                    ),
                },
                {
                    "key": "real_world",
                    "heading": "Example in real world",
                    "text": (
                        "Attackers have used SQL injection to bypass admin logins, dump customer records, "
                        "and modify database contents. It affects both developers who write insecure code "
                        "and users who trust compromised applications."
                    ),
                },
            ],
            "real_world_examples": [
                "Login bypass on admin panels using `' OR '1'='1` payloads",
                "Search boxes used to extract usernames and password hashes",
                "E-commerce sites compromised through unsanitized order lookup fields",
            ],
        },
    },
}


def get_all_attacks() -> list[dict[str, Any]]:
    return list(ATTACKS.values())


def get_attack(attack_id: str) -> dict[str, Any] | None:
    return ATTACKS.get(attack_id)


def _simulation_step_count(attack: dict[str, Any]) -> int:
    hard = attack.get("hard_simulation", {})
    if isinstance(hard, dict) and hard.get("steps"):
        return len(hard["steps"])
    return len(attack.get("steps", []))


def list_attack_summaries() -> list[dict[str, Any]]:
    return [
        {
            "id": attack["id"],
            "name": attack["name"],
            "icon": attack["icon"],
            "difficulty": attack["difficulty"],
            "short_description": attack["short_description"],
            "category": attack.get("category", ""),
            "category_label": attack.get("category_label", ""),
            "step_count": _simulation_step_count(attack),
            "quiz_count": len(attack["quiz"]),
        }
        for attack in ATTACKS.values()
    ]
