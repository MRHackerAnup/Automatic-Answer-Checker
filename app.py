import os
import logging
import json
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect, CSRFError
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create database base class
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Initialize CSRF protection
csrf = CSRFProtect()

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///answer_checker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the database with the app
db.init_app(app)

# Initialize CSRF protection
csrf.init_app(app)

# Custom Jinja2 filters
@app.template_filter('fromjson')
def fromjson_filter(value):
    return json.loads(value)

# CSRF error handler
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

with app.app_context():
    # Import models here to avoid circular imports
    from models import User, Question, Answer, Exam, ExamQuestion, StudentExam

    # Create database tables
    db.create_all()
