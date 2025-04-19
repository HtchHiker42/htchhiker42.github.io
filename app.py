import os
from flask import Flask, render_template, request, redirect, url_for, session
import random
from data import QUOTES

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.route("/", methods=["GET", "POST"])
def index():
    if "score" not in session:
        session["score"] = 0
    if "quote" not in session:
        session["quote"] = random.choice(QUOTES)

    if request.method == "POST":
        case = request.form.get("case")
        use = request.form.get("use")

        correct_case = session["quote"]["case"]
        correct_use = session["quote"]["use"]

        if case == correct_case and use == correct_use:
            session["score"] += 10
            result = "Correct!"
        else:
            session["score"] -= 10
            result = f"Wrong! Correct answer: {correct_case}, {correct_use}"

        # Store the result and disable the submit button after submission
        session["submitted"] = True
        return render_template("index.html",
                               quote=session["quote"]["text"],
                               score=session["score"],
                               result=result,
                               submitted=True)

    return render_template("index.html",
                           quote=session["quote"]["text"],
                           score=session["score"],
                           result=None,
                           submitted=False)

@app.route("/next")
def next_quote():
    session["quote"] = random.choice(QUOTES)
    session["submitted"] = False  # Reset submission state for next quote
    return redirect(url_for("index"))

if __name__ == "__main__":
    # Dynamically use the PORT environment variable if available (for deployment)
    port = int(os.environ.get("PORT", 5000))  # Default to 5000 for local dev
    app.run(debug=True, host="0.0.0.0", port=port)