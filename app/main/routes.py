from flask import Blueprint, flash, make_response, redirect, render_template, request, session, Flask, url_for
from datetime import datetime
import random
import json
import os
import time

main = Blueprint("main", __name__)

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask import render_template

class QuizForm(FlaskForm):
    # assuming you have some fields for your quiz
    submit = SubmitField('Submit')

# Load questions from a JSON file
def load_questions():
    with open(os.path.join(os.path.dirname(__file__), 'questions.json'), 'r', encoding='utf-8') as file:
        return json.load(file)

from flask import render_template, request, session, redirect, url_for
import random

# Assuming load_questions() and QuizForm are defined elsewhere
@main.route("/quiz", methods=["GET", "POST"])
def quiz():
    form = QuizForm()
    questions = load_questions()

    if "remaining_questions" not in session or request.method == "GET":
        session["remaining_questions"] = list(range(len(questions)))

    if request.method == "POST":
        try:
            user_answer = request.form.get("choice")
            question_id = int(request.form.get("question_id", 0))
            question = questions[question_id]

            # Assuming session["lang"] is set and correct_feedback, wrong_feedback are defined
            lang = session.get("lang", "en")
            feedback = "Correct answer!" if user_answer == question.get("answer", "") else "Wrong answer! The correct answer was: " + question.get("answer", "")
            
            session["remaining_questions"].remove(question_id)
        except (KeyError, IndexError, ValueError):
            feedback = "An error occurred. Moving to the next question."

        if not session["remaining_questions"]:
            session["remaining_questions"] = list(range(len(questions)))

        next_question_id = random.choice(session["remaining_questions"])
        next_question = questions[next_question_id]

        return render_template("quiz.html", question=next_question, feedback=feedback, question_id=next_question_id, form=form)

    # For GET requests or if no questions are left
    if not session["remaining_questions"]:
        return "No more questions or session not started."
    question_id = session["remaining_questions"][0]
    question = questions[question_id]
    return render_template("quiz.html", question=question, question_id=question_id, form=form)


@main.route('/set_language/<language>')
def set_language(language):
    session['lang'] = language
    redirect_url = url_for('.quiz') if 'quiz' in request.referrer else url_for('.home')
    return redirect(redirect_url)

@main.route("/")
@main.route("/home")
def home():
    return render_template("home.html")
