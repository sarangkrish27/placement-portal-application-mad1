from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user, login_user
from forms import SignupForm, CompanyProfileForm, PlacementDriveForm
from auth_decorators import company_required
from models import db, User, Company, PlacementDrive
from app import bcrypt
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime, date
from utils import greet

company_bp = Blueprint('company', __name__)

@company_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = SignupForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('User already exists. Please login', 'success')
            return redirect(url_for('auth.login'))
        if form.password.data == form.confirm_password.data:
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            new_user = User(email=form.email.data, password=hashed_password, role='company', )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('auth.login'))
        else:
            flash("Password and confirm password do not match.", "danger")
            return redirect(url_for('company.register'))
    return render_template('company/new-company.html', form=form)

@company_bp.route('/complete-profile', methods=['GET', 'POST'])
@login_required
@company_required
def complete_profile():
    form = CompanyProfileForm()
    if form.validate_on_submit():
        profile = form.profile.data
        original_name = secure_filename(profile.filename)
        ext = os.path.splitext(original_name)[1]
        profile_filename = f"{uuid.uuid4().hex}{ext}"
        save_path = os.path.join("static/uploads", "profiles", profile_filename)
        profile.save(save_path)

        update_profile = Company(
            uid = current_user.id,
            company_name = form.company_name.data,
            description = form.description.data,
            industry = form.industry.data,
            profile_filename = profile_filename,
            hr_name = form.hr_name.data,
            website = form.website.data,
        )
        db.session.add(update_profile)
        current_user.is_profile_completed =1
        db.session.commit()
        return redirect(url_for('company.dashboard'))
    return render_template('company/complete-profile.html', form=form)

@company_bp.route('/company/approvel')
@login_required
@company_required
def approval_pending():
    return render_template('/company/approval-pending.html')

@company_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
@company_required
def dashboard():
    if current_user.is_profile_completed == 0:
        return redirect(url_for('company.complete_profile'))
    else:
        if current_user.company.approval_status == 'pending':
            return redirect(url_for('company.approval_pending'))
        else:
            company = Company.query.filter_by(uid=current_user.id).first()
            greeting = greet(datetime.now().hour)
            return render_template('company/dashboard.html', company=company, greet=greeting)

@company_bp.route('/drives')
@login_required
@company_required
def drives():
    company = Company.query.filter_by(uid=current_user.id).first()
    drives = PlacementDrive.query.filter_by(company_id=company.id)
    return render_template('/company/drives.html', company=company, drives=drives)

@company_bp.route('/create-drives', methods = ['GET', 'POST'])
@login_required
@company_required
def createDrive():
    form =PlacementDriveForm()
    company = Company.query.filter_by(uid=current_user.id).first()
    if form.validate_on_submit():
        new_drive = PlacementDrive(
            company_id = company.id,
            job_title = form.job_title.data,
            location = form.job_location.data,
            work_mode = form.job_mode.data,
            job_type = form.job_type.data,
            job_description = form.job_description.data,
            key_responsibility = form.key_responsibility.data,
            eligible_degrees = ", ".join(form.eligible_degrees.data),
            preferred_departments = ", ".join(form.preferred_departments.data),
            cgpa = form.cgpa.data,
            other_eligibility = form.other_eligibility.data,
            required_skills = form.required_skills.data,
            preferred_skills = form.preferred_skills.data,
            compensation_benefits = form.compensation_benefits.data,
            application_deadline = form.application_deadline.data
        )
        db.session.add(new_drive)
        db.session.commit()
        flash("The placement drive has been created and is pending administrator approval. Editing will be disabled after approval.", "success")
        return redirect(url_for('company.drives'))
    return render_template('/company/create-drive.html', company=company, date=date, form=form)

@company_bp.route('/drive/<int:drive_id>/detail')
@login_required
@company_required
def driveDetails(drive_id):
    company = Company.query.filter_by(uid=current_user.id).first()
    drive = PlacementDrive.query.filter_by(id=drive_id).first()
    return render_template('/company/drive_details.html', company=company, drive=drive)