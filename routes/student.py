from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user, login_user
from forms import SignupForm, StudentProfileForm
from models import db, User, Student
from auth_decorators import student_required
from app import bcrypt 
from werkzeug.utils import secure_filename
import os
import uuid
from utils import validate_smail, validate_department, get_department, greet
from datetime import datetime


student_bp = Blueprint('student', __name__)

@student_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = SignupForm()
    if form.validate_on_submit():
        if validate_smail(form.email.data) and validate_department(form.email.data):
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                flash('User already exists. Please login', 'success')
                return redirect(url_for('auth.login'))
            if form.password.data == form.confirm_password.data:
                hashed_password = bcrypt.generate_password_hash(form.password.data)
                new_user = User(email=form.email.data, password=hashed_password, role='student')
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('auth.login'))
        else:
            flash('Invalid student login', 'danger')
            return redirect(url_for('student.register'))

    return render_template('student/new-student.html', form=form)

@student_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
@student_required
def dashboard():
    if current_user.is_profile_completed == 0:
        return redirect(url_for('student.complete_profile'))
    greeting = greet(datetime.now().hour)
    return render_template('student/dashboard.html', user=current_user, greet=greeting)

@student_bp.route('/complete-profile', methods=['GET', 'POST'])
@login_required
@student_required
def complete_profile():
    form = StudentProfileForm()
    if form.validate_on_submit():
        profile = form.profile.data
        original_name = secure_filename(profile.filename)
        ext = os.path.splitext(original_name)[1]
        profile_filename = f"{uuid.uuid4().hex}{ext}"
        save_path = os.path.join("static/uploads", "profiles", profile_filename)
        profile.save(save_path)

        resume = form.resume.data
        original_name = secure_filename(resume.filename)
        ext = os.path.splitext(original_name)[1]
        resume_filename = f"{uuid.uuid4().hex}{ext}"
        save_path = os.path.join("static/uploads", "resumes", resume_filename)
        resume.save(save_path)

        department = get_department(current_user.email)

        update_profile = Student(
            uid=current_user.id,
            name=form.name.data,
            profile_filename=profile_filename,
            department=department,
            degree=form.degree.data,
            yos=form.yos.data,
            cgpa=form.cgpa.data,
            resume_filename=resume_filename
        )

        db.session.add(update_profile)
        current_user.is_profile_completed =1
        db.session.commit()
        return redirect(url_for('student.dashboard'))

    return render_template('student/complete-profile.html', form=form)

@student_bp.route('/search', methods=['GET', 'POST'])
@login_required
@student_required
def search():
    return 'serach'

@student_bp.route('/drives', methods=['GET', 'POST'])
@login_required
@student_required
def drives():
    return 'drives'

@student_bp.route('/applications', methods=['GET', 'POST'])
@login_required
@student_required
def applications():
    return 'application'

@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@student_required
def profile():
    return 'profile'