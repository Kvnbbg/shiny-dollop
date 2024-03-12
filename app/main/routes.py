from flask import Blueprint, render_template, request, session, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import SubmitField
import os
import json
import random

main = Blueprint("main", __name__)

class QuizForm(FlaskForm):
    submit = SubmitField('Submit')

def load_questions():
    """Load questions from the JSON file."""
    filepath = os.path.join(os.path.dirname(__file__), 'questions.json')
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

@main.route("/quiz", methods=["GET", "POST"])
def quiz():
    form = QuizForm()
    questions = load_questions()

    if "remaining_questions" not in session or request.method == "GET":
        session["remaining_questions"] = list(range(len(questions)))

    if request.method == "POST":
        user_answer = request.form.get("choice")
        question_id = int(request.form.get("question_id", 0))
        if question_id in session["remaining_questions"]:
            question = questions[question_id]
            correct_answer = question.get("answer", "")
            feedback = "Correct answer!" if user_answer == correct_answer else f"Wrong answer! The correct answer was: {correct_answer}"
            session["remaining_questions"].remove(question_id)
        else:
            feedback = "An error occurred. Moving to the next question."

        if not session["remaining_questions"]:
            # Reset the questions if all have been answered
            return redirect(url_for('.quiz_complete'))

        next_question_id = random.choice(session["remaining_questions"])
        next_question = questions[next_question_id]
        return render_template("quiz.html", question=next_question, feedback=feedback, question_id=next_question_id, form=form)

    # Handle GET request
    question_id = random.choice(session["remaining_questions"])
    question = questions[question_id]
    return render_template("quiz.html", question=question, question_id=question_id, form=form)

@main.route('/quiz_complete')
def quiz_complete():
    """Display the quiz completion message and reset the session."""
    session.pop('remaining_questions', None)  # Clean up session
    return render_template("quiz_complete.html")

@main.route('/set_language/<language>')
def set_language(language):
    """Set the preferred language in the session."""
    session['lang'] = language
    return redirect(request.referrer or url_for('.home'))

@main.route("/")
@main.route("/home")
def home():
    """Render the home page."""
    return render_template("home.html")
