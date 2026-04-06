from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, login_user
from forms import SignupForm, StudentProfileForm
from models import db, User, Student, PlacementDrive, Application, Company
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
                flash('Password and confirmation password do not match.', 'danger')
            return redirect(url_for('student.register'))
        else:
            flash('Invalid student login', 'danger')
            return redirect(url_for('student.register'))

    return render_template('student/new-student.html', form=form)

@student_bp.route('/complete-profile', methods=['GET', 'POST'])
@login_required
@student_required
def complete_profile():
    form = StudentProfileForm()
    if form.validate_on_submit():
        profile = form.profile.data
        resume = form.resume.data

        if not profile or not profile.filename:
            flash('Please upload a profile picture.', 'danger')
            return redirect(url_for('student.complete_profile', form=form))
        if not resume or not resume.filename:
            flash('Please upload a resume.', 'danger')
            return redirect(url_for('student.complete_profile', form=form))

        original_name = secure_filename(profile.filename)
        ext = os.path.splitext(original_name)[1]
        profile_filename = f"{uuid.uuid4().hex}{ext}"
        save_path = os.path.join("static/uploads", "profiles", profile_filename)
        profile.save(save_path)

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

@student_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
@student_required
def dashboard():
    if current_user.is_profile_completed == 0:
        return redirect(url_for('student.complete_profile'))
    greeting = greet(datetime.now().hour)
    applications = Application.query.filter_by(student_id=current_user.student.id).order_by(Application.id.desc()).all()
    applied = 0
    shortlisted = 0
    selected = 0
    rejected = 0
    for application in applications:
        if application.status == 'selected':
            selected+=1
        elif application.status == 'shortlisted':
            shortlisted+=1
        elif application.status == 'rejected':
            rejected+=1
        else:
            applied+=1
    return render_template('student/dashboard.html', 
                           user=current_user, 
                           greet=greeting, 
                           applications=applications,
                           applied=applied,
                           shortlisted=shortlisted,
                           selected=selected,
                           rejected=rejected
                           )

@student_bp.route('/search', methods=['GET', 'POST'])
@login_required
@student_required
def search():
    if request.method == 'POST':
        search_filter = request.form.get('search-by')
        keyword = request.form.get('search-input')
        not_found = ''

        if search_filter == 'Companies':
            results = Company.query.join(User).filter(Company.company_name.ilike(f"%{keyword}%")).order_by(Company.company_name).all()

        elif search_filter == 'Drives':
           results = PlacementDrive.query.join(Company).filter(PlacementDrive.job_title.ilike(f"%{keyword}%")).order_by(PlacementDrive.job_title).all()
        else:
            flash("Select search by", "danger")
            return redirect(url_for('student.search'))
        
        if len(results) == 0:
            not_found = "No results"

        return render_template('student/search.html', user=current_user, search_filter=search_filter,results=results, not_found=not_found)
    return render_template('student/search.html', user=current_user)


@student_bp.route('/<int:company_id>/details')
@login_required
@student_required
def companyDetails(company_id):
    company = Company.query.filter_by(id=company_id).first()
    return render_template('/student/company-details.html', user=current_user, company=company)

@student_bp.route('company/<int:company_id>/drives')
@login_required
@student_required
def companySpecificDrives(company_id):
    drives = PlacementDrive.query.filter_by(company_id=company_id, status = 'approved').order_by(PlacementDrive.created_at.desc()).all()
    return render_template('/student/drives.html', drives=drives, user=current_user)

@student_bp.route('/drives', methods=['GET', 'POST'])
@login_required
@student_required
def drives():
    drives = PlacementDrive.query.filter_by(status='approved').order_by(PlacementDrive.created_at.desc()).all()
    return render_template('/student/drives.html', drives=drives, user=current_user)

@student_bp.route('/drive/<int:drive_id>/details')
@login_required
@student_required
def driveDetails(drive_id):
    drive = PlacementDrive.query.filter_by(id=drive_id).first()
    existing = Application.query.filter_by(student_id=current_user.student.id, drive_id=drive_id).first()
    return render_template('/student/drive-details.html', drive=drive, user=current_user, existing=existing)

@student_bp.route("/student/apply-drive/<int:drive_id>", methods=["POST"])
@login_required
@student_required
def applyDrive(drive_id):
    drive = PlacementDrive.query.filter_by(id = drive_id).first()
    if current_user.student.cgpa >= drive.cgpa:
        new_application = Application(student_id=current_user.student.id, drive_id=drive_id)
        db.session.add(new_application)
        db.session.commit()
        flash("Placement drive applied successfully! 🎉", "success")
        return redirect(url_for("student.drives"))
    else:
        flash("You don't meet CGPA requirements", "danger")
        return redirect(url_for("student.drives"))


@student_bp.route('/applications', methods=['GET', 'POST'])
@login_required
@student_required
def applications():
    applied_drives = Application.query.filter_by(student_id=current_user.student.id).order_by(Application.applied_at.desc()).all()
    return render_template('/student/application.html', applied_drives=applied_drives, user=current_user)


@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@student_required
def profile():
    return render_template('/student/profile.html', user=current_user)

@student_bp.route('/edit', methods=['GET','POST'])
@login_required
@student_required
def editProfile():
    student = Student.query.filter_by(uid=current_user.id).first()
    form = StudentProfileForm(obj=student)

    if form.validate_on_submit():
        profile = form.profile.data
        resume=form.resume.data
    
        if profile and profile.filename:
            original_name = secure_filename(profile.filename)
            ext = os.path.splitext(original_name)[1]
            profile_filename = f"{uuid.uuid4().hex}{ext}"
            save_path = os.path.join("static/uploads", "profiles", profile_filename)
            profile.save(save_path)
            student.profile_filename = profile_filename

        if resume and resume.filename:
            resume = form.resume.data
            original_name = secure_filename(resume.filename)
            ext = os.path.splitext(original_name)[1]
            resume_filename = f"{uuid.uuid4().hex}{ext}"
            save_path = os.path.join("static/uploads", "resumes", resume_filename)
            resume.save(save_path)
            student.resume_filename = resume_filename

        student.name=form.name.data
        student.degree=form.degree.data
        student.yos=form.yos.data
        student.cgpa=form.cgpa.data

        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('student.profile'))
    return render_template('/student/complete-profile.html', student=student, user=current_user, form=form)