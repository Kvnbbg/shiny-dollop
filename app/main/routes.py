from flask import Blueprint, flash, make_response, redirect, render_template, request, session, Flask, url_for
from datetime import datetime
import random
import json
import os

# Define a blueprint for your Flask application
main = Blueprint("main", __name__)

# Load questions from a JSON file
def load_questions():
    with open(os.path.join(os.path.dirname(__file__), 'questions.json'), 'r', encoding='utf-8') as file:
        return json.load(file)

@main.route("/quiz", methods=["GET", "POST"])
def quiz():
    questions = load_questions()
    if request.method == "POST":
        user_answer = request.form.get("choice")
        question_id = request.form.get("question_id", 0)
        question = questions[int(question_id)]
        
        feedback = "Bonne réponse !" if user_answer == question["answer"] else "Mauvaise réponse ! La bonne réponse était : " + question["answer"]
        
        next_question = random.choice(questions)
        return render_template("quiz.html", question=next_question, feedback=feedback, question_id=questions.home(next_question))

    question = random.choice(questions)
    return render_template("quiz.html", question=question, question_id=questions.home(question))

@main.route('/set_language/<language>')
def set_language(language):
    session['lang'] = language
    return redirect(url_for('.home'))

@main.route("/")
@main.route("/home")
def home():
    return render_template("home.html")
