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

PHISHING_WEBSITE_STEPS = [
    {
        "title": "Fake Portal Verification",
        "narrative": (
            "You receive a message telling you to verify your account on a campus portal. The link opens a login page that looks official, but you need to check the URL and the page behavior carefully before entering anything."
        ),
        "interface_type": "email",
        "interface": {
            "from_name": "UP Portal Security",
            "from": "security@up-portal-verify.net",
            "subject": "Action Required: Verify your campus portal access",
            "greeting": "Dear student,",
            "body": "Your campus account must be verified immediately to avoid service interruption. Click the link below to open the portal and log in.",
            "signoff": "Regards,\nUP Portal Support",
            "highlight": "up-portal-verify.net/login",
            "link_actual": "https://up-portal-verify.net/login",
            "footer_label": "University Portal Access",
        },
        "choices": [
            _choice(
                "open",
                "Open the link and log in immediately",
                "You entered credentials into a fake portal and handed them to the attacker.",
                "Cloned login pages are designed to harvest usernames and passwords.",
                0,
            ),
            _choice(
                "verify",
                "Verify the portal through the official university website",
                "You avoided the fake portal and confirmed the real website through a trusted source.",
                "The safest response is to navigate to the official site yourself instead of trusting the email link.",
                100,
                is_best=True,
            ),
            _choice(
                "reply",
                "Reply and ask the sender to confirm",
                "The attacker received more information and could continue the scam.",
                "Never use the suspicious email thread to verify identity.",
                40,
            ),
        ],
    }
]

PHISHING_WEBSITE_QUIZ = [
    {
        "question": "What is the safest way to verify a portal verification email?",
        "options": [
            "Click the link in the email and sign in",
            "Open the official website yourself and check notices there",
            "Reply to the sender asking if the link is real",
            "Forward the message to everyone in your class",
        ],
        "correct": 1,
        "explanation": "Typing the official website yourself or using a trusted bookmark avoids cloned login pages.",
    },
    {
        "question": "Which detail most strongly suggests a fake website?",
        "options": [
            "A page that uses the school logo",
            "A domain name with extra words like verify or security",
            "A login page that asks for your username",
            "A page that loads quickly",
        ],
        "correct": 1,
        "explanation": "Attackers often register look-alike domains that sound official but are not the real university site.",
    },
]

PHISHING_WEBSITE_EASY, PHISHING_WEBSITE_HARD = _simulation_block(
    PHISHING_WEBSITE_STEPS,
    indicators=[
        {
            "element": "sender_domain",
            "title": "Look-alike sender domain",
            "description": "The sender uses a domain that looks official at first glance but is not the real campus domain.",
            "wrong": "security@up-portal-verify.net",
            "correct": "Official university notices should come from a trusted university domain you already know.",
        },
        {
            "element": "urgent_subject",
            "title": "Urgent subject line",
            "description": "The message pushes you to act immediately before you have time to verify the website.",
            "wrong": "Action Required: Verify your campus portal access",
            "correct": "Legitimate notices do not pressure you into clicking a link without verification.",
        },
        {
            "element": "link_url",
            "title": "Suspicious login URL",
            "description": "The link points to a look-alike portal that is not the official university site.",
            "wrong": "https://up-portal-verify.net/login",
            "correct": "Always open the portal through the official university homepage or a trusted bookmark.",
        },
        {
            "element": "generic_greeting",
            "title": "Generic greeting",
            "description": "The email does not address you by name, which is common in bulk phishing campaigns.",
            "wrong": "Dear student,",
            "correct": "Personalized messages should match your actual account details and official records.",
        },
    ],
    signs=[
        {"id": "lookalike_domain", "label": "Look-alike sender domain"},
        {"id": "urgent_language", "label": "Urgent language"},
        {"id": "suspicious_url", "label": "Suspicious login URL"},
        {"id": "generic_greeting", "label": "Generic greeting"},
    ],
)

KEYLOGGER_STEPS = [
    {
        "title": "Keyboard Helper Installer",
        "narrative": "A free keyboard utility promises faster typing and asks for full access to capture keystrokes for 'productivity analytics'.",
        "interface_type": "popup",
        "interface": {
            "title": "Enable Keyboard Assistant",
            "body": "This tool needs access to all key presses so it can provide shortcuts, auto-fill, and productivity analytics.",
            "publisher": "QuickKeys Studio",
            "cta": "Allow keyboard access",
            "url": "https://quickkeys-helper.example/install",
        },
        "choices": [
            _choice(
                "allow",
                "Allow the keyboard access request",
                "The utility could record every keystroke, including passwords and private messages.",
                "Full keyboard access is a classic keylogger warning sign.",
                0,
            ),
            _choice(
                "deny",
                "Deny the request and uninstall the utility",
                "You blocked a potentially malicious tool before it could capture your input.",
                "Unknown utilities should never receive full keyboard permissions without a clear, trusted need.",
                100,
                is_best=True,
            ),
            _choice(
                "later",
                "Click allow later and keep using it",
                "The program continued running and could still monitor your typing.",
                "Delaying the decision does not remove the risk.",
                25,
            ),
        ],
    }
]

KEYLOGGER_QUIZ = [
    {
        "question": "What is the strongest sign that an app may be a keylogger?",
        "options": [
            "It has a dark theme",
            "It requests full keyboard access or keystroke monitoring",
            "It opens quickly",
            "It shows a logo on the installer",
        ],
        "correct": 1,
        "explanation": "Keyloggers need access to your keystrokes, so permission prompts are a major red flag.",
    },
    {
        "question": "What should you do before installing an unknown keyboard utility?",
        "options": [
            "Allow full access first so you can test it",
            "Verify the publisher and install only from a trusted source",
            "Use it once and remove it later",
            "Share your password to check whether it logs correctly",
        ],
        "correct": 1,
        "explanation": "Trusted publishers and official download sources reduce the chance of installing a keylogger.",
    },
]

