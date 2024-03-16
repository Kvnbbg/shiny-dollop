import sqlite3
from flask import Blueprint, jsonify, render_template, request, session, redirect, url_for, flash, current_app
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, RadioField, HiddenField, SubmitField
from wtforms.validators import DataRequired
import os
import json
import random

main = Blueprint("main", __name__)

# Ensure CSRF is initialized and applied to your application in the main app file
csrf = CSRFProtect()

class QuizForm(FlaskForm):
    choice = RadioField('Choices', coerce=str, validators=[DataRequired(message="Please make a selection.")])
    question_id = HiddenField()
    submit = SubmitField('Submit')
    skip = SubmitField('Skip')

def load_questions(filename="questions.json"):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(base_dir, 'static', 'questions', filename)
    if not os.path.exists(filepath):
        flash("Question file not found. Loading default questions.", "warning")
        filepath = os.path.join(base_dir, 'static', 'questions', 'default_questions.json')
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            questions = json.load(file)
    except json.JSONDecodeError:
        flash("Error loading questions. Please check the question file format.", "error")
        return []
    random.shuffle(questions)
    return questions

@main.route("/quiz", methods=["GET", "POST"])
def quiz():
    form = QuizForm()
    questions = session.get('questions', [])  # Default to an empty list if not found

    if 'filter' in request.args or not questions:
        question_file = request.args.get('filter', 'questions.json')
        questions = load_questions(question_file)
        session['questions'] = questions
        session['current_index'] = 0
        session.modified = True

    current_index = session.get('current_index', 0)

    # Redirect to quiz completion if there are no questions or all questions have been answered
    if not questions or current_index >= len(questions):
        return redirect(url_for('.quiz_complete'))

    current_question = questions[current_index]
    form.choice.choices = [(str(i), choice) for i, choice in enumerate(current_question.get('choices', []))]

    # Additional logic remains unchanged
    if request.method == 'POST' and 'skip' in request.form:
        session['skipped_answers'] = session.get('skipped_answers', 0) + 1
        session['current_index'] = current_index + 1
        session.modified = True
        return redirect(url_for('.quiz'))

    if form.validate_on_submit():
        correct_answer = str(current_question['answer'])
        if form.choice.data == correct_answer:
            session['correct_answers'] = session.get('correct_answers', 0) + 1
            feedback = "🥳 Correct!"
        else:
            session['wrong_answers'] = session.get('wrong_answers', 0) + 1
            feedback = f"🛹 💥 {correct_answer}."
        flash(feedback, 'info')
        session['current_index'] = current_index + 1
        session.modified = True
        return redirect(url_for('.quiz'))

    return render_template("quiz.html", question=current_question, form=form, countdown_duration=35)

@main.route('/quiz_complete')
def quiz_complete():
    results = {key: session.pop(key, 0) for key in ['correct_answers', 'wrong_answers', 'skipped_answers']}
    session.pop('questions', None)
    session.pop('current_index', None)
    session.modified = True
    return render_template("quiz_complete.html", **results)

@main.route('/donate')
def donate():
    return render_template("donate.html")

@main.route('/feedback', methods=['GET', 'POST'])
def feedback():  # Renamed from donate to feedback
    # Function body remains the same
    return render_template("feedback.html")


@main.route('/set_language/<language>')
def set_language(language):
    session['lang'] = language
    flash(f"Language set to {'English' if language == 'en' else 'French'}.", "info")
    session.modified = True
    return redirect(request.referrer or url_for('.home'))

@main.route("/")
def home():
    return render_template("home.html", lang=session.get('lang', 'en'))

# Flask application error handlers
@main.app_errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404


@main.app_errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500

@main.route('/handle_feedback', methods=['POST'])
def handle_feedback():
    emoji_feedback = request.form.get('emojiFeedback')
    DATABASE_PATH = os.path.join(current_app.root_path, 'static', 'misc', 'feedback.db')

    if emoji_feedback:
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO feedback (emoji) VALUES (?)', (emoji_feedback,))
            conn.commit()
            flash("Feedback received!", "success")
        except sqlite3.Error as e:
            current_app.logger.error(f"Database error: {e}")
            flash("An error occurred while saving your feedback.", "error")
        finally:
            conn.close()
    else:
        flash("No feedback received. Please select an emoji.", "error")

    return redirect(url_for('main.feedback'))