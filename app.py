from flask import Flask, render_template, request, abort, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func, or_
from flask import jsonify
import random
import os
from utils.nav import get_nav_items
from utils.quiz_db import get_random_questions, get_question_by_id

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'example.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Avoids a warning
db = SQLAlchemy(app)

@app.context_processor
def inject_nav():
    # Provide `nav_items` to all templates; scanning templates folder for links
    try:
        nav_items = get_nav_items()
    except Exception:
        nav_items = []
    return {'nav_items': nav_items}

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

class STUDENT(db.Model):
    ID = db.Column(db.String(255), primary_key=True, nullable=False)
    NAME = db.Column(db.String(25), nullable=False )
    CLASS = db.Column(db.String(25))
    Score = db.Column(db.Integer)

class Thesis(db.Model):
    ID = db.Column(db.String(25), primary_key = True, nullable=False)
    Author = db.Column(db.String(25),nullable = False)
    Category = db.Column(db.String(25), nullable = False)
    Supervisor = db.Column(db.String(25), nullable = False)
    Name = db.Column(db.String(255),nullable = False)
    File_name = db.Column(db.String(25), nullable = False)

class question(db.Model):
    ID = db.Column(db.String(255) , primary_key = True , nullable = False)
    QName = db.Column(db.String(255), nullable = False)
    CorrectA = db.Column(db.String(25), nullable = False)
    DecoyB = db.Column(db.String(25), nullable = False)
    DecoyC = db.Column(db.String(25), nullable = False)
    DecoyD = db.Column(db.String(25), nullable = False)

@app.route('/')
def main_home():
    return render_template('home.html')

@app.route('/learning')
def to_learning():
    return render_template('quiz/learning.html')

@app.route('/thesis')
def to_thesis():
    return render_template('thesis_archive/thesis.html')

@app.route('/vnmap')
def to_vnmap():
    return render_template('vnmap.html')

@app.route('/gallery/')
def to_gallery():
    # gallery.html not present; show a simple placeholder list or redirect
    # If you have a gallery template, replace with its path.
    return render_template('home.html')

@app.route('/gallery/infographic')
def to_infographic():
    # infographic template not found; reuse thesis search result as placeholder
    return render_template('thesis_archive/thesis_search_result.html')

@app.route('/library/')
def to_library():
    return render_template('music_library/library.html')

# Alias route matching nav hrefs generated from templates folder
@app.route('/music_library/library')
def to_music_library_alias():
    return render_template('music_library/library.html')

@app.route('/music_world/')
def to_musicworld():
    return render_template('music_world.html')

@app.route('/music_world/3dpreview/')
def to_3dpreview():
    return render_template('3d_model_viewer/3dpreview.html')
@app.route('/music_world/3dpreview/<string:inname>')
def render_3d(inname):
    filename= inname+ ".glb"
    return render_template('3d_model_viewer/3d_view.html', modelname=filename)

@app.route('/testdb')
def test_db():
    profiles = db.session.query(STUDENT).all()
    return render_template('quiz/testdb.html', profiles=profiles)

@app.route('/thesis/search')
def search_thesis():
    q = request.args.get("q", "")
    search_pattern = f"%{q}%"
    result = db.session.execute(db.select(Thesis).where(or_(
        Thesis.Name.like(search_pattern),
        Thesis.ID.like(search_pattern),
        Thesis.Author.like(search_pattern),
        Thesis.Supervisor.like(search_pattern),
        Thesis.Category.like(search_pattern)
    ))).scalars()
    return render_template('thesis_archive/thesis_search_result.html', result = result)
    
@app.route('/thesis/<thesisname>')
def serve_thesis_pdf(thesisname):
    filename = f"{os.path.basename(thesisname)}.pdf"
    directory = os.path.join(app.root_path, 'templates')
    return send_from_directory(directory, filename, as_attachment=False)

@app.route('/quiz/')
def to_quiz():
    return render_template('quiz/quiz.html')

@app.route('/quiz/question')
def to_quest():
    data = get_random_questions(db, limit=3)
    return render_template('quiz/question.html', questions=data)

def fetch_all_relevant_questions(form_keys):
    question_ids = list(form_keys)
    questions_db = db.session.execute(db.select(question).where(question.ID.in_(question_ids))).scalars().all()
    return {q.ID: q for q in questions_db}

def compare_user_answer(user_answer, correct_answer):
    return user_answer == correct_answer

def save_details_for_result_page(actual_question, user_answer, is_correct):
    return {
        'question': actual_question.QName,
        'your_answer': user_answer,
        'correct_answer': actual_question.CorrectA,
        'is_correct': is_correct
    }

@app.route("/submit-quiz", methods=["POST"])
def submit_quiz():
    score = 0
    total_questions = 0
    results_summary = []
    
    question_map = fetch_all_relevant_questions(request.form.keys())

    for q_id, user_answer in request.form.items():
        actual_question = question_map.get(q_id)

        if actual_question:
            total_questions += 1
            is_correct = compare_user_answer(user_answer, actual_question.CorrectA)
            if is_correct:
                score += 1
            
            results_summary.append(save_details_for_result_page(actual_question, user_answer, is_correct))

    return render_template('quiz/quiz_result.html', 
                           score=score, 
                           total=total_questions, 
                           summary=results_summary)





@app.route('/<path:subpath>')
def spa_catch_all(subpath: str):
    # For any other GET route not matched above, serve the SPA shell.
    return render_template('home.html')


# Alias routes to match nav hrefs created from templates folder

@app.route('/thesis_archive/thesis')
def thesis_archive_alias():
    return render_template('thesis_archive/thesis.html')

@app.route('/quiz/learning')
def quiz_learning_alias():
    return render_template('quiz/learning.html')

@app.route('/quiz/quest')
def quiz_quest_alias():
    return render_template('quiz/quest.html')

@app.route('/quiz/quiz')
def quiz_quiz_alias():
    return render_template('quiz/quiz.html')

@app.route('/quiz/testdb')
def quiz_testdb_alias():
    return render_template('quiz/testdb.html')

@app.route('/3d_model_viewer/3dpreview')
def modelviewer_preview_alias():
    return render_template('3d_model_viewer/3dpreview.html')


if __name__ == '__main__':
    with app.app_context():  # Needed for DB operations outside a request
        db.create_all()      # Creates the database and tables
        db.Model.metadata.reflect(db.engine)
        print("Reflected tables:", db.Model.metadata.tables.keys())
        print("Database file URI:", app.config['SQLALCHEMY_DATABASE_URI'])
    app.run(host='0.0.0.0', port=3000, debug=True)