KEYLOGGER_EASY, KEYLOGGER_HARD = _simulation_block(
    KEYLOGGER_STEPS,
    indicators=[
        {
            "element": "publisher",
            "title": "Unknown publisher",
            "description": "The tool comes from a publisher you do not recognize.",
            "wrong": "QuickKeys Studio",
            "correct": "Only install software from publishers you trust and can verify.",
        },
        {
            "element": "access_request",
            "title": "Full keyboard access request",
            "description": "The app wants permission to capture keystrokes, which is unnecessary for most legitimate utilities.",
            "wrong": "Allow keyboard access",
            "correct": "Legitimate tools should request only the minimum permissions they need.",
        },
        {
            "element": "source_url",
            "title": "Suspicious download source",
            "description": "The download page is not the official vendor site.",
            "wrong": "https://quickkeys-helper.example/install",
            "correct": "Use an official store or the vendor's verified site instead of a look-alike domain.",
        },
    ],
    signs=[
        {"id": "unknown_publisher", "label": "Unknown publisher"},
        {"id": "full_keyboard_access", "label": "Full keyboard access request"},
        {"id": "lookalike_site", "label": "Look-alike download site"},
    ],
)

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
        {
            "element": "ransom_headline",
            "title": "Threatening ransom headline",
            "description": "The screen uses alarming language to pressure you into paying immediately.",
            "wrong": "YOUR FILES HAVE BEEN ENCRYPTED",
            "correct": "Legitimate system notices do not threaten you with file encryption.",
        },
        {
            "element": "payment_demand",
            "title": "Cryptocurrency payment demand",
            "description": "Attackers demand payment in Bitcoin or other cryptocurrency to restore access.",
            "wrong": "Pay 0.5 BTC to recover your documents",
            "correct": "Never pay ransoms without consulting IT. Payment does not guarantee recovery.",
        },
        {
            "element": "timer_pressure",
            "title": "Countdown timer pressure",
            "description": "A ticking timer is used to rush you into paying before you can get help.",
            "wrong": "Timer: 47:59:12 remaining",
            "correct": "Urgent countdowns are a common ransomware tactic to prevent calm incident response.",
        },
        {
            "element": "file_encryption",
            "title": "Changed file extensions",
            "description": "Your documents now have strange extensions like .locked, meaning they were encrypted.",
            "wrong": "report.docx.locked, presentation.pptx.locked",
            "correct": "Sudden mass file extension changes are a strong sign of active ransomware.",
        },
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
        {
            "element": "unknown_publisher",
            "title": "Unknown extension publisher",
            "description": "The extension comes from a publisher you do not recognize or cannot verify.",
            "wrong": "UltraCapture Free",
            "correct": "Install extensions only from trusted publishers in the official browser store.",
        },
        {
            "element": "excessive_permissions",
            "title": "Excessive permission requests",
            "description": "The extension wants access to all websites, clipboard, and downloads — far more than it needs.",
            "wrong": "Read all data on all websites, Access clipboard, Manage downloads",
            "correct": "Legitimate tools request only the minimum permissions required for their function.",
        },
        {
            "element": "negative_reviews",
            "title": "Suspicious user reviews",
            "description": "Other users report account theft or suspicious behavior after installing this extension.",
            "wrong": "Mixed — some users report account theft",
            "correct": "Check reviews and reports before granting broad access to your browser data.",
        },
        {
            "element": "broad_access",
            "title": "Full permission install prompt",
            "description": "The install button asks you to grant all permissions at once without a limited option.",
            "wrong": "Add extension with full permissions",
            "correct": "Decline extensions that require sweeping access to sensitive data.",
        },
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
        "title": "Suspicious IT Support Call",
        "narrative": "You receive a phone call. The caller ID displays 'TUP-T IT Helpdesk'. The caller knows your name and claims there is suspicious activity on your account.",
        "interface_type": "phone_call",
        "interface": {
            "caller_id": "TUP-T IT Helpdesk",
            "caller_number": "+63 2 5310-0000",
            "connected_label": "Connected",
            "transcript": [
                {
                    "speaker": "caller",
                    "text": "Hello, is this a TUP-T student? This is Mark from the TUP-T IT Security Office.",
                    "flag_id": None,
                },
                {
                    "speaker": "caller",
                    "text": "We've detected some suspicious login activity on your TUP-T Portal account. For your security, I need to verify your identity right now.",
                    "flag_id": "urgency",
                },
                {
                    "speaker": "caller",
                    "text": "I can see here your student number is 2021-12345 — correct? We just need to confirm a few more details.",
                    "flag_id": "personal_info_bait",
                },
                {
                    "speaker": "caller",
                    "text": "We just sent a 6-digit verification code to your registered mobile number. Can you read that code to me so I can secure your account?",
                    "flag_id": "otp_request",
                },
                {
                    "speaker": "caller",
                    "text": "Please hurry — if I don't receive the code within the next 5 minutes, your account will be automatically suspended.",
                    "flag_id": "urgency_deadline",
                },
            ],
        },
        "choices": [
            _choice(
                "read_otp",
                "Read the OTP code to the caller",
                "The attacker used your code to access your account, change your password, and lock you out.",
                "Legitimate IT staff will never ask for a one-time password over the phone. OTPs are your second factor — sharing them voids that protection entirely.",
                0,
            ),
            _choice(
                "hang_up_verify",
                "Hang up and call the official TUP-T helpdesk number yourself",
                "You independently verified there was no breach. The social engineering attempt was logged and reported.",
                "Hanging up and calling through an official number you look up yourself is the only way to confirm you are actually talking to IT — not an impersonator.",
                100,
                is_best=True,
            ),
            _choice(
                "give_student_id",
                "Confirm your student number but refuse to share the OTP",
                "The attacker used your confirmed student number to craft more targeted attacks against your other accounts.",
                "Even seemingly harmless information like a student number helps attackers build a profile and launch more convincing follow-up attacks.",
                35,
            ),
        ],
    },
]

