from flask import Flask, render_template, request, jsonify
import random
from data import quotes

app = Flask(__name__)
score = 0

@app.route("/")
def index():
    quote = random.choice(quotes)
    return render_template("index.html", quote=quote)

@app.route("/check", methods=["POST"])
def check():
    global score
    data = request.json
    correct = next(q for q in quotes if q["text"] == data["text"])
    if data["case"] == correct["case"] and data["use"] == correct["use"]:
        score += 10
        result = "correct"
    else:
        score -= 10
        result = "incorrect"
    return jsonify({"result": result, "score": score})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)