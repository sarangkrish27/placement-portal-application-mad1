from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, login_user
from forms import SignupForm, CompanyProfileForm, PlacementDriveForm
from auth_decorators import company_required
from models import db, User, Company, Student, PlacementDrive, Application
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

        if not profile or not profile.filename:
            flash('Please upload a profile picture.', 'danger')
            return redirect(url_for('company.complete_profile', form=form))
        
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

@company_bp.route('/approvel')
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
            drives = PlacementDrive.query.filter_by(company_id=current_user.company.id).all()
            greeting = greet(datetime.now().hour)
            pending = 0
            approved = 0
            rejected_drive = 0
            closed = 0
            for drive in drives:
                if drive.status == 'pending':
                    pending+=1
                elif drive.status == 'approved':
                    approved+=1
                elif drive.status == 'rejected':
                    rejected_drive+=1
                else:
                    closed+=1
            applications = Application.query.join(PlacementDrive).filter(PlacementDrive.company_id == current_user.company.id).all()
            applied = 0
            rejected = 0
            shortlisted = 0
            selected = 0
            for application in applications:
                if application.status == 'applied':
                    applied+=1
                elif application.status == 'rejected':
                    rejected+=1
                elif application.status == 'shortlisted':
                    shortlisted+=1
                else:
                    selected+=1
            return render_template('company/dashboard.html', 
                                   company=company,
                                   drives=drives[::-1],
                                   greet=greeting, 
                                   pending=pending, 
                                   approved=approved,
                                   rejected_drive=rejected_drive, 
                                   closed=closed,
                                   applied=applied,
                                   rejected=rejected,
                                   shortlisted=shortlisted,
                                   selected=selected
                                   )

@company_bp.route('/drives')
@login_required
@company_required
def drives():
    company = Company.query.filter_by(uid=current_user.id).first()
    status = request.args.get("filter-by-status")

    if status == 'pending':
        drives = PlacementDrive.query.filter_by(company_id=company.id, status='pending').all()
    elif status == 'approved':
        drives = PlacementDrive.query.filter_by(company_id=company.id, status='approved').all()
    elif status == 'closed':
        drives = PlacementDrive.query.filter_by(company_id=company.id, status='closed').all()
    else:
        drives = PlacementDrive.query.filter_by(company_id=company.id).all()
    return render_template('/company/drives.html', company=company, drives=drives[::-1])

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
            location = form.location.data,
            work_mode = form.work_mode.data,
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

@company_bp.route('/drive/<int:drive_id>/edit', methods=['GET','POST'])
@login_required
@company_required
def editDrive(drive_id):
    drive = PlacementDrive.query.filter_by(id=drive_id).first()
    company = Company.query.filter_by(uid=current_user.id).first()
    form = PlacementDriveForm(obj=drive)
    if drive:
        form.eligible_degrees.data = [d.strip() for d in drive.eligible_degrees.split(',')] if drive.eligible_degrees else []
        form.preferred_departments.data = [d.strip() for d in drive.preferred_departments.split(',')] if drive.preferred_departments else []
    
    if form.validate_on_submit():
        drive.job_title = form.job_title.data
        drive.location = form.location.data
        drive.work_mode = form.work_mode.data
        drive.job_type = form.job_type.data
        drive.job_description = form.job_description.data
        drive.key_responsibility = form.key_responsibility.data
        drive.eligible_degrees = ", ".join(form.eligible_degrees.data)
        drive.preferred_departments = ", ".join(form.preferred_departments.data)
        drive.cgpa = form.cgpa.data
        drive.other_eligibility = form.other_eligibility.data
        drive.required_skills = form.required_skills.data
        drive.preferred_skills = form.preferred_skills.data
        drive.compensation_benefits = form.compensation_benefits.data
        drive.application_deadline = form.application_deadline.data

        db.session.commit()
        flash('Drive updated successfully! 🎉', 'success')
        return redirect(url_for('company.driveDetails', drive_id=drive.id))
    return render_template('/company/create-drive.html', drive=drive, company=company, form=form, date=date)

@company_bp.route('/drive/<int:drive_id>/close', methods=['POST'])
@login_required
@company_required
def closeDrive(drive_id):
    drive = PlacementDrive.query.filter_by(id=drive_id).first()
    drive.status = 'closed'
    db.session.commit()
    flash('Drive closed successfully!', 'success')
    return redirect(url_for('company.driveDetails', drive_id=drive.id))

@company_bp.route('/applications')
@login_required
@company_required
def applications():
    company = Company.query.filter_by(uid=current_user.id).first()
    status = request.args.get("filter-by-status")

    if status == 'pending':
        drives = PlacementDrive.query.filter_by(company_id=company.id, status='pending').all()
    elif status == 'approved':
        drives = PlacementDrive.query.filter_by(company_id=company.id, status='approved').all()
    elif status == 'closed':
        drives = PlacementDrive.query.filter_by(company_id=company.id, status='closed').all()
    else:
        drives = PlacementDrive.query.filter_by(company_id=company.id).all()

    return render_template('/company/applications.html', company=company, drives=drives[::-1])

@company_bp.route('/applicants/<int:drive_id>')
@login_required
@company_required
def applicants(drive_id):
    status = request.args.get("filter-by-status")
    if status:
        applications = Application.query.filter_by(drive_id=drive_id, status=status).all()
    else:
        applications = Application.query.filter_by(drive_id=drive_id).all()
    company = Company.query.filter_by(uid=current_user.id).first()
    return render_template('company/applicants.html', applications=applications[::-1], company=company, drive_id=drive_id)

@company_bp.route('application/<int:application_id>/student/<int:student_id>/details')
@login_required
@company_required
def studentDetails(application_id, student_id):
    student= Student.query.filter_by(id=student_id).first()
    company = Company.query.filter_by(uid=current_user.id).first()
    application = Application.query.filter_by(id=application_id).first()
    return render_template('/company/student_details.html', student=student, company=company, drive_id=application.drive_id)

@company_bp.route('/company/review-decision/<int:student_id>/<int:drive_id>', methods=["POST"])
@login_required
@company_required
def reviewDecision(student_id, drive_id):
    application = Application.query.filter_by(student_id=student_id, drive_id=drive_id).first()
    reviewDecision = request.form.get('review-decision', "").strip()
    if reviewDecision == "shortlisted" or reviewDecision == "selected" or reviewDecision == "rejected":
        application.status = reviewDecision
        db.session.commit()
        flash("Decision updated successfully", "success")
        return redirect(url_for('company.applicants', drive_id=drive_id))

@company_bp.route('/profile')
@login_required
@company_required
def profile():
    company = Company.query.filter_by(uid=current_user.id).first()
    return render_template('/company/profile.html', company=company)

@company_bp.route('/profile/edit', methods=['GET','POST'])
@login_required
@company_required
def editProfile():
    company = Company.query.filter_by(uid=current_user.id).first()
    form = CompanyProfileForm(obj=company)

    if form.validate_on_submit():
        profile = form.profile.data

        if profile and profile.filename:
            original_name = secure_filename(profile.filename)
            ext = os.path.splitext(original_name)[1]
            profile_filename = f"{uuid.uuid4().hex}{ext}"
            save_path = os.path.join("static/uploads", "profiles", profile_filename)
            profile.save(save_path)
            company.profile_filename = profile_filename

        company.company_name = form.company_name.data
        company.description = form.description.data
        company.industry = form.industry.data
        company.hr_name = form.hr_name.data
        company.website = form.website.data

        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('company.profile'))
    
    return render_template('/company/complete-profile.html', company=company, form=form)