SOCIAL_ENGINEERING_EASY, SOCIAL_ENGINEERING_HARD = _simulation_block(
    SOCIAL_ENGINEERING_STEPS,
    indicators=[
        {
            "element": "spoofed_caller_id",
            "title": "Caller ID can be spoofed",
            "description": (
                "The phone displays 'TUP-T IT Helpdesk' but caller ID is trivially easy to fake. "
                "Anyone with a basic VoIP service can display any name or number they choose. "
                "Seeing a familiar name on your screen is not proof the call is legitimate."
            ),
            "wrong_label": "What you see on your screen",
            "wrong": "TUP-T IT Helpdesk — +63 2 5310-0000",
            "correct_label": "What this actually proves",
            "correct": (
                "Absolutely nothing. Caller ID only shows what the caller chose to display. "
                "Real IT verification happens when you hang up and call the official number yourself."
            ),
            "tip": "Never trust a caller based on what their number looks like. Always call back through a number you find independently.",
        },
        {
            "element": "personal_info_bait",
            "title": "Using your personal details to seem legitimate",
            "description": (
                "The caller already knows your name and student number. This feels convincing — "
                "but attackers collect this information from social media, leaked databases, and public directories. "
                "Knowing your details does not mean they are who they claim to be."
            ),
            "wrong_label": "What the caller said",
            "wrong": "I can see here your student number is 2021-12345 — correct?",
            "correct_label": "Why this is a manipulation tactic",
            "correct": (
                "Showing they know basic details builds false trust and makes you feel verified. "
                "Legitimate IT staff confirm their own identity to you — not yours to them."
            ),
            "tip": "Ask the caller for their employee ID and extension, then call the main helpdesk to confirm those details before continuing.",
        },
        {
            "element": "otp_request",
            "title": "Asking for your one-time password (OTP)",
            "description": (
                "No legitimate IT department, bank, university, or organization will ever ask you "
                "to read a verification code over the phone. OTP codes are specifically designed "
                "so that only you use them — sharing one is equivalent to handing someone your key."
            ),
            "wrong_label": "What the caller asked",
            "wrong": "Can you read that 6-digit verification code to me so I can secure your account?",
            "correct_label": "What legitimate IT actually does",
            "correct": (
                "Real IT can verify your identity through their own internal systems. "
                "They never need a code sent to your phone — that code exists purely for you to use, not to share."
            ),
            "tip": "If anyone — even someone claiming to be from IT — asks for an OTP, hang up immediately. This is the clearest possible sign of a scam.",
        },
        {
            "element": "urgency_deadline",
            "title": "Artificial urgency and countdown threat",
            "description": (
                "Saying 'your account will be suspended in 5 minutes' is designed to make you panic and act "
                "without thinking. Urgency is one of social engineering's most effective tools — it bypasses "
                "critical thinking and pushes victims into rash decisions."
            ),
            "wrong_label": "The pressure tactic used",
            "wrong": "If I don't receive the code within 5 minutes, your account will be automatically suspended.",
            "correct_label": "How real security alerts work",
            "correct": (
                "Genuine account security alerts give you time to verify through official channels. "
                "They do not demand immediate action over a phone call or threaten instant consequences."
            ),
            "tip": "Whenever someone on the phone creates extreme time pressure, treat it as a red flag. Legitimate requests can wait the 60 seconds it takes to hang up and call back.",
        },
    ],
    signs=[
        {"id": "spoofed_caller_id", "label": "Caller ID could be spoofed"},
        {"id": "urgency", "label": "Artificial urgency and time pressure"},
        {"id": "personal_info_bait", "label": "Uses personal info to build false trust"},
        {"id": "otp_request", "label": "Requests a one-time password or verification code"},
        {"id": "authority_pressure", "label": "Claims authority to pressure immediate compliance"},
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


ADWARE_POP_UP_STEPS = [
    {
        "title": "Suspicious browser installer popup",
        "narrative": "A pop-up offers a free system cleaner and urges you to install it immediately.",
        "interface_type": "popup",
        "interface": {
            "title": "Your browser is infected!",
            "body": "Your browser is running slowly. Install the recommended cleaner now to speed it up.",
            "publisher": "UltraBoost Software",
            "cta": "Install now",
            "url": "https://cleaner-boost.example/install",
        },
        "choices": [
            _choice(
                "install",
                "Install the recommended cleaner",
                "You installed an unwanted program that keeps showing ads and slows down the browser.",
                "The installer uses scare tactics and a suspicious publisher to push software you do not need.",
                0,
            ),
            _choice(
                "close",
                "Close the pop-up and scan the system",
                "You avoided the adware and verified the system through a trusted scanner.",
                "Closing the popup and checking the system with a trusted tool is the safer response.",
                100,
                is_best=True,
            ),
        ],
    }
]

ADWARE_POP_UP_QUIZ = [
    {
        "question": "What is the safest response to an unexpected installer pop-up that claims your browser is infected?",
        "options": [
            "Click the install button immediately to fix the issue",
            "Close the pop-up and verify through a trusted security tool or browser settings",
            "Share the link with friends to see if they also get the message",
            "Disable your browser updates so the pop-up stops appearing",
        ],
        "correct": 1,
        "explanation": "Unexpected security pop-ups often try to trick you into installing unwanted software. Closing them and verifying through trusted tools is safer.",
    },
    {
        "question": "Which sign strongly suggests the popup is adware rather than a legitimate security warning?",
        "options": [
            "It appears in a normal browser tab",
            "It uses urgent scare language and an unknown publisher",
            "It only shows once after a browser restart",
            "It offers a free software update",
        ],
        "correct": 1,
        "explanation": "Adware often uses fear, urgency, and vague publishers to trick users into installing unwanted software.",
    },
]

ADWARE_POP_UP_EASY, ADWARE_POP_UP_HARD = _simulation_block(
    ADWARE_POP_UP_STEPS,
    indicators=[
        {
            "element": "scare_message",
            "title": "Scare-based warning",
            "description": "The message uses fear and urgency to push you into acting quickly.",
            "wrong": "Your browser is infected!",
            "correct": "Legitimate security messages usually explain the issue clearly and do not pressure you to install a program immediately.",
        },
        {
            "element": "urgency",
            "title": "Urgent install prompt",
            "description": "The popup tells you to install something right away, which is a common adware tactic.",
            "wrong": "Install now",
            "correct": "A trusted tool should let you review the details before you agree to install anything.",
        },
        {
            "element": "publisher",
            "title": "Unknown publisher",
            "description": "The software name is from an unknown or suspicious publisher.",
            "wrong": "UltraBoost Software",
            "correct": "You should prefer recognized developers and official app stores for software installation.",
        },
        {
            "element": "download_link",
            "title": "Suspicious download link",
            "description": "The popup offers a software install from an unfamiliar domain.",
            "wrong": "https://cleaner-boost.example/install",
            "correct": "Trusted installers should come from an official website or source you already know and trust.",
        },
        {
            "element": "url",
            "title": "Unfamiliar source",
            "description": "The popup source URL is not a familiar security vendor or official download page.",
            "wrong": "cleaner-boost.example",
            "correct": "Check the domain carefully and avoid installing software from suspicious or look-alike websites.",
        },
    ],
    signs=[
        {"id": "scare_language", "label": "Scare language"},
        {"id": "unknown_publisher", "label": "Unknown publisher"},
        {"id": "urgent_install", "label": "Urgent install prompt"},
    ],
)


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
            "media": {
                "folder": "phishing",
                "spotlight": [
                    "image1_phishing.jpg",
                    "image2_phishing.png",
                    "image3_phishing.png",
                ],
                "video_poster": "video-poster.svg",
                "video": "https://www.youtube.com/embed/AsnaqTCA95o",
            },
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
    "phishing_fake_website": {
        "id": "phishing_fake_website",
        "name": "Phishing: Fake Website",
        "icon": "🌐",
        "image": "img/modules/phishing/module_phishing.jpg",
        "difficulty": "Beginner",
        "short_description": "Learn to spot cloned login pages and suspicious URLs before entering credentials.",
        "category": "social_based",
        "category_label": "Social-Based Attacks",
        "overview": {
            "explanation": "Phishing: fake website attacks use a cloned login page or look-alike portal to steal credentials by making you think you are on the real site.",
            "why_used": "Attackers use fake websites because they look legitimate long enough for victims to type usernames, passwords, and one-time codes.",
            "how_encountered": "You may encounter fake websites through urgent links, sponsored search results, QR codes, or cloned login pages shared in chat.",
            "how_it_happens": [
                "Attacker copies a real portal and places it on a look-alike domain.",
                "Victim opens the site and sees familiar branding and urgency.",
                "Victim types credentials into the fake form.",
                "Attacker captures the data and uses it to access the real account.",
            ],
            "warning_signs": [
                "Look-alike domains with extra words or misspellings",
                "Urgent messages demanding immediate verification",
                "Fake login pages that ask for full credentials",
                "Unexpected redirects from links in emails or messages",
            ],
            "prevention_tips": [
                "Open important portals by typing the address yourself",
                "Check the domain carefully before entering credentials",
                "Use multi-factor authentication on school accounts",
                "Report suspicious links to IT or security staff",
            ],
        },
        "easy_simulation": {
            "steps": [
                {
                    "title": "Portal verification page",
                    "narrative": "A campus portal asks you to verify your account after a security update. Check the page carefully before logging in.",
                    "interface_type": "login_form",
                    "interface": {
                        "site_name": "UP Portal Verification",
                        "url": "https://up-portal-verify.net/login",
                        "banner": "Security update required",
                        "username_label": "University email",
                        "password_label": "Password",
                        "submit_label": "Verify account",
                        "cta": "Access the official portal",
                    },
                }
            ],
            "indicators": [
                {
                    "element": "lookalike_domain",
                    "title": "Look-alike domain",
                    "description": "The portal uses a domain that mimics the real university site but is not the official domain.",
                    "wrong": "https://up-portal-verify.net/login",
                    "correct": "Open the portal through the official university website or a trusted bookmark.",
                },
                {
                    "element": "urgent_banner",
                    "title": "Urgent security banner",
                    "description": "The page creates pressure to act immediately before you have time to verify the site.",
                    "wrong": "Security update required",
                    "correct": "Real portals do not force you into a login page through panic language.",
                },
                {
                    "element": "missing_security",
                    "title": "Missing expected security cues",
                    "description": "The page lacks the usual university portal URL and verified branding details you would expect.",
                    "wrong": "No verified university URL shown",
                    "correct": "Always confirm the exact domain and portal branding before entering credentials.",
                },
                {
                    "element": "credential_request",
                    "title": "Credential request on first visit",
                    "description": "The site asks for your full credentials before any account context or warning explanation.",
                    "wrong": "University email and password",
                    "correct": "Unexpected credential prompts are a major phishing warning sign.",
                },
            ],
        },
        "hard_simulation": {
            "steps": [
                {
                    "title": "Cloned Campus Login",
                    "narrative": "A cloned campus portal is asking you to sign in after a supposed account verification alert. Inspect it closely and decide whether it is safe.",
                    "interface_type": "login_form",
                    "interface": {
                        "site_name": "UP Campus Portal",
                        "url": "https://up-portal-verify.net/login",
                        "banner": "Account verification required",
                        "username_label": "University email",
                        "password_label": "Password",
                        "submit_label": "Sign in",
                        "cta": "Proceed to login",
                    },
                }
            ],
            "signs": [
                {"id": "lookalike_domain", "label": "Look-alike domain"},
                {"id": "urgent_banner", "label": "Urgent security banner"},
                {"id": "missing_security", "label": "Missing expected security cues"},
                {"id": "credential_request", "label": "Credential request on first visit"},
            ],
        },
        "quiz": PHISHING_WEBSITE_QUIZ,
        "info_page": {
            "media": {
                "folder": "phishing-website",
                "spotlight": [
                    "image1_phishing_web.jpg",
                    "image2_phishing_web.jpg",
                    "image3_phishing_web.png",
                ],
                "video_poster": "video-poster.svg",
                "video": "https://www.youtube.com/embed/-kB5r4Jlclk",
            },
            "spotlight": [
                {
                    "key": "about",
                    "heading": "About",
                    "text": "Phishing fake websites clone a real login portal and trap users into entering credentials on a look-alike domain.",
                },
                {
                    "key": "origin",
                    "heading": "How It Works",
                    "text": "Attackers pair a convincing alert with a cloned site that looks like the official portal but sends data to the attacker.",
                },
            ],
        },
    },
    "social_engineering": {
        "id": "social_engineering",
        "name": "Social Engineering",
        "icon": "🎭",
        "image": "img/modules/social-engineering/module_social.jpg",
        "difficulty": "Intermediate",
        "short_description": "Practice identifying and resisting manipulation tactics that exploit human trust, authority, and urgency.",
        "category": "social_based",
        "category_label": "Social-Based Attacks",
        "overview": {
            "explanation": (
                "Social engineering is the art of manipulating people into revealing confidential information "
                "or performing actions that compromise security — without exploiting any software vulnerability. "
                "It works by targeting the human element: trust, authority, fear, and urgency."
            ),
            "why_used": (
                "Attackers use social engineering because it is often easier and cheaper than breaking through "
                "technical defenses. A single well-crafted phone call or message can bypass firewalls, "
                "antivirus software, and encryption — because it targets the person, not the system."
            ),
            "how_encountered": (
                "Social engineering appears as phone calls from fake IT support, impersonation of authority figures, "
                "pretexting scenarios where the attacker fabricates a believable backstory, "
                "and urgent messages that demand immediate action."
            ),
            "how_it_happens": [
                "Attacker researches the target — gathering name, role, contact details from social media or public sources.",
                "They craft a believable pretext: IT support, university admin, bank security, or a known contact.",
                "They make contact and use authority, urgency, or fear to push the victim into acting quickly.",
                "The victim shares sensitive information — passwords, OTPs, or account details — believing the request is legitimate.",
                "Attacker uses that information to access accounts, steal data, or launch further targeted attacks.",
            ],
            "warning_signs": [
                "Unsolicited calls or messages asking you to verify account details",
                "Requests for one-time passwords, PINs, or security codes over the phone",
                "Unusual urgency — threats of account suspension, fines, or immediate consequences",
                "Caller already knows personal details, using them to seem trustworthy",
                "Pressure to bypass normal procedures 'just this once'",
                "Reluctance to let you call back through an official number",
            ],
            "prevention_tips": [
                "Never share OTPs, PINs, or passwords with anyone over the phone — even IT staff",
                "Always hang up and call back through a number you look up yourself, not one the caller provides",
                "Verify the identity of anyone requesting sensitive information before complying",
                "Slow down — urgency is a manipulation tactic; legitimate requests can wait",
                "Report suspicious calls to your IT department or security team immediately",
            ],
        },
        "easy_simulation": SOCIAL_ENGINEERING_EASY,
        "hard_simulation": SOCIAL_ENGINEERING_HARD,
        "quiz": [
            {
                "question": "A caller claims to be from TUP-T IT Security and asks you to read them the OTP just sent to your phone. What should you do?",
                "options": [
                    "Read the OTP — they already know your student number so they must be legitimate",
                    "Give them the first three digits only as a compromise",
                    "Hang up immediately and call the official TUP-T IT helpdesk number yourself",
                    "Ask them to email you first, then read the OTP if the email looks real",
                ],
                "correct": 2,
                "explanation": "No legitimate IT staff will ever ask for an OTP over the phone. Hanging up and calling through an official number you find yourself is the only way to verify identity.",
            },
            {
                "question": "The caller displays 'TUP-T IT Helpdesk' on your caller ID and knows your name and student number. This means:",
                "options": [
                    "The call is definitely legitimate — they passed the identity check",
                    "Caller ID can be spoofed, and basic personal details are easy to find online",
                    "You should share the OTP since they already know who you are",
                    "The university gave them your information for this call",
                ],
                "correct": 1,
                "explanation": "Caller ID is trivially easy to fake using VoIP tools. Knowing your name and student number proves nothing — this information is often available through social media, leaks, or public directories.",
            },
            {
                "question": "The caller says your account will be suspended in 5 minutes if you do not provide the code right now. This is an example of:",
                "options": [
                    "A standard IT security protocol for urgent account protection",
                    "An artificial urgency tactic designed to stop you from thinking critically",
                    "A legitimate warning that you should act on immediately",
                    "A two-factor authentication step the university requires",
                ],
                "correct": 1,
                "explanation": "Creating extreme time pressure is one of social engineering's most effective tools. It bypasses rational judgment and pushes victims into panicking and complying. Real security alerts give you time to verify.",
            },
            {
                "question": "You decide to hang up. The caller insists you should not hang up and that only they can fix the problem. What does this behavior indicate?",
                "options": [
                    "The situation is so urgent you really should stay on the line",
                    "It is a sign of a legitimate IT process that requires continuous communication",
                    "It is a manipulation tactic — legitimate staff will always let you call back through official channels",
                    "You should apologize and give them the code to resolve the issue",
                ],
                "correct": 2,
                "explanation": "A real IT staff member will never pressure you to stay on the line or refuse to let you call back. Resistance to verification is one of the clearest signs you are being manipulated.",
            },
            {
                "question": "After the call, you want to verify whether there was actually suspicious activity on your account. What is the correct approach?",
                "options": [
                    "Log into your account using the link the caller sent you",
                    "Call back the number that appeared on your caller ID",
                    "Check your account by going directly to the official TUP-T portal URL yourself",
                    "Wait to see if your account gets suspended, then contact IT",
                ],
                "correct": 2,
                "explanation": "Always navigate to official websites by typing the address yourself or using a trusted bookmark. Never use links or numbers provided by the suspicious caller.",
            },
        ],
        "info_page": {
            "media": {
                "folder": "social-engineering",
                "spotlight": [
                    "image1_social.jpg",
                    "image2_social.png",
                    "image3_social.png",
                ],
                "video_poster": "video-poster.svg",
                "video": "https://www.youtube.com/embed/L8169DHNeQ0",
            },
            "spotlight": [
                {
                    "key": "about",
                    "heading": "About",
                    "text": (
                        "Social engineering is the manipulation of people into revealing confidential information "
                        "or performing unsafe actions — without any technical exploit. It targets the most "
                        "vulnerable part of any security system: the human. Attackers build false trust through "
                        "impersonation, fabricated scenarios, and psychological pressure to bypass even the "
                        "strongest technical defenses."
                    ),
                },
                {
                    "key": "origin",
                    "heading": "Origin",
                    "text": (
                        "Social engineering predates computers entirely. Con artists and spies have used "
                        "impersonation and manipulation for centuries. In the digital era, the techniques "
                        "evolved into vishing (voice phishing), pretexting, and baiting — adapting old "
                        "psychological tactics to exploit the scale and anonymity of modern communication. "
                        "The core principle has never changed: it is far easier to trick a person than to "
                        "break a well-built system."
                    ),
                },
                {
                    "key": "real_world",
                    "heading": "Example in Real World",
                    "text": (
                        "In 2020, Twitter was breached when attackers called Twitter employees pretending to be "
                        "internal IT staff. They convinced employees to share credentials that gave access to "
                        "internal admin tools — resulting in high-profile accounts being hijacked to promote a "
                        "Bitcoin scam. No software was hacked. The entire breach started with a phone call."
                    ),
                },
            ],
            "real_world_examples": [
                "2020 Twitter hack: attackers called employees pretending to be IT, gaining access to internal admin tools",
                "Bank impersonation calls tricking customers into reading OTPs for fraudulent transactions",
                "Fake university IT calls targeting students during enrollment periods to harvest portal credentials",
                "Pretexting attacks where attackers pose as auditors to extract employee account information",
            ],
        },
    },
    "keylogger": {
        "id": "keylogger",
        "name": "Keylogger",
        "icon": "⌨️",
        "image": "img/modules/keylogger/module_keylogger.jpg",
        "difficulty": "Intermediate",
        "short_description": "Understand how keyloggers capture keystrokes and how to spot them before typing sensitive data.",
        "category": "malware_based",
        "category_label": "Malware-Based Attacks",
        "overview": {
            "explanation": "A keylogger is malware or a malicious utility that records what you type, including passwords, messages, and OTPs.",
            "why_used": "Attackers use keyloggers to steal credentials, session tokens, and private data with minimal visible activity.",
            "how_encountered": "You may encounter keyloggers through fake utilities, malicious downloads, or software that requests excessive input permissions.",
            "how_it_happens": [
                "Victim installs a utility that appears useful or trustworthy.",
                "The program requests keyboard or input-monitoring permissions.",
                "Keystrokes are logged silently in the background.",
                "Attacker collects passwords, messages, and account details.",
            ],
            "warning_signs": [
                "Unknown publisher asking for keyboard access",
                "Unexpected permissions related to input monitoring",
                "Background processes that stay active while idle",
                "Performance slowdowns after installing a utility",
            ],
            "prevention_tips": [
                "Install software only from trusted publishers",
                "Review permissions before allowing access",
                "Avoid unknown utilities that claim to improve typing or shortcuts",
                "Use endpoint protection and keep systems updated",
            ],
        },
        "easy_simulation": KEYLOGGER_EASY,
        "hard_simulation": KEYLOGGER_HARD,
        "quiz": KEYLOGGER_QUIZ,
        "info_page": {
            "media": {
                "folder": "keylogger",
                "spotlight": [
                    "image1_keylogger.png",
                    "image2_keylogger.jpeg",
                    "image3_keylogger.png",
                ],
                "video_poster": "video-poster.svg",
                "video": "https://www.youtube.com/embed/L8169DHNeQ0",
            },
            "spotlight": [
                {
                    "key": "about",
                    "heading": "About",
                    "text": "Keyloggers capture keystrokes so attackers can steal passwords, messages, and sensitive notes.",
                },
                {
                    "key": "origin",
                    "heading": "How It Works",
                    "text": "They often hide inside fake tools or utilities that request more access than they actually need.",
                },
                {
                    "key": "real_world",
                    "heading": "Example in Real World",
                    "text": "A malicious browser extension or fake utility can quietly record keystrokes until a victim notices suspicious account activity or stolen credentials.",
                },
            ],
            "real_world_examples": [
                "Fake password managers that silently record everything you type",
                "Malicious browser add-ons that capture OTPs and logins",
                "Trojanized utilities bundled with free downloads",
            ],
        },
    },
    "adware_pop_up": {
        "id": "adware_pop_up",
        "name": "Adware: Pop-up Installer",
        "icon": "🧲",
        "image": "img/modules/adware/module_adware.jpg",
        "difficulty": "Beginner",
        "short_description": "Learn to recognize adware-style installer pop-ups that try to trick you into installing unwanted software.",
        "category": "malware_based",
        "category_label": "Malware-Based Attacks",
        "overview": {
            "explanation": "Adware is unwanted software that usually arrives through misleading pop-ups, fake update prompts, or bundled installs and is designed to flood you with ads or slow your system down.",
            "why_used": "Attackers and software vendors use adware because it can generate revenue through aggressive advertising or by steering users to bundled products.",
            "how_encountered": "You may see adware through browser pop-ups, fake software updates, or free app installers.",
            "how_it_happens": [
                "The user sees a convincing pop-up claiming the browser or system needs urgent maintenance.",
                "The pop-up pushes a download or installer that is not actually needed.",
                "The unwanted app installs and starts showing ads or modifying browser settings.",
            ],
            "warning_signs": [
                "Urgent scare language",
                "Unknown publisher or unfamiliar download source",
                "Offers to install software immediately",
                "Fake browser or system cleanup alerts",
            ],
            "prevention_tips": [
                "Close suspicious pop-ups instead of clicking the install button",
                "Install software only from official sources",
                "Keep browser and security tools updated",
                "Use your browser or OS built-in app management to review installed software",
            ],
        },
        "easy_simulation": ADWARE_POP_UP_EASY,
        "hard_simulation": ADWARE_POP_UP_HARD,
        "quiz": ADWARE_POP_UP_QUIZ,
        "info_page": {
            "media": {
                "folder": "adware",
                "spotlight": [
                    "image1_adware.jpg",
                    "image2_adware.jfif",
                    "image3_adware.jpg",
                ],
                "video_poster": "video-poster.svg",
                "video": "https://www.youtube.com/embed/xt6QYHLrW_M",
            },
            "spotlight": [
                {
                    "key": "about",
                    "heading": "About",
                    "text": "Adware is unwanted software that usually arrives through misleading pop-ups, fake update prompts, or bundled installs and is designed to flood you with ads or slow your system down.",
                },
                {
                    "key": "origin",
                    "heading": "Origin",
                    "text": "Adware is commonly bundled with free software, browser extensions, or deceptive download prompts that encourage users to install more than they intended.",
                },
            ],
        },
    },
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
        "info_page": {
            "media": {
                "folder": "ransomware",
                "spotlight": [
                    "image1_ransomware.jfif",
                    "image2_ransomware.jpeg",
                    "image3_ransomware.png",
                ],
                "video_poster": "video-poster.svg",
                "video": "https://www.youtube.com/embed/-KL9APUjj3E",
            },
            "spotlight": [
                {
                    "key": "about",
                    "heading": "About",
                    "text": "Ransomware encrypts files or locks devices, then demands payment to restore access.",
                },
                {
                    "key": "origin",
                    "heading": "How It Works",
                    "text": "It usually enters through phishing, exposed services, or unpatched software, then spreads before the victim can react.",
                },
                {
                    "key": "real_world",
                    "heading": "Example in Real World",
                    "text": "Organizations often discover ransomware only after shared drives, backups, or entire endpoints suddenly become unreadable.",
                },
            ],
            "real_world_examples": [
                "Enterprises hit by encrypted file shares and ransom notes",
                "Hospitals and schools forced offline during active encryption",
                "Criminal groups demanding cryptocurrency for decryption keys",
            ],
        },
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
        "info_page": {
            "media": {
                "folder": "spyware",
                "spotlight": [
                    "image1_spyware.png",
                    "image2_spyware.jfif",
                    "image3_spyware.png",
                ],
                "video_poster": "video-poster.svg",
                "video": "https://www.youtube.com/embed/-Z3pp14oUiA",
            },
            "spotlight": [
                {
                    "key": "about",
                    "heading": "About",
                    "text": "Spyware secretly monitors user activity and sends sensitive data to attackers.",
                },
                {
                    "key": "origin",
                    "heading": "How It Works",
                    "text": "It often hides inside bundled installers, extensions, or free tools that request too much access.",
                },
                {
                    "key": "real_world",
                    "heading": "Example in Real World",
                    "text": "Spyware can capture browsing history, credentials, screenshots, and messages long before the victim notices unusual account activity.",
                },
            ],
            "real_world_examples": [
                "Browser extensions that silently harvest login tokens",
                "Free screen recorders bundled with spyware payloads",
                "Mobile apps that access microphone and location without clear need",
            ],
        },
    },
    "mitm": {
        "id": "mitm",
        "name": "Man-in-the-Middle (MITM)",
        "icon": "🔀",
        "image": "img/modules/mitm/module_mitm.jpg",
        "difficulty": "Advanced",
        "short_description": "Learn how attackers intercept network traffic on unsecured connections.",
        "category": "network_based",
        "category_label": "Network-Based Attacks",
        "overview": {
            "explanation": (
                "A Man-in-the-Middle (MITM) attack occurs when an attacker secretly intercepts and potentially "
                "alters communication between two parties who each believe they are communicating directly with "
                "the other. The attacker positions themselves in the middle of the connection without either "
                "victim knowing."
            ),
            "why_used": (
                "MITM attacks are used to eavesdrop on sensitive data — such as login credentials, banking "
                "details, or private messages — and to inject malicious content into otherwise legitimate "
                "traffic. They are especially effective on unsecured or public networks."
            ),
            "how_encountered": (
                "You may encounter MITM attacks on public WiFi networks, through ARP spoofing on a local "
                "network, via rogue hotspots, or through DNS hijacking that redirects you to fake websites "
                "even when you type the correct address."
            ),
            "how_it_happens": [
                "Attacker gains a foothold on the same network as the victim (e.g., public WiFi or ARP spoofing).",
                "Attacker intercepts packets flowing between the victim and the legitimate server.",
                "Data is read, logged, or altered before being forwarded to avoid detection.",
                "Victim remains unaware — their session appears normal while credentials or data are stolen.",
            ],
            "warning_signs": [
                "Unexpected certificate warnings or SSL/TLS errors in your browser",
                "Slower-than-usual connection speeds on a network you trust",
                "Being redirected to login pages when you didn't request them",
                "Unusual network activity or unknown devices on your local network",
                "Sites serving HTTP instead of HTTPS on sensitive pages",
            ],
            "prevention_tips": [
                "Always use HTTPS websites — look for the padlock icon before entering credentials",
                "Avoid sensitive transactions on public or unsecured WiFi networks",
                "Use a trusted VPN to encrypt all traffic when on public networks",
                "Enable HSTS (HTTP Strict Transport Security) in supported browsers",
                "Verify SSL certificates and report unexpected certificate errors immediately",
            ],
        },
        "easy_simulation": {
            "steps": [
                {
                    "title": "Public WiFi Banking Session",
                    "narrative": (
                        "You are at a coffee shop using the free WiFi to check your online bank account "
                        "and make a transfer. Something feels off — your job is to find all the red flags "
                        "before confirming the transaction."
                    ),
                    "interface_type": "browser",
                    "interface": {
                        "wifi_name": "CoffeeBrew_Free",
                        "url": "http://securebank.com/transfer",
                        "recipient": "Maria Santos — Acct #4421-XXXX",
                        "amount_entered": "500.00",
                        "amount_confirmed": "5,000.00",
                    },
                }
            ],
            "indicators": [
                {
                    "element": "no_https",
                    "title": "No HTTPS — connection is unencrypted",
                    "description": (
                        "The address bar shows 'Not Secure' and uses HTTP instead of HTTPS. "
                        "This means all data you send — including your banking credentials and "
                        "transaction details — travels over the network in plain text that anyone "
                        "on the same network can read."
                    ),
                    "wrong": "http://securebank.com/transfer  — No padlock, 'Not Secure' label, unencrypted",
                    "correct": (
                        "A legitimate bank site always uses HTTPS (the padlock icon). "
                        "The address should read https://securebank.com with a closed padlock — "
                        "never HTTP on any page that handles money or personal data."
                    ),
                    "tip": (
                        "Before entering any financial or personal information, always check that the "
                        "address bar shows HTTPS and a padlock. If it says 'Not Secure', leave immediately."
                    ),
                },
                {
                    "element": "open_wifi",
                    "title": "Open WiFi network with no password",
                    "description": (
                        "The WiFi network you are connected to — 'CoffeeBrew_Free' — has no password "
                        "protection (the open lock icon confirms this). On an open network, any device "
                        "nearby can intercept the traffic flowing between you and the internet, including "
                        "an attacker performing a MITM attack."
                    ),
                    "wrong": "CoffeeBrew_Free 🔓 — Open network, no encryption, anyone can intercept traffic",
                    "correct": (
                        "For sensitive tasks like banking, only use your personal mobile data or a trusted "
                        "password-protected network. If you must use public WiFi, connect through a VPN "
                        "first to encrypt all your traffic."
                    ),
                    "tip": (
                        "An open WiFi network is like having a conversation in a crowded room — "
                        "anyone nearby can listen. Never conduct banking or sensitive transactions "
                        "on an open network without a VPN."
                    ),
                },
                {
                    "element": "dismissed_cert",
                    "title": "A certificate warning was dismissed",
                    "description": (
                        "A yellow banner at the top of the browser shows that a security certificate "
                        "warning was dismissed earlier in this session. Certificate warnings appear "
                        "when your browser cannot verify that the site is who it claims to be — "
                        "a common sign of a MITM attacker intercepting HTTPS traffic using a fake certificate."
                    ),
                    "wrong": "A certificate warning appeared and was clicked away — the site's identity was never verified",
                    "correct": (
                        "Certificate warnings should never be dismissed on banking or sensitive sites. "
                        "If your browser warns that a certificate cannot be verified, close the tab "
                        "immediately and report it. Legitimate banks do not trigger certificate errors."
                    ),
                    "tip": (
                        "A MITM attacker using SSL stripping or a self-signed certificate will often "
                        "trigger a browser certificate warning. Clicking 'Proceed anyway' is exactly "
                        "what the attacker is counting on."
                    ),
                },
                {
                    "element": "altered_amount",
                    "title": "Transaction amount was silently altered",
                    "description": (
                        "You entered ₱500.00 in the amount field, but the transaction confirmation "
                        "summary shows ₱5,000.00. This is a classic MITM data injection — the attacker "
                        "intercepted your form submission and modified the amount before it reached "
                        "the bank's server, without you seeing any error or warning."
                    ),
                    "wrong": "You entered ₱500.00 — the confirmation shows ₱5,000.00 (10× more than intended)",
                    "correct": (
                        "Always verify that the confirmation summary exactly matches what you typed before "
                        "confirming any transaction. Any discrepancy — even a single digit — is a serious "
                        "red flag that your data may have been tampered with in transit."
                    ),
                    "tip": (
                        "MITM attackers do not just eavesdrop — they can actively modify your data. "
                        "HTTPS with a valid certificate prevents this. On an unencrypted HTTP connection, "
                        "any value in any form field can be changed by an attacker before it reaches the server."
                    ),
                },
            ],
        },
        "hard_simulation": _placeholder_module(
            "mitm", "Man-in-the-Middle (MITM)", "🔀", "Advanced",
            "Learn how attackers intercept network traffic on unsecured connections.",
            "network_based", "Network-Based Attacks",
            image="img/modules/mitm/module_mitm.jpg",
        )["hard_simulation"],
        "quiz": _placeholder_module(
            "mitm", "Man-in-the-Middle (MITM)", "🔀", "Advanced",
            "Learn how attackers intercept network traffic on unsecured connections.",
            "network_based", "Network-Based Attacks",
            image="img/modules/mitm/module_mitm.jpg",
        )["quiz"],
        "info_page": {
            "media": {
                "folder": "mitm",
                "spotlight": [
                    "module_mitm.jpg",
                    "image1_mitm.jpg",
                    "image2_mitm.png",
                ],
                "video_poster": "video-poster.svg",
                "video": "https://www.youtube.com/embed/SYAux_gSCck",
            },
            "spotlight": [
                {
                    "key": "about",
                    "heading": "About",
                    "text": (
                        "A Man-in-the-Middle attack is a form of eavesdropping where an attacker secretly "
                        "relays and can alter communication between two parties. Neither party realizes a "
                        "third actor is sitting in the middle of their conversation, silently reading — "
                        "or rewriting — every message that passes through."
                    ),
                },
                {
                    "key": "origin",
                    "heading": "How It Works",
                    "text": (
                        "The attacker first establishes interception — often via ARP spoofing, a rogue WiFi "
                        "hotspot, or DNS hijacking — then quietly forwards traffic between victim and server. "
                        "Because the connection appears normal to both sides, the attack can continue "
                        "indefinitely without triggering suspicion."
                    ),
                },
                {
                    "key": "real_world",
                    "heading": "Real-World Impact",
                    "text": (
                        "MITM attacks have targeted banking sessions, corporate VPNs, and public WiFi users "
                        "at airports and coffee shops. Attackers have stolen session tokens, intercepted "
                        "two-factor authentication codes, and injected malware into downloads — all while "
                        "the victim saw nothing unusual in their browser."
                    ),
                },
            ],
            "real_world_examples": [
                "Belkin router MITM (2003) — router firmware intercepted HTTP searches and injected ads without user consent",
                "DigiNotar breach (2011) — fraudulent SSL certificates enabled nation-state MITM on Iranian Gmail users",
                "Superfish adware (2015) — Lenovo laptops shipped with pre-installed software that performed HTTPS MITM on users",
                "Public WiFi credential harvesting — security researchers routinely demonstrate live credential capture at conferences using open hotspots",
                "BGP hijacking (2018) — attackers rerouted Amazon Route 53 DNS traffic to steal cryptocurrency wallet credentials",
            ],
        },
    },
    "evil_twin": {
        "id": "evil_twin",
        "name": "Evil Twin / Rogue WiFi",
        "icon": "📶",
        "image": "img/modules/evil-twin/module_eviltwin.png",
        "difficulty": "Intermediate",
        "short_description": "Learn how attackers clone legitimate Wi-Fi hotspots to steal credentials and intercept traffic.",
        "category": "network_based",
        "category_label": "Network-Based Attacks",
        "overview": {
            "explanation": "An evil twin is a rogue Wi-Fi access point that impersonates a legitimate hotspot, tricking users into connecting and exposing their traffic.",
            "why_used": "Attackers use evil twins because public users often trust familiar network names and connect without verifying the access point identity.",
            "how_encountered": "You may encounter rogue Wi-Fi networks in airports, cafés, universities, or events where multiple hotspots appear to be legitimate.",
            "how_it_happens": [
                "The attacker creates a hotspot with a name that looks familiar or official.",
                "Victims connect because the name seems trustworthy or the signal is stronger.",
                "The attacker captures traffic, credentials, or redirects victims to fake login pages.",
            ],
            "warning_signs": [
                "A network name that is slightly different from the official one",
                "Unexpectedly strong signal from a hotspot with no visible sponsor",
                "A captive portal that asks for credentials immediately",
                "No official branding or validation from the venue",
            ],
            "prevention_tips": [
                "Confirm the official SSID with staff or signage before connecting",
                "Use a VPN on public Wi-Fi",
                "Avoid entering credentials on captive portals you did not expect",
                "Prefer your mobile hotspot or a trusted network when handling sensitive tasks",
            ],
        },
        "easy_simulation": {
            "steps": [
                {
                    "title": "Public Wi-Fi Selection",
                    "narrative": "You are at the university canteen. Several Wi-Fi networks appear. One of them is designed to look official. Identify the warning signs before connecting.",
                    "interface_type": "wifi",
                    "interface": {
                        "networks": [
                            {
                                "name": "UP-Student",
                                "security": "WPA2",
                                "signal": "Strong",
                                "status": "Official",
                                "official": True,
                            },
                            {
                                "name": "UP-Student_Free",
                                "security": "Open",
                                "signal": "Very Strong",
                                "status": "Available",
                                "official": False,
                            },
                            {
                                "name": "GuestNet",
                                "security": "Open",
                                "signal": "Medium",
                                "status": "Available",
                                "official": False,
                            },
                        ],
                        "captive_portal": {
                            "title": "Campus Wi-Fi Login",
                            "body": "Sign in to continue browsing.",
                        },
                    },
                }
            ],
            "indicators": [
                {
                    "element": "rogue_name",
                    "title": "Network name looks almost official",
                    "description": "The suspicious network uses a name that is very close to the legitimate one, which is a common evil twin trick.",
                    "wrong": "UP-Student_Free",
                    "correct": "Always verify the exact SSID with staff or the venue's official signage before connecting.",
                    "tip": "Attackers often use a tiny variation in the name to trick users into connecting automatically.",
                },
                {
                    "element": "open_security",
                    "title": "Open or weak security",
                    "description": "The suspicious hotspot is open and does not require a password, which makes it easy to impersonate and intercept traffic.",
                    "wrong": "Open network — no password required",
                    "correct": "A legitimate campus hotspot should be clearly identified and should not rely on an unverified open network to collect credentials.",
                },
                {
                    "element": "captive_portal",
                    "title": "Unexpected login portal",
                    "description": "The captive portal appears immediately and asks for credentials before you even confirm the network is legitimate.",
                    "wrong": "Sign in to continue browsing",
                    "correct": "A legitimate portal should be expected and tied to the official venue or campus service, not a sudden prompt from a suspicious network.",
                },
                {
                    "element": "signal",
                    "title": "Unusually strong signal",
                    "description": "The rogue network broadcasts a very strong signal that can overpower the genuine hotspot.",
                    "wrong": "Very Strong signal",
                    "correct": "Signal strength alone is not proof of legitimacy. Always verify the network name and who is operating it.",
                },
            ],
        },
        "hard_simulation": {
            "steps": [
                {
                    "title": "Rogue Wi-Fi Investigation",
                    "narrative": "You have entered a public area with several similar-looking hotspots. Determine which one is trustworthy before using it.",
                    "interface_type": "wifi",
                    "interface": {
                        "networks": [
                            {"name": "UP-Student", "security": "WPA2", "signal": "Strong", "official": True},
                            {"name": "UP-Student_Free", "security": "Open", "signal": "Very Strong", "official": False},
                            {"name": "CampusGuest", "security": "Open", "signal": "Medium", "official": False},
                        ]
                    },
                }
            ],
            "signs": [
                {"id": "rogue_name", "label": "Suspicious SSID variation"},
                {"id": "open_security", "label": "Open network without password"},
                {"id": "unexpected_login", "label": "Unexpected captive portal"},
            ],
        },
        "quiz": [
            {
                "question": "What is an evil twin Wi-Fi network?",
                "options": [
                    "A secure Wi-Fi network with a stronger signal",
                    "A rogue access point that mimics a legitimate hotspot",
                    "A network that only appears in the evening",
                    "A hotspot that requires MFA",
                ],
                "correct": 1,
                "explanation": "An evil twin is a rogue access point that impersonates a legitimate network to trick users into connecting.",
            },
            {
                "question": "What is the safest action when you see a suspicious hotspot that looks like the official one?",
                "options": [
                    "Connect immediately because the signal is strongest",
                    "Ask staff or verify the official network name before connecting",
                    "Enter your password anyway to test if it is real",
                    "Use the open network because it is faster",
                ],
                "correct": 1,
                "explanation": "Always verify the official SSID through trusted sources before connecting to a public hotspot.",
            },
        ],
        "info_page": {
            "media": {
                "folder": "evil-twin",
                "spotlight": [
                    "image1_eviltwin.jpg",
                    "image2_eviltwin.png",
                    "image3_eviltwin.png",
                ],
                "video_poster": "video-poster.svg",
                "video": "https://www.youtube.com/embed/FCplxKNpxJ8",
            },
            "spotlight": [
                {
                    "key": "about",
                    "heading": "About",
                    "text": "Evil twin attacks copy legitimate Wi-Fi names and lure users into connecting to a fake hotspot that captures credentials or traffic.",
                },
                {
                    "key": "origin",
                    "heading": "How It Works",
                    "text": "Attackers use a rogue access point with a familiar SSID and strong signal so users connect without checking whether the hotspot is legitimate.",
                },
            ],
        },
    },
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
                "video": "https://www.youtube.com/embed/wcaiKgQU6VE",
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
