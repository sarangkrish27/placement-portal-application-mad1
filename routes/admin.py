from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from auth_decorators import admin_required
from models import db, User, Student, Company, PlacementDrive, Application
from app import bcrypt
from datetime import datetime
from utils import greet

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    greeting = greet(datetime.now().hour)
    return render_template('/admin/dashboard.html', greet=greeting)

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
            results = Student.query.with_entities(Student.id,Student.profile_filename,Student.name,Student.degree,Student.department).filter(Student.name.ilike(f"%{keyword}%")).all()

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

@admin_bp.route('/<int:student_id>/applications')
@login_required
@admin_required
def studentApplications(student_id):
    return 'hai'

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

@admin_bp.route('/admin/drives/<int:company_id>')
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

