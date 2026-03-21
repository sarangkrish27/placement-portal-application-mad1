from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user, login_user
from forms import SignupForm, CompanyProfileForm
from auth_decorators import company_required
from models import db, User, Company
from app import bcrypt
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
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
            user_id = current_user.id
            company = Company.query.filter_by(uid=user_id).first()
            greeting = greet(datetime.now().hour)
            return render_template('company/dashboard.html', company=company, greet=greeting)

@company_bp.route('/company/approvel')
@login_required
@company_required
def approval_pending():
    return render_template('/company/approval-pending.html')

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