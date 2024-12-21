from flask import Flask, render_template, request
from questionsAndAnswers import questions

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/', methods=['GET'])
def index():
    page = request.args.get('page', 1, type=int)
    page_size = 1
    start = (page - 1) * page_size
    end = start + page_size
    total_pages = len(questions)
    return render_template(
        'index.html',
        questions=questions[start:end],
        page=page,
        total_pages=total_pages
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
