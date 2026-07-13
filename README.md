# PhishGuard

A phishing awareness and education web application built with Python and Flask, developed as coursework for the Cybersecurity and Digital Forensics programme at Softwarica College of IT and E-Commerce (Coventry University).

---

## Features

- Phishing lessons (beginner to advanced)
- Knowledge quiz with scoring and attempt history
- URL scanner with heuristic risk analysis
- Email header analyzer (SPF, DKIM detection)
- Threat reporting system
- User authentication with role-based access (user/admin)
- Admin panel for managing lessons, quiz questions, and reports

---

## Tech Stack

- **Backend:** Python 3, Flask 3.0
- **Database:** MySQL, Flask-SQLAlchemy (ORM), PyMySQL
- **Auth:** Werkzeug password hashing
- **Frontend:** Jinja2, HTML, CSS

---

## Setup

```bash
git clone https://github.com/puranterminal/phishguard_project-.git
cd phishguard_project-
pip install -r requirements.txt
```

Create a `.env` file:
```
SECRET_KEY=your-secret-key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_DATABASE=phishguard_db
SQLALCHEMY_DATABASE_URI=mysql+pymysql://root:your-password@localhost/phishguard_db
```

Run the app:
```bash
python run.py
```

Default admin login: `admin@admin.com` / `admin123`

---

## Author

Puran —  Softwarica College of IT and E-Commerce, Nepal