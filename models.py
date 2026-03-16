from flask_sqlalchemy import SQLAlchemy
from datetime import date
from werkzeug.security import generate_password_hash
from app import app, db

class User(db.Model):
    __tablename__ = 'user'
    
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    hashedpassword = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_profile_completed = db.Column(db.Boolean, nullable=False, default=False)
    is_blacklisted = db.Column(db.Boolean, default=False)
    blacklist_reason = db.Column(db.String(100))
    created_at = db.Column(db.DateTime,server_default=db.func.now())
    
    student = db.relationship('Student', backref='user', cascade="all, delete-orphan", uselist=False)
    company = db.relationship('Company', backref='user', cascade="all, delete-orphan", uselist=False)


class Student(db.Model):
    __tablename__ = 'student'
    
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'), nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)
    profile_filename = db.Column(db.String(100))
    department = db.Column(db.String(100), nullable=False)
    degree = db.Column(db.String(100), nullable=False)
    yos = db.Column(db.Integer, nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    resume_filename = db.Column(db.String(255), nullable=False)


class Company(db.Model):
    __tablename__ = 'company'

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'), nullable=False, unique=True)
    company_name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    industry = db.Column(db.String(100), nullable=False)
    profile_filename = db.Column(db.String(100))
    hr_name = db.Column(db.String(100), nullable=False)
    website = db.Column(db.String(100), nullable=False)
    approval_status = db.Column(db.String(100), default='pending', nullable=False)

class PlacementDrive(db.Model):
    __tablename__ = 'placement_drive'

    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(
        db.Integer,
        db.ForeignKey('company.id'),
        nullable=False
    )

    job_title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    work_mode = db.Column(db.String(100), nullable=False)
    job_type = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    key_responsibility = db.Column(db.Text, nullable=False)
    eligible_degrees = db.Column(db.String(255), nullable=False)
    preferred_departments = db.Column(db.String(255), nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    other_eligibility = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.Text, nullable=False)
    preferred_skills = db.Column(db.Text, nullable=False)
    compensation_benefits = db.Column(db.Text, nullable=False)
    application_deadline = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime,server_default=db.func.now())

    status = db.Column(
        db.String(50),
        nullable=False,
        default='pending'
    )

    company = db.relationship(
        'Company',
        backref=db.backref('placement_drives', lazy=True)
    )

class Application(db.Model):
    __tablename__ = 'application'

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey('student.id'),
        nullable=False
    )

    drive_id = db.Column(
        db.Integer,
        db.ForeignKey('placement_drive.id'),
        nullable=False
    )


    status = db.Column(
        db.String(50),
        nullable=False,
        default='applied'
    )
    # applied / shortlisted / selected / rejected

    applied_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    student = db.relationship(
        'Student',
        backref=db.backref('applications', lazy=True)
    )

    drive = db.relationship(
        'PlacementDrive',
        backref=db.backref('applications', lazy=True)
    )


def update_drive_status():
    today = date.today()
    expired_drive = PlacementDrive.query.filter(PlacementDrive.application_deadline < today, PlacementDrive.status != 'closed').all()

    for drive in expired_drive:
        drive.status = 'closed'
    
    if expired_drive:
        db.session.commit()

def reset_application_status_on_blacklist():
    all_applications = Application.query.all()

    for application in all_applications:
        if application.student.user.is_blacklisted:
            db.session.delete(application)
    db.session.commit()


with app.app_context():
    db.create_all()
    admin = User.query.filter_by(role='admin').first()
    update_drive_status()
    reset_application_status_on_blacklist()

    if not admin:
        passowrd = generate_password_hash('admin123')
        admin = User(email='admin@placement.nist.edu', hashedpassword=passowrd, role='admin', is_profile_completed=1)
        db.session.add(admin)
        db.session.commit()