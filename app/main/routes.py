from datetime import datetime
from flask import Blueprint, flash, make_response, redirect, render_template, request, url_for, session, Flask
import random

# Define a blueprint for your Flask application
main = Blueprint("main", __name__)

# Les questions du quiz
questions = [
    {"question": "Quel est le principe fondamental des API RESTful ?",
     "choices": ["Étatless (Sans état)", "Utiliser uniquement XML", "Conserver l'état sur le serveur"],
     "answer": "Étatless (Sans état)"},
    # Ajoutez d'autres questions ici
]

@app.route("/", methods=["GET", "POST"])
def quiz():
    if request.method == "POST":
        # Obtenez la réponse de l'utilisateur
        user_answer = request.form.get("choice")
        # Obtenez la question actuelle
        question = questions[0]  # Pour cet exemple, prenez toujours la première question
        
        if user_answer == question["answer"]:
            feedback = "Bonne réponse !"
        else:
            feedback = "Mauvaise réponse ! La bonne réponse était : " + question["answer"]
        
        # Sélection aléatoire d'une nouvelle question pour le prochain tour
        next_question = random.choice(questions)
        return render_template("quiz.html", question=next_question, feedback=feedback)

    # Commencez le jeu avec une question aléatoire
    question = random.choice(questions)
    return render_template("quiz.html", question=question)


@main.route('/set_language/<language>')
def set_language(language):
    session['lang'] = language
    return redirect(url_for('home'))




def improved_home_with_maintenance_date():
    """
    Renders the home page with dynamic messages and displays the duration since the maintenance started.
    This function assumes it's being called within a Flask route.
    """
    # Get the current date and time
    now = datetime.now()
    formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")

    # Predefined maintenance start date (for illustration, adjust as needed)
    maintenance_start_date = datetime(2024, 1, 1, 0, 0, 0)
    formatted_maintenance_start_date = maintenance_start_date.strftime("%Y-%m-%d %H:%M:%S")

    # Calculate the duration since maintenance started
    duration_since_maintenance = now - maintenance_start_date
    days_since_maintenance = duration_since_maintenance.days

    # Get the last visited date and visit count from the cookies
    request.cookies.get("last_visited")
    visit_count = request.cookies.get("visit_count", 0)
    # Convert visit_count to int and increment
    visit_count = int(visit_count) + 1

    # Dynamic messages list
    dynamic_messages = [
        f"Site has been in maintenance since {formatted_maintenance_start_date}.",
        f"{days_since_maintenance} days since maintenance began. We apologize for any inconvenience.",
        "Thank you for your patience during our maintenance period."
    ]
    # Select a dynamic message based on the visit count
    message_index = visit_count % len(dynamic_messages)
    dynamic_message = dynamic_messages[message_index]

    # Flash the dynamic message
    flash(dynamic_message, "warning")  # 'warning' for maintenance notices

    # Prepare the response and set cookies
    response = make_response(render_template("home.html"))
    response.set_cookie("last_visited", formatted_now, max_age=60*60*24*365*2) # 2 years
    response.set_cookie("visit_count", str(visit_count), max_age=60*60*24*365*2) # 2 years

    return response

@main.route("/")
@main.route("/home")
def home():
    """
    Renders the home page and displays a maintenance message.
    This function calls the improved_home_with_maintenance_date function to handle the logic.
    """
    return improved_home_with_maintenance_date()
