from flask import Flask, render_template, request, redirect, url_for, session
import random
from data import QUOTES, NOVICE_QUOTES

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Route to select mode (novice or literature)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_mode/<mode>')
def set_mode(mode):
    session['mode'] = mode
    if mode == "novice":
        session['quote'] = random.choice(NOVICE_QUOTES)
    else:
        session['quote'] = random.choice(QUOTES)
    
    return redirect(url_for('quiz'))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'quote' not in session:
        return redirect(url_for('index'))
    
    quote = session['quote']
    if request.method == 'POST':
        selected_case = request.form['case']
        selected_use = request.form['use']
        
        correct_case = quote['case']
        correct_use = quote['use']
        
        if selected_case == correct_case and selected_use in correct_use:
            result = "Correct!"
        else:
            result = f"Incorrect. The correct case is {correct_case} and the use is {', '.join(correct_use)}."
        
        session['correct'] = session.get('correct', 0) + (1 if selected_case == correct_case and selected_use in correct_use else 0)
        session['incorrect'] = session.get('incorrect', 0) + (0 if selected_case == correct_case and selected_use in correct_use else 1)
        session['result'] = result
        
        # Select a new quote for the next round
        if session['mode'] == "novice":
            session['quote'] = random.choice(NOVICE_QUOTES)
        else:
            session['quote'] = random.choice(QUOTES)
    
    return render_template('quiz.html', quote=quote, result=session.get('result', ''), score=session.get('correct', 0), correct=session.get('correct', 0), incorrect=session.get('incorrect', 0))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
