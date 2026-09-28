# PocketSmart AI

PocketSmart AI is a Generative AI powered budget and recommendation assistant.

The application provides:

- Home Interior Planner
- Party Planner
- Jewelry Planner
- Gemini AI integration
- Image-aware jewelry planning
- User registration
- Login/logout
- Session management
- Recommendation history
- SQLite database
- FastAPI backend
- Responsive frontend
- Fallback recommendations

---

# Project Structure

```text
PocketSmartAI/
│
├── app.py
├── config.py
├── database.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── models/
│   ├── __init__.py
│   └── schemas.py
│
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   ├── pages.py
│   ├── planners.py
│   └── session.py
│
├── services/
│   ├── __init__.py
│   ├── catalog.py
│   └── gemini_service.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   ├── home.html
│   ├── party.html
│   ├── jewelry.html
│   └── 404.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── app.js
│       └── planners.js
│
└── tests/
    └── test_app.py