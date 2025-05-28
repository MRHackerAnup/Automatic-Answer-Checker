from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms import TextAreaField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('student', 'Student'), ('teacher', 'Teacher')], validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different one.')


class QuestionForm(FlaskForm):
    question_text = TextAreaField('Question Text', validators=[DataRequired()])
    question_type = SelectField('Question Type', choices=[('multiple_choice', 'Multiple Choice'), ('short_answer', 'Short Answer')], validators=[DataRequired()])
    option1 = StringField('Option 1')
    option2 = StringField('Option 2')
    option3 = StringField('Option 3')
    option4 = StringField('Option 4')
    correct_answer = TextAreaField('Correct Answer', validators=[DataRequired()])
    points = IntegerField('Points', validators=[DataRequired(), NumberRange(min=1)], default=1)
    submit = SubmitField('Save Question')


class ExamForm(FlaskForm):
    title = StringField('Exam Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    time_limit = IntegerField('Time Limit (minutes)', validators=[DataRequired(), NumberRange(min=5)], default=60)
    questions = SelectMultipleField('Select Questions', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Create Exam')
