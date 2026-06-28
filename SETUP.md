# Secure-IT — Local Setup Guide

Follow these steps to get the project running on your machine.

## Prerequisites

Install these before starting:

- **Python 3.11+** — https://www.python.org/downloads/
- **Git** — https://git-scm.com/downloads
- A **MongoDB Atlas** account (ask the team lead for the connection string)
- A **Firebase** project with a service account key (ask the team lead)
- A **Gmail** account with an App Password for email sending (or ask for the team's shared credentials)

---

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_ORG/Secure-IT.git
cd Secure-IT
```

---

## 2. Create the Virtual Environment

From the project root:

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt.

---

## 3. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

---

## 4. Set Up the `.env` File

Copy the example file and fill in the real values:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Then open `.env` and fill in every value:

```env
# MongoDB
DB_URI=mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/?appName=Cluster0
DB_NAME=secure_it

# Server
PORT=4001
NODE_ENV=DEVELOPMENT

# Email (Gmail SMTP)
EMAIL_FROM=Secure-IT <noreply@yourdomain.com>
GMAIL_USER=your.email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx    # 16-char App Password from Google Account settings

# Email verification settings
EMAIL_VERIFY_TTL_HOURS=24
REQUIRE_EMAIL_VERIFICATION=true

# Cloudinary (for profile picture uploads)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Firebase (Google Sign-In)
FIREBASE_API_KEY=
FIREBASE_AUTH_DOMAIN=
FIREBASE_PROJECT_ID=
FIREBASE_APP_ID=
FIREBASE_CREDENTIALS_PATH=firebase-service-account.json
```

### Getting a Gmail App Password

1. Go to **myaccount.google.com → Security**
2. Enable **2-Step Verification** if not already on
3. Go to **App passwords**, create one for "Mail"
4. Paste the 16-character password (no spaces) into `GMAIL_APP_PASSWORD`

---

## 5. Add the Firebase Service Account File

The team lead will share a file called `firebase-service-account.json`.

Place it directly in the **project root** (`Secure-IT/firebase-service-account.json`).

> This file is in `.gitignore` — never commit it.

---

## 6. Seed the Database

Run this once to create the default profile and indexes in MongoDB:

```bash
cd backend
python seed_mongo.py
```

Expected output:
```
Inserted default profile
Inserted default metrics
Inserted default attempts
Ready: badges collection (empty, indexed)
...
Seeded database: secure_it
```

---

## 7. Run the App

```bash
cd backend
python app.py
```

Open your browser at: **http://127.0.0.1:4001**

---

## Project Structure

```
Secure-IT/
├── backend/
│   ├── app.py                  # Flask entry point
│   ├── database.py             # MongoDB connection
│   ├── firebase_auth.py        # Google Sign-In token verification
│   ├── mailer.py               # Gmail SMTP email sender
│   ├── simulation_data.py      # All simulation/quiz content
│   ├── simulation_missions.py  # Mission registry
│   ├── seed_mongo.py           # One-time DB seeder
│   ├── requirements.txt
│   └── secure_it/
│       ├── __init__.py         # create_app() factory
│       └── routes/             # Flask blueprints (auth, dashboard, simulations, etc.)
├── frontend/
│   ├── templates/              # Jinja2 HTML templates
│   └── static/
│       ├── css/                # Stylesheets
│       ├── js/                 # Client-side scripts
│       └── img/                # Static images (see IMAGE_GUIDE.md)
├── .env                        # Your local secrets (NOT committed)
├── .env.example                # Template — safe to commit
├── firebase-service-account.json  # Firebase key (NOT committed)
└── SETUP.md                    # This file
```

---

## Common Issues

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Make sure your venv is activated and you ran `pip install -r backend/requirements.txt` |
| `MongoDB connection not available` | Check `DB_URI` in `.env` — make sure your IP is whitelisted in Atlas |
| `Email not sending` | Verify `GMAIL_USER` and `GMAIL_APP_PASSWORD` are correct; 2FA must be on |
| `Firebase login not working` | Check that `firebase-service-account.json` is in the project root and `FIREBASE_CREDENTIALS_PATH` matches |
| `Port already in use` | Change `PORT=4001` to another number in `.env` |
