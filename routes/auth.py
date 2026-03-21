from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from forms import LoginForm
from models import db, User
from flask_bcrypt import Bcrypt

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth_bp.route('/')
def index():
    return render_template('index.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        if current_user.role == 'student':
            return redirect(url_for('student.dashboard'))
        elif current_user.role == 'company':
            return redirect(url_for('company.dashboard'))
        else:
            return redirect(url_for('admin.dashboard'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                if user.role == 'student':
                    return redirect(url_for('student.dashboard'))
                elif user.role == 'company':
                    return redirect(url_for('company.dashboard'))
                else:
                    return redirect(url_for('admin.dashboard'))
            else:
                flash("Incorrect password", "danger")
        else:
            flash("User does not exist", "danger")
            return redirect(url_for('auth.login'))
    return render_template('login.html', form=form)

@auth_bp.route('/newuser')
def newuser():
    return render_template('new-user.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash("Logged out successfully", "success")
    return redirect(url_for('auth.login'))

@auth_bp.route('/access-forbidden')
def accessForbidden():
    return render_template('403.html')