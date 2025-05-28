from flask import render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from datetime import datetime

from app import app, db
from models import User, Question, Answer, Exam, ExamQuestion, StudentExam, UserRole, QuestionType
from forms import LoginForm, RegistrationForm, QuestionForm, ExamForm
from grading_engine import grade_multiple_choice, grade_short_answer
from utils import required_roles

# Import OpenAI utilities if API key is available
OPENAI_AVAILABLE = bool(os.environ.get("OPENAI_API_KEY"))
if OPENAI_AVAILABLE:
    try:
        from openai_utils import generate_question_suggestions
    except ImportError:
        OPENAI_AVAILABLE = False


# Home route
@app.route('/')
def index():
    return render_template('index.html')


# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == UserRole.TEACHER:
            return redirect(url_for('dashboard_teacher'))
        else:
            return redirect(url_for('dashboard_student'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if user.role == UserRole.TEACHER:
                return redirect(next_page) if next_page else redirect(url_for('dashboard_teacher'))
            else:
                return redirect(next_page) if next_page else redirect(url_for('dashboard_student'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        role = UserRole.TEACHER if form.role.data == 'teacher' else UserRole.STUDENT
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            role=role
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Account created successfully! You can now login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# Teacher routes
@app.route('/dashboard/teacher')
@login_required
@required_roles(UserRole.TEACHER)
def dashboard_teacher():
    exams = Exam.query.filter_by(teacher_id=current_user.id).order_by(Exam.created_at.desc()).all()
    questions_count = Question.query.filter_by(teacher_id=current_user.id).count()
    student_count = StudentExam.query.join(Exam).filter(Exam.teacher_id == current_user.id).with_entities(StudentExam.student_id).distinct().count()
    
    return render_template('dashboard_teacher.html', 
                          exams=exams, 
                          questions_count=questions_count,
                          student_count=student_count)


@app.route('/questions/create', methods=['GET', 'POST'])
@login_required
@required_roles(UserRole.TEACHER)
def create_question():
    form = QuestionForm()
    
    if form.validate_on_submit():
        options = None
        if form.question_type.data == 'multiple_choice':
            options_list = [
                form.option1.data,
                form.option2.data,
                form.option3.data,
                form.option4.data
            ]
            # Filter out any empty options
            options_list = [opt for opt in options_list if opt and isinstance(opt, str) and opt.strip()]
            
            # Make sure we have a well-formed JSON string
            options = json.dumps(options_list, ensure_ascii=False)
        
        question = Question(
            teacher_id=current_user.id,
            question_text=form.question_text.data,
            question_type=QuestionType.MULTIPLE_CHOICE if form.question_type.data == 'multiple_choice' else QuestionType.SHORT_ANSWER,
            correct_answer=form.correct_answer.data,
            options=options,
            points=form.points.data
        )
        
        db.session.add(question)
        db.session.commit()
        
        flash('Question created successfully!', 'success')
        return redirect(url_for('manage_questions'))
    
    return render_template('create_question.html', form=form)


@app.route('/questions/manage')
@login_required
@required_roles(UserRole.TEACHER)
def manage_questions():
    questions = Question.query.filter_by(teacher_id=current_user.id).order_by(Question.created_at.desc()).all()
    # Pass OPENAI_AVAILABLE to template to show/hide AI generation button
    return render_template('manage_questions.html', questions=questions, openai_available=OPENAI_AVAILABLE)


@app.route('/questions/ai-generator', methods=['GET', 'POST'])
@login_required
@required_roles(UserRole.TEACHER)
def ai_question_generator():
    # If OpenAI is not available, redirect to manual question creation
    if not OPENAI_AVAILABLE:
        flash('AI question generation is not available. Please add your OpenAI API key.', 'warning')
        return redirect(url_for('create_question'))
    
    generated_questions = []
    
    if request.method == 'POST':
        topic = request.form.get('topic')
        question_type = request.form.get('question_type')
        count = int(request.form.get('count', 3))
        
        try:
            # Generate questions using OpenAI
            questions = generate_question_suggestions(topic, question_type, count)
            if questions:
                # Format questions for the template
                generated_questions = [
                    {
                        'question_text': q.get('question_text', ''),
                        'correct_answer': q.get('correct_answer', ''),
                        'options': q.get('options', []),
                        'type': question_type
                    }
                    for q in questions
                ]
                flash(f'Successfully generated {len(generated_questions)} questions!', 'success')
            else:
                flash('No questions were generated. Please try a different topic.', 'warning')
        except Exception as e:
            print(f"Error generating questions: {e}")
            flash('Error generating questions. Please try again or contact support.', 'danger')
    
    return render_template('ai_question_generator.html', generated_questions=generated_questions)


@app.route('/questions/save-ai', methods=['POST'])
@login_required
@required_roles(UserRole.TEACHER)
def save_ai_question():
    if not request.form:
        flash('Invalid request. No question data provided.', 'danger')
        return redirect(url_for('ai_question_generator'))
    
    try:
        question_text = request.form.get('question_text')
        question_type = request.form.get('question_type')
        correct_answer = request.form.get('correct_answer')
        
        # Create new question
        options = None
        if question_type == 'multiple_choice':
            options_list = [
                request.form.get('option1', ''),
                request.form.get('option2', ''),
                request.form.get('option3', ''),
                request.form.get('option4', '')
            ]
            # Filter out any empty options
            options_list = [opt for opt in options_list if opt and isinstance(opt, str) and opt.strip()]
            
            # Make sure we have a well-formed JSON string
            options = json.dumps(options_list, ensure_ascii=False)
        
        question = Question(
            teacher_id=current_user.id,
            question_text=question_text,
            question_type=QuestionType.MULTIPLE_CHOICE if question_type == 'multiple_choice' else QuestionType.SHORT_ANSWER,
            correct_answer=correct_answer,
            options=options,
            points=1  # Default to 1 point, teacher can edit later
        )
        
        db.session.add(question)
        db.session.commit()
        
        flash('AI-generated question saved successfully!', 'success')
        return redirect(url_for('manage_questions'))
    
    except Exception as e:
        print(f"Error saving AI question: {e}")
        flash('Error saving question. Please try again.', 'danger')
        return redirect(url_for('ai_question_generator'))


@app.route('/questions/edit/<int:question_id>', methods=['GET', 'POST'])
@login_required
@required_roles(UserRole.TEACHER)
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    
    # Make sure the question belongs to the current teacher
    if question.teacher_id != current_user.id:
        flash('You are not authorized to edit this question', 'danger')
        return redirect(url_for('manage_questions'))
    
    form = QuestionForm()
    
    if request.method == 'GET':
        form.question_text.data = question.question_text
        form.question_type.data = 'multiple_choice' if question.question_type == QuestionType.MULTIPLE_CHOICE else 'short_answer'
        form.correct_answer.data = question.correct_answer
        form.points.data = question.points
        
        if question.options:
            options = json.loads(question.options)
            if len(options) >= 1:
                form.option1.data = options[0]
            if len(options) >= 2:
                form.option2.data = options[1]
            if len(options) >= 3:
                form.option3.data = options[2]
            if len(options) >= 4:
                form.option4.data = options[3]
    
    if form.validate_on_submit():
        question.question_text = form.question_text.data
        question.question_type = QuestionType.MULTIPLE_CHOICE if form.question_type.data == 'multiple_choice' else QuestionType.SHORT_ANSWER
        question.correct_answer = form.correct_answer.data
        question.points = form.points.data
        
        if form.question_type.data == 'multiple_choice':
            options_list = [
                form.option1.data,
                form.option2.data,
                form.option3.data,
                form.option4.data
            ]
            # Filter out any empty options
            options_list = [opt for opt in options_list if opt and isinstance(opt, str) and opt.strip()]
            
            # Make sure we have a well-formed JSON string
            question.options = json.dumps(options_list, ensure_ascii=False)
        else:
            question.options = None
        
        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('manage_questions'))
    
    return render_template('create_question.html', form=form, edit_mode=True)


@app.route('/questions/delete/<int:question_id>', methods=['POST'])
@login_required
@required_roles(UserRole.TEACHER)
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    
    # Make sure the question belongs to the current teacher
    if question.teacher_id != current_user.id:
        flash('You are not authorized to delete this question', 'danger')
        return redirect(url_for('manage_questions'))
    
    db.session.delete(question)
    db.session.commit()
    
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('manage_questions'))


@app.route('/exams/create', methods=['GET', 'POST'])
@login_required
@required_roles(UserRole.TEACHER)
def create_exam():
    form = ExamForm()
    
    # Get available questions for the select field
    questions = Question.query.filter_by(teacher_id=current_user.id).all()
    form.questions.choices = [(q.id, f"{q.question_text[:30]}... ({q.question_type.value})") for q in questions]
    
    if form.validate_on_submit():
        # Create the exam
        exam = Exam(
            title=form.title.data,
            description=form.description.data,
            teacher_id=current_user.id,
            time_limit=form.time_limit.data,
            is_active=True
        )
        
        db.session.add(exam)
        db.session.flush()  # Get the exam ID without committing
        
        # Add selected questions to the exam
        for i, question_id in enumerate(form.questions.data):
            exam_question = ExamQuestion(
                exam_id=exam.id,
                question_id=question_id,
                order=i
            )
            db.session.add(exam_question)
        
        db.session.commit()
        flash('Exam created successfully!', 'success')
        return redirect(url_for('dashboard_teacher'))
    
    return render_template('create_exam.html', form=form)


@app.route('/exams/view/<int:exam_id>')
@login_required
@required_roles(UserRole.TEACHER)
def view_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    
    # Make sure the exam belongs to the current teacher
    if exam.teacher_id != current_user.id:
        flash('You are not authorized to view this exam', 'danger')
        return redirect(url_for('dashboard_teacher'))
    
    # Get all questions in this exam
    exam_questions = ExamQuestion.query.filter_by(exam_id=exam.id).order_by(ExamQuestion.order).all()
    questions = [eq.question for eq in exam_questions]
    
    # Get student submissions
    student_exams = StudentExam.query.filter_by(exam_id=exam.id).all()
    
    return render_template('view_exam.html', exam=exam, questions=questions, student_exams=student_exams)


@app.route('/exams/toggle/<int:exam_id>', methods=['POST'])
@login_required
@required_roles(UserRole.TEACHER)
def toggle_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    
    # Make sure the exam belongs to the current teacher
    if exam.teacher_id != current_user.id:
        flash('You are not authorized to modify this exam', 'danger')
        return redirect(url_for('dashboard_teacher'))
    
    exam.is_active = not exam.is_active
    db.session.commit()
    
    status = "activated" if exam.is_active else "deactivated"
    flash(f'Exam {status} successfully!', 'success')
    return redirect(url_for('dashboard_teacher'))


@app.route('/analytics/question/<int:question_id>')
@login_required
@required_roles(UserRole.TEACHER)
def question_analytics(question_id):
    question = Question.query.get_or_404(question_id)
    
    # Make sure the question belongs to the current teacher
    if question.teacher_id != current_user.id:
        flash('You are not authorized to view analytics for this question', 'danger')
        return redirect(url_for('dashboard_teacher'))
    
    # Get all answers to this question
    answers = Answer.query.filter_by(question_id=question.id).all()
    
    # Calculate statistics
    total_answers = len(answers)
    if total_answers == 0:
        avg_score = 0
    else:
        avg_score = sum(answer.score or 0 for answer in answers) / total_answers
    
    # For multiple choice questions, get distribution of answers
    answer_distribution = {}
    if question.question_type == QuestionType.MULTIPLE_CHOICE and question.options:
        options = json.loads(question.options)
        for option in options:
            answer_distribution[option] = 0
        
        for answer in answers:
            if answer.answer_text in answer_distribution:
                answer_distribution[answer.answer_text] += 1
    
    return render_template('question_analytics.html', 
                          question=question, 
                          answers=answers, 
                          total_answers=total_answers,
                          avg_score=avg_score,
                          answer_distribution=answer_distribution)


@app.route('/analytics/student/<int:student_id>')
@login_required
@required_roles(UserRole.TEACHER)
def student_analytics(student_id):
    student = User.query.get_or_404(student_id)
    
    # Make sure the student is actually a student
    if student.role != UserRole.STUDENT:
        flash('This user is not a student', 'danger')
        return redirect(url_for('dashboard_teacher'))
    
    # Get all exams submitted by this student for exams created by the current teacher
    student_exams = StudentExam.query.join(Exam).filter(
        StudentExam.student_id == student_id,
        Exam.teacher_id == current_user.id
    ).all()
    
    return render_template('student_analytics.html', student=student, student_exams=student_exams)


# Student routes
@app.route('/dashboard/student')
@login_required
@required_roles(UserRole.STUDENT)
def dashboard_student():
    # Get active exams that the student hasn't taken yet
    active_exams = Exam.query.filter_by(is_active=True).all()
    
    # Get the exams the student has already taken
    taken_exam_ids = [se.exam_id for se in StudentExam.query.filter_by(student_id=current_user.id).all()]
    
    # Filter out exams that have already been taken
    available_exams = [exam for exam in active_exams if exam.id not in taken_exam_ids]
    
    # Get the student's completed exams
    completed_exams = StudentExam.query.filter_by(student_id=current_user.id).all()
    
    return render_template('dashboard_student.html', 
                          available_exams=available_exams,
                          completed_exams=completed_exams)


@app.route('/exams/take/<int:exam_id>', methods=['GET', 'POST'])
@login_required
@required_roles(UserRole.STUDENT)
def take_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    
    # Check if the exam is active
    if not exam.is_active:
        flash('This exam is no longer available', 'danger')
        return redirect(url_for('dashboard_student'))
    
    # Check if the student has already taken this exam
    existing_attempt = StudentExam.query.filter_by(student_id=current_user.id, exam_id=exam.id).first()
    if existing_attempt:
        flash('You have already taken this exam', 'warning')
        return redirect(url_for('view_results', student_exam_id=existing_attempt.id))
    
    # Get all questions for this exam
    exam_questions = ExamQuestion.query.filter_by(exam_id=exam.id).order_by(ExamQuestion.order).all()
    questions = [eq.question for eq in exam_questions]
    
    if request.method == 'POST':
        # Create a new StudentExam record
        student_exam = StudentExam(
            student_id=current_user.id,
            exam_id=exam.id,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow()
        )
        
        db.session.add(student_exam)
        db.session.flush()  # Get the student_exam ID without committing
        
        total_points = 0
        earned_points = 0
        
        # Process each question and answer
        for question in questions:
            answer_text = request.form.get(f'answer_{question.id}', '')
            
            # Grade the answer
            if question.question_type == QuestionType.MULTIPLE_CHOICE:
                score, feedback = grade_multiple_choice(answer_text, question.correct_answer, question.points)
            else:
                score, feedback = grade_short_answer(answer_text, question.correct_answer, question.points)
            
            # Create a new Answer record
            answer = Answer(
                student_exam_id=student_exam.id,
                question_id=question.id,
                answer_text=answer_text,
                score=score,
                feedback=feedback
            )
            
            db.session.add(answer)
            
            total_points += question.points
            earned_points += score
        
        # Calculate the overall score
        if total_points > 0:
            student_exam.score = (earned_points / total_points) * 100
        else:
            student_exam.score = 0
        
        db.session.commit()
        
        flash('Exam submitted successfully!', 'success')
        return redirect(url_for('view_results', student_exam_id=student_exam.id))
    
    return render_template('take_exam.html', exam=exam, questions=questions)


@app.route('/results/<int:student_exam_id>')
@login_required
def view_results(student_exam_id):
    student_exam = StudentExam.query.get_or_404(student_exam_id)
    
    # Make sure the current user is either the student who took the exam or the teacher who created it
    if current_user.id != student_exam.student_id and current_user.id != student_exam.exam.teacher_id:
        flash('You are not authorized to view these results', 'danger')
        if current_user.role == UserRole.TEACHER:
            return redirect(url_for('dashboard_teacher'))
        else:
            return redirect(url_for('dashboard_student'))
    
    # Get all answers for this exam
    answers = Answer.query.filter_by(student_exam_id=student_exam.id).all()
    
    return render_template('view_results.html', student_exam=student_exam, answers=answers)
