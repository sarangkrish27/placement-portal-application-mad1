from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from auth_decorators import admin_required
from models import db, User, Student, Company
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

@admin_bp.route('/search')
@login_required
@admin_required
def search():
    return "Search"

@admin_bp.route('/students')
@login_required
@admin_required
def students():
    return "Students"

@admin_bp.route('/companies')
@login_required
@admin_required
def companies():
    pending_request = Company.query.filter_by(approval_status='pending').all()
    all_company = Company.query.filter_by(approval_status='approved').all()
    return render_template('/admin/companies.html', pending_request=pending_request, all_company=all_company)

@admin_bp.route('/drives')
@login_required
@admin_required
def drives():
    return "Drives"


@admin_bp.route('/<string:company_name>/details')
@login_required
@admin_required
def companyDetails(company_name):
    company = Company.query.filter_by(company_name=company_name).first()
    user = User.query.filter_by(id=company.uid).first()
    return render_template('admin/company_details.html', user=user, company=company)

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

@admin_bp.route('/blacklist/<int:uid>', methods=['POST'])
@login_required
@admin_required
def userBlacklist(uid):
    reason = request.form.get("reason", "").strip()
    user = User.query.filter_by(uid=uid).first()
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
    user = User.query.filter_by(uid=uid).first()
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

