import os
import random
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from data import QUOTES, NOVICE_QUOTES

app = Flask(__name__)
# Use an environment variable for secret key in production
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")

# Store sessions on the filesystem so data persists across requests
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def pick_quote():
    """Return a random quote dict based on the chosen mode."""
    if session.get("mode") == "novice":
        return random.choice(NOVICE_QUOTES)
    else:
        return random.choice(QUOTES)

@app.route("/", methods=["GET", "POST"])
def index():
    # If mode not chosen yet, show mode selection
    if "mode" not in session:
        return render_template("mode.html")

    # Initialize counters if needed
    session.setdefault("score", 0)
    session.setdefault("correct", 0)
    session.setdefault("incorrect", 0)

    # Pick an initial quote if none in session
    if "quote" not in session:
        session["quote"] = pick_quote()

    quote_data = session["quote"]
    quote_text = quote_data.get("quote", "")

    if request.method == "POST":
        selected_case = request.form["case"]
        selected_use = request.form["use"]

        correct_case = quote_data["case"]
        correct_use = quote_data["use"]

        # Check answer
        points = 10 if session["mode"] == "novice" else 15
        if selected_case == correct_case and selected_use in correct_use:
            session["score"] += points
            session["correct"] += 1
            result = "✅ Correct!"
        else:
            session["score"] -= points
            session["incorrect"] += 1
            result = f"❌ Wrong! Correct answer: {correct_case}, {correct_use}"  # Display full word

        # Render result, but keep the same quote on screen until user clicks Next
        return render_template("index.html",
                               quote=quote_text,
                               score=session["score"],
                               correct=session["correct"],
                               incorrect=session["incorrect"],
                               result=result,
                               submitted=True)

    # GET request: show quiz with no result yet
    return render_template("index.html",
                           quote=quote_text,
                           score=session["score"],
                           correct=session["correct"],
                           incorrect=session["incorrect"],
                           submitted=False)

@app.route("/next_quote")
def next_quote():
    # Choose a new quote for the quiz
    session["quote"] = pick_quote()
    return redirect(url_for("index"))

@app.route("/choose_mode", methods=["POST"])
def choose_mode():
    # Set mode to 'novice' or 'literature' and reset stats
    mode = request.form.get("mode", "novice")
    session["mode"] = mode
    session["score"] = 0
    session["correct"] = 0
    session["incorrect"] = 0
    session.pop("quote", None)
    return redirect(url_for("index"))

@app.route("/set_mode/<mode>")
def set_mode(mode):
    # Set mode to 'novice' or 'literature'
    session["mode"] = mode
    session["score"] = 0
    session["correct"] = 0
    session["incorrect"] = 0
    session.pop("quote", None)
    return redirect(url_for("index"))

@app.route("/mode")
def mode():
    # This route renders the mode selection page
    return render_template("mode.html")

@app.route('/select_cases', methods=['GET', 'POST'])
def select_cases():
    if request.method == 'POST':
        selected_cases = request.form.getlist('cases')
        selected_set = request.form.get('quote_set')

        if not selected_cases or not selected_set:
            return redirect(url_for('select_cases'))

        # Choose the quote set
        all_quotes = NOVICE_QUOTES if selected_set == 'novice' else QUOTES

        # Filter quotes matching selected cases
        filtered_quotes = [q for q in all_quotes if q['case'] in selected_cases]

        session['selected_quotes'] = filtered_quotes
        session['mode'] = 'selected'
        session['score'] = 0
        session['correct'] = 0
        session['incorrect'] = 0
        session['points'] = 10 if selected_set == 'novice' else 15

        return redirect(url_for('quiz'))

    return render_template('select_cases.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'selected_quotes' not in session or not session['selected_quotes']:
        return redirect(url_for('select_cases'))  # Fallback if session expired

    if request.method == 'POST':
        selected_case = request.form.get('case')
        selected_use = request.form.get('use')
        correct_case = session.get('current_case')
        correct_use = session.get('current_use')

        submitted = True
        if selected_case == correct_case and selected_use == correct_use:
            session['score'] += session.get('points', 10)
            session['correct'] += 1
            result = "Correct!"
        else:
            session['incorrect'] += 1
            result = f"Incorrect. Correct answer: {correct_case.title()}, {correct_use.title()}"
    else:
        submitted = False
        result = ""

    # Pick a new quote
    quote_data = random.choice(session['selected_quotes'])
    session['current_case'] = quote_data['case']
    session['current_use'] = quote_data['use']
    quote = quote_data['quote']

    return render_template('quiz.html',
                           quote=quote,
                           submitted=submitted,
                           result=result,
                           score=session.get('score', 0),
                           correct=session.get('correct', 0),
                           incorrect=session.get('incorrect', 0))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Bind to 0.0.0.0 for Render compatibility
    app.run(debug=True, host="0.0.0.0", port=port)