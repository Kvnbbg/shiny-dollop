import sqlite3
from flask import Blueprint, jsonify, render_template, request, session, redirect, url_for, flash, current_app
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, RadioField, HiddenField, SubmitField
from wtforms.validators import DataRequired
import os
import json
import random
from app.main.flashcards_storage import load_flashcard_store, save_flashcard_store

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
        session['current_index'] = 0  # Reset the current index to 0 when loading new questions to avoid out of range errors
        session.modified = False  # Set to False to avoid creating a new session cookie on redirect

    current_index = session.get('current_index', 0) # Default to 0 if not found

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
            feedback = "🥳 Correct! {correct_answer}"
        else:
            session['wrong_answers'] = session.get('wrong_answers', 0) + 1
            feedback = f"💥 {correct_answer}"
        flash(feedback, 'info')
        session['current_index'] = current_index + 1
        session.modified = False  # Set to False to avoid creating a new session cookie on redirect
        return redirect(url_for('.quiz'))

    return render_template("quiz.html", question=current_question, form=form, countdown_duration=35, current_index=current_index + 1, total_questions=len(questions), form_name=form.__class__.__name__) # Add form_name to the context

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


@main.route("/flashcards")
def flashcards():
    return render_template("flashcards.html")


@main.route("/api/flashcards", methods=["GET"])
def flashcard_store():
    return jsonify(load_flashcard_store())


@main.route("/api/flashcards/sets", methods=["POST"])
def create_flashcard_set():
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    cards = payload.get("cards") or []
    if not title or not isinstance(cards, list):
        return jsonify({"error": "Title and cards are required."}), 400

    store = load_flashcard_store()
    normalized_cards = [
        {"front": card.get("front", "").strip(), "back": card.get("back", "").strip()}
        for card in cards
        if card.get("front") and card.get("back")
    ]
    if not normalized_cards:
        return jsonify({"error": "At least one valid card is required."}), 400

    set_id = (payload.get("id") or title.lower().replace(" ", "-")).strip()
    new_set = {
        "id": set_id,
        "title": title,
        "description": (payload.get("description") or "").strip(),
        "tags": payload.get("tags") or [],
        "difficulty": payload.get("difficulty") or "medium",
        "cards": normalized_cards,
    }
    store.setdefault("sets", []).append(new_set)
    save_flashcard_store(store)
    return jsonify(new_set), 201


@main.route("/api/flashcards/progress", methods=["POST"])
def update_flashcard_progress():
    payload = request.get_json(silent=True) or {}
    points = int(payload.get("points", 0))
    streak = int(payload.get("streak", 0))
    store = load_flashcard_store()
    stats = store.setdefault("stats", {})
    stats["total_points"] = int(stats.get("total_points", 0)) + points
    stats["sessions"] = int(stats.get("sessions", 0)) + 1
    stats["best_streak"] = max(int(stats.get("best_streak", 0)), streak)
    save_flashcard_store(store)
    return jsonify({"status": "ok", "stats": stats})

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
