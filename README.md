# 🎓 Placement Portal

A role-based campus placement management system built with **Flask**, **Jinja2**, **Bootstrap**, and **SQLite**. It streamlines the recruitment workflow between the placement cell (Admin), recruiting organizations (Company), and students, from posting a placement drive to tracking a student's application status.

> Built as the CS2003 (Modern Application Development I) course project for the IIT Madras BS in Data Science program.

## ✨ Features

🛡️ **Admin**
- Approves or rejects company registrations before they can post drives
- Oversees all placement drives, students, and companies on the platform
- Seeded automatically on first run with a default admin account

🏢 **Company**
- Registers and completes a company profile (industry, HR contact, website, description)
- Posts placement drives with eligibility criteria — CGPA cutoff, eligible degrees/departments, required and preferred skills, compensation, and application deadline
- Reviews applications submitted by eligible students

🎒 **Student**
- Registers and completes a profile (department, degree, year of study, CGPA, resume upload)
- Browses open placement drives and applies to the ones they're eligible for
- Tracks the status of submitted applications

⚙️ **System behavior**
- Passwords are hashed with `bcrypt`; sessions are handled via `Flask-Login`
- Placement drives are automatically marked `closed` once their application deadline passes
- Companies must be approved by an admin before their drives go live

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask (application factory + blueprints) |
| Templating | Jinja2 |
| Styling | Bootstrap |
| Database | SQLite via Flask-SQLAlchemy (SQLAlchemy 2.x) |
| Auth | Flask-Login, Flask-Bcrypt |
| Forms | Flask-WTF / WTForms |
| Config | python-dotenv |

## 📁 Project Structure

```
placement-portal-application-mad1/
├── app.py                 # Application factory, extension init, admin seeding
├── config.py               # Loads SECRET_KEY and DB URI from environment
├── models.py                # User, Student, Company, PlacementDrive, Application
├── forms.py                # WTForms form definitions
├── auth_decorators.py       # Role-based access control decorators
├── utils.py                 # Helper functions
├── routes/                  # Blueprints (auth, admin, company, student, etc.)
├── templates/                # Jinja2 templates
├── static/                   # CSS, JS, uploaded files
└── requirements.txt
```

## 🗄️ Data Model

- **User** — base account with `email`, hashed `password`, and a `role` (`admin` / `company` / `student`); can be blacklisted with a reason
- **Student** — profile linked 1:1 to a User (department, degree, year of study, CGPA, resume)
- **Company** — profile linked 1:1 to a User, with an `approval_status` (`pending` by default)
- **PlacementDrive** — posted by a Company, with eligibility rules, required/preferred skills, compensation, deadline, and `status` (auto-updated to `closed` after the deadline)
- **Application** — links a Student to a PlacementDrive, with a `status` (`applied` by default)

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### 1️⃣ Clone the repository

```bash
git clone https://github.com/sarangkrish27/placement-portal-application-mad1.git
cd placement-portal-application-mad1
```

### 2️⃣ Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3️⃣ Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
SQLALCHEMY_DATABASE_URI=sqlite:///placement.db
```

### 4️⃣ Run the application

```bash
python app.py
```

On first run, the database tables are created automatically and a default **admin** account is seeded:

```
Email:    admin@placement.nist.edu
Password: admin123
```

> ℹ️ **Disclaimer:** This project ("Placement Portal") and the institution name "NIST" used in the seeded admin email are hypothetical, created for academic/demonstration purposes. Any resemblance to real placement portals, companies, or institutions is purely coincidental.

> ⚠️ Change this password immediately in any non-local deployment.

The app will be available at `http://127.0.0.1:5000` 🌐 (adjust if you run it differently, e.g. via `flask run`).

## 🧭 Usage

1. 🛡️ **Admin** logs in with the seeded credentials to approve pending company registrations.
2. 🏢 **Companies** sign up, complete their profile, and — once approved — post placement drives with eligibility criteria.
3. 🎒 **Students** sign up, complete their profile with a resume upload, browse open drives, and apply.
4. ⏰ Drives automatically close once the application deadline passes.

## 📄 License

This project was developed for academic purposes as part of the IIT Madras BS Data Science program.
