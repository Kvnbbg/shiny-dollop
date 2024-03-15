from flask import Blueprint, jsonify, render_template, request, session, redirect, url_for, flash, current_app
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import RadioField, HiddenField, SubmitField
from wtforms.validators import DataRequired
import os
import json
import random

main = Blueprint("main", __name__)

# Assuming CSRF is initialized elsewhere in your application
csrf = CSRFProtect()

class QuizForm(FlaskForm):
    choice = RadioField('Choices', validators=[DataRequired(message="Please make a selection.")])
    question_id = HiddenField()
    submit = SubmitField('Submit')
    skip = SubmitField('Skip')

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
    form = QuizForm()
    # Load questions just once or when the filter changes
    if 'filter' in request.args or 'questions' not in session:
        question_file = request.args.get('filter', session.get('question_file', 'questions.json'))
        questions = load_questions(question_file)
        session['questions'] = questions
        session['current_index'] = 0
        session['correct_answers'] = 0
        session['wrong_answers'] = 0
        session['skipped_answers'] = 0
        session['question_file'] = question_file
        return redirect(url_for('.quiz'))

    current_index = session.get('current_index', 0)
    questions = session.get('questions', [])
    if current_index < len(questions):
        current_question = questions[current_index]
        form.choice.choices = [(str(i), choice) for i, choice in enumerate(current_question['choices'])]
    else:
        return redirect(url_for('.quiz_complete'))

    if form.validate_on_submit():
        if form.skip.data:
            session['skipped_answers'] += 1
            feedback = "Question skipped."
        else:
            correct_answer = current_question['answer']
            if form.choice.data == str(correct_answer):
                session['correct_answers'] += 1
                feedback = "Correct answer!"
            else:
                session['wrong_answers'] += 1
                feedback = f"Wrong answer! The correct answer was: {correct_answer}."
        flash(feedback)
        session['current_index'] += 1
        return redirect(url_for('.quiz'))

    return render_template("quiz.html", question=current_question, form=form, countdown_duration=35)

@main.route('/quiz_complete')
def quiz_complete():
    quiz_results = {
        'correct_answers': session.pop('correct_answers', 0),
        'wrong_answers': session.pop('wrong_answers', 0),
        'skipped_answers': session.pop('skipped_answers', 0),
    }
    # Clear quiz-specific session data
    session.pop('questions', None)
    session.pop('current_index', None)
    return render_template("quiz_complete.html", **quiz_results)

@main.route('/set_language/<language>')
def set_language(language):
    session['lang'] = language
    flash(f"Language set to {'English' if language == 'en' else 'French'}.", "info")
    return redirect(request.referrer or url_for('.home'))

@main.route("/")
def home():
    return render_template("home.html", lang=session.get('lang', 'en'))
