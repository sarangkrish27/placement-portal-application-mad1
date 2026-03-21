from flask import redirect, url_for
from functools import wraps
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            return redirect(url_for('auth.accessForbidden'))
        return f(*args, **kwargs)
    return decorated

def student_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'student':
            return redirect(url_for('auth.accessForbidden'))
        return f(*args, **kwargs)
    return decorated

def company_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'company':
            return redirect(url_for('auth.accessForbidden'))
        return f(*args, **kwargs)
    return decorated