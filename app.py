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
        quote_set = request.form.get('quote_set')
        if selected_cases and quote_set:
            session['selected_cases'] = selected_cases
            session['quote_set'] = quote_set
            session['mode'] = 'selected'  # So your quiz logic knows to use this filter
            return redirect(url_for('quiz'))
        else:
            return "Please select at least one case and a quote set.", 400
    return render_template('select_cases.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    # Get selected cases and quote set from the session
    selected_cases = session.get('selected_cases', [])
    quote_set = session.get('quote_set', 'novice')  # Default to 'novice' if nothing is selected

    # Fetch quotes based on selected cases and quote set
    if quote_set == 'novice':
        quotes = NOVICE_QUOTES
    else:
        quotes = QUOTES

    # Filter the quotes based on the selected cases
    filtered_quotes = [quote for quote in quotes if quote['case'] in selected_cases]

    # Pick a random quote for the quiz
    if filtered_quotes:
        quote = random.choice(filtered_quotes)
    else:
        quote = None  # No quotes to show if no match

    # Handle form submission
    if request.method == 'POST':
        case_answer = request.form.get('case')
        use_answer = request.form.get('use')

        # Check if the answer is correct and return feedback
        correct_case = quote['case'] == case_answer
        correct_use = quote['use'] == use_answer
        result = 'Correct!' if correct_case and correct_use else 'Incorrect'

        # Track score (you can store score in session if necessary)
        return render_template('quiz.html', quote=quote, result=result)

    # Render the quiz page
    return render_template('quiz.html', quote=quote)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Bind to 0.0.0.0 for Render compatibility
    app.run(debug=True, host="0.0.0.0", port=port)