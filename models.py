from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import relationship
import enum


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class UserRole(enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    questions = relationship("Question", back_populates="teacher")
    student_exams = relationship("StudentExam", back_populates="student")
    created_exams = relationship("Exam", back_populates="teacher")


class QuestionType(enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.Enum(QuestionType), nullable=False)
    correct_answer = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=True)  # JSON string for multiple-choice options
    points = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    teacher = relationship("User", back_populates="questions")
    exam_questions = relationship("ExamQuestion", back_populates="question")
    answers = relationship("Answer", back_populates="question")


class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    teacher_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    time_limit = db.Column(db.Integer, default=60)  # time limit in minutes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    teacher = relationship("User", back_populates="created_exams")
    exam_questions = relationship("ExamQuestion", back_populates="exam")
    student_exams = relationship("StudentExam", back_populates="exam")


class ExamQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, ForeignKey('exam.id'), nullable=False)
    question_id = db.Column(db.Integer, ForeignKey('question.id'), nullable=False)
    order = db.Column(db.Integer, default=0)
    
    # Relationships
    exam = relationship("Exam", back_populates="exam_questions")
    question = relationship("Question", back_populates="exam_questions")


class StudentExam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    exam_id = db.Column(db.Integer, ForeignKey('exam.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Float, nullable=True)
    
    # Relationships
    student = relationship("User", back_populates="student_exams")
    exam = relationship("Exam", back_populates="student_exams")
    answers = relationship("Answer", back_populates="student_exam")


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_exam_id = db.Column(db.Integer, ForeignKey('student_exam.id'), nullable=False)
    question_id = db.Column(db.Integer, ForeignKey('question.id'), nullable=False)
    answer_text = db.Column(db.Text, nullable=False)
    score = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student_exam = relationship("StudentExam", back_populates="answers")
    question = relationship("Question", back_populates="answers")
