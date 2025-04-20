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
            is_correct = True
        else:
            session["score"] -= 10
            result = f"Wrong! Correct answer: {correct_case}, {correct_use}"
            is_correct = False

        return render_template("index.html",
                               quote=session["quote"]["text"],
                               score=session["score"],
                               result=result,
                               submitted=True,
                               is_correct=is_correct)

    return render_template("index.html",
                           quote=session["quote"]["text"],
                           score=session["score"],
                           result=None,
                           submitted=False,
                           is_correct=None)

@app.route("/next")
def next_quote():
    session["quote"] = random.choice(QUOTES)
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)