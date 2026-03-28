from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from forms import CompanyProfileForm, PlacementDriveForm, StudentProfileForm
from auth_decorators import admin_required
from models import db, User, Student, Company, PlacementDrive, Application
from app import bcrypt
from datetime import datetime
from utils import greet
from werkzeug.utils import secure_filename
from datetime import datetime, date
import os
import uuid

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    greeting = greet(datetime.now().hour)
    companies = Company.query.filter_by(approval_status='approved').count()
    drives = PlacementDrive.query.filter_by(status='approved').count()
    students = Student.query.count()
    return render_template('/admin/dashboard.html', greet=greeting, companies=companies, drives=drives, students=students)

@admin_bp.route('/search', methods=['GET', 'POST'])
@login_required
@admin_required
def search():
    not_found = ''
    if request.method == 'POST':
        search_filter = request.form.get('search-by')
        keyword = request.form.get('search-input')

        if search_filter == 'Companies':
            results = Company.query.join(User).filter(Company.company_name.ilike(f"%{keyword}%")).all()
        
        elif search_filter == 'Students':
            try:
                student_id = int(keyword)
                results = Student.query.with_entities(
                    Student.id, Student.profile_filename, Student.name,
                    Student.degree, Student.department
                ).filter(Student.id == student_id).all()

            except ValueError:
                if keyword.endswith("@smail.nist.edu"):
                    results = Student.query.with_entities(
                        Student.id, Student.profile_filename, Student.name,
                        Student.degree, Student.department
                    ).join(Student.user).filter(User.email == keyword).all()
                else:
                    results = Student.query.with_entities(
                        Student.id, Student.profile_filename, Student.name,
                        Student.degree, Student.department
                    ).filter(Student.name.ilike(f"%{keyword}%")).all()

        elif search_filter == 'Drives':
            results = PlacementDrive.query.join(Company).filter(PlacementDrive.job_title.ilike(f"%{keyword}%")).all()

        else:
            flash("Select search by", "danger")
            return render_template('admin/search.html')

        if len(results) == 0:
            not_found = "No results"
        return render_template('admin/search.html',search_filter=search_filter,results=results, not_found=not_found)
    return render_template('admin/search.html')


@admin_bp.route('/students')
@login_required
@admin_required
def students():
    degree = request.args.get("filter-by-degree")
    department = request.args.get("filter-by-department")

    query = Student.query

    if degree:
        query = query.filter(Student.degree == degree)

    if department:
        query = query.filter(Student.department == department)

    students = query.all()
    return render_template('/admin/students.html', students=students)


@admin_bp.route('student/<int:student_id>')
@login_required
@admin_required
def studentDetails(student_id):
    student = Student.query.filter_by(id=student_id).first()
    return render_template('admin/student_details.html', student=student)

@admin_bp.route('/edit/student/<int:student_id>', methods=['GET','POST'])
@login_required
@admin_required
def editStudent(student_id):
    student = Student.query.filter_by(id=student_id).first()
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
        return redirect(url_for('admin.studentDetails', student_id=student.id))

    return render_template('/admin/student_edit_profile.html', form=form, student=student)

@admin_bp.route('/<int:student_id>/applications')
@login_required
@admin_required
def studentApplications(student_id):
    applications = Application.query.filter_by(student_id=student_id).all()
    return render_template('admin/student_applications.html', applications=applications)

@admin_bp.route('/companies')
@login_required
@admin_required
def companies():
    pending_request = Company.query.filter_by(approval_status='pending').all()

    query = Company.query.filter_by(approval_status='approved')

    industry = request.args.get("filter-by-industry")
    if industry:
        query = query.filter(Company.industry == industry)

    all_company = query.all()

    return render_template('/admin/companies.html', pending_request=pending_request, all_company=all_company)

@admin_bp.route('/drives')
@login_required
@admin_required
def drives():
    pending_request = PlacementDrive.query.filter_by(status='pending').all()
    all_drives = PlacementDrive.query.filter_by(status='approved').order_by(PlacementDrive.id.desc()).all()
    return render_template('/admin/drives.html', pending_request=pending_request, all_drives=all_drives)

@admin_bp.route('/<int:drive_id>/details')
@login_required
@admin_required
def driveDetails(drive_id):
    drive = PlacementDrive.query.filter_by(id=drive_id).first()
    return render_template('/admin/drive_details.html', drive=drive)

