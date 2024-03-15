from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import RadioField, HiddenField, SubmitField
from wtforms.validators import DataRequired
import os
import json
import random

main = Blueprint("main", __name__)

class QuizForm(FlaskForm):
    choice = RadioField('Choices', validators=[DataRequired(message="Please make a selection.")])
    question_id = HiddenField()
    submit = SubmitField('Submit')
    skip = SubmitField('Skip')

    def set_choices(self, choices):
        self.choice.choices = choices

def load_questions(filename="questions.json"):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(base_dir, 'static', 'questions', filename)
    if not os.path.exists(filepath):
        flash("Question file not found. Loading default questions.", "warning")
        filepath = os.path.join(base_dir, 'static', 'questions', 'default_questions.json')
    with open(filepath, 'r', encoding='utf-8') as file:
        questions = json.load(file)
    random.shuffle(questions)
    return questions

@main.route("/quiz", methods=["GET", "POST"])
def quiz():
    question_file = session.get('question_file', 'questions.json')
    questions = session.setdefault('quiz_progress', {'questions': load_questions(question_file), 'current_index': 0, 'correct_answers': 0, 'wrong_answers': 0, 'skipped_answers': 0})['questions']
    progress = session['quiz_progress']
    current_index = progress['current_index']

    # Dynamic choice setting
    if current_index < len(questions):
        current_choices = [(str(i), choice) for i, choice in enumerate(questions[current_index]['choices'])]
    else:
        current_choices = []

    form = QuizForm()
    form.set_choices(current_choices)

    if 'filter' in request.args:
        question_file = request.args.get('filter')
        session['question_file'] = question_file
        # Reset progress on filter change
        session.pop('quiz_progress', None)
        return redirect(url_for('.quiz'))

    if form.validate_on_submit():
        feedback = handle_submission(form, progress, questions)
        flash(feedback, 'info')
        if current_index >= len(questions):
            return redirect(url_for('.quiz_complete'))
    else:
        form.set_choices(current_choices)  # Ensure choices are updated if form is not submitted

    if current_index < len(questions):
        current_question = questions[current_index]
    else:
        return redirect(url_for('.quiz_complete'))

    return render_template("quiz.html", question=current_question, form=form, countdown_duration=35)

def handle_submission(form, progress, questions):
    current_index = progress['current_index']
    current_question = questions[current_index]
    
    if form.skip.data:
        progress['skipped_answers'] += 1
        feedback = "Question skipped."
    else:
        user_answer = form.choice.data
        correct_answer = str(current_question['answer'])
        if user_answer == correct_answer:
            progress['correct_answers'] += 1
            feedback = "Correct answer!"
        else:
            progress['wrong_answers'] += 1
            feedback = f"Wrong answer! The correct answer was: {correct_answer}"
            
    progress['current_index'] += 1
    session['quiz_progress'] = progress  # Ensure progress is updated in session
    return feedback

@main.route('/quiz_complete')
def quiz_complete():
    # Additional logic to provide a summary or cleanup as needed
    session.pop('quiz_progress', None)  # Ensure cleanup
    return render_template("quiz_complete.html")

@main.route('/set_language/<language>')
def set_language(language):
    session['lang'] = language
    flash(f"Language set to {'English' if language == 'en' else 'French'}.", "info")
    return redirect(request.referrer or url_for('.home'))

@main.route("/")
def home():
    return render_template("home.html", lang=session.get('lang', 'en'))
