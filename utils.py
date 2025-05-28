from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def required_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login'))
            if current_user.role not in roles:
                flash('You do not have permission to access this page.', 'danger')
                if current_user.role.value == 'teacher':
                    return redirect(url_for('dashboard_teacher'))
                else:
                    return redirect(url_for('dashboard_student'))
            return f(*args, **kwargs)
        return wrapped
    return wrapper