@admin_bp.route("drive/<int:drive_id>/application")
@login_required
@admin_required
def driveApplications(drive_id):
    status = request.args.get("filter-by-status")
    if status:
        applications = Application.query.filter_by(drive_id=drive_id, status=status).all()
    else:
        applications = Application.query.filter_by(drive_id=drive_id).all()
    return render_template('admin/drive_applications.html', applications=applications, drive_id=drive_id)


@admin_bp.route('/<string:company_name>/details')
@login_required
@admin_required
def companyDetails(company_name):
    company = Company.query.filter_by(company_name=company_name).first()
    user = User.query.filter_by(id=company.uid).first()
    return render_template('admin/company_details.html', user=user, company=company)

@admin_bp.route('/edit/company/<int:company_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editCompany(company_id):
    company = Company.query.filter_by(id=company_id).first()
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
        return redirect(url_for('admin.companyDetails', company_name=company.company_name))
    return render_template('/admin/company_edit_profile.html', form=form, company=company)

@admin_bp.route('/<int:drive_id>/edit_drive', methods=['GET','POST'])
@login_required
@admin_required
def editDrive(drive_id):
    drive = PlacementDrive.query.filter_by(id=drive_id).first()
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
        flash('Drive updated successfully', 'success')
        return redirect(url_for('admin.driveDetails', drive_id=drive.id))

    return render_template('/admin/edit_drive.html', form=form, date=date)


@admin_bp.route('/drives/<int:company_id>')
@login_required
@admin_required
def companyDrives(company_id):
    pending_request = PlacementDrive.query.filter_by(company_id=company_id, status='pending').all()
    all_drives = PlacementDrive.query.filter_by(company_id=company_id, status='approved').order_by(PlacementDrive.id.desc()).all()
    return render_template('admin/drives.html', pending_request=pending_request, all_drives=all_drives)

@admin_bp.route("/approve-company/<int:company_id>", methods=["POST"])
@login_required
@admin_required
def approve_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.approval_status = "approved"
    db.session.commit()
    flash("Company approved successfully!", "success")
    return redirect(url_for("admin.companies"))

@admin_bp.route("/reject-company/<int:company_id>", methods=["POST"])
@login_required
@admin_required
def reject_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.approval_status = "rejected"
    db.session.commit()
    flash("Company rejected successfully!", "danger")
    return redirect(url_for("admin.companies"))

@admin_bp.route("/admin/approve-drive/<int:drive_id>", methods=["POST"])
@login_required
@admin_required
def approve_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = "approved"
    db.session.commit()
    flash("Placement drive approved successfully!", "success")
    return redirect(url_for("admin.drives"))

@admin_bp.route("/admin/reject-drive/<int:drive_id>", methods=["POST"])
@login_required
@admin_required
def reject_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = "rejected"
    db.session.commit()
    flash("Placement drive rejected successfully!", "danger")
    return redirect(url_for("admin.drives"))

@admin_bp.route('/blacklist/<int:uid>', methods=['POST'])
@login_required
@admin_required
def userBlacklist(uid):
    reason = request.form.get("reason", "").strip()
    user = User.query.filter_by(id=uid).first()
    user.is_blacklisted = 1
    user.blacklist_reason = reason
    db.session.commit()
    if user.role == 'student':
        flash("Student blacklisted successfully!", "success")
        return redirect(url_for('admin.students'))
    else:
        flash("Company blacklisted successfully!", "success")
        return redirect(url_for('admin.companies'))
    
@admin_bp.route('/revoke-blacklist/<int:uid>')
@login_required
@admin_required
def userRevokeBlacklist(uid):
    user = User.query.filter_by(id=uid).first()
    user.is_blacklisted = 0
    user.blacklist_reason = ""
    db.session.commit()
    if user.role == 'student':
        flash("Student blacklist status revoked successfully!", "success")
        return redirect(url_for('admin.students'))
    else:
        flash("Company blacklist status revoked successfully.!", "success")
        return redirect(url_for('admin.companies'))
    
@admin_bp.route('/delete/<int:uid>', methods=['POST'])
@login_required
@admin_required
def userDelete(uid):
    user = User.query.filter_by(uid=uid).first()
    db.session.delete(user)
    db.session.commit()
    flash("Student deleted successfully!", "success")
    return redirect(url_for('admin.students'))

@admin_bp.route('/drive/delete/<int:drive_id>', methods=['POST'])
@login_required
@admin_required
def driveDelete(drive_id):
    drive = PlacementDrive.query.filter_by(id=drive_id).first()
    db.session.delete(drive)
    db.session.commit()
    flash("Drive deleted successfully!", "success")
    return redirect(url_for('admin.drives'